__all__ = ["print_string"]


def print_string(s: str) -> str:
    """Print a string as a GraphQL StringValue literal.

    Replaces control characters and excluded characters (" U+0022 and \\ U+005C)
    with escape sequences.
    """
    if not isinstance(s, str):
        s = str(s)
    return f'"{s.translate(escape_sequences)}"'


escape_sequences = {
    0x00: "\\u0000",
    0x01: "\\u0001",
    0x02: "\\u0002",
    0x03: "\\u0003",
    0x04: "\\u0004",
    0x05: "\\u0005",
    0x06: "\\u0006",
    0x07: "\\u0007",
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0B: "\\u000B",
    0x0C: "\\f",
    0x0D: "\\r",
    0x0E: "\\u000E",
    0x0F: "\\u000F",
    0x10: "\\u0010",
    0x11: "\\u0011",
    0x12: "\\u0012",
    0x13: "\\u0013",
    0x14: "\\u0014",
    0x15: "\\u0015",
    0x16: "\\u0016",
    0x17: "\\u0017",
    0x18: "\\u0018",
    0x19: "\\u0019",
    0x1A: "\\u001A",
    0x1B: "\\u001B",
    0x1C: "\\u001C",
    0x1D: "\\u001D",
    0x1E: "\\u001E",
    0x1F: "\\u001F",
    0x22: '\\"',
    0x5C: "\\\\",
    0x7F: "\\u007F",
    0x80: "\\u0080",
    0x81: "\\u0081",
    0x82: "\\u0082",
    0x83: "\\u0083",
    0x84: "\\u0084",
    0x85: "\\u0085",
    0x86: "\\u0086",
    0x87: "\\u0087",
    0x88: "\\u0088",
    0x89: "\\u0089",
    0x8A: "\\u008A",
    0x8B: "\\u008B",
    0x8C: "\\u008C",
    0x8D: "\\u008D",
    0x8E: "\\u008E",
    0x8F: "\\u008F",
    0x90: "\\u0090",
    0x91: "\\u0091",
    0x92: "\\u0092",
    0x93: "\\u0093",
    0x94: "\\u0094",
    0x95: "\\u0095",
    0x96: "\\u0096",
    0x97: "\\u0097",
    0x98: "\\u0098",
    0x99: "\\u0099",
    0x9A: "\\u009A",
    0x9B: "\\u009B",
    0x9C: "\\u009C",
    0x9D: "\\u009D",
    0x9E: "\\u009E",
    0x9F: "\\u009F",
}
