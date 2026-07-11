namespace NicotineCafe.Core.DTOs;

/// <summary>
/// Wire format sent by the Python voice engine over the local TCP bridge.
/// One JSON object per line (newline-delimited JSON). Recognition is
/// brand-only now (no per-variant/model matching), so this carries a
/// BrandId, not a ProductId.
/// </summary>
public sealed class RecognizedBrandMessage
{
    public string Type { get; set; } = "recognition"; // "recognition" | "status"
    public bool IsValid { get; set; }
    public int? BrandId { get; set; }
    public string? RawText { get; set; }
    public string? NormalisedText { get; set; }
    public double Confidence { get; set; }
    public string? Message { get; set; } // used for "status" type
}
