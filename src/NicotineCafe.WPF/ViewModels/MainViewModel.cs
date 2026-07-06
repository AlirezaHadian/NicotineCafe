using System.Windows.Threading;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.WPF.ViewModels;

/// <summary>
/// Drives the single-product display screen:
///  - listens to the (always-on, VAD-driven) speech engine for recognitions
///  - shows a product for up to 5 minutes
///  - hides early on: (a) a new product being recognised, (b) operator clicking the X
/// No button, no push-to-talk — the engine listens continuously and pushes
/// a recognition the instant a customer finishes speaking.
/// </summary>
public partial class MainViewModel : ObservableObject
{
    private static readonly TimeSpan DisplayDuration = TimeSpan.FromMinutes(5);

    private readonly IProductService _productService;
    private readonly ISpeechEngineClient _speechClient;
    private readonly DispatcherTimer _hideTimer;

    [ObservableProperty] private Product? _currentProduct;
    [ObservableProperty] private bool _isProductVisible;
    [ObservableProperty] private bool _isEngineConnected;
    [ObservableProperty] private bool _isPaused;
    [ObservableProperty] private double _audioLevel; // 0.0–1.0, bound to the equalizer/orb visual
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
            StatusText = connected ? "در انتظار مشتری..." : "در حال اتصال به موتور تشخیص...";
        };

        _ = _speechClient.ConnectAsync();
    }

    private async void OnProductRecognized(object? sender, Core.DTOs.RecognizedProductMessage msg)
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
            if (msg.Message == "paused") IsPaused = true;
            if (msg.Message == "resumed") IsPaused = false;
            return;
        }

        if (!msg.IsValid || msg.ProductId is null)
        {
            StatusText = "محصول شناسایی نشد — دوباره بفرمایید";
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

        _hideTimer.Stop();
        _hideTimer.Start();
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
        IsProductVisible = false;
        CurrentProduct = null;
        StatusText = "در انتظار مشتری...";
    }
}
