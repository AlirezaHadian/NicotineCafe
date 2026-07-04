using System.Collections.ObjectModel;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Animation;
using System.Windows.Threading;

namespace NicotineCafe.WPF.Controls;

/// <summary>
/// 9-bar reactive equalizer. Bound to a 0..1 "Level" value pushed by the
/// speech engine (mic RMS). Each bar has a phase offset so the idle
/// animation looks organic instead of flat.
/// </summary>
public partial class AudioEqualizerControl : UserControl
{
    private const int BarCount = 9;
    private readonly DispatcherTimer _idleTimer;
    private readonly double[] _phase = new double[BarCount];
    private readonly Random _rng = new();

    public static readonly DependencyProperty LevelProperty =
        DependencyProperty.Register(nameof(Level), typeof(double), typeof(AudioEqualizerControl),
            new PropertyMetadata(0.0, OnLevelChanged));

    public double Level
    {
        get => (double)GetValue(LevelProperty);
        set => SetValue(LevelProperty, value);
    }

    public ObservableCollection<double> BarHeights { get; } = new();

    public AudioEqualizerControl()
    {
        InitializeComponent();
        for (int i = 0; i < BarCount; i++)
        {
            BarHeights.Add(6);
            _phase[i] = _rng.NextDouble() * Math.PI * 2;
        }

        _idleTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(80) };
        _idleTimer.Tick += (_, _) => Animate();
        _idleTimer.Start();
    }

    private static void OnLevelChanged(DependencyObject d, DependencyPropertyChangedEventArgs e) { }

    private void Animate()
    {
        double baseLevel = Math.Clamp(Level, 0.0, 1.0);
        for (int i = 0; i < BarCount; i++)
        {
            _phase[i] += 0.35 + baseLevel * 0.6;
            // Idle: gentle sine breathing. Active: level dominates with per-bar jitter.
            double idle = (Math.Sin(_phase[i]) + 1) / 2.0;      // 0..1
            double target = 6 + (idle * 6) + (baseLevel * 34 * (0.6 + _rng.NextDouble() * 0.4));
            BarHeights[i] = Math.Clamp(target, 6, 40);
        }
    }
}
