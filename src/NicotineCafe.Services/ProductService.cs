using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.Services;

/// <summary>
/// Business logic on top of IProductRepository. Adds a simple in-memory
/// cache of the catalog (refreshed on demand) so repeated voice hits
/// don't round-trip to SQLite every time.
/// </summary>
public sealed class ProductService : IProductService
{
    private readonly IProductRepository _repository;
    private IReadOnlyList<Product>? _cache;
    private readonly SemaphoreSlim _lock = new(1, 1);

    public ProductService(IProductRepository repository) => _repository = repository;

    public async Task<Product?> FindProductAsync(int productId, CancellationToken ct = default)
    {
        var catalog = await GetCatalogAsync(ct);
        return catalog.FirstOrDefault(p => p.Id == productId)
               ?? await _repository.GetByIdAsync(productId, ct);
    }

    public async Task<IReadOnlyList<Product>> GetCatalogAsync(CancellationToken ct = default)
    {
        if (_cache is not null) return _cache;

        await _lock.WaitAsync(ct);
        try
        {
            _cache ??= await _repository.GetAllAsync(ct);
            return _cache;
        }
        finally
        {
            _lock.Release();
        }
    }

    public async Task RecordRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default)
    {
        await _repository.LogRecognitionAsync(entry, ct);
    }

    /// <summary>Call after admin edits so next read reflects fresh data.</summary>
    public void InvalidateCache() => _cache = null;

    public Task<IReadOnlyList<NamedOption>> GetBrandOptionsAsync(CancellationToken ct = default)
        => _repository.GetBrandOptionsAsync(ct);

    public Task<IReadOnlyList<NamedOption>> GetVariantOptionsAsync(CancellationToken ct = default)
        => _repository.GetVariantOptionsAsync(ct);

    public async Task<int> AddProductAsync(Product product, CancellationToken ct = default)
    {
        var id = await _repository.AddAsync(product, ct);
        InvalidateCache();
        return id;
    }

    public async Task UpdateProductAsync(Product product, CancellationToken ct = default)
    {
        await _repository.UpdateAsync(product, ct);
        InvalidateCache();
    }

    public async Task DeleteProductAsync(int productId, CancellationToken ct = default)
    {
        await _repository.DeleteAsync(productId, ct);
        InvalidateCache();
    }
}
