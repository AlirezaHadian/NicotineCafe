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
}
