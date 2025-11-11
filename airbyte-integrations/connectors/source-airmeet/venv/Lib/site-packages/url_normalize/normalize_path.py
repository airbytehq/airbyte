"""URL path normalization."""

from __future__ import annotations

from .tools import quote, unquote


def normalize_path(path: str, scheme: str) -> str:
    """Normalize path part of the url.

    Remove mention of default path number

    Params:
        path : string : url path, e.g., '/section/page.html'
        scheme : string : url scheme, e.g., 'http'

    Returns:
        string : normalized path data.

    """
    # Only perform percent-encoding where it is essential.
    # Always use uppercase A-through-F characters when percent-encoding.
    # All portions of the URI must be utf-8 encoded NFC from Unicode strings
    path = quote(unquote(path), "~:/#[]@!$&'()*+,;=")
    # Prevent dot-segments appearing in non-relative URI paths.
    if scheme in {"", "http", "https", "ftp", "file"}:
        output: list[str] = []
        for part in path.split("/"):
            if part == "":
                if not output:
                    output.append(part)
            elif part == ".":
                pass
            elif part == "..":
                if len(output) > 1:
                    output.pop()
            else:
                output.append(part)
        # The part variable is used in the final check
        last_part = part
        if last_part in {"", ".", ".."}:
            output.append("")
        path = "/".join(output)
    # For schemes that define an empty path to be equivalent to a path of "/",
    # use "/".
    if not path and scheme in {"http", "https", "ftp", "file"}:
        path = "/"
    return path
