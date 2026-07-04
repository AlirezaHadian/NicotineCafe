using NicotineCafe.Core.DTOs;

namespace NicotineCafe.Core.Interfaces;

/// <summary>
/// Abstraction over the connection to the Python voice-recognition engine.
/// Implemented by NicotineCafe.Services.SpeechEngineClient (TCP loopback).
/// </summary>
public interface ISpeechEngineClient : IAsyncDisposable
{
    event EventHandler<RecognizedProductMessage>? ProductRecognized;
    event EventHandler<double>? AudioLevelChanged; // 0.0–1.0, for the equalizer UI
    event EventHandler<bool>? ConnectionStateChanged;

    Task ConnectAsync(CancellationToken ct = default);
    Task DisconnectAsync();
    Task SendCommandAsync(string commandType, CancellationToken ct = default);
    bool IsConnected { get; }
}
