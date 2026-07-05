namespace NicotineCafe.Core.Models;

/// <summary>Lightweight (Id, NameFa) pair for admin dropdowns.</summary>
public sealed record NamedOption(int Id, string NameFa);

public sealed class RecognitionLogEntry
{
    public string RawText { get; init; } = string.Empty;
    public string NormalisedText { get; init; } = string.Empty;
    public int? MatchedProductId { get; init; }
    public double Confidence { get; init; }
    public bool IsValid { get; init; }
}
