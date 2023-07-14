#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from unittest.mock import MagicMock

import freezegun
import pendulum
import pytest
import requests_mock
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from source_square.components import SquareSubstreamIncrementalSync
from source_square.source import SourceSquare

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
CURSOR_GRANULARITY = "PT0.000001S"


@pytest.fixture
def req_mock():
    with requests_mock.Mocker() as mock:
        yield mock


def test_source_wrong_credentials():
    source = SourceSquare()
    config = {
        "credentials": {"auth_type": "Apikey", "api_key": "bla"},
        "is_sandbox": True,
        "start_date": "2021-06-01",
        "include_deleted_objects": False,
    }
    status, error = source.check_connection(logger=logging.getLogger("airbyte"), config=config)
    assert not status


@freezegun.freeze_time("2020-01-01")
def test_refresh_access_token(req_mock):
    URL = "https://example.com"
    TOKEN = "test_token"
    next_day = "2020-01-02T00:00:00Z"
    config = {
        "refresh_endpoint": URL,
        "client_id": "some_client_id",
        "client_secret": "some_client_secret",
        "token_expiry_date": pendulum.now().subtract(days=2).to_rfc3339_string(),
    }
    parameters = {"refresh_token": "some_refresh_token"}

    req_mock.post(URL, json={"access_token": TOKEN, "expires_in": next_day})
    authenticator = DeclarativeOauth2Authenticator(
        token_refresh_endpoint=URL,
        client_secret="client_secret",
        client_id="client_id",
        refresh_token="refresh_token",
        token_expiry_date_format="YYYY-MM-DDTHH:mm:ss[Z]",
        config=config,
        parameters=parameters,
    )
    token = authenticator.get_access_token()
    assert token == TOKEN
    assert authenticator.get_token_expiry_date() == pendulum.parse(next_day)


@pytest.mark.parametrize(
    "state, last_record, expected, expected_stream_slice, records",
    [
        (
            {},
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            {"location_ids": ["some_id"]},
            [{"id": "some_id"}],
        ),
        (
            {"updated_at": "2023-01-01T00:00:00.000000Z"},
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            {"updated_at": "2023-01-01T00:00:00.000000Z"},
            {"location_ids": ["some_id"], "updated_at": "2023-01-01T00:00:00.000000Z"},
            [{"id": "some_id"}],
        ),
        (
            {"updated_at": "2200-01-01T00:00:00.000000Z"},
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            {"location_ids": ["some_id"], "updated_at": "expects_current_time_when_state_is_greater"},
            [{"id": "some_id"}],
        ),
        ({}, None, {}, {}, []),
    ],
)
def test_substream_incremental_sync(state, last_record, expected, expected_stream_slice, records):
    parent_stream = MagicMock()
    parent_stream.read_records = MagicMock(return_value=records)
    slicer = SquareSubstreamIncrementalSync(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000+0000", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000+0000", parameters={}),
        step="P1D",
        cursor_field="updated_at",
        datetime_format=DATETIME_FORMAT,
        cursor_granularity=CURSOR_GRANULARITY,
        parameters=None,
        config={"start_date": "2021-01-01T00:00:00.000000+0000"},
        parent_key="id",
        parent_stream=parent_stream,
    )

    slicer.set_initial_state(state)
    actual_stream_slice = next(slicer.stream_slices()) if records else {}

    # Covers the test case for abnormal state that is greater than the current time
    if "updated_at" in state and state["updated_at"] > datetime.now().strftime(DATETIME_FORMAT):
        assert actual_stream_slice["updated_at"] != state["updated_at"]
    else:
        assert actual_stream_slice == expected_stream_slice
        slicer.close_slice(actual_stream_slice, last_record)
        assert slicer.get_stream_state() == expected


@pytest.mark.parametrize(
    "last_record, records, expected_data",
    [
        (
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            [{"id": "some_id1"}],
            {"location_ids": ["some_id1"], "start_date": "2021-01-01T00:00:00.000000Z"},
        ),
        (
            {"updated_at": "2022-09-05T10:10:10.000000Z"},
            [{"id": f"some_id{x}"} for x in range(11)],
            {"location_ids": [f"some_id{x}" for x in range(10)], "start_date": "2021-01-01T00:00:00.000000Z"},
        ),
    ],
)
def test_sub_slicer_request_body(last_record, records, expected_data):
    parent_stream = MagicMock
    parent_stream.read_records = MagicMock(return_value=records)
    slicer = SquareSubstreamIncrementalSync(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.000000Z", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-01-10T00:00:00.000000Z", parameters={}),
        step="P1D",
        cursor_field="updated_at",
        datetime_format=DATETIME_FORMAT,
        cursor_granularity=CURSOR_GRANULARITY,
        parameters=None,
        config={"start_date": "2021-01-01T00:00:00.000000Z"},
        parent_key="id",
        parent_stream=parent_stream,
    )
    stream_slice = next(slicer.stream_slices()) if records else {}
    expected_request_body = {
        "location_ids": expected_data.get("location_ids"),
        "query": {
            "filter": {"date_time_filter": {"updated_at": {"start_at": expected_data.get("start_date")}}},
            "sort": {"sort_field": "UPDATED_AT", "sort_order": "ASC"},
        },
    }
    assert slicer.get_request_body_json(stream_state=slicer.get_stream_state(), stream_slice=stream_slice) == expected_request_body
