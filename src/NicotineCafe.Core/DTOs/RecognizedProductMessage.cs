namespace NicotineCafe.Core.DTOs;

/// <summary>
/// Wire format sent by the Python voice engine over the local TCP bridge.
/// One JSON object per line (newline-delimited JSON).
/// </summary>
public sealed class RecognizedProductMessage
{
    public string Type { get; set; } = "recognition"; // "recognition" | "status" | "error"
    public bool IsValid { get; set; }
    public int? ProductId { get; set; }
    public string? RawText { get; set; }
    public string? NormalisedText { get; set; }
    public double Confidence { get; set; }
    public string? Message { get; set; } // used for "status"/"error" types
}
