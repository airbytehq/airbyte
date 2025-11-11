"""URL scheme validation and attachment."""

from __future__ import annotations

from .normalize_scheme import DEFAULT_SCHEME

# Schemes that require authority component reconstruction with //
AUTHORITY_SCHEMES = frozenset(["http", "https", "ftp", "ftps"])


def provide_url_scheme(url: str, default_scheme: str = DEFAULT_SCHEME) -> str:
    """Make sure we have valid url scheme.

    Params:
        url : string : the URL
        default_scheme : string : default scheme to use, e.g. 'https'

    Returns:
        string : updated url with validated/attached scheme

    """
    has_scheme = ":" in url[:7]
    is_universal_scheme = url.startswith("//")
    is_file_path = url == "-" or (url.startswith("/") and not is_universal_scheme)
    if not url or is_file_path:
        return url
    if not has_scheme:
        return f"{default_scheme}://{url.lstrip('/')}"
    scheme_part, rest = url.split(":", 1)
    if scheme_part.lower() not in AUTHORITY_SCHEMES:
        # handle cases like tel:, mailto:, etc.
        return url
    return f"{scheme_part}://{rest.lstrip('/')}"
