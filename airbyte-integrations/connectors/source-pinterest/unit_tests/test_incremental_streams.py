#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from pytest import fixture
from source_pinterest.streams import IncrementalPinterestSubStream

from .conftest import get_stream_by_name
from .utils import create_requests_response


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalPinterestSubStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalPinterestSubStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalPinterestSubStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    expected_cursor_field = "updated_time"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, test_current_stream_state):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    inputs = {"current_stream_state": test_current_stream_state, "latest_record": test_current_stream_state}
    expected_state = {"updated_time": "2021-10-22"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, test_current_stream_state, test_incremental_config):
    stream = IncrementalPinterestSubStream(None, config=test_incremental_config)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": "updated_time", "stream_state": test_current_stream_state}
    expected_stream_slice = {"start_date": "2021-10-22", "end_date": "2021-11-21"}
    assert next(stream.stream_slices(**inputs)) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(IncrementalPinterestSubStream, "cursor_field", "dummy_field")
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalPinterestSubStream(None, config=MagicMock())
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


@pytest.mark.parametrize(
    ("http_status", "expected_response_action"),
    (
        (HTTPStatus.OK, ResponseAction.SUCCESS),
        (HTTPStatus.BAD_REQUEST, ResponseAction.RETRY),
        (HTTPStatus.TOO_MANY_REQUESTS, ResponseAction.RETRY),
        (HTTPStatus.INTERNAL_SERVER_ERROR, ResponseAction.RETRY),
    ),
)
def test_should_retry(requests_mock, test_config, http_status, expected_response_action):
    response_mock = create_requests_response(requests_mock, http_status, {"code": 1} if HTTPStatus.BAD_REQUEST else {})
    stream = get_stream_by_name("campaign_analytics_report", test_config)
    assert stream._http_client._error_handler.interpret_response(response_mock).response_action == expected_response_action


@pytest.mark.parametrize(
    ("start_date", "stream_state", "expected_records"),
    (
        (
            None,
            {},
            [
                {"id": "campaign_id_1", "ad_account_id": "ad_account_id", "updated_time": 1711929600},
                {"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400},
            ],
        ),
        ("2024-04-02", {}, [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}]),
        (
            "2024-03-30",
            {
                "states": [
                    {"partition": {"id": "ad_account_id", "parent_slice": {}}, "cursor": {"updated_time": 1712016000}},
                ],
            },
            [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}],
        ),
        (
            "2024-04-02",
            {
                "states": [
                    {"partition": {"id": "ad_account_id", "parent_slice": {}}, "cursor": {"updated_time": 1711929599}},
                ],
            },
            [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}],
        ),
        (
            None,
            {
                "states": [
                    {"partition": {"id": "ad_account_id", "parent_slice": {}}, "cursor": {"updated_time": 1712016000}},
                ],
            },
            [{"id": "campaign_id_2", "ad_account_id": "ad_account_id", "updated_time": 1712102400}],
        ),
    ),
)
def test_semi_incremental_read(requests_mock, test_config, start_date, stream_state, expected_records):
    stream = get_stream_by_name("campaigns", test_config)
    stream.config["start_date"] = start_date

    ad_account_id = "ad_account_id"
    requests_mock.get(url="https://api.pinterest.com/v5/ad_accounts", json={"items": [{"id": ad_account_id}]})
    requests_mock.get(
        url=f"https://api.pinterest.com/v5/ad_accounts/{ad_account_id}/campaigns",
        json={
            "items": [
                {"id": "campaign_id_1", "ad_account_id": ad_account_id, "updated_time": 1711929600},  # 2024-04-01
                {"id": "campaign_id_2", "ad_account_id": ad_account_id, "updated_time": 1712102400},  # 2024-04-03
            ],
        },
    )

    stream.state = stream_state
    actual_records = [
        dict(record) for stream_slice in stream.stream_slices(sync_mode=SyncMode.incremental)
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)
    ]
    assert actual_records == expected_records
