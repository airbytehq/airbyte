# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Optional, Union
from urllib.parse import parse_qs, urlencode, urlparse

ANY_QUERY_PARAMS = "any query_parameters"


def _is_subdict(small: Mapping[str, str], big: Mapping[str, str]) -> bool:
    return dict(big, **small) == big


class HttpRequest:
    def __init__(
        self,
        url: str,
        query_params: Optional[Union[str, Mapping[str, Union[str, List[str]]]]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._parsed_url = urlparse(url)
        self._query_params = query_params
        if not self._parsed_url.query and query_params:
            self._parsed_url = urlparse(f"{url}?{self._encode_qs(query_params)}")
        elif self._parsed_url.query and query_params:
            raise ValueError("If query params are provided as part of the url, `query_params` should be empty")

        self._headers = headers or {}

    def _encode_qs(self, query_params: Union[str, Mapping[str, Union[str, List[str]]]]) -> str:
        if isinstance(query_params, str):
            return query_params
        return urlencode(query_params, doseq=True)

    def matches(self, other: Any) -> bool:
        """
        Note that headers only need to be a subset of `other` in order to match
        """
        if isinstance(other, HttpRequest):
            return (
                self._parsed_url.scheme == other._parsed_url.scheme
                and self._parsed_url.hostname == other._parsed_url.hostname
                and self._parsed_url.path == other._parsed_url.path
                and (
                    ANY_QUERY_PARAMS in [self._query_params, other._query_params]
                    or parse_qs(self._parsed_url.query) == parse_qs(other._parsed_url.query)
                )
                and _is_subdict(other._headers, self._headers)
            )
        return False

    def __str__(self) -> str:
        return f"{self._parsed_url} with headers {self._headers})"

    def __repr__(self) -> str:
        return f"HttpRequest(request={self._parsed_url}, headers={self._headers})"
