"""URL domain validation and attachment."""

from __future__ import annotations


def provide_url_domain(url: str, default_domain: str | None = None) -> str:
    """Add default domain to URL if needed.

    For absolute paths (starting with '/'), adds the specified default domain.

    Params:
        url : str : the URL
        default_domain : str | None : default domain to use, e.g. 'example.com'

    Returns:
        str : URL with domain added if applicable

    """
    # Skip processing if no default domain provided or URL is empty or stdout
    if not default_domain or not url or url == "-":
        return url

    # Only apply to absolute paths (starting with '/')
    # but not scheme-relative URLs ('//')
    if url.startswith("/") and not url.startswith("//"):
        return "//" + default_domain + url

    return url
