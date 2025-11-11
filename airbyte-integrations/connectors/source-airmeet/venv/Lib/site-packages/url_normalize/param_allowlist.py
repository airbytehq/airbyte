# Copyright (c) 2023. All rights reserved.
"""URL query parameter allowlist module."""

from __future__ import annotations

DEFAULT_ALLOWLIST = {
    "google.com": ["q", "ie"],
    "baidu.com": ["wd", "ie"],
    "bing.com": ["q"],
    "youtube.com": ["v", "search_query"],
}


def get_allowed_params(
    host: str | None = None,
    allowlist: dict | list | None = None,
) -> set[str]:
    """Get allowed parameters for a given domain.

    Params:
        host: Domain name to check (e.g. 'google.com')
        allowlist: Optional override for default allowlist
            If provided as a list, it will be used as is.
            If provided as a dictionary, it should map domain names to
            lists of allowed parameters.
            If None, the default allowlist will be used.

    Returns:
        Set of allowed parameter names for the domain

    """
    if isinstance(allowlist, list):
        return set(allowlist)

    if not host:
        return set()

    # Normalize host by removing www and port
    domain = host.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    domain = domain.split(":")[0]

    # Use default allowlist if none provided
    if allowlist is None:
        allowlist = DEFAULT_ALLOWLIST

    # Return allowed parameters for the domain, or an empty set if not found
    return set(allowlist.get(domain, []))
