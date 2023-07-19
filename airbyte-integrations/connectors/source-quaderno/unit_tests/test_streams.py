#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import Mock

from source_quaderno.streams import QuadernoStream


class TestQuadernoStream(unittest.TestCase):

    def setUp(self):
        # Initialize the QuadernoStream class with mock configuration data
        config = {
            'account_name': 'test_account',
            'start_date': '2023-01-01',
        }
        self.stream = QuadernoStream(config=config)

    def test_url_base(self):
        self.assertEqual(self.stream.url_base, "https://test_account.quadernoapp.com/api/")

    def test_primary_key(self):
        self.assertEqual(self.stream.primary_key, "id")

    def test_limit(self):
        self.assertEqual(self.stream.limit, 100)

    def test_next_page_token_has_more(self):
        # Mock the response with headers indicating there's another page
        response_mock = Mock()
        response_mock.headers = {
            'x-pages-hasmore': 'true',
            'x-pages-nextpage': 'https://test_account.quadernoapp.com/api/invoices?limit=100&created_before=1337'
        }

        # Call the next_page_token method
        next_page_token = self.stream.next_page_token(response_mock)

        # Assertions
        self.assertIsNotNone(next_page_token)
        self.assertEqual(next_page_token, {'limit': '100', 'created_before': '1337'})

    def test_next_page_token_no_more(self):
        # Mock the response with headers indicating there's no more page
        response_mock = Mock()
        response_mock.headers = {
            'x-pages-hasmore': 'false',
        }

        # Call the next_page_token method
        next_page_token = self.stream.next_page_token(response_mock)

        # Assertions
        self.assertIsNone(next_page_token)

    def test_request_params_with_next_page_token(self):
        # Call the request_params method with a next_page_token
        next_page_token = {'limit': 100, 'created_before': 1337}
        params = self.stream.request_params(stream_state={}, next_page_token=next_page_token)

        # Assertions
        self.assertEqual(params, {'limit': 100, 'created_before': 1337})

    def test_request_params_without_next_page_token(self):
        # Call the request_params method without a next_page_token
        params = self.stream.request_params(stream_state={})

        # Assertions
        self.assertEqual(params, {'limit': 100})

    def test_parse_response(self):
        # Mock the response.json() method
        response_mock = Mock()
        response_mock.json.return_value = [
            {"id": 1, "number": "1337", "issue_date": "2023-07-19"},
            {"id": 2, "number": "1338", "issue_date": "2023-07-19"}
        ]

        # Call the parse_response method
        records = list(self.stream.parse_response(response_mock))

        # Assertions
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], {"id": 1, "number": "1337", "issue_date": "2023-07-19"})
        self.assertEqual(records[1], {"id": 2, "number": "1338", "issue_date": "2023-07-19"})


# @pytest.fixture
# def patch_base_class(mocker):
#     # Mock abstract methods to enable instantiating abstract class
#     mocker.patch.object(QuadernoStream, "path", "v0/example_endpoint")
#     mocker.patch.object(QuadernoStream, "primary_key", "test_primary_key")
#     mocker.patch.object(QuadernoStream, "__abstractmethods__", set())


# def test_request_params(patch_base_class):
#     stream = QuadernoStream()
#     # TODO: replace this with your input parameters
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     # TODO: replace this with your expected request parameters
#     expected_params = {}
#     assert stream.request_params(**inputs) == expected_params


# def test_next_page_token(patch_base_class):
#     stream = QuadernoStream()
#     # TODO: replace this with your input parameters
#     inputs = {"response": MagicMock()}
#     # TODO: replace this with your expected next page token
#     expected_token = None
#     assert stream.next_page_token(**inputs) == expected_token


# def test_parse_response(patch_base_class):
#     stream = QuadernoStream()
#     # TODO: replace this with your input parameters
#     inputs = {"response": MagicMock()}
#     # TODO: replace this with your expected parced object
#     expected_parsed_object = {}
#     assert next(stream.parse_response(**inputs)) == expected_parsed_object


# def test_request_headers(patch_base_class):
#     stream = QuadernoStream()
#     # TODO: replace this with your input parameters
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     # TODO: replace this with your expected request headers
#     expected_headers = {}
#     assert stream.request_headers(**inputs) == expected_headers


# def test_http_method(patch_base_class):
#     stream = QuadernoStream()
#     # TODO: replace this with your expected http request method
#     expected_method = "GET"
#     assert stream.http_method == expected_method


# @pytest.mark.parametrize(
#     ("http_status", "should_retry"),
#     [
#         (HTTPStatus.OK, False),
#         (HTTPStatus.BAD_REQUEST, False),
#         (HTTPStatus.TOO_MANY_REQUESTS, True),
#         (HTTPStatus.INTERNAL_SERVER_ERROR, True),
#     ],
# )
# def test_should_retry(patch_base_class, http_status, should_retry):
#     response_mock = MagicMock()
#     response_mock.status_code = http_status
#     stream = QuadernoStream()
#     assert stream.should_retry(response_mock) == should_retry


# def test_backoff_time(patch_base_class):
#     response_mock = MagicMock()
#     stream = QuadernoStream()
#     expected_backoff_time = None
#     assert stream.backoff_time(response_mock) == expected_backoff_time
