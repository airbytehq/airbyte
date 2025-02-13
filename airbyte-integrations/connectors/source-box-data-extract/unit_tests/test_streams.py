#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

# from http import HTTPStatus
from typing import Any, Mapping

# from unittest.mock import MagicMock
import pytest
from source_box_data_extract.box_api import get_box_ccg_client
from source_box_data_extract.source import StreamTextRepresentationFolder


# @pytest.fixture
# def patch_base_class(mocker):
#     # Mock abstract methods to enable instantiating abstract class
#     # mocker.patch.object(BoxFileTextStream, "path", "v0/example_endpoint")
#     mocker.patch.object(StreamTextRepresentationFolder, "primary_key", "test_primary_key")
#     mocker.patch.object(StreamTextRepresentationFolder, "__abstractmethods__", set())


@pytest.fixture
def sample_config() -> Mapping[str, Any]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "box_subject_type": "user",
        "box_subject_id": "test_box_subject_id",
        "folder_id": "test_folder_id",
    }


def test_stream_text_representation_folder(sample_config):
    client = get_box_ccg_client(sample_config)
    stream = StreamTextRepresentationFolder(client, sample_config["folder_id"])

    assert stream.folder_id == sample_config["folder_id"]
    assert stream.client == client
    assert stream.primary_key == "id"


# def test_request_params(patch_base_class):
#     stream = BoxFileTextStream()
#     # TODO: replace this with your input parameters
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     # TODO: replace this with your expected request parameters
#     expected_params = {}
#     assert stream.request_params(**inputs) == expected_params


# def test_next_page_token(patch_base_class):
#     stream = BoxFileTextStream()
#     # TODO: replace this with your input parameters
#     inputs = {"response": MagicMock()}
#     # TODO: replace this with your expected next page token
#     expected_token = None
#     assert stream.next_page_token(**inputs) == expected_token


# def test_parse_response(patch_base_class):
#     config: Mapping[str, Any] = {}
#     config["client_id"] = "test_client_id"
#     config["client_secret"] = "test_client_secret"
#     config["box_subject_type"] = "user"
#     config["box_subject_id"] = "test_box_subject_id"

#     config["folder_id"] = "test_folder_id"


#     client = get_box_ccg_client(config)
#     stream = StreamTextRepresentationFolder(client,config["folder_id"])

#     # TODO: replace this with your input parameters
#     inputs = {"response": MagicMock()}
#     # TODO: replace this with your expected parced object
#     expected_parsed_object = {}
#     assert next(stream.parse_response(**inputs)) == expected_parsed_object


# def test_request_headers(patch_base_class):
#     stream = BoxFileTextStream()
#     # TODO: replace this with your input parameters
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     # TODO: replace this with your expected request headers
#     expected_headers = {}
#     assert stream.request_headers(**inputs) == expected_headers


# def test_http_method(patch_base_class):
#     stream = BoxFileTextStream()
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
#     stream = BoxFileTextStream()
#     assert stream.should_retry(response_mock) == should_retry


# def test_backoff_time(patch_base_class):
#     response_mock = MagicMock()
#     stream = BoxFileTextStream()
#     expected_backoff_time = None
#     assert stream.backoff_time(response_mock) == expected_backoff_time
