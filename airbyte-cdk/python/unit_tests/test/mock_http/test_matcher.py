# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase
from unittest.mock import Mock

from airbyte_cdk.test.mock_http.matcher import HttpRequestMatcher
from airbyte_cdk.test.mock_http.request import HttpRequest


class HttpRequestMatcherTest(TestCase):
    def setUp(self) -> None:
        self._a_request = Mock(spec=HttpRequest)
        self._another_request = Mock(spec=HttpRequest)
        self._request_to_match = Mock(spec=HttpRequest)
        self._matcher = HttpRequestMatcher(self._request_to_match, 1)

    def test_given_request_matches_when_matches_then_has_expected_match_count(self):
        self._a_request.matches.return_value = True
        self._matcher.matches(self._a_request)
        assert self._matcher.has_expected_match_count()

    def test_given_request_does_not_match_when_matches_then_does_not_have_expected_match_count(self):
        self._a_request.matches.return_value = False
        self._matcher.matches(self._a_request)

        assert not self._matcher.has_expected_match_count()
        assert self._matcher.actual_number_of_matches == 0

    def test_given_many_requests_with_some_match_when_matches_then_has_expected_match_count(self):
        self._a_request.matches.return_value = True
        self._another_request.matches.return_value = False
        self._matcher.matches(self._a_request)
        self._matcher.matches(self._another_request)

        assert self._matcher.has_expected_match_count()
        assert self._matcher.actual_number_of_matches == 1

    def test_given_expected_number_of_requests_met_when_matches_then_has_expected_match_count(self):
        _matcher = HttpRequestMatcher(self._request_to_match, 2)
        self._a_request.matches.return_value = True
        _matcher.matches(self._a_request)
        _matcher.matches(self._a_request)

        assert _matcher.has_expected_match_count()
        assert _matcher.actual_number_of_matches == 2

    def test_given_expected_number_of_requests_not_met_when_matches_then_does_not_have_expected_match_count(self):
        _matcher = HttpRequestMatcher(self._request_to_match, 2)
        self._a_request.matches.side_effect = [True, False]
        _matcher.matches(self._a_request)
        _matcher.matches(self._a_request)

        assert not _matcher.has_expected_match_count()
