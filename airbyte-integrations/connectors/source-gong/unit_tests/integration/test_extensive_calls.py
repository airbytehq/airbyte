#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import START_DATE, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import empty_response, error_response, extensive_calls_response
from .utils import config, read_output


@pytest.fixture
def mock_config():
    return ConfigBuilder().build()


@HttpMocker()
def test_read_records(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.post(
        RequestBuilder.extensive_calls_endpoint().with_any_query_params().build(),
        extensive_calls_response(),
    )
    output = read_output(mock_config, "extensiveCalls", SyncMode.full_refresh)
    assert len(output.records) == 1
    # extensiveCalls adds id and startdatetime from metaData via transformations
    assert output.records[0].record.data["metaData"]["id"] == "test_call_789"
    assert output.records[0].record.data["metaData"]["title"] == "Test Extensive Call"


@HttpMocker()
def test_read_records_empty(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.post(
        RequestBuilder.extensive_calls_endpoint().with_any_query_params().build(),
        empty_response("calls"),
    )
    output = read_output(mock_config, "extensiveCalls", SyncMode.full_refresh)
    assert len(output.records) == 0


@HttpMocker()
def test_read_records_with_pagination(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.post(
        RequestBuilder.extensive_calls_endpoint().with_any_query_params().build(),
        [
            extensive_calls_response(call_id="call_1", has_next=True, cursor="cursor_1"),
            extensive_calls_response(call_id="call_2", has_next=False),
        ],
    )
    output = read_output(mock_config, "extensiveCalls", SyncMode.full_refresh)
    assert len(output.records) == 2


@HttpMocker()
def test_read_records_with_error_401(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.post(
        RequestBuilder.extensive_calls_endpoint().with_any_query_params().build(),
        error_response(),
    )
    output = read_output(mock_config, "extensiveCalls", SyncMode.full_refresh)
    assert len(output.records) == 0
