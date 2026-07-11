namespace NicotineCafe.Core.Models;

/// <summary>A brand row, as managed from the admin screen.</summary>
public sealed class Brand
{
    public int Id { get; set; }
    public string NameFa { get; set; } = string.Empty;
    public string NameEn { get; set; } = string.Empty;
    public string? ImagePath { get; set; }
    public bool IsActive { get; set; } = true;
}

/// <summary>A single "model we carry" row for a brand, editable from the admin screen.</summary>
public sealed class BrandModelEntry
{
    public int Id { get; set; }
    public string ModelName { get; set; } = string.Empty;
}
