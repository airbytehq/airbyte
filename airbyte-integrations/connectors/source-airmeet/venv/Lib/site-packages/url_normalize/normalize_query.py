"""URL query normalization."""

from __future__ import annotations

from .param_allowlist import get_allowed_params
from .tools import quote, unquote

QUERY_PARAM_SAFE_CHARS = "~:/?[]@!$'()*+,;"


def process_query_param(param: str) -> str:
    """Process a single query parameter.

    This function normalizes the parameter by quoting reserved characters
    and ensuring the parameter is in the correct format.

    Params:
        param: The query parameter to process.

    Returns:
        str: The normalized query parameter.

    """
    if not param:
        return ""
    return quote(unquote(param), QUERY_PARAM_SAFE_CHARS)


def normalize_query(
    query: str,
    *,  # Force keyword-only arguments
    host: str | None = None,
    filter_params: bool = False,
    param_allowlist: list | dict | None = None,
) -> str:
    """Normalize query while preserving parameter order.

    Params:
        query: URL query string (e.g. 'param1=val1&param2')
        host: Domain for allowlist checks
        filter_params: If True, removes non-allowlisted parameters
        param_allowlist: Optional override for default allowlist

    Returns:
        Normalized query string with original parameter order

    """
    if not query:
        return ""

    processed = []
    for param in query.split("&"):
        if not param:
            continue
        key, _, value = param.partition("=")
        key = process_query_param(key)
        if filter_params:
            allowed_params = get_allowed_params(host, param_allowlist)
            if key not in allowed_params:
                continue
        value = process_query_param(value)
        processed.append(f"{key}={value}" if value else key)

    return "&".join(processed)
