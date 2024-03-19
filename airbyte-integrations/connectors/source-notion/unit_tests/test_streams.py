# #
# # Copyright (c) 2023 Airbyte, Inc., all rights reserved.
# #

# import random
# from http import HTTPStatus
# from unittest.mock import MagicMock

# import freezegun
# import pytest
# import requests
# from airbyte_cdk.models import SyncMode
# from source_notion.streams import Blocks, NotionStream


# @pytest.fixture
# def patch_base_class(mocker):
#     # Mock abstract methods to enable instantiating abstract class
#     mocker.patch.object(NotionStream, "path", "v0/example_endpoint")
#     mocker.patch.object(NotionStream, "primary_key", "test_primary_key")
#     mocker.patch.object(NotionStream, "__abstractmethods__", set())


# def test_request_params(patch_base_class):
#     stream = NotionStream(config=MagicMock())
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     expected_params = {}
#     assert stream.request_params(**inputs) == expected_params


# def test_next_page_token(patch_base_class, requests_mock):
#     stream = NotionStream(config=MagicMock())
#     requests_mock.get("https://dummy", json={"next_cursor": "aaa"})
#     inputs = {"response": requests.get("https://dummy")}
#     expected_token = {"next_cursor": "aaa"}
#     assert stream.next_page_token(**inputs) == expected_token


# @pytest.mark.parametrize(
#     "response_json, expected_output",
#     [({"next_cursor": "some_cursor", "has_more": True}, {"next_cursor": "some_cursor"}), ({"has_more": False}, None), ({}, None)],
# )
# def test_next_page_token_with_no_cursor(patch_base_class, response_json, expected_output):
#     stream = NotionStream(config=MagicMock())
#     mock_response = MagicMock()
#     mock_response.json.return_value = response_json
#     result = stream.next_page_token(mock_response)
#     assert result == expected_output


# def test_parse_response(patch_base_class, requests_mock):
#     stream = NotionStream(config=MagicMock())
#     requests_mock.get("https://dummy", json={"results": [{"a": 123}, {"b": "xx"}]})
#     resp = requests.get("https://dummy")
#     inputs = {"response": resp, "stream_state": MagicMock()}
#     expected_parsed_object = [{"a": 123}, {"b": "xx"}]
#     assert list(stream.parse_response(**inputs)) == expected_parsed_object


# def test_request_headers(patch_base_class):
#     stream = NotionStream(config=MagicMock())
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     expected_headers = {"Notion-Version": "2022-06-28"}
#     assert stream.request_headers(**inputs) == expected_headers


# def test_http_method(patch_base_class):
#     stream = NotionStream(config=MagicMock())
#     expected_method = "GET"
#     assert stream.http_method == expected_method


# @pytest.mark.parametrize(
#     ("http_status", "should_retry"),
#     [
#         (HTTPStatus.OK, False),
#         (HTTPStatus.BAD_REQUEST, True),
#         (HTTPStatus.TOO_MANY_REQUESTS, True),
#         (HTTPStatus.INTERNAL_SERVER_ERROR, True),
#         (HTTPStatus.BAD_GATEWAY, True),
#         (HTTPStatus.FORBIDDEN, False),
#     ],
# )
# def test_should_retry(patch_base_class, http_status, should_retry):
#     response_mock = MagicMock()
#     response_mock.status_code = http_status
#     stream = NotionStream(config=MagicMock())
#     assert stream.should_retry(response_mock) == should_retry


# def test_should_not_retry_with_ai_block(requests_mock):
#     stream = Blocks(parent=None, config=MagicMock())
#     json_response = {
#         "object": "error",
#         "status": 400,
#         "code": "validation_error",
#         "message": "Block type ai_block is not supported via the API.",
#     }
#     requests_mock.get("https://api.notion.com/v1/blocks/123", json=json_response, status_code=400)
#     test_response = requests.get("https://api.notion.com/v1/blocks/123")
#     assert not stream.should_retry(test_response)


# def test_should_not_retry_with_not_found_block(requests_mock):
#     stream = Blocks(parent=None, config=MagicMock())
#     json_response = {
#         "object": "error",
#         "status": 404,
#         "message": "Not Found for url: https://api.notion.com/v1/blocks/123/children?page_size=100",
#     }
#     requests_mock.get("https://api.notion.com/v1/blocks/123", json=json_response, status_code=404)
#     test_response = requests.get("https://api.notion.com/v1/blocks/123")
#     assert not stream.should_retry(test_response)


# def test_empty_blocks_results(requests_mock):
#     stream = Blocks(parent=None, config=MagicMock())
#     requests_mock.get(
#         "https://api.notion.com/v1/blocks/aaa/children",
#         json={
#             "next_cursor": None,
#         },
#     )
#     stream.block_id_stack = ["aaa"]
#     assert list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice=[])) == []


# @pytest.mark.parametrize(
#     "status_code,retry_after_header,expected_backoff",
#     [
#         (429, "10", 10.0),  # Case for 429 error with retry-after header
#         (429, None, 5.0),  # Case for 429 error without retry-after header, should default to 5.0
#         (504, None, None),  # Case for 500-level error, should default to None and use CDK exponential backoff
#         (400, None, 10.0),  # Case for specific 400-level error handled by check_invalid_start_cursor
#     ],
# )
# def test_backoff_time(status_code, retry_after_header, expected_backoff, patch_base_class):
#     response_mock = MagicMock(spec=requests.Response)
#     response_mock.status_code = status_code
#     response_mock.headers = {"retry-after": retry_after_header} if retry_after_header else {}
#     stream = NotionStream(config=MagicMock())

#     assert stream.backoff_time(response_mock) == expected_backoff


# @pytest.mark.parametrize(
#     "config, expected_start_date, current_time",
#     [
#         (
#             {"authenticator": "secret_token", "start_date": "2021-09-01T00:00:00.000Z"},
#             "2021-09-01T00:00:00.000Z",
#             "2022-09-22T00:00:00.000Z",
#         ),
#         ({"authenticator": "super_secret_token", "start_date": None}, "2020-09-22T00:00:00.000Z", "2022-09-22T00:00:00.000Z"),
#         ({"authenticator": "even_more_secret_token"}, "2021-01-01T12:30:00.000Z", "2023-01-01T12:30:00.000Z"),
#     ],
# )
# def test_set_start_date(patch_base_class, config, expected_start_date, current_time):
#     """
#     Test that start_date in config is either:
#       1. set to the value provided by the user
#       2. defaults to two years from the present date set by the test environment.
#     """
#     with freezegun.freeze_time(current_time):
#         stream = NotionStream(config=config)
#         assert stream.start_date == expected_start_date
