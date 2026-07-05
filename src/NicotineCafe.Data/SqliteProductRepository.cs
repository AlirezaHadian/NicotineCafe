using Dapper;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.Data;

/// <summary>
/// IProductRepository implementation backed by SQLite (Dapper, no ORM overhead).
/// This is the ONLY class in the solution that contains raw SQL for products.
/// </summary>
public sealed class SqliteProductRepository : IProductRepository
{
    private const string BaseSelect = """
        SELECT
            p.Id, p.BrandId, p.VariantId,
            p.NameFa, p.NameEn,
            b.NameFa AS BrandNameFa, b.NameEn AS BrandNameEn,
            v.NameFa AS VariantNameFa, v.NameEn AS VariantNameEn,
            p.ImagePath, p.TarMg, p.NicotineMg, p.CarbonMonoxideMg,
            p.PackSize, p.Price, p.IsActive
        FROM Products p
        JOIN Brands b   ON b.Id = p.BrandId
        LEFT JOIN Variants v ON v.Id = p.VariantId
        """;

    private readonly SqliteConnectionFactory _factory;

    public SqliteProductRepository(SqliteConnectionFactory factory) => _factory = factory;

    public async Task<Product?> GetByIdAsync(int id, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var sql = BaseSelect + " WHERE p.Id = @id";
        return await conn.QuerySingleOrDefaultAsync<Product>(sql, new { id });
    }

    public async Task<IReadOnlyList<Product>> GetAllAsync(CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var sql = BaseSelect + " WHERE p.IsActive = 1 ORDER BY b.NameFa, v.NameFa";
        var rows = await conn.QueryAsync<Product>(sql);
        return rows.ToList();
    }

    public async Task<IReadOnlyList<Product>> SearchAsync(string term, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var sql = BaseSelect + """
             WHERE p.IsActive = 1
               AND (p.NameFa LIKE @t OR p.NameEn LIKE @t
                    OR b.NameFa LIKE @t OR b.NameEn LIKE @t)
            """;
        var rows = await conn.QueryAsync<Product>(sql, new { t = $"%{term}%" });
        return rows.ToList();
    }

    public async Task<int> AddAsync(Product product, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath,
                                   TarMg, NicotineMg, CarbonMonoxideMg, PackSize, Price, IsActive)
            VALUES (@BrandId, @VariantId, @NameFa, @NameEn, @ImagePath,
                    @TarMg, @NicotineMg, @CarbonMonoxideMg, @PackSize, @Price, 1);
            SELECT last_insert_rowid();
            """;
        return await conn.ExecuteScalarAsync<int>(sql, product);
    }

    public async Task UpdateAsync(Product product, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            UPDATE Products SET
                BrandId = @BrandId, VariantId = @VariantId,
                NameFa = @NameFa, NameEn = @NameEn, ImagePath = @ImagePath,
                TarMg = @TarMg, NicotineMg = @NicotineMg, CarbonMonoxideMg = @CarbonMonoxideMg,
                PackSize = @PackSize, Price = @Price, IsActive = @IsActive
            WHERE Id = @Id
            """;
        await conn.ExecuteAsync(sql, product);
    }

    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        await conn.ExecuteAsync("UPDATE Products SET IsActive = 0 WHERE Id = @id", new { id });
    }

    public async Task<IReadOnlyList<NamedOption>> GetBrandOptionsAsync(CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var rows = await conn.QueryAsync<NamedOption>(
            "SELECT Id, NameFa FROM Brands WHERE IsActive = 1 ORDER BY NameFa");
        return rows.ToList();
    }

    public async Task<IReadOnlyList<NamedOption>> GetVariantOptionsAsync(CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var rows = await conn.QueryAsync<NamedOption>(
            "SELECT Id, NameFa FROM Variants WHERE IsActive = 1 ORDER BY NameFa");
        return rows.ToList();
    }

    public async Task LogRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            INSERT INTO RecognitionLog (RawText, NormalisedText, MatchedProductId, Confidence, IsValid)
            VALUES (@RawText, @NormalisedText, @MatchedProductId, @Confidence, @IsValid)
            """;
        await conn.ExecuteAsync(sql, entry);
    }
}
