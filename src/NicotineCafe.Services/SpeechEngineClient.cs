using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using NicotineCafe.Core.DTOs;
using NicotineCafe.Core.Interfaces;

namespace NicotineCafe.Services;

/// <summary>
/// TCP loopback client for the Python voice engine.
/// Protocol: newline-delimited JSON, one RecognizedBrandMessage per line.
/// The Python side is started as a child process by the WPF app
/// (see ProcessLauncher) and listens on 127.0.0.1:{port}.
/// </summary>
public sealed class SpeechEngineClient : ISpeechEngineClient
{
    private readonly string _host;
    private readonly int _port;
    private TcpClient? _client;
    private CancellationTokenSource? _readCts;

    public event EventHandler<RecognizedBrandMessage>? BrandRecognized;
    public event EventHandler<double>? AudioLevelChanged;
    public event EventHandler<bool>? ConnectionStateChanged;

    public bool IsConnected => _client?.Connected ?? false;

    public SpeechEngineClient(string host = "127.0.0.1", int port = 8765)
    {
        _host = host;
        _port = port;
    }

    /// <summary>
    /// Keeps retrying until connected or cancelled. The engine process can
    /// take many seconds to start (Whisper model load, first-run download),
    /// so a single connect attempt right at app startup is not enough.
    /// </summary>
    public async Task ConnectAsync(CancellationToken ct = default)
    {
        var delay = TimeSpan.FromSeconds(1);
        while (!ct.IsCancellationRequested)
        {
            try
            {
                _client = new TcpClient();
                await _client.ConnectAsync(_host, _port, ct);
                _readCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                _ = Task.Run(() => ReadLoopAsync(_readCts.Token), _readCts.Token);
                ConnectionStateChanged?.Invoke(this, true);
                return;
            }
            catch (Exception ex) when (ex is SocketException or IOException)
            {
                _client?.Dispose();
                _client = null;
                ConnectionStateChanged?.Invoke(this, false);
                try { await Task.Delay(delay, ct); } catch (OperationCanceledException) { return; }
                if (delay < TimeSpan.FromSeconds(5)) delay += TimeSpan.FromSeconds(1);
            }
        }
    }

    public Task DisconnectAsync()
    {
        _readCts?.Cancel();
        _client?.Close();
        return Task.CompletedTask;
    }

    public async Task SendCommandAsync(string commandType, CancellationToken ct = default)
    {
        if (_client is null || !_client.Connected) return;
        var line = JsonSerializer.Serialize(new { type = commandType }) + "\n";
        var bytes = Encoding.UTF8.GetBytes(line);
        await _client.GetStream().WriteAsync(bytes, ct);
    }

    private async Task ReadLoopAsync(CancellationToken ct)
    {
        if (_client is null) return;
        var stream = _client.GetStream();
        using var reader = new StreamReader(stream, Encoding.UTF8);

        try
        {
            while (!ct.IsCancellationRequested)
            {
                var line = await reader.ReadLineAsync(ct);
                if (line is null) break; // connection closed by engine
                if (string.IsNullOrWhiteSpace(line)) continue;

                Dispatch(line);
            }
        }
        catch (OperationCanceledException) { /* expected on disconnect */ }
        catch (IOException) { /* engine process died — WPF should restart it */ }
    }

    private void Dispatch(string jsonLine)
    {
        try
        {
            using var doc = JsonDocument.Parse(jsonLine);
            var type = doc.RootElement.GetProperty("type").GetString();

            if (type == "audio_level")
            {
                var level = doc.RootElement.GetProperty("level").GetDouble();
                AudioLevelChanged?.Invoke(this, level);
                return;
            }

            var msg = JsonSerializer.Deserialize<RecognizedBrandMessage>(jsonLine,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            if (msg is not null)
                BrandRecognized?.Invoke(this, msg);
        }
        catch (JsonException)
        {
            // malformed line from engine — ignore and keep reading
        }
    }

    public async ValueTask DisposeAsync()
    {
        _readCts?.Cancel();
        _client?.Dispose();
        await Task.CompletedTask;
    }
}
