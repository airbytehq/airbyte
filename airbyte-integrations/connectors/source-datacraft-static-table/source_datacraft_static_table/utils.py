from urllib.parse import urlparse


def is_url_valid(url: str) -> bool:
    """
    Checks if the url is valid.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def normalize_url(url: str) -> str:
    """
    Normalizes the url.
    """
    return url.rstrip("/")


datacraft_type_to_json_type_map = {
    "STRING": "string",
    "INTEGER": "integer",
    "FLOAT": "number",
    "BOOLEAN": "boolean",
    "DATE": "string",
    "DATETIME": "string",
    "TIME": "string",
}
