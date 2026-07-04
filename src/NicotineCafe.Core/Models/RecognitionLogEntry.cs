namespace NicotineCafe.Core.Models;

public sealed class RecognitionLogEntry
{
    public string RawText { get; init; } = string.Empty;
    public string NormalisedText { get; init; } = string.Empty;
    public int? MatchedProductId { get; init; }
    public double Confidence { get; init; }
    public bool IsValid { get; init; }
}
