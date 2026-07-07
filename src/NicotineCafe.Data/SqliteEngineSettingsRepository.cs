using Dapper;
using NicotineCafe.Core.Interfaces;

namespace NicotineCafe.Data;

public sealed class SqliteEngineSettingsRepository : IEngineSettingsRepository
{
    private readonly SqliteConnectionFactory _factory;

    public SqliteEngineSettingsRepository(SqliteConnectionFactory factory) => _factory = factory;

    public async Task<IReadOnlyDictionary<string, string>> GetAllAsync(CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        var rows = await conn.QueryAsync("SELECT Key, Value FROM EngineSettings");
        return rows.ToDictionary(r => (string)r.Key, r => (string)r.Value);
    }

    public async Task SetAsync(string key, string value, CancellationToken ct = default)
    {
        using var conn = _factory.Create();
        const string sql = """
            INSERT INTO EngineSettings (Key, Value) VALUES (@key, @value)
            ON CONFLICT(Key) DO UPDATE SET Value = excluded.Value
            """;
        await conn.ExecuteAsync(sql, new { key, value });
    }
}
