using System.ComponentModel;
using System.IO;
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using NicotineCafe.WPF.ViewModels;

namespace NicotineCafe.WPF;

public partial class MainWindow : Window
{
    private MainViewModel? _viewModel;

    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        _viewModel = viewModel;
        viewModel.PropertyChanged += ViewModel_PropertyChanged;
    }

    private void ViewModel_PropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName != nameof(MainViewModel.IsShowingBrandVideo)) return;
        if (_viewModel is null) return;

        if (_viewModel.IsShowingBrandVideo)
            PlayBrandVideo();
        else
            StopBrandVideo();
    }

    private void PlayBrandVideo()
    {
        var relativePath = _viewModel?.CurrentBrand?.VideoPath;
        if (string.IsNullOrWhiteSpace(relativePath)) return;

        // Stored as "Videos/xyz.mp4" (see AdminViewModel.BrowseForVideo),
        // same convention as ImagePathToSourceConverter uses for images —
        // resolved relative to Assets/ next to the exe.
        var fullPath = Path.Combine(AppContext.BaseDirectory, "Assets", relativePath);
        if (!File.Exists(fullPath)) return;

        try
        {
            BrandVideoElement.Source = new Uri(fullPath, UriKind.Absolute);
            BrandVideoElement.Position = TimeSpan.Zero;
            BrandVideoElement.Play();
        }
        catch (Exception)
        {
            // Corrupt/unsupported file, missing codec, etc. — fail silently
            // and just leave the static image showing underneath.
        }
    }

    private void StopBrandVideo()
    {
        try
        {
            BrandVideoElement.Stop();
            BrandVideoElement.Source = null;
        }
        catch (Exception)
        {
            // best-effort cleanup only
        }
    }

    private void BrandVideoElement_MediaEnded(object sender, RoutedEventArgs e)
    {
        // MediaElement has no built-in loop flag — restart manually.
        BrandVideoElement.Position = TimeSpan.Zero;
        BrandVideoElement.Play();
    }

    private void BrandVideoElement_MediaFailed(object sender, ExceptionRoutedEventArgs e)
    {
        // Bad video file for this brand — don't crash the kiosk, just leave
        // the static image visible (IsShowingBrandVideo binding still flips
        // the Image's visibility off, but a failed MediaElement renders
        // nothing, which is an acceptable degraded state until the operator
        // fixes/replaces the file from Admin).
    }

    private void AdminButton_Click(object sender, RoutedEventArgs e)
    {
        var admin = App.Services.GetRequiredService<Views.AdminWindow>();
        admin.Owner = this;
        admin.ShowDialog();
    }

    private void MinimizeButton_Click(object sender, RoutedEventArgs e)
    {
        WindowState = WindowState.Minimized;
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        Application.Current.Shutdown();
    }
}
