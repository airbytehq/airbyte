"""URL fragment normalization."""

from __future__ import annotations

from .tools import quote, unquote


def normalize_fragment(fragment: str) -> str:
    """Normalize fragment part of the url.

    Params:
        fragment : string : url fragment, e.g., 'fragment'

    Returns:
        string : normalized fragment data.

    Notes:
        According to RFC 3986, the following characters are allowed in a fragment:
        fragment    = *( pchar / "/" / "?" )
        pchar       = unreserved / pct-encoded / sub-delims / ":" / "@"
        unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
        sub-delims  = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="
        We specifically allow "~" and "=" as safe characters during normalization.
        Other sub-delimiters could potentially be added to the `safe` list if needed.

    """
    return quote(unquote(fragment), safe="~=")
