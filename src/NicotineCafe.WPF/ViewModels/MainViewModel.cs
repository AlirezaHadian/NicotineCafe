using System.Windows.Threading;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.WPF.ViewModels;

/// <summary>
/// Drives the single-product display screen:
///  - listens to the speech engine for recognitions
///  - shows a product for up to 5 minutes
///  - hides early on: (a) a new product being recognised, (b) operator clicking the X
/// </summary>
public partial class MainViewModel : ObservableObject
{
    private static readonly TimeSpan DisplayDuration = TimeSpan.FromMinutes(5);

    private readonly IProductService _productService;
    private readonly ISpeechEngineClient _speechClient;
    private readonly DispatcherTimer _hideTimer;

    [ObservableProperty] private Product? _currentProduct;
    [ObservableProperty] private bool _isProductVisible;
    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(StartRecordingCommand))]
    [NotifyCanExecuteChangedFor(nameof(StopRecordingCommand))]
    private bool _isEngineConnected;
    [ObservableProperty] private double _audioLevel; // 0.0–1.0, bound to the equalizer control
    [ObservableProperty] private bool _isRecording;
    [ObservableProperty] private string _statusText = "در حال اتصال به موتور تشخیص...";

    public MainViewModel(IProductService productService, ISpeechEngineClient speechClient)
    {
        _productService = productService;
        _speechClient = speechClient;

        _hideTimer = new DispatcherTimer { Interval = DisplayDuration };
        _hideTimer.Tick += (_, _) => HideProduct();

        _speechClient.ProductRecognized += OnProductRecognized;
        _speechClient.AudioLevelChanged += (_, level) => AudioLevel = level;
        _speechClient.ConnectionStateChanged += (_, connected) =>
        {
            IsEngineConnected = connected;
            if (!connected)
                StatusText = "در حال اتصال به موتور تشخیص...";
        };

        _ = _speechClient.ConnectAsync();
    }

    [RelayCommand(CanExecute = nameof(CanRecord))]
    private async Task StartRecordingAsync()
    {
        IsRecording = true;
        StatusText = "در حال شنیدن...";
        await _speechClient.SendCommandAsync("start_recording");
    }

    [RelayCommand(CanExecute = nameof(CanRecord))]
    private async Task StopRecordingAsync()
    {
        IsRecording = false;
        StatusText = "در حال پردازش...";
        await _speechClient.SendCommandAsync("stop_recording");
    }

    private bool CanRecord() => IsEngineConnected;

    private async void OnProductRecognized(object? sender, Core.DTOs.RecognizedProductMessage msg)
    {
        if (msg.Type == "status")
        {
            StatusText = msg.Message switch
            {
                "engine_ready" => "برای صحبت، دکمه میکروفون را نگه دارید",
                "recording_started" => "در حال شنیدن...",
                "no_speech_detected" => "صدا واضح نبود — دوباره امتحان کنید",
                "recording_too_short" => "ضبط خیلی کوتاه بود — دوباره امتحان کنید",
                "no_audio_captured" => "صدایی دریافت نشد",
                _ => StatusText,
            };
            return;
        }

        if (!msg.IsValid || msg.ProductId is null)
        {
            StatusText = "محصول شناسایی نشد — دوباره امتحان کنید";
            return;
        }

        var product = await _productService.FindProductAsync(msg.ProductId.Value);
        if (product is null) return;

        // Rule: a NEW recognised product always replaces whatever is showing,
        // and resets the 5-minute window.
        App.Current.Dispatcher.Invoke(() => ShowProduct(product));
    }

    private void ShowProduct(Product product)
    {
        CurrentProduct = product;
        IsProductVisible = true;
        StatusText = string.Empty;

        _hideTimer.Stop();
        _hideTimer.Start();
    }

    [RelayCommand]
    private void CloseProduct() => HideProduct();

    private void HideProduct()
    {
        _hideTimer.Stop();
        IsProductVisible = false;
        CurrentProduct = null;
        StatusText = "در انتظار گفتار...";
    }
}
