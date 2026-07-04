using Microsoft.Data.Sqlite;

namespace NicotineCafe.Data;

/// <summary>
/// Creates short-lived SQLite connections. One factory instance per app,
/// registered as a singleton in DI; every repository method opens/uses/
/// disposes its own connection (SQLite is fine with this — no pooling needed).
/// </summary>
public sealed class SqliteConnectionFactory
{
    private readonly string _connectionString;

    public SqliteConnectionFactory(string databasePath)
    {
        var builder = new SqliteConnectionStringBuilder
        {
            DataSource = databasePath,
            Mode = SqliteOpenMode.ReadWriteCreate,
            Cache = SqliteCacheMode.Shared,
        };
        _connectionString = builder.ToString();
    }

    public SqliteConnection Create()
    {
        var conn = new SqliteConnection(_connectionString);
        conn.Open();
        using var pragma = conn.CreateCommand();
        pragma.CommandText = "PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;";
        pragma.ExecuteNonQuery();
        return conn;
    }
}
