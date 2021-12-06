class NetsuiteAPIRequestError(Exception):
    """Raised when a Netsuite REST API request fails"""

    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self):
        return f"HTTP{self.status_code} - {self.response_text}"


class NetsuiteAPIResponseParsingError(NetsuiteAPIRequestError):
    """Raised when parsing a Netsuite REST API response fails"""
