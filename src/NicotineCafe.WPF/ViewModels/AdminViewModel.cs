using System.Collections.ObjectModel;
using System.IO;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Win32;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.WPF.ViewModels;

/// <summary>
/// Backs the product-management screen. Recognition is brand-only now, so
/// this is entirely about Brands: add/edit/delete a brand, pick its image
/// (via a Browse button — no manual path typing), manage its aliases (what
/// the voice engine should recognise), and manage its "models we carry"
/// list (what the display card shows under the brand name).
/// </summary>
public partial class AdminViewModel : ObservableObject
{
    private readonly IBrandService _brandService;
    private readonly IEngineSettingsRepository _settingsRepository;

    public ObservableCollection<Brand> Brands { get; } = new();
    public ObservableCollection<AliasEntry> SelectedBrandAliases { get; } = new();
    public ObservableCollection<BrandModelEntry> SelectedBrandModels { get; } = new();

    [ObservableProperty] private Brand? _selectedBrand;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveNewCommand))]
    [NotifyCanExecuteChangedFor(nameof(SaveChangesCommand))]
    private string _formNameFa = string.Empty;
    [ObservableProperty] private string _formNameEn = string.Empty;
    [ObservableProperty] private string _formImagePath = string.Empty;
    [ObservableProperty] private string _formVideoPath = string.Empty;

    [ObservableProperty] private string _newAliasText = string.Empty;
    [ObservableProperty] private string _newModelText = string.Empty;

    [ObservableProperty] private string _statusMessage = string.Empty;

    // --- Voice engine + display settings (EngineSettings table) ---
    [ObservableProperty] private string _settingModelSize = "tiny";
    [ObservableProperty] private string _settingBeamSize = "1";
    [ObservableProperty] private string _settingSpeechThreshold = "0.09";
    [ObservableProperty] private string _settingSilenceHangoverS = "0.55";
    [ObservableProperty] private string _settingMinUtteranceS = "0.9";
    [ObservableProperty] private string _settingCpuThreads = "4";
    [ObservableProperty] private string _settingMinConfidence = "0.60";
    [ObservableProperty] private bool _settingShowModelList = true;
    [ObservableProperty] private string _settingsStatusMessage = string.Empty;

    public AdminViewModel(IBrandService brandService, IEngineSettingsRepository settingsRepository)
    {
        _brandService = brandService;
        _settingsRepository = settingsRepository;
        _ = LoadBrandsAsync();
        _ = LoadSettingsAsync();
    }

    private async Task LoadBrandsAsync()
    {
        try
        {
            Brands.Clear();
            foreach (var b in await _brandService.GetBrandsAsync())
                Brands.Add(b);
            if (Brands.Count == 0)
                StatusMessage = "هیچ برندی توی دیتابیس نیست — از فرم کنار همین صفحه یکی اضافه کن.";
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در بارگذاری برندها: {ex.Message}";
        }
    }

    partial void OnSelectedBrandChanged(Brand? value)
    {
        SelectedBrandAliases.Clear();
        SelectedBrandModels.Clear();

        if (value is null)
        {
            FormNameFa = string.Empty;
            FormNameEn = string.Empty;
            FormImagePath = string.Empty;
            FormVideoPath = string.Empty;
            return;
        }

        FormNameFa = value.NameFa;
        FormNameEn = value.NameEn;
        FormImagePath = value.ImagePath ?? string.Empty;
        FormVideoPath = value.VideoPath ?? string.Empty;

        _ = LoadAliasesAndModelsAsync(value.Id);
    }

    private async Task LoadAliasesAndModelsAsync(int brandId)
    {
        try
        {
            SelectedBrandAliases.Clear();
            foreach (var a in await _brandService.GetBrandAliasesAsync(brandId))
                SelectedBrandAliases.Add(a);

            SelectedBrandModels.Clear();
            foreach (var m in await _brandService.GetBrandModelsAsync(brandId))
                SelectedBrandModels.Add(m);
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در بارگذاری الیاس‌ها/مدل‌ها: {ex.Message}";
        }
    }

    [RelayCommand]
    private void ClearForm()
    {
        SelectedBrand = null;
        FormNameFa = string.Empty;
        FormNameEn = string.Empty;
        FormImagePath = string.Empty;
        FormVideoPath = string.Empty;
        SelectedBrandAliases.Clear();
        SelectedBrandModels.Clear();
        StatusMessage = string.Empty;
    }

    /// <summary>
    /// Opens a file picker and copies the chosen image into
    /// Assets/Images next to the exe, so it works immediately without a
    /// rebuild (images are Content/CopyToOutputDirectory, not embedded
    /// Resources). Sets FormImagePath to the resulting relative path.
    /// </summary>
    [RelayCommand]
    private void BrowseForImage()
    {
        var dialog = new OpenFileDialog
        {
            Title = "انتخاب عکس برند",
            Filter = "تصاویر (*.png;*.jpg;*.jpeg;*.bmp;*.webp)|*.png;*.jpg;*.jpeg;*.bmp;*.webp|همه‌ی فایل‌ها|*.*",
        };
        if (dialog.ShowDialog() != true) return;

        try
        {
            var imagesDir = Path.Combine(AppContext.BaseDirectory, "Assets", "Images");
            Directory.CreateDirectory(imagesDir);

            var fileName = Path.GetFileName(dialog.FileName);
            var destPath = Path.Combine(imagesDir, fileName);
            File.Copy(dialog.FileName, destPath, overwrite: true);

            FormImagePath = $"Images/{fileName}";
            StatusMessage = $"عکس کپی شد: {fileName}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در کپی‌کردن عکس: {ex.Message}";
        }
    }

    /// <summary>
    /// Opens a file picker and copies the chosen video into
    /// Assets/Videos next to the exe (same pattern as BrowseForImage) —
    /// works immediately without a rebuild. Sets FormVideoPath to the
    /// resulting relative path. This is the per-brand demo video shown
    /// (looped) once a customer has had the brand card on screen for
    /// about a minute.
    /// </summary>
    [RelayCommand]
    private void BrowseForVideo()
    {
        var dialog = new OpenFileDialog
        {
            Title = "انتخاب ویدیوی دمو برند",
            Filter = "ویدیو (*.mp4;*.wmv;*.avi;*.mov)|*.mp4;*.wmv;*.avi;*.mov|همه‌ی فایل‌ها|*.*",
        };
        if (dialog.ShowDialog() != true) return;

        try
        {
            var videosDir = Path.Combine(AppContext.BaseDirectory, "Assets", "Videos");
            Directory.CreateDirectory(videosDir);

            var fileName = Path.GetFileName(dialog.FileName);
            var destPath = Path.Combine(videosDir, fileName);
            File.Copy(dialog.FileName, destPath, overwrite: true);

            FormVideoPath = $"Videos/{fileName}";
            StatusMessage = $"ویدیو کپی شد: {fileName}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"خطا در کپی‌کردن ویدیو: {ex.Message}";
        }
    }

    [RelayCommand]
    private void ClearVideo() => FormVideoPath = string.Empty;

    private bool CanSave() => !string.IsNullOrWhiteSpace(FormNameFa);

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveNewAsync()
    {
        var brand = new Brand
        {
            NameFa = FormNameFa.Trim(),
            NameEn = FormNameEn.Trim(),
            ImagePath = string.IsNullOrWhiteSpace(FormImagePath) ? null : FormImagePath.Trim(),
            VideoPath = string.IsNullOrWhiteSpace(FormVideoPath) ? null : FormVideoPath.Trim(),
        };
        var id = await _brandService.AddBrandAsync(brand);
        StatusMessage = $"«{brand.NameFa}» اضافه شد — حالا الیاس و مدل‌هاش رو اضافه کن.";
        await LoadBrandsAsync();
        SelectedBrand = Brands.FirstOrDefault(b => b.Id == id);
    }

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveChangesAsync()
    {
        if (SelectedBrand is null) return;
        var updated = new Brand
        {
            Id = SelectedBrand.Id,
            NameFa = FormNameFa.Trim(),
            NameEn = FormNameEn.Trim(),
            ImagePath = string.IsNullOrWhiteSpace(FormImagePath) ? null : FormImagePath.Trim(),
            VideoPath = string.IsNullOrWhiteSpace(FormVideoPath) ? null : FormVideoPath.Trim(),
            IsActive = true,
        };
        await _brandService.UpdateBrandAsync(updated);
        StatusMessage = $"«{updated.NameFa}» ذخیره شد.";
        await LoadBrandsAsync();
        SelectedBrand = Brands.FirstOrDefault(b => b.Id == updated.Id);
    }

    [RelayCommand]
    private async Task DeleteSelectedAsync()
    {
        if (SelectedBrand is null) return;
        var name = SelectedBrand.NameFa;
        await _brandService.DeleteBrandAsync(SelectedBrand.Id);
        StatusMessage = $"«{name}» حذف شد.";
        await LoadBrandsAsync();
        ClearForm();
    }

    // --- Aliases ---

    [RelayCommand]
    private async Task AddAliasAsync()
    {
        if (SelectedBrand is null || string.IsNullOrWhiteSpace(NewAliasText)) return;
        await _brandService.AddBrandAliasAsync(SelectedBrand.Id, NewAliasText.Trim());
        NewAliasText = string.Empty;
        await LoadAliasesAndModelsAsync(SelectedBrand.Id);
    }

    [RelayCommand]
    private async Task DeleteAliasAsync(AliasEntry? alias)
    {
        if (alias is null || SelectedBrand is null) return;
        await _brandService.DeleteBrandAliasAsync(alias.Id);
        await LoadAliasesAndModelsAsync(SelectedBrand.Id);
    }

    // --- Models ("what we carry") ---

    [RelayCommand]
    private async Task AddModelAsync()
    {
        if (SelectedBrand is null || string.IsNullOrWhiteSpace(NewModelText)) return;
        await _brandService.AddBrandModelAsync(SelectedBrand.Id, NewModelText.Trim());
        NewModelText = string.Empty;
        await LoadAliasesAndModelsAsync(SelectedBrand.Id);
    }

    [RelayCommand]
    private async Task DeleteModelAsync(BrandModelEntry? model)
    {
        if (model is null || SelectedBrand is null) return;
        await _brandService.DeleteBrandModelAsync(model.Id);
        await LoadAliasesAndModelsAsync(SelectedBrand.Id);
    }

    // --- Engine + display settings ---

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
            if (s.TryGetValue("show_model_list", out var v8))
                SettingShowModelList = v8.Equals("true", StringComparison.OrdinalIgnoreCase);
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
            await _settingsRepository.SetAsync("show_model_list", SettingShowModelList ? "true" : "false");
            SettingsStatusMessage = "ذخیره شد — برای اعمال، برنامه رو ببند و دوباره باز کن.";
        }
        catch (Exception ex)
        {
            SettingsStatusMessage = $"خطا در ذخیره‌سازی: {ex.Message}";
        }
    }
}
