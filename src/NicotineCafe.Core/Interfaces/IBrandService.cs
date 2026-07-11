using NicotineCafe.Core.Models;

namespace NicotineCafe.Core.Interfaces;

/// <summary>
/// Business-logic layer consumed by the UI (ViewModels). Wraps
/// IBrandRepository and adds caching.
/// </summary>
public interface IBrandService
{
    Task<BrandDisplay?> GetBrandDisplayAsync(int brandId, CancellationToken ct = default);
    Task<IReadOnlyList<Brand>> GetBrandsAsync(CancellationToken ct = default);
    Task RecordRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default);

    Task<int> AddBrandAsync(Brand brand, CancellationToken ct = default);
    Task UpdateBrandAsync(Brand brand, CancellationToken ct = default);
    Task DeleteBrandAsync(int brandId, CancellationToken ct = default);

    Task<IReadOnlyList<AliasEntry>> GetBrandAliasesAsync(int brandId, CancellationToken ct = default);
    Task AddBrandAliasAsync(int brandId, string alias, CancellationToken ct = default);
    Task DeleteBrandAliasAsync(int aliasId, CancellationToken ct = default);

    Task<IReadOnlyList<BrandModelEntry>> GetBrandModelsAsync(int brandId, CancellationToken ct = default);
    Task AddBrandModelAsync(int brandId, string modelName, CancellationToken ct = default);
    Task DeleteBrandModelAsync(int modelId, CancellationToken ct = default);
}
