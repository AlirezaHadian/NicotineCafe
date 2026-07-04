namespace NicotineCafe.Core.Models;

/// <summary>
/// Immutable read model for a product row (Products table + joined Brand/Variant).
/// </summary>
public sealed class Product
{
    public int Id { get; init; }
    public int BrandId { get; init; }
    public int? VariantId { get; init; }

    public string NameFa { get; init; } = string.Empty;
    public string NameEn { get; init; } = string.Empty;

    public string BrandNameFa { get; init; } = string.Empty;
    public string BrandNameEn { get; init; } = string.Empty;
    public string? VariantNameFa { get; init; }
    public string? VariantNameEn { get; init; }

    public string? ImagePath { get; init; }

    public double? TarMg { get; init; }
    public double? NicotineMg { get; init; }
    public double? CarbonMonoxideMg { get; init; }
    public int? PackSize { get; init; }
    public int? Price { get; init; }

    public bool IsActive { get; init; } = true;
}
