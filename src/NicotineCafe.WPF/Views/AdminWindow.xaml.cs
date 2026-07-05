using System.Windows;
using NicotineCafe.WPF.ViewModels;

namespace NicotineCafe.WPF.Views;

public partial class AdminWindow : Window
{
    public AdminWindow(AdminViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
