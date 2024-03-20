from urllib.parse import parse_qs, urlparse


def parse_url_query_params(url: str) -> dict[str, str]:
    """Parse query parameters from URL.

    Example:
    >>> parse_url_query_params('https://example.com/?a=1&b=2')
    {'a': '1', 'b': '2'}
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return {key: value[0] for key, value in query_params.items()}
