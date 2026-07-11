using System.Globalization;
using System.IO;
using System.Windows.Data;
using System.Windows.Media.Imaging;

namespace NicotineCafe.WPF.Converters;

/// <summary>
/// Resolves a relative image path (e.g. "Images/winston.png", as stored in
/// the DB) against the app's output directory and loads it as a BitmapImage.
/// Returns null (no image shown) if the path is empty or the file doesn't
/// exist yet, instead of throwing — a product/brand with no picture yet
/// shouldn't crash the display.
/// </summary>
public sealed class ImagePathToSourceConverter : IValueConverter
{
    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is not string relativePath || string.IsNullOrWhiteSpace(relativePath))
            return null;

        try
        {
            var fullPath = Path.IsPathRooted(relativePath)
                ? relativePath
                : Path.Combine(AppContext.BaseDirectory, "Assets", relativePath);

            if (!File.Exists(fullPath))
                return null;

            var bitmap = new BitmapImage();
            bitmap.BeginInit();
            bitmap.CacheOption = BitmapCacheOption.OnLoad; // release the file handle immediately
            bitmap.UriSource = new Uri(fullPath, UriKind.Absolute);
            bitmap.EndInit();
            bitmap.Freeze();
            return bitmap;
        }
        catch
        {
            return null; // a bad/corrupt image file shouldn't crash the UI
        }
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
