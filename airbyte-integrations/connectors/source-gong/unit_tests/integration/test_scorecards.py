#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker

from .config import START_DATE, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import empty_response, error_response, scorecards_response
from .utils import config, read_output


@pytest.fixture
def mock_config():
    return ConfigBuilder().build()


@HttpMocker()
def test_read_records(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.get(
        RequestBuilder.scorecards_endpoint().with_any_query_params().build(),
        scorecards_response(),
    )
    output = read_output(mock_config, "scorecards", SyncMode.full_refresh)
    assert len(output.records) == 1
    assert output.records[0].record.data["scorecardId"] == "test_scorecard_678"
    assert output.records[0].record.data["scorecardName"] == "Test Scorecard"


@HttpMocker()
def test_read_records_empty(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.get(
        RequestBuilder.scorecards_endpoint().with_any_query_params().build(),
        empty_response("scorecards"),
    )
    output = read_output(mock_config, "scorecards", SyncMode.full_refresh)
    assert len(output.records) == 0


@HttpMocker()
def test_read_records_with_pagination(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.get(
        RequestBuilder.scorecards_endpoint().with_any_query_params().build(),
        [
            scorecards_response(scorecard_id="scorecard_1", has_next=True, cursor="cursor_1"),
            scorecards_response(scorecard_id="scorecard_2", has_next=False),
        ],
    )
    output = read_output(mock_config, "scorecards", SyncMode.full_refresh)
    assert len(output.records) == 2


@HttpMocker()
def test_read_records_with_error_401(http_mocker: HttpMocker, mock_config) -> None:
    http_mocker.get(
        RequestBuilder.scorecards_endpoint().with_any_query_params().build(),
        error_response(),
    )
    output = read_output(mock_config, "scorecards", SyncMode.full_refresh)
    assert len(output.records) == 0
