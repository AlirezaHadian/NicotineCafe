using NicotineCafe.Core.Models;

namespace NicotineCafe.Core.Interfaces;

/// <summary>
/// Pure data-access contract — no business logic here.
/// Every method that hits the database (queries/commands) belongs behind
/// this interface, implemented in NicotineCafe.Data.
/// </summary>
public interface IProductRepository
{
    Task<Product?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Product>> GetAllAsync(CancellationToken ct = default);
    Task<IReadOnlyList<Product>> SearchAsync(string term, CancellationToken ct = default);

    Task<int> AddAsync(Product product, CancellationToken ct = default);
    Task UpdateAsync(Product product, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);

    Task LogRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default);
}
