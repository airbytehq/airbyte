# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.request import HttpRequest


class HttpRequestMatcher:
    def __init__(self, request: HttpRequest, minimum_number_of_expected_match: int):
        self._request_to_match = request
        self._minimum_number_of_expected_match = minimum_number_of_expected_match
        self._actual_number_of_matches = 0

    def matches(self, request: HttpRequest) -> bool:
        hit = request.matches(self._request_to_match)
        if hit:
            self._actual_number_of_matches += 1
        return hit

    def has_expected_match_count(self) -> bool:
        return self._actual_number_of_matches >= self._minimum_number_of_expected_match

    @property
    def actual_number_of_matches(self) -> int:
        return self._actual_number_of_matches

    @property
    def request(self) -> HttpRequest:
        return self._request_to_match

    def __str__(self) -> str:
        return (
            f"HttpRequestMatcher("
            f"request_to_match={self._request_to_match}, "
            f"minimum_number_of_expected_match={self._minimum_number_of_expected_match}, "
            f"actual_number_of_matches={self._actual_number_of_matches})"
        )
