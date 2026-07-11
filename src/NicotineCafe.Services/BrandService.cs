using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.Services;

/// <summary>
/// Business logic on top of IBrandRepository. Adds a simple in-memory
/// cache of the brand list (refreshed on demand) so repeated voice hits
/// don't round-trip to SQLite every time.
/// </summary>
public sealed class BrandService : IBrandService
{
    private readonly IBrandRepository _repository;
    private IReadOnlyList<Brand>? _cache;
    private readonly SemaphoreSlim _lock = new(1, 1);

    public BrandService(IBrandRepository repository) => _repository = repository;

    public async Task<IReadOnlyList<Brand>> GetBrandsAsync(CancellationToken ct = default)
    {
        if (_cache is not null) return _cache;
        await _lock.WaitAsync(ct);
        try
        {
            _cache ??= await _repository.GetAllBrandsAsync(ct);
            return _cache;
        }
        finally
        {
            _lock.Release();
        }
    }

    public Task<BrandDisplay?> GetBrandDisplayAsync(int brandId, CancellationToken ct = default)
        => _repository.GetBrandDisplayAsync(brandId, ct);

    public Task RecordRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default)
        => _repository.LogRecognitionAsync(entry, ct);

    /// <summary>Call after admin edits so next read reflects fresh data.</summary>
    public void InvalidateCache() => _cache = null;

    public async Task<int> AddBrandAsync(Brand brand, CancellationToken ct = default)
    {
        var id = await _repository.AddBrandAsync(brand, ct);
        InvalidateCache();
        return id;
    }

    public async Task UpdateBrandAsync(Brand brand, CancellationToken ct = default)
    {
        await _repository.UpdateBrandAsync(brand, ct);
        InvalidateCache();
    }

    public async Task DeleteBrandAsync(int brandId, CancellationToken ct = default)
    {
        await _repository.DeleteBrandAsync(brandId, ct);
        InvalidateCache();
    }

    public Task<IReadOnlyList<AliasEntry>> GetBrandAliasesAsync(int brandId, CancellationToken ct = default)
        => _repository.GetBrandAliasesAsync(brandId, ct);

    public Task AddBrandAliasAsync(int brandId, string alias, CancellationToken ct = default)
        => _repository.AddBrandAliasAsync(brandId, alias, ct);

    public Task DeleteBrandAliasAsync(int aliasId, CancellationToken ct = default)
        => _repository.DeleteBrandAliasAsync(aliasId, ct);

    public Task<IReadOnlyList<BrandModelEntry>> GetBrandModelsAsync(int brandId, CancellationToken ct = default)
        => _repository.GetBrandModelsAsync(brandId, ct);

    public Task AddBrandModelAsync(int brandId, string modelName, CancellationToken ct = default)
        => _repository.AddBrandModelAsync(brandId, modelName, ct);

    public Task DeleteBrandModelAsync(int modelId, CancellationToken ct = default)
        => _repository.DeleteBrandModelAsync(modelId, ct);
}
