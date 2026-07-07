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
    private readonly IEngineSettingsRepository _settingsRepository;

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

    // --- Voice engine tuning (EngineSettings table; needs an app restart to take effect) ---
    [ObservableProperty] private string _settingModelSize = "tiny";
    [ObservableProperty] private string _settingBeamSize = "1";
    [ObservableProperty] private string _settingSpeechThreshold = "0.09";
    [ObservableProperty] private string _settingSilenceHangoverS = "0.55";
    [ObservableProperty] private string _settingMinUtteranceS = "0.9";
    [ObservableProperty] private string _settingCpuThreads = "2";
    [ObservableProperty] private string _settingMinConfidence = "0.60";
    [ObservableProperty] private string _settingsStatusMessage = string.Empty;

    public AdminViewModel(IProductService productService, IEngineSettingsRepository settingsRepository)
    {
        _productService = productService;
        _settingsRepository = settingsRepository;
        _ = LoadAsync();
        _ = LoadSettingsAsync();
    }

    private async Task LoadSettingsAsync()
    {
        try
        {
            var s = await _settingsRepository.GetAllAsync();
            if (s.TryGetValue("model_size", out var v1)) SettingModelSize = v1;
            if (s.TryGetValue("beam_size", out var v2)) SettingBeamSize = v2;
            if (s.TryGetValue("speech_threshold", out var v3)) SettingSpeechThreshold = v3;
            if (s.TryGetValue("silence_hangover_s", out var v4)) SettingSilenceHangoverS = v4;
            if (s.TryGetValue("min_utterance_s", out var v5)) SettingMinUtteranceS = v5;
            if (s.TryGetValue("cpu_threads", out var v6)) SettingCpuThreads = v6;
            if (s.TryGetValue("min_confidence", out var v7)) SettingMinConfidence = v7;
        }
        catch (Exception ex)
        {
            SettingsStatusMessage = $"خطا در بارگذاری تنظیمات: {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        try
        {
            await _settingsRepository.SetAsync("model_size", SettingModelSize.Trim());
            await _settingsRepository.SetAsync("beam_size", SettingBeamSize.Trim());
            await _settingsRepository.SetAsync("speech_threshold", SettingSpeechThreshold.Trim());
            await _settingsRepository.SetAsync("silence_hangover_s", SettingSilenceHangoverS.Trim());
            await _settingsRepository.SetAsync("min_utterance_s", SettingMinUtteranceS.Trim());
            await _settingsRepository.SetAsync("cpu_threads", SettingCpuThreads.Trim());
            await _settingsRepository.SetAsync("min_confidence", SettingMinConfidence.Trim());
            SettingsStatusMessage = "ذخیره شد — برای اعمال، برنامه رو ببند و دوباره باز کن.";
        }
        catch (Exception ex)
        {
            SettingsStatusMessage = $"خطا در ذخیره‌سازی: {ex.Message}";
        }
    }

    private async Task LoadAsync()
    {
        try
        {
            Products.Clear();
            foreach (var p in await _productService.GetCatalogAsync())
                Products.Add(p);
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در بارگذاری محصولات: {ex.Message}";
        }

        try
        {
            Brands.Clear();
            var brands = await _productService.GetBrandOptionsAsync();
            foreach (var b in brands)
                Brands.Add(b);
            if (Brands.Count == 0)
                StatusMessage = "هیچ برندی توی دیتابیس پیدا نشد — ابتدا باید حداقل یک برند (Brands) اضافه کنی.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در بارگذاری برندها: {ex.Message}";
        }

        try
        {
            Variants.Clear();
            foreach (var v in await _productService.GetVariantOptionsAsync())
                Variants.Add(v);
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در بارگذاری تنوع‌ها: {ex.Message}";
        }
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
