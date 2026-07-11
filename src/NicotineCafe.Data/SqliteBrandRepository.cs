using Dapper;
using NicotineCafe.Core.Interfaces;
using NicotineCafe.Core.Models;

namespace NicotineCafe.Data;

/// <summary>
/// IBrandRepository implementation backed by SQLite (Dapper, no ORM overhead).
/// This is the ONLY class in the solution that contains raw SQL for brands.
/// </summary>
public sealed class SqliteBrandRepository : IBrandRepository
{
    private readonly SqliteConnectionFactory _factory;

    public SqliteBrandRepository(SqliteConnectionFactory factory) => _factory = factory;

    public async Task<IReadOnlyList<Brand>> GetAllBrandsAsync(CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var rows = await conn.QueryAsync<Brand>(
            "SELECT Id, NameFa, NameEn, ImagePath, IsActive FROM Brands WHERE IsActive = 1 ORDER BY NameFa");
        return rows.ToList();
    }

    public async Task<Brand?> GetBrandByIdAsync(int id, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        return await conn.QuerySingleOrDefaultAsync<Brand>(
            "SELECT Id, NameFa, NameEn, ImagePath, IsActive FROM Brands WHERE Id = @id", new { id });
    }

    public async Task<int> AddBrandAsync(Brand brand, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            INSERT INTO Brands (NameFa, NameEn, ImagePath, IsActive) VALUES (@NameFa, @NameEn, @ImagePath, 1);
            SELECT last_insert_rowid();
            """;
        return await conn.ExecuteScalarAsync<int>(sql, brand);
    }

    public async Task UpdateBrandAsync(Brand brand, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            UPDATE Brands SET NameFa = @NameFa, NameEn = @NameEn, ImagePath = @ImagePath, IsActive = @IsActive
            WHERE Id = @Id
            """;
        await conn.ExecuteAsync(sql, brand);
    }

    public async Task DeleteBrandAsync(int id, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        await conn.ExecuteAsync("UPDATE Brands SET IsActive = 0 WHERE Id = @id", new { id });
    }

    public async Task<BrandDisplay?> GetBrandDisplayAsync(int brandId, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var brand = await conn.QuerySingleOrDefaultAsync(
            "SELECT Id, NameFa, NameEn, ImagePath FROM Brands WHERE Id = @brandId AND IsActive = 1",
            new { brandId });
        if (brand is null) return null;

        var modelNames = await conn.QueryAsync<string>(
            "SELECT ModelName FROM BrandModels WHERE BrandId = @brandId ORDER BY ModelName",
            new { brandId });

        return new BrandDisplay
        {
            BrandId = (int)brand.Id,
            NameFa = (string)brand.NameFa,
            NameEn = (string)brand.NameEn,
            ImagePath = (string?)brand.ImagePath,
            ModelNames = modelNames.ToList(),
        };
    }

    public async Task<IReadOnlyList<AliasEntry>> GetBrandAliasesAsync(int brandId, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var rows = await conn.QueryAsync<AliasEntry>(
            "SELECT Id, Alias FROM BrandAliases WHERE BrandId = @brandId ORDER BY Alias", new { brandId });
        return rows.ToList();
    }

    public async Task AddBrandAliasAsync(int brandId, string alias, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        await conn.ExecuteAsync("INSERT INTO BrandAliases (BrandId, Alias) VALUES (@brandId, @alias)",
            new { brandId, alias });
    }

    public async Task DeleteBrandAliasAsync(int aliasId, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        await conn.ExecuteAsync("DELETE FROM BrandAliases WHERE Id = @aliasId", new { aliasId });
    }

    public async Task<IReadOnlyList<BrandModelEntry>> GetBrandModelsAsync(int brandId, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var rows = await conn.QueryAsync<BrandModelEntry>(
            "SELECT Id, ModelName FROM BrandModels WHERE BrandId = @brandId ORDER BY ModelName", new { brandId });
        return rows.ToList();
    }

    public async Task AddBrandModelAsync(int brandId, string modelName, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        await conn.ExecuteAsync("INSERT INTO BrandModels (BrandId, ModelName) VALUES (@brandId, @modelName)",
            new { brandId, modelName });
    }

    public async Task DeleteBrandModelAsync(int modelId, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        await conn.ExecuteAsync("DELETE FROM BrandModels WHERE Id = @modelId", new { modelId });
    }

    public async Task LogRecognitionAsync(RecognitionLogEntry entry, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            INSERT INTO RecognitionLog (RawText, NormalisedText, MatchedBrandId, Confidence, IsValid)
            VALUES (@RawText, @NormalisedText, @MatchedBrandId, @Confidence, @IsValid)
            """;
        await conn.ExecuteAsync(sql, entry);
    }
}
