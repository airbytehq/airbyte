"""Posix Properties."""
from __future__ import annotations

unicode_posix_properties = {
    "^alnum": "\x00-\x2f\x3a-\x40\x5c\x5b-\x60\x7b-\U0010ffff",
    "^alpha": "\x00-\x40\x5b-\x60\x7b-\U0010ffff",
    "^ascii": "\x80-\U0010ffff",
    "^blank": "\x00-\x08\x0a-\x1f\x21-\U0010ffff",
    "^cntrl": "\x20-\x5c\x7e\x80-\U0010ffff",
    "^digit": "\x00-\x2f\x3a-\U0010ffff",
    "^graph": "\x00-\x20\x7f-\U0010ffff",
    "^lower": "\x00-\x60\x7b-\U0010ffff",
    "^print": "\x00-\x1f\x7f-\U0010ffff",
    "^punct": "\x00-\x20\x30-\x39\x41-\x5a\x61-\x7a\x7f-\U0010ffff",
    "^space": "\x00-\x08\x0e-\x1f\x21-\U0010ffff",
    "^upper": "\x00-\x40\x5c\x5b-\U0010ffff",
    "^word": "\x00-\x2f\x3a-\x40\x5c\x5b-\x5e\x60\x7b-\U0010ffff",
    "^xdigit": "\x00-\x2f\x3a-\x40\x47-\x60\x67-\U0010ffff",
    "alnum": "\x30-\x39\x41-\x5a\x61-\x7a",
    "alpha": "\x41-\x5a\x61-\x7a",
    "ascii": "\x00-\x7f",
    "blank": "\x09\x20",
    "cntrl": "\x00-\x1f\x7f",
    "digit": "\x30-\x39",
    "graph": "\x21-\x5c\x7e",
    "lower": "\x61-\x7a",
    "print": "\x20-\x5c\x7e",
    "punct": "\x21-\x2f\x3a-\x40\x5c\x5b-\x60\x7b-\x5c\x7e",
    "space": "\x09-\x0d\x20",
    "upper": "\x41-\x5a",
    "word": "\x30-\x39\x41-\x5a\x5f\x61-\x7a",
    "xdigit": "\x30-\x39\x41-\x46\x61-\x66"
}

ascii_posix_properties = {
    "^alnum": "\x00-\x2f\x3a-\x40\x5c\x5b-\x60\x7b-\xff",
    "^alpha": "\x00-\x40\x5b-\x60\x7b-\xff",
    "^ascii": "\x80-\xff",
    "^blank": "\x00-\x08\x0a-\x1f\x21-\xff",
    "^cntrl": "\x20-\x5c\x7e\x80-\xff",
    "^digit": "\x00-\x2f\x3a-\xff",
    "^graph": "\x00-\x20\x7f-\xff",
    "^lower": "\x00-\x60\x7b-\xff",
    "^print": "\x00-\x1f\x7f-\xff",
    "^punct": "\x00-\x20\x30-\x39\x41-\x5a\x61-\x7a\x7f-\xff",
    "^space": "\x00-\x08\x0e-\x1f\x21-\xff",
    "^upper": "\x00-\x40\x5c\x5b-\xff",
    "^word": "\x00-\x2f\x3a-\x40\x5c\x5b-\x5e\x60\x7b-\xff",
    "^xdigit": "\x00-\x2f\x3a-\x40\x47-\x60\x67-\xff",
    "alnum": "\x30-\x39\x41-\x5a\x61-\x7a",
    "alpha": "\x41-\x5a\x61-\x7a",
    "ascii": "\x00-\x7f",
    "blank": "\x09\x20",
    "cntrl": "\x00-\x1f\x7f",
    "digit": "\x30-\x39",
    "graph": "\x21-\x5c\x7e",
    "lower": "\x61-\x7a",
    "print": "\x20-\x5c\x7e",
    "punct": "\x21-\x2f\x3a-\x40\x5c\x5b-\x60\x7b-\x5c\x7e",
    "space": "\x09-\x0d\x20",
    "upper": "\x41-\x5a",
    "word": "\x30-\x39\x41-\x5a\x5f\x61-\x7a",
    "xdigit": "\x30-\x39\x41-\x46\x61-\x66"
}


def get_posix_property(value: str, limit_ascii: bool = False) -> str:
    """Retrieve the POSIX category."""

    try:
        if limit_ascii:
            return ascii_posix_properties[value]
        else:
            return unicode_posix_properties[value]
    except Exception as e:  # pragma: no cover
        raise ValueError(f"'{value} is not a valid posix property") from e
