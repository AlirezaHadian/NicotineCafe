using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Data;
using NicotineCafe.Services;
using NicotineCafe.WPF.ViewModels;

namespace NicotineCafe.WPF;

public partial class App : Application
{
    public static IServiceProvider Services { get; private set; } = null!;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var dbPath = System.IO.Path.Combine(AppContext.BaseDirectory, "Data", "nicotinecafe.db");

        var services = new ServiceCollection();

        // --- Data layer ---
        services.AddSingleton(new SqliteConnectionFactory(dbPath));
        services.AddSingleton<IBrandRepository, SqliteBrandRepository>();
        services.AddSingleton<IEngineSettingsRepository, SqliteEngineSettingsRepository>();

        // --- Service layer ---
        services.AddSingleton<IBrandService, BrandService>();
        services.AddSingleton<ISpeechEngineClient>(_ => new SpeechEngineClient());

        // Prefer a bundled, private copy of Python (python-embed\python.exe next
        // to the exe) so the installer doesn't depend on Python being installed
        // system-wide at all. Falls back to "python" on PATH if not bundled —
        // useful during development.
        var bundledPython = System.IO.Path.Combine(AppContext.BaseDirectory, "python-embed", "python.exe");
        var pythonExe = System.IO.File.Exists(bundledPython) ? bundledPython : "python";

        // Prefer a bundled, pre-downloaded Whisper model cache (Data\models\)
        // so the app never needs internet at all, even on first run. This is
        // the SAME folder server.py pins its faster-whisper download_root to
        // (derived from --db's parent directory) — keep both in sync so
        // there's exactly one place to pre-populate, not two that could
        // disagree. See the installer guide for how to fill this folder.
        var bundledModelCache = System.IO.Path.Combine(AppContext.BaseDirectory, "Data", "models");
        var hfHomeDir = System.IO.Directory.Exists(bundledModelCache) ? bundledModelCache : null;

        services.AddSingleton(_ => new VoiceEngineProcessLauncher(
            pythonExe: pythonExe,
            scriptPath: System.IO.Path.Combine(AppContext.BaseDirectory, "voice-engine", "main.py"),
            dbPath: dbPath,
            port: 8765,
            modelPath: null,
            hfHomeDir: hfHomeDir));

        // --- ViewModels / Windows ---
        services.AddSingleton<MainViewModel>();
        services.AddSingleton<MainWindow>();
        services.AddTransient<ViewModels.AdminViewModel>();
        services.AddTransient<Views.AdminWindow>();

        Services = services.BuildServiceProvider();

        var launcher = Services.GetRequiredService<VoiceEngineProcessLauncher>();
        launcher.StartupFailed += (_, message) =>
            MessageBox.Show($"موتور تشخیص گفتار استارت نشد:\n\n{message}\n\n" +
                             $"جزئیات کامل در voice-engine.log کنار فایل اجرایی.",
                             "خطای راه‌اندازی موتور صدا", MessageBoxButton.OK, MessageBoxImage.Warning);
        launcher.Start();

        var window = Services.GetRequiredService<MainWindow>();
        window.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        (Services.GetService<VoiceEngineProcessLauncher>())?.Dispose();
        base.OnExit(e);
    }
}
