# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS

from .config import BUSINESS_UNIT_ID


ACCESS_TOKEN = "test-access-token"


def login_request(host: str = "login.salesforce.com") -> HttpRequest:
    """The login request. The body is compared as it is sent, so the order of its fields counts."""
    return HttpRequest(
        f"https://{host}/services/oauth2/token",
        body="client_id=test-client-id&grant_type=refresh_token&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )


class PardotRequestBuilder:
    """Builds a data request. It matches only a request with exactly these query parameters and both headers."""

    @classmethod
    def endpoint(cls, path: str) -> "PardotRequestBuilder":
        return cls(path)

    def __init__(self, path: str) -> None:
        self._path = path
        self._host = "pi.pardot.com"
        self._query_params: dict[str, str | list[str]] = {}
        self._any_query_params = False

    def with_host(self, host: str) -> "PardotRequestBuilder":
        self._host = host
        return self

    def with_query_param(self, name: str, value: str | int | list[str]) -> "PardotRequestBuilder":
        self._query_params[name] = value if isinstance(value, list) else str(value)
        return self

    def with_any_query_params(self) -> "PardotRequestBuilder":
        self._any_query_params = True
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            f"https://{self._host}/api/{self._path}",
            query_params=ANY_QUERY_PARAMS if self._any_query_params else self._query_params or None,
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID},
        )

    def url(self) -> str:
        """The request as the API writes it into `nextPageUrl`."""
        return f"https://{self._host}/api/{self._path}?{urlencode(self._query_params, safe=',')}"
