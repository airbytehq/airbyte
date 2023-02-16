#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_nvd.source import Cpes, Cves, NvdStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(NvdStream, "path", "cves/2.0")
    mocker.patch.object(NvdStream, "primary_key", "id")
    mocker.patch.object(NvdStream, "cursor_field", "last_modified")
    mocker.patch.object(NvdStream, "__abstractmethods__", set())


@pytest.fixture
def stream_config():
    return {"modStartDate": "2022-01-01T00:00:00"}


def test_request_params(patch_base_class, stream_config):
    stream = NvdStream(stream_config)
    inputs = {
        "stream_slice": {"start_date": datetime(2022, 1, 1), "end_date": datetime(2022, 1, 2)},
        "stream_state": None,
        "next_page_token": {"startIndex": 1337},
    }
    expected_params = {"lastModStartDate": "2022-01-01T00:00:00.000000", "lastModEndDate": "2022-01-02T00:00:00.000000", "startIndex": 1337}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, stream_config):
    stream = NvdStream(stream_config)

    response = MagicMock()
    response.json = lambda: {"resultsPerPage": 2000, "startIndex": 0, "totalResults": 10000}

    inputs = {"response": response}
    expected_token = {"startIndex": 2000}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response_cves(stream_config):
    stream = Cves(stream_config)

    response = MagicMock()
    response.json = lambda: {"vulnerabilities": [{"cve": {"id": "CVE-1999-0095", "lastModified": "2019-06-11T20:29:00.263"}}]}
    expected_parsed_object = {
        "id": "CVE-1999-0095",
        "last_modified": "2019-06-11T20:29:00.263+00:00",
        "cve": {"id": "CVE-1999-0095", "lastModified": "2019-06-11T20:29:00.263"},
    }
    assert next(stream.parse_response(response)) == expected_parsed_object


def test_parse_response_cpes(stream_config):
    stream = Cpes(stream_config)

    response = MagicMock()
    response.json = lambda: {
        "products": [{"cpe": {"cpeNameId": "cpe:2.3:a:3com:3cdaemon:-:*:*:*:*:*:*:*", "lastModified": "2011-01-12T14:35:43.723"}}]
    }
    expected_parsed_object = {
        "id": "cpe:2.3:a:3com:3cdaemon:-:*:*:*:*:*:*:*",
        "last_modified": "2011-01-12T14:35:43.723+00:00",
        "cpe": {"cpeNameId": "cpe:2.3:a:3com:3cdaemon:-:*:*:*:*:*:*:*", "lastModified": "2011-01-12T14:35:43.723"},
    }
    assert next(stream.parse_response(response)) == expected_parsed_object


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        (HTTPStatus.FORBIDDEN, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry, stream_config):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = NvdStream(stream_config)
    assert stream.should_retry(response_mock) == should_retry


def test_stream_slices(patch_base_class, stream_config):
    stream = NvdStream(stream_config)
    inputs = {"sync_mode": None, "cursor_field": [], "stream_state": {"last_modified": "2022-12-12T00:00:00.000+00:00"}}
    expected_stream_slice = {
        "start_date": datetime(2022, 12, 12, tzinfo=timezone.utc),
        "end_date": datetime(2022, 12, 13, tzinfo=timezone.utc),
    }
    assert expected_stream_slice in stream.stream_slices(**inputs)


def test_supports_incremental(patch_base_class, stream_config):
    stream = NvdStream(stream_config)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_base_class, stream_config):
    stream = NvdStream(stream_config)
    assert stream.source_defined_cursor
