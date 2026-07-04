using System.Diagnostics;

namespace NicotineCafe.Services;

/// <summary>
/// Starts/stops the Python voice-engine as a child process
/// (python main.py serve --port 8765 --db "path\to\nicotinecafe.db").
/// Kept separate from SpeechEngineClient so the WPF app can restart
/// the engine independently of the socket connection.
///
/// All stdout/stderr from the Python process is written to
/// "voice-engine.log" next to the exe — check that file first if the
/// UI stays stuck on "در انتظار گفتار".
/// </summary>
public sealed class VoiceEngineProcessLauncher : IDisposable
{
    private Process? _process;
    private readonly string _pythonExe;
    private readonly string _scriptPath;
    private readonly string _dbPath;
    private readonly int _port;
    private readonly string? _modelPath;
    private readonly string _logPath;

    public event EventHandler<string>? StartupFailed;

    public VoiceEngineProcessLauncher(string pythonExe, string scriptPath, string dbPath, int port = 8765, string? modelPath = null)
    {
        _pythonExe = pythonExe;
        _scriptPath = scriptPath;
        _dbPath = dbPath;
        _port = port;
        _modelPath = modelPath;
        _logPath = System.IO.Path.Combine(AppContext.BaseDirectory, "voice-engine.log");
    }

    public void Start()
    {
        if (_process is { HasExited: false }) return;

        if (IsSomethingAlreadyListening())
        {
            AppendLog($"[{DateTime.Now:u}] Port {_port} is already accepting connections — " +
                      "assuming a voice-engine from a previous run is still alive and reusing it " +
                      "instead of starting a duplicate. If recognition seems stuck, close ALL " +
                      "python.exe processes in Task Manager and restart the app.");
            return;
        }

        if (!File.Exists(_scriptPath))
        {
            Report($"main.py not found at: {_scriptPath}. " +
                   "Did the voice-engine folder get copied to the output directory?");
            return;
        }
        if (!File.Exists(_dbPath))
        {
            Report($"Database not found at: {_dbPath}. " +
                   "Copy database\\nicotinecafe.db.sample to Data\\nicotinecafe.db in the output folder, " +
                   "or check the csproj copy rule.");
            return;
        }

        var modelArg = string.IsNullOrWhiteSpace(_modelPath) ? "" : $" --model-path \"{_modelPath}\"";
        var psi = new ProcessStartInfo
        {
            FileName = _pythonExe,
            Arguments = $"\"{_scriptPath}\" serve --port {_port} --db \"{_dbPath}\"{modelArg}",
            WorkingDirectory = System.IO.Path.GetDirectoryName(_scriptPath),
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = System.Text.Encoding.UTF8,
            StandardErrorEncoding = System.Text.Encoding.UTF8,
        };
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        psi.EnvironmentVariables["PYTHONUTF8"] = "1";

        try
        {
            File.WriteAllText(_logPath, $"[{DateTime.Now:u}] Starting: {_pythonExe} {psi.Arguments}\n");
            _process = Process.Start(psi);
            if (_process is null)
            {
                Report($"Process.Start returned null for '{_pythonExe}'. Is Python installed and on PATH?");
                return;
            }

            _process.OutputDataReceived += (_, e) => AppendLog(e.Data);
            _process.ErrorDataReceived += (_, e) => AppendLog(e.Data);
            _process.BeginOutputReadLine();
            _process.BeginErrorReadLine();

            _process.Exited += (_, _) =>
            {
                if (_process.ExitCode != 0)
                    Report($"voice-engine process exited early with code {_process.ExitCode}. See voice-engine.log for details.");
            };
            _process.EnableRaisingEvents = true;
        }
        catch (System.ComponentModel.Win32Exception ex)
        {
            // Thrown when the FileName ('python') can't be found on PATH at all.
            Report($"Could not start '{_pythonExe}': {ex.Message}. " +
                   "Make sure Python is installed and 'python' is on PATH " +
                   "(try 'python3' or the full path to python.exe instead).");
        }
    }

    private bool IsSomethingAlreadyListening()
    {
        try
        {
            using var probe = new System.Net.Sockets.TcpClient();
            var task = probe.ConnectAsync("127.0.0.1", _port);
            return task.Wait(TimeSpan.FromMilliseconds(300)) && probe.Connected;
        }
        catch
        {
            return false;
        }
    }

    private void AppendLog(string? line)
    {
        if (line is null) return;
        try { File.AppendAllText(_logPath, line + Environment.NewLine); } catch { /* best-effort */ }
    }

    private void Report(string message)
    {
        AppendLog($"[ERROR] {message}");
        StartupFailed?.Invoke(this, message);
    }

    public void Stop()
    {
        if (_process is { HasExited: false })
        {
            _process.Kill(entireProcessTree: true);
        }
        _process = null;
    }

    public void Dispose() => Stop();
}
