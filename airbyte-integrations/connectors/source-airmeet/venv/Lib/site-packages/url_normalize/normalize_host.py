"""URL host normalization."""

from __future__ import annotations

import idna

from .tools import force_unicode

DEFAULT_CHARSET = "utf-8"


def normalize_host(host: str, charset: str = DEFAULT_CHARSET) -> str:
    """Normalize host part of the url.

    Lowercase and strip of final dot.
    Also, handle IDN domains using IDNA2008 with UTS46 transitional processing.

    Params:
        host : string : url host, e.g., 'site.com'
        charset : string : encoding charset

    Returns:
        string : normalized host data.

    """
    host = force_unicode(host, charset)
    host = host.lower()
    host = host.strip(".")

    # Split domain into parts to handle each label separately
    parts = host.split(".")
    try:
        # Process each label separately to handle mixed unicode/ascii domains
        parts = [
            idna.encode(p, uts46=True, transitional=True).decode(charset)
            for p in parts
            if p
        ]
        return ".".join(parts)
    except idna.IDNAError:
        # Fallback to direct encoding if IDNA2008 processing fails
        return host.encode("idna").decode(charset)
