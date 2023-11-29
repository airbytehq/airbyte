# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from unittest.mock import Mock

from airbyte_cdk.test.http.matcher import HttpRequestMatcher
from airbyte_cdk.test.http.request import HttpRequest


class HttpRequestMatcherTest(TestCase):
    def setUp(self) -> None:
        self._a_request = Mock(spec=HttpRequest)
        self._another_request = Mock(spec=HttpRequest)
        self._request_to_match = Mock(spec=HttpRequest)
        self._matcher = HttpRequestMatcher(self._request_to_match)

    def test_given_request_matches_when_matches_then_was_called(self):
        self._a_request.matches.return_value = True
        self._matcher.matches(self._a_request)
        assert self._matcher.was_called()

    def test_given_request_does_not_match_when_matches_then_was_not_called(self):
        self._a_request.matches.return_value = False
        self._matcher.matches(self._a_request)
        assert not self._matcher.was_called()

    def test_given_many_requests_with_some_match_when_matches_then_was_called(self):
        self._a_request.matches.side_effect = [True, False]
        self._matcher.matches(self._a_request)
        self._matcher.matches(self._another_request)
        assert self._matcher.was_called()
