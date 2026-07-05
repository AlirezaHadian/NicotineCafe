using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.WPF.ViewModels;

/// <summary>
/// Backs the product management screen: list existing products, add a new
/// one, edit the selected one, or (soft-)delete it. Talks only to
/// IProductService — no SQL here, matching the rest of the solution's
/// service-layer pattern.
/// </summary>
public partial class AdminViewModel : ObservableObject
{
    private readonly IProductService _productService;

    public ObservableCollection<Product> Products { get; } = new();
    public ObservableCollection<NamedOption> Brands { get; } = new();
    public ObservableCollection<NamedOption> Variants { get; } = new();

    [ObservableProperty] private Product? _selectedProduct;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveNewCommand))]
    [NotifyCanExecuteChangedFor(nameof(SaveChangesCommand))]
    private NamedOption? _formBrand;
    [ObservableProperty] private NamedOption? _formVariant; // null = "no variant" (brand-only product)
    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveNewCommand))]
    [NotifyCanExecuteChangedFor(nameof(SaveChangesCommand))]
    private string _formNameFa = string.Empty;
    [ObservableProperty] private string _formNameEn = string.Empty;
    [ObservableProperty] private string _formImagePath = string.Empty;
    [ObservableProperty] private double? _formTarMg;
    [ObservableProperty] private double? _formNicotineMg;
    [ObservableProperty] private double? _formCarbonMonoxideMg;
    [ObservableProperty] private int? _formPackSize = 20;
    [ObservableProperty] private int? _formPrice;

    [ObservableProperty] private string _statusMessage = string.Empty;

    public AdminViewModel(IProductService productService)
    {
        _productService = productService;
        _ = LoadAsync();
    }

    private async Task LoadAsync()
    {
        Products.Clear();
        foreach (var p in await _productService.GetCatalogAsync())
            Products.Add(p);

        Brands.Clear();
        foreach (var b in await _productService.GetBrandOptionsAsync())
            Brands.Add(b);

        Variants.Clear();
        foreach (var v in await _productService.GetVariantOptionsAsync())
            Variants.Add(v);
    }

    partial void OnSelectedProductChanged(Product? value)
    {
        if (value is null) return;
        FormBrand = Brands.FirstOrDefault(b => b.Id == value.BrandId);
        FormVariant = value.VariantId is null ? null : Variants.FirstOrDefault(v => v.Id == value.VariantId);
        FormNameFa = value.NameFa;
        FormNameEn = value.NameEn;
        FormImagePath = value.ImagePath ?? string.Empty;
        FormTarMg = value.TarMg;
        FormNicotineMg = value.NicotineMg;
        FormCarbonMonoxideMg = value.CarbonMonoxideMg;
        FormPackSize = value.PackSize;
        FormPrice = value.Price;
    }

    [RelayCommand]
    private void ClearForm()
    {
        SelectedProduct = null;
        FormBrand = null;
        FormVariant = null;
        FormNameFa = string.Empty;
        FormNameEn = string.Empty;
        FormImagePath = string.Empty;
        FormTarMg = null;
        FormNicotineMg = null;
        FormCarbonMonoxideMg = null;
        FormPackSize = 20;
        FormPrice = null;
        StatusMessage = string.Empty;
    }

    private bool CanSave() => FormBrand is not null && !string.IsNullOrWhiteSpace(FormNameFa);

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveNewAsync()
    {
        var product = new Product
        {
            BrandId = FormBrand!.Id,
            VariantId = FormVariant?.Id,
            NameFa = FormNameFa.Trim(),
            NameEn = FormNameEn.Trim(),
            ImagePath = string.IsNullOrWhiteSpace(FormImagePath) ? null : FormImagePath.Trim(),
            TarMg = FormTarMg,
            NicotineMg = FormNicotineMg,
            CarbonMonoxideMg = FormCarbonMonoxideMg,
            PackSize = FormPackSize,
            Price = FormPrice,
        };
        await _productService.AddProductAsync(product);
        StatusMessage = $"«{product.NameFa}» اضافه شد.";
        await LoadAsync();
        ClearForm();
    }

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveChangesAsync()
    {
        if (SelectedProduct is null) return;
        var updated = new Product
        {
            Id = SelectedProduct.Id,
            BrandId = FormBrand!.Id,
            VariantId = FormVariant?.Id,
            NameFa = FormNameFa.Trim(),
            NameEn = FormNameEn.Trim(),
            ImagePath = string.IsNullOrWhiteSpace(FormImagePath) ? null : FormImagePath.Trim(),
            TarMg = FormTarMg,
            NicotineMg = FormNicotineMg,
            CarbonMonoxideMg = FormCarbonMonoxideMg,
            PackSize = FormPackSize,
            Price = FormPrice,
            IsActive = true,
        };
        await _productService.UpdateProductAsync(updated);
        StatusMessage = $"«{updated.NameFa}» ذخیره شد.";
        await LoadAsync();
    }

    [RelayCommand]
    private async Task DeleteSelectedAsync()
    {
        if (SelectedProduct is null) return;
        var name = SelectedProduct.NameFa;
        await _productService.DeleteProductAsync(SelectedProduct.Id);
        StatusMessage = $"«{name}» حذف شد.";
        await LoadAsync();
        ClearForm();
    }
}
