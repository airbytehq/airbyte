# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import pytest
import requests
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

# Ensure that the scheme is HTTP as requests only partially supports other schemes
# see https://github.com/psf/requests/blob/0b4d494192de489701d3a2e32acef8fb5d3f042e/src/requests/models.py#L424-L429
_A_URL = "http://test.com/"
_ANOTHER_URL = "http://another-test.com/"
_A_RESPONSE_BODY = "a body"
_ANOTHER_RESPONSE_BODY = "another body"
_A_RESPONSE = HttpResponse("any response")
_SOME_QUERY_PARAMS = {"q1": "query value"}
_SOME_HEADERS = {"h1": "header value"}
_OTHER_HEADERS = {"h2": "another header value"}
_SOME_REQUEST_BODY_MAPPING = {"first_field": "first_value", "second_field": 2}
_SOME_REQUEST_BODY_STR = "some_request_body"


class HttpMockerTest(TestCase):
    @HttpMocker()
    def test_given_get_request_match_when_decorate_then_return_response(self, http_mocker):
        http_mocker.get(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS),
            HttpResponse(_A_RESPONSE_BODY, 474, _OTHER_HEADERS),
        )

        response = requests.get(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS)

        assert response.text == _A_RESPONSE_BODY
        assert response.status_code == 474
        assert response.headers == _OTHER_HEADERS

    @HttpMocker()
    def test_given_delete_request_match_when_decorate_then_return_response(self, http_mocker):
        http_mocker.delete(
            HttpRequest(_A_URL, headers=_SOME_HEADERS),
            HttpResponse(_A_RESPONSE_BODY, 204, _OTHER_HEADERS),
        )

        response = requests.delete(_A_URL, headers=_SOME_HEADERS)

        assert response.text == _A_RESPONSE_BODY
        assert response.status_code == 204
        assert response.headers == _OTHER_HEADERS

    @HttpMocker()
    def test_given_loose_headers_matching_when_decorate_then_match(self, http_mocker):
        http_mocker.get(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS),
            HttpResponse(_A_RESPONSE_BODY, 474),
        )

        requests.get(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS | {"more strict query param key": "any value"})

    @HttpMocker()
    def test_given_post_request_match_when_decorate_then_return_response(self, http_mocker):
        http_mocker.post(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS, _SOME_REQUEST_BODY_STR),
            HttpResponse(_A_RESPONSE_BODY, 474),
        )

        response = requests.post(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS, data=_SOME_REQUEST_BODY_STR)

        assert response.text == _A_RESPONSE_BODY
        assert response.status_code == 474

    @HttpMocker()
    def test_given_multiple_responses_when_decorate_get_request_then_return_response(self, http_mocker):
        http_mocker.get(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS),
            [HttpResponse(_A_RESPONSE_BODY, 1), HttpResponse(_ANOTHER_RESPONSE_BODY, 2)],
        )

        first_response = requests.get(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS)
        second_response = requests.get(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS)

        assert first_response.text == _A_RESPONSE_BODY
        assert first_response.status_code == 1
        assert second_response.text == _ANOTHER_RESPONSE_BODY
        assert second_response.status_code == 2

    @HttpMocker()
    def test_given_multiple_responses_when_decorate_delete_request_then_return_response(self, http_mocker):
        http_mocker.delete(
            HttpRequest(_A_URL, headers=_SOME_HEADERS),
            [HttpResponse(_A_RESPONSE_BODY, 1), HttpResponse(_ANOTHER_RESPONSE_BODY, 2)],
        )

        first_response = requests.delete(_A_URL, headers=_SOME_HEADERS)
        second_response = requests.delete(_A_URL, headers=_SOME_HEADERS)

        assert first_response.text == _A_RESPONSE_BODY
        assert first_response.status_code == 1
        assert second_response.text == _ANOTHER_RESPONSE_BODY
        assert second_response.status_code == 2

    @HttpMocker()
    def test_given_multiple_responses_when_decorate_post_request_then_return_response(self, http_mocker):
        http_mocker.post(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS, _SOME_REQUEST_BODY_STR),
            [HttpResponse(_A_RESPONSE_BODY, 1), HttpResponse(_ANOTHER_RESPONSE_BODY, 2)],
        )

        first_response = requests.post(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS, data=_SOME_REQUEST_BODY_STR)
        second_response = requests.post(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS, data=_SOME_REQUEST_BODY_STR)

        assert first_response.text == _A_RESPONSE_BODY
        assert first_response.status_code == 1
        assert second_response.text == _ANOTHER_RESPONSE_BODY
        assert second_response.status_code == 2

    @HttpMocker()
    def test_given_more_requests_than_responses_when_decorate_then_raise_error(self, http_mocker):
        http_mocker.get(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS),
            [HttpResponse(_A_RESPONSE_BODY, 1), HttpResponse(_ANOTHER_RESPONSE_BODY, 2)],
        )

        last_response = [requests.get(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS) for _ in range(10)][-1]

        assert last_response.text == _ANOTHER_RESPONSE_BODY
        assert last_response.status_code == 2

    @HttpMocker()
    def test_given_all_requests_match_when_decorate_then_do_not_raise(self, http_mocker):
        http_mocker.get(
            HttpRequest(_A_URL, _SOME_QUERY_PARAMS, _SOME_HEADERS),
            _A_RESPONSE,
        )
        requests.get(_A_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS)

    def test_given_missing_requests_when_decorate_then_raise(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            http_mocker.get(
                HttpRequest(_A_URL),
                _A_RESPONSE,
            )

        with pytest.raises(ValueError) as exc_info:
            decorated_function()
        assert "Invalid number of matches" in str(exc_info.value)

    def test_given_assertion_error_when_decorate_then_raise_assertion_error(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            http_mocker.get(
                HttpRequest(_A_URL),
                _A_RESPONSE,
            )
            requests.get(_A_URL)
            assert False

        with pytest.raises(AssertionError):
            decorated_function()

    def test_given_assertion_error_but_missing_request_when_decorate_then_raise_missing_http_request(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            http_mocker.get(
                HttpRequest(_A_URL),
                _A_RESPONSE,
            )
            assert False

        with pytest.raises(ValueError) as exc_info:
            decorated_function()
        assert "Invalid number of matches" in str(exc_info.value)

    def test_given_request_does_not_match_when_decorate_then_raise(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            http_mocker.get(
                HttpRequest(_A_URL),
                _A_RESPONSE,
            )
            requests.get(_ANOTHER_URL, params=_SOME_QUERY_PARAMS, headers=_SOME_HEADERS)

        with pytest.raises(ValueError) as exc_info:
            decorated_function()
        assert "No matcher matches" in str(exc_info.value)

    def test_given_request_matches_multiple_matchers_when_decorate_then_match_first_one(self):
        less_granular_headers = {"less_granular": "1"}
        more_granular_headers = {"more_granular": "2"} | less_granular_headers

        @HttpMocker()
        def decorated_function(http_mocker):
            http_mocker.get(
                HttpRequest(_A_URL, headers=more_granular_headers),
                _A_RESPONSE,
            )
            http_mocker.get(
                HttpRequest(_A_URL, headers=less_granular_headers),
                _A_RESPONSE,
            )
            requests.get(_A_URL, headers=more_granular_headers)

        with pytest.raises(ValueError) as exc_info:
            decorated_function()
        assert "more_granular" in str(exc_info.value)  # the matcher corresponding to the first `http_mocker.get` is not matched

    def test_given_exact_number_of_call_provided_when_assert_number_of_calls_then_do_not_raise(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            request = HttpRequest(_A_URL)
            http_mocker.get(request, _A_RESPONSE)

            requests.get(_A_URL)
            requests.get(_A_URL)

            http_mocker.assert_number_of_calls(request, 2)

        decorated_function()
        # then do not raise

    def test_given_invalid_number_of_call_provided_when_assert_number_of_calls_then_raise(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            request = HttpRequest(_A_URL)
            http_mocker.get(request, _A_RESPONSE)

            requests.get(_A_URL)
            requests.get(_A_URL)

            http_mocker.assert_number_of_calls(request, 1)

        with pytest.raises(AssertionError):
            decorated_function()

    def test_given_unknown_request_when_assert_number_of_calls_then_raise(self):
        @HttpMocker()
        def decorated_function(http_mocker):
            http_mocker.get(HttpRequest(_A_URL), _A_RESPONSE)
            http_mocker.assert_number_of_calls(HttpRequest(_ANOTHER_URL), 1)

        with pytest.raises(ValueError):
            decorated_function()
