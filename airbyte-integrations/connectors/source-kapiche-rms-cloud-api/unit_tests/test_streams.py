from http import HTTPStatus
from unittest.mock import MagicMock
import pandas as pd

import pytest
from source_kapiche_export_api.source import KapicheExportApiStream, ExportDataGet


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(KapicheExportApiStream, "path", "test_endpoint/")
    # mocker.patch.object(KapicheExportApiStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = ExportDataGet("123", None)
    inputs = {"start_document_id": 1, "docs_count": 100, "export_format": "parquet"}
    expected_params = {
        "start_document_id": 1,
        "docs_count": 100,
        "export_format": "parquet",
    }
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = ExportDataGet("mock-uuid", MagicMock(), "name")
    # TODO: replace this with your input parameters
    headers = {"Kapiche-next-document-id": 100}
    response = MagicMock()
    response.headers = headers
    inputs = {"response": response}

    expected_token = 100
    assert stream.next_page_token(**inputs)[stream.cursor_field] == expected_token


def test_parse_response(patch_base_class):
    stream = ExportDataGet("uuid", MagicMock(), None)

    def iterate_content(*args, **kwargs):
        with open("./unit_tests/test_data.parquet", "rb") as file:
            yield file.read()

    response = MagicMock()
    expected_parsed_object = [
        {
            "document_id__": 490,
            "Aircraft": "Boeing 777-200ER",
            "Cabin Flown": "Business Class",
            "Date Flown": "2019-02-14T00:00:00",
            "Date Published": "2011-03-04T00:00:00",
            "NPS Category": "Detractor",
            "NPS Response": 7.0,
        },
        {
            "document_id__": 491,
            "Aircraft": "Boeing 777-200ER",
            "Cabin Flown": "Business Class",
            "Date Flown": "2018-07-15T00:00:00",
            "Date Published": "2018-09-07T00:00:00",
            "NPS Category": "Detractor",
            "NPS Response": 8.0,
        },
    ]
    response.iter_content = iterate_content
    inputs = {"response": response, "fname": "./test_data.parquet"}
    record_iter = stream.parse_response(**inputs)
    assert next(record_iter) == expected_parsed_object[0]
    assert next(record_iter) == expected_parsed_object[1]


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = ExportDataGet("uuid", MagicMock(), None)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = ExportDataGet("uuid", MagicMock(), None)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
