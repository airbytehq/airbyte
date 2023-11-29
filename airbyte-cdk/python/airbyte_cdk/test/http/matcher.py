# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.http.request import HttpRequest


class HttpRequestMatcher:
    def __init__(self, request: HttpRequest):
        self._request_to_match = request
        self._called = False

    def matches(self, request: HttpRequest) -> bool:
        hit = request.matches(self._request_to_match)
        if hit:
            self._called = True
        return hit

    def was_called(self) -> bool:
        return self._called

    @property
    def request(self) -> HttpRequest:
        return self._request_to_match

    def __str__(self) -> str:
        return f"HttpRequestMatcher(request_to_match={self._request_to_match}, called={self._called})"
