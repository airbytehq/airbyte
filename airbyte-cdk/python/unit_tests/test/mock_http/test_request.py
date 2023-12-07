# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import pytest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest


class HttpRequestMatcherTest(TestCase):
    def test_given_query_params_as_dict_and_string_then_query_params_are_properly_considered(self):
        with_string = HttpRequest("mock://test.com/path", query_params="a_query_param=q1&a_list_param=first&a_list_param=second")
        with_dict = HttpRequest("mock://test.com/path", query_params={"a_query_param": "q1", "a_list_param": ["first", "second"]})
        assert with_string.matches(with_dict) and with_dict.matches(with_string)

    def test_given_query_params_in_url_and_also_provided_then_raise_error(self):
        with pytest.raises(ValueError):
            HttpRequest("mock://test.com/path?a_query_param=1", query_params={"another_query_param": "2"})

    def test_given_same_url_query_params_and_subset_headers_when_matches_then_return_true(self):
        request_to_match = HttpRequest("mock://test.com/path", {"a_query_param": "q1"}, {"first_header": "h1"})
        request_received = HttpRequest("mock://test.com/path", {"a_query_param": "q1"}, {"first_header": "h1", "second_header": "h2"})
        assert request_received.matches(request_to_match)

    def test_given_url_differs_when_matches_then_return_false(self):
        assert not HttpRequest("mock://test.com/another_path").matches(HttpRequest("mock://test.com/path"))

    def test_given_query_params_differs_when_matches_then_return_false(self):
        request_to_match = HttpRequest("mock://test.com/path", {"a_query_param": "q1"})
        request_received = HttpRequest("mock://test.com/path", {"another_query_param": "q2"})
        assert not request_received.matches(request_to_match)

    def test_given_query_params_is_subset_differs_when_matches_then_return_false(self):
        request_to_match = HttpRequest("mock://test.com/path", {"a_query_param": "q1"})
        request_received = HttpRequest("mock://test.com/path", {"a_query_param": "q1", "another_query_param": "q2"})
        assert not request_received.matches(request_to_match)

    def test_given_headers_is_subset_differs_when_matches_then_return_true(self):
        request_to_match = HttpRequest("mock://test.com/path", headers={"first_header": "h1"})
        request_received = HttpRequest("mock://test.com/path", headers={"first_header": "h1", "second_header": "h2"})
        assert request_received.matches(request_to_match)

    def test_given_headers_value_does_not_match_differs_when_matches_then_return_false(self):
        request_to_match = HttpRequest("mock://test.com/path", headers={"first_header": "h1"})
        request_received = HttpRequest("mock://test.com/path", headers={"first_header": "value does not match"})
        assert not request_received.matches(request_to_match)

    def test_given_any_matcher_for_query_param_when_matches_then_return_true(self):
        request_to_match = HttpRequest("mock://test.com/path", {"a_query_param": "q1"})
        request_received = HttpRequest("mock://test.com/path", ANY_QUERY_PARAMS)

        assert request_received.matches(request_to_match)
        assert request_to_match.matches(request_received)

    def test_given_any_matcher_for_both_when_matches_then_return_true(self):
        request_to_match = HttpRequest("mock://test.com/path", ANY_QUERY_PARAMS)
        request_received = HttpRequest("mock://test.com/path", ANY_QUERY_PARAMS)
        assert request_received.matches(request_to_match)
