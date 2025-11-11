"""URL port normalization."""

from __future__ import annotations

DEFAULT_PORT = {
    "ftp": "21",
    "gopher": "70",
    "http": "80",
    "https": "443",
    "news": "119",
    "nntp": "119",
    "snews": "563",
    "snntp": "563",
    "telnet": "23",
    "ws": "80",
    "wss": "443",
}


def normalize_port(port: str, scheme: str) -> str:
    """Normalize port part of the url.

    Remove mention of default port number

    Params:
        port : string : url port, e.g., '8080'
        scheme : string : url scheme, e.g., 'http'

    Returns:
        string : normalized port data.

    """
    if not port.isdigit():
        return port
    port = str(int(port))
    if DEFAULT_PORT.get(scheme) == port:
        return ""
    return port
