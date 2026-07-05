using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;

namespace NicotineCafe.WPF.Controls;

/// <summary>
/// "Listening orb": idle breathing animation + reactive pulse driven by the
/// live mic level (0..1) streamed from the always-on VAD recorder. No
/// interaction — purely a passive "I'm listening" indicator, since there's
/// no button to press anymore.
/// </summary>
public partial class AudioEqualizerControl : UserControl
{
    private readonly DispatcherTimer _timer;
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
        _timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(33) };
        _timer.Tick += (_, _) => Animate();
        _timer.Start();
    }

    private void Animate()
    {
        _phase += 0.045;
        double idle = (Math.Sin(_phase) + 1) / 2.0; // 0..1 slow breathing

        double target = Math.Clamp(Level, 0.0, 1.0);
        _smoothedLevel += (target - _smoothedLevel) * 0.25; // ease toward target

        double core = 0.92 + idle * 0.06 + _smoothedLevel * 0.28;
        double r1 = 0.95 + idle * 0.04 + _smoothedLevel * 0.22;
        double r2 = 0.97 + idle * 0.03 + _smoothedLevel * 0.16;
        double r3 = 0.98 + idle * 0.02 + _smoothedLevel * 0.10;

        CoreScale.ScaleX = CoreScale.ScaleY = core;
        Ring1Scale.ScaleX = Ring1Scale.ScaleY = r1;
        Ring2Scale.ScaleX = Ring2Scale.ScaleY = r2;
        Ring3Scale.ScaleX = Ring3Scale.ScaleY = r3;
    }
}
