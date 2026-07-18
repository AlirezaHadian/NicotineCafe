namespace NicotineCafe.Core.Models;

/// <summary>
/// What the main screen displays after a recognition: the BRAND (name +
/// one representative image), plus the list of "models we carry" for it.
/// Recognition is brand-only (no per-variant matching) — this is purely a
/// display concern.
/// </summary>
public sealed class BrandDisplay
{
    public int BrandId { get; init; }
    public string NameFa { get; init; } = string.Empty;
    public string NameEn { get; init; } = string.Empty;
    public string? ImagePath { get; init; }
    public string? VideoPath { get; init; } // optional demo video, looped after 1 min on the display card
    public IReadOnlyList<string> ModelNames { get; init; } = Array.Empty<string>();
}

/// <summary>A single brand alias row, editable from the admin screen.</summary>
public sealed class AliasEntry
{
    public int Id { get; set; }
    public string Alias { get; set; } = string.Empty;
}

public sealed class RecognitionLogEntry
{
    public string RawText { get; init; } = string.Empty;
    public string NormalisedText { get; init; } = string.Empty;
    public int? MatchedBrandId { get; init; }
    public double Confidence { get; init; }
    public bool IsValid { get; init; }
}
