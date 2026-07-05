using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using NicotineCafe.WPF.ViewModels;

namespace NicotineCafe.WPF;

public partial class MainWindow : Window
{
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    private void AdminButton_Click(object sender, RoutedEventArgs e)
    {
        var admin = App.Services.GetRequiredService<Views.AdminWindow>();
        admin.Owner = this;
        admin.ShowDialog();
    }
}
