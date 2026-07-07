namespace NicotineCafe.Core.Interfaces;

/// <summary>
/// Key-value store for tunable voice-engine parameters (EngineSettings
/// table) — kept separate from IProductRepository since it's a different
/// concern (engine tuning, not product data).
/// </summary>
public interface IEngineSettingsRepository
{
    Task<IReadOnlyDictionary<string, string>> GetAllAsync(CancellationToken ct = default);
    Task SetAsync(string key, string value, CancellationToken ct = default);
}
