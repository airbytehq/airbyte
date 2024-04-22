# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
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
        body: Optional[Union[str, bytes, Mapping[str, Any]]] = None,
    ) -> None:
        self._parsed_url = urlparse(url)
        self._query_params = query_params
        if not self._parsed_url.query and query_params:
            self._parsed_url = urlparse(f"{url}?{self._encode_qs(query_params)}")
        elif self._parsed_url.query and query_params:
            raise ValueError("If query params are provided as part of the url, `query_params` should be empty")

        self._headers = headers or {}
        self._body = body

    @staticmethod
    def _encode_qs(query_params: Union[str, Mapping[str, Union[str, List[str]]]]) -> str:
        if isinstance(query_params, str):
            return query_params
        return urlencode(query_params, doseq=True)

    def matches(self, other: Any) -> bool:
        """
        If the body of any request is a Mapping, we compare as Mappings which means that the order is not important.
        If the body is a string, encoding ISO-8859-1 will be assumed
        Headers only need to be a subset of `other` in order to match
        """
        if isinstance(other, HttpRequest):
            # if `other` is a mapping, we match as an object and formatting is not considers
            if isinstance(self._body, Mapping) or isinstance(other._body, Mapping):
                body_match = self._to_mapping(self._body) == self._to_mapping(other._body)
            else:
                body_match = self._to_bytes(self._body) == self._to_bytes(other._body)

            return (
                self._parsed_url.scheme == other._parsed_url.scheme
                and self._parsed_url.hostname == other._parsed_url.hostname
                and self._parsed_url.path == other._parsed_url.path
                and (
                    ANY_QUERY_PARAMS in (self._query_params, other._query_params)
                    or parse_qs(self._parsed_url.query) == parse_qs(other._parsed_url.query)
                )
                and _is_subdict(other._headers, self._headers)
                and body_match
            )
        return False

    @staticmethod
    def _to_mapping(body: Optional[Union[str, bytes, Mapping[str, Any]]]) -> Optional[Mapping[str, Any]]:
        if isinstance(body, Mapping):
            return body
        elif isinstance(body, bytes):
            return json.loads(body.decode())  # type: ignore  # assumes return type of Mapping[str, Any]
        elif isinstance(body, str):
            return json.loads(body)  # type: ignore  # assumes return type of Mapping[str, Any]
        return None

    @staticmethod
    def _to_bytes(body: Optional[Union[str, bytes]]) -> bytes:
        if isinstance(body, bytes):
            return body
        elif isinstance(body, str):
            # `ISO-8859-1` is the default encoding used by requests
            return body.encode("ISO-8859-1")
        return b""

    def __str__(self) -> str:
        return f"{self._parsed_url} with headers {self._headers} and body {self._body!r})"

    def __repr__(self) -> str:
        return f"HttpRequest(request={self._parsed_url}, headers={self._headers}, body={self._body!r})"
