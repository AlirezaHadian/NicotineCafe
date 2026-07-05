using NicotineCafe.Core.Models;

namespace NicotineCafe.Core.Interfaces;

/// <summary>
/// Business-logic layer consumed by the UI (ViewModels).
/// Wraps IProductRepository and adds caching / validation / rules.
/// </summary>
public interface IProductService
{
    Task<Product?> FindProductAsync(int productId, CancellationToken ct = default);
    Task<IReadOnlyList<Product>> GetCatalogAsync(CancellationToken ct = default);
    Task RecordRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default);

    // --- Admin operations (used by the product management screen) ---
    Task<IReadOnlyList<NamedOption>> GetBrandOptionsAsync(CancellationToken ct = default);
    Task<IReadOnlyList<NamedOption>> GetVariantOptionsAsync(CancellationToken ct = default);
    Task<int> AddProductAsync(Product product, CancellationToken ct = default);
    Task UpdateProductAsync(Product product, CancellationToken ct = default);
    Task DeleteProductAsync(int productId, CancellationToken ct = default);
}
