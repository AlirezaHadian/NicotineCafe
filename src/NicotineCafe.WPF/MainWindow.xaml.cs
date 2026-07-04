using System.Windows;
using System.Windows.Input;
using NicotineCafe.WPF.ViewModels;

namespace NicotineCafe.WPF;

public partial class MainWindow : Window
{
    private MainViewModel ViewModel => (MainViewModel)DataContext;

    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    // Push-to-talk: hold the mic button while speaking, release to send for recognition.
    private void MicButton_PressStart(object sender, MouseButtonEventArgs e)
    {
        if (ViewModel.StartRecordingCommand.CanExecute(null))
            ViewModel.StartRecordingCommand.Execute(null);
    }

    private void MicButton_PressEnd(object sender, MouseButtonEventArgs e)
    {
        if (ViewModel.StopRecordingCommand.CanExecute(null))
            ViewModel.StopRecordingCommand.Execute(null);
    }
}
