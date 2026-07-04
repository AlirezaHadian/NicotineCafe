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
        services.AddSingleton<IProductRepository, SqliteProductRepository>();

        // --- Service layer ---
        services.AddSingleton<IProductService, ProductService>();
        services.AddSingleton<ISpeechEngineClient>(_ => new SpeechEngineClient());
        services.AddSingleton(_ => new VoiceEngineProcessLauncher(
            pythonExe: "python",
            scriptPath: System.IO.Path.Combine(AppContext.BaseDirectory, "voice-engine", "main.py"),
            dbPath: dbPath,
            port: 8765,
            // If you have a pre-downloaded faster-whisper model folder (no internet needed),
            // point this at it, e.g.: @"C:\models\faster-whisper-base"
            modelPath: null));

        // --- ViewModels / Windows ---
        services.AddSingleton<MainViewModel>();
        services.AddSingleton<MainWindow>();

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
