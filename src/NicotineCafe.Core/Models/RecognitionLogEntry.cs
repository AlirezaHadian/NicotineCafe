namespace NicotineCafe.Core.Models;

/// <summary>Lightweight (Id, NameFa) pair for admin dropdowns.</summary>
public sealed class NamedOption
{
    public int Id { get; set; }
    public string NameFa { get; set; } = string.Empty;

    public override string ToString() => NameFa; // helps if a control binds without DisplayMemberPath
}

public sealed class RecognitionLogEntry
{
    public string RawText { get; init; } = string.Empty;
    public string NormalisedText { get; init; } = string.Empty;
    public int? MatchedProductId { get; init; }
    public double Confidence { get; init; }
    public bool IsValid { get; init; }
}
