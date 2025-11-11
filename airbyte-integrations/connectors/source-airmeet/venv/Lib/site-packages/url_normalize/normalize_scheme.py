"""URL scheme normalization."""

from __future__ import annotations

DEFAULT_SCHEME = "https"


def normalize_scheme(scheme: str) -> str:
    """Normalize scheme part of the url.

    Params:
        scheme : string : url scheme, e.g., 'https'

    Returns:
        string : normalized scheme data.

    """
    return scheme.lower()
