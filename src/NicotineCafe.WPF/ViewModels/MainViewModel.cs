using System.Windows.Threading;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.WPF.ViewModels;

/// <summary>
/// Drives the single-brand display screen:
///  - listens to the (always-on, VAD-driven) speech engine for recognitions
///  - shows a BRAND card (name + image + "what we carry" model list) for up
///    to 5 minutes — recognition is brand-only now, no per-variant matching
///  - hides early on: (a) a new brand being recognised, (b) operator clicking the X
/// No button, no push-to-talk — the engine listens continuously and pushes
/// a recognition the instant a customer finishes speaking.
/// </summary>
public partial class MainViewModel : ObservableObject
{
    private static readonly TimeSpan DisplayDuration = TimeSpan.FromMinutes(5);
    private static readonly TimeSpan BrandVideoDelay = TimeSpan.FromMinutes(1);

    private readonly IBrandService _brandService;
    private readonly ISpeechEngineClient _speechClient;
    private readonly IEngineSettingsRepository _settingsRepository;
    private readonly DispatcherTimer _hideTimer;
    private readonly DispatcherTimer _brandVideoTimer;

    [ObservableProperty] private BrandDisplay? _currentBrand;
    [ObservableProperty] private bool _isProductVisible;
    [ObservableProperty] private bool _isEngineConnected;
    [ObservableProperty] private bool _isPaused;
    [ObservableProperty] private bool _showModelList = true; // from EngineSettings("show_model_list"), operator-toggleable
    [ObservableProperty] private double _audioLevel; // 0.0–1.0, bound to the equalizer/orb visual
    [ObservableProperty] private string _statusText = "در حال اتصال به موتور تشخیص...";

    /// <summary>
    /// True while the engine is actively transcribing/matching an utterance.
    /// Shown as a small overlay pill regardless of whether the idle screen
    /// or a brand card is currently on screen (previously the "processing"
    /// status only reached the idle screen's status text, so it was
    /// invisible whenever a brand card was up).
    /// </summary>
    [ObservableProperty] private bool _isProcessing;

    /// <summary>
    /// True once the CURRENT brand card has been on screen for about a
    /// minute AND that brand has its own demo video configured (Admin ->
    /// per-brand "ویدیوی دمو"). The image is then swapped for that video,
    /// looping, until a new brand is recognised or the card is closed.
    /// </summary>
    [ObservableProperty] private bool _isShowingBrandVideo;

    public MainViewModel(IBrandService brandService, ISpeechEngineClient speechClient,
        IEngineSettingsRepository settingsRepository)
    {
        _brandService = brandService;
        _speechClient = speechClient;
        _settingsRepository = settingsRepository;

        _hideTimer = new DispatcherTimer { Interval = DisplayDuration };
        _hideTimer.Tick += (_, _) => HideProduct();

        _brandVideoTimer = new DispatcherTimer { Interval = BrandVideoDelay };
        _brandVideoTimer.Tick += (_, _) =>
        {
            _brandVideoTimer.Stop();
            if (!string.IsNullOrWhiteSpace(CurrentBrand?.VideoPath))
                IsShowingBrandVideo = true;
        };

        _speechClient.BrandRecognized += OnBrandRecognized;
        _speechClient.AudioLevelChanged += (_, level) => AudioLevel = level;
        _speechClient.ConnectionStateChanged += (_, connected) =>
        {
            IsEngineConnected = connected;
            StatusText = connected ? "در انتظار مشتری..." : "در حال اتصال به موتور تشخیص...";
        };

        _ = _speechClient.ConnectAsync();
        _ = LoadDisplaySettingsAsync();
    }

    private async Task LoadDisplaySettingsAsync()
    {
        try
        {
            var settings = await _settingsRepository.GetAllAsync();
            if (settings.TryGetValue("show_model_list", out var v))
                ShowModelList = v.Equals("true", StringComparison.OrdinalIgnoreCase);
        }
        catch
        {
            // keep the default (true) if settings can't be read for any reason
        }
    }

    private async void OnBrandRecognized(object? sender, Core.DTOs.RecognizedBrandMessage msg)
    {
        if (msg.Type == "status")
        {
            StatusText = msg.Message switch
            {
                "engine_ready" => "در انتظار مشتری...",
                "processing" => "در حال پردازش...",
                "no_speech_detected" => "متوجه نشدم — دوباره بفرمایید",
                "paused" => "موقتاً متوقف شد",
                "resumed" => "در انتظار مشتری...",
                _ => StatusText,
            };
            IsProcessing = msg.Message == "processing";
            if (msg.Message == "paused") IsPaused = true;
            if (msg.Message == "resumed") IsPaused = false;
            return;
        }

        IsProcessing = false;

        if (!msg.IsValid || msg.BrandId is null)
        {
            StatusText = "برند شناسایی نشد — دوباره بفرمایید";
            return;
        }

        var brandDisplay = await _brandService.GetBrandDisplayAsync(msg.BrandId.Value);
        if (brandDisplay is null) return;

        // Rule: a NEW recognised brand always replaces whatever is showing,
        // and resets the 5-minute window (and the per-brand video timer).
        App.Current.Dispatcher.Invoke(() => ShowBrand(brandDisplay));
    }

    private void ShowBrand(BrandDisplay brand)
    {
        CurrentBrand = brand;
        IsProductVisible = true;
        IsShowingBrandVideo = false;

        _hideTimer.Stop();
        _hideTimer.Start();

        _brandVideoTimer.Stop();
        _brandVideoTimer.Start();
    }

    [RelayCommand]
    private void CloseProduct() => HideProduct();

    [RelayCommand]
    private async Task ToggleListeningAsync()
    {
        if (IsPaused)
            await _speechClient.SendCommandAsync("resume");
        else
            await _speechClient.SendCommandAsync("pause");
    }

    private void HideProduct()
    {
        _hideTimer.Stop();
        _brandVideoTimer.Stop();
        IsProductVisible = false;
        IsShowingBrandVideo = false;
        CurrentBrand = null;
        StatusText = "در انتظار مشتری...";
    }
}
