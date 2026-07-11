using NicotineCafe.Core.Models;

namespace NicotineCafe.Core.Interfaces;

/// <summary>
/// Pure data-access contract — no business logic here. Every method that
/// hits the database belongs behind this interface, implemented in
/// NicotineCafe.Data. Recognition is brand-only now: no Products/Variants
/// tables, just Brands + BrandAliases + BrandModels (display-only list).
/// </summary>
public interface IBrandRepository
{
    Task<IReadOnlyList<Brand>> GetAllBrandsAsync(CancellationToken ct = default);
    Task<Brand?> GetBrandByIdAsync(int id, CancellationToken ct = default);
    Task<int> AddBrandAsync(Brand brand, CancellationToken ct = default);
    Task UpdateBrandAsync(Brand brand, CancellationToken ct = default);
    Task DeleteBrandAsync(int id, CancellationToken ct = default);

    /// <summary>Brand + its "what we carry" model list — what the main screen shows.</summary>
    Task<BrandDisplay?> GetBrandDisplayAsync(int brandId, CancellationToken ct = default);

    Task<IReadOnlyList<AliasEntry>> GetBrandAliasesAsync(int brandId, CancellationToken ct = default);
    Task AddBrandAliasAsync(int brandId, string alias, CancellationToken ct = default);
    Task DeleteBrandAliasAsync(int aliasId, CancellationToken ct = default);

    Task<IReadOnlyList<BrandModelEntry>> GetBrandModelsAsync(int brandId, CancellationToken ct = default);
    Task AddBrandModelAsync(int brandId, string modelName, CancellationToken ct = default);
    Task DeleteBrandModelAsync(int modelId, CancellationToken ct = default);

    Task LogRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default);
}
