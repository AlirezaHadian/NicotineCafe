using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;

namespace NicotineCafe.WPF.Controls;

/// <summary>
/// Bar-style "listening equalizer": idle organic wave motion (each bar has
/// its own phase, so they don't move in lockstep) plus a reactive boost
/// driven by the live mic level (0..1) streamed from the always-on VAD
/// recorder. No interaction — purely a passive "I'm listening" indicator.
/// </summary>
public partial class AudioEqualizerControl : UserControl
{
    private readonly DispatcherTimer _timer;
    private readonly ScaleTransform[] _bars;
    private readonly double[] _phaseOffsets;
    private double _phase;
    private double _smoothedLevel;

    public static readonly DependencyProperty LevelProperty =
        DependencyProperty.Register(nameof(Level), typeof(double), typeof(AudioEqualizerControl),
            new PropertyMetadata(0.0));

    public double Level
    {
        get => (double)GetValue(LevelProperty);
        set => SetValue(LevelProperty, value);
    }

    public AudioEqualizerControl()
    {
        InitializeComponent();

        _bars = new[]
        {
            Bar1Scale, Bar2Scale, Bar3Scale, Bar4Scale, Bar5Scale, Bar6Scale, Bar7Scale,
        };
        // Spread starting phases across a full cycle so bars idle
        // independently instead of pulsing in unison — the middle bar
        // (index 3) is slightly taller/wider in XAML, so it also gets a
        // bit more idle swing to draw the eye.
        _phaseOffsets = new double[] { 0.0, 0.9, 1.8, 2.7, 3.6, 4.5, 5.4 };

        _timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(33) };
        _timer.Tick += (_, _) => Animate();
        _timer.Start();
    }

    private void Animate()
    {
        _phase += 0.09;

        double target = Math.Clamp(Level, 0.0, 1.0);
        _smoothedLevel += (target - _smoothedLevel) * 0.25; // ease toward target

        for (int i = 0; i < _bars.Length; i++)
        {
            double idle = (Math.Sin(_phase + _phaseOffsets[i]) + 1) / 2.0; // 0..1, own phase per bar
            double centerBoost = i == 3 ? 1.2 : 1.0; // middle bar swings a bit more

            double scale = 1.0
                           + idle * 0.45 * centerBoost   // idle organic wave
                           + _smoothedLevel * 2.3 * centerBoost; // live mic reaction

            _bars[i].ScaleY = scale;
        }
    }
}
