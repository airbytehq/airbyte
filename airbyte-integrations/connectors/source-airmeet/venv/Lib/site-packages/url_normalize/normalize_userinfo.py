"""URL userinfo normalization."""

from __future__ import annotations


def normalize_userinfo(userinfo: str) -> str:
    """Normalize userinfo part of the url.

    Params:
        userinfo : string : url userinfo, e.g., 'user@'

    Returns:
        string : normalized userinfo data.

    """
    if userinfo in ["@", ":@"]:
        return ""
    return userinfo
