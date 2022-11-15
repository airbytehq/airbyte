#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import logging
from unittest.mock import MagicMock

import freezegun
import pendulum
import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from source_square.components import Oauth2AuthenticatorSquare, SquareSlicer, SquareSubstreamSlicer
from source_square.source import SourceSquare


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
    status, error = source.check_connection(logger=logging.getLogger('airbyte'), config=config)
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
        # "custom_field": "in_outbound_request",
        # "another_field": "exists_in_body",
    }
    options = {"refresh_token": "some_refresh_token"}

    req_mock.post(URL, json={"access_token": TOKEN, "expires_in": next_day})
    authenticator = Oauth2AuthenticatorSquare(
        token_refresh_endpoint=URL,
        client_secret="client_secret",
        client_id="client_id",
        refresh_token="refresh_token",
        config=config,
        options=options
    )
    token = authenticator.get_access_token()
    assert token == TOKEN
    assert authenticator.get_token_expiry_date() == pendulum.parse(next_day)


def test_slicer():
    date_time = "2022-09-05T10:10:10.000000Z"
    date_time_dict = {date_time: date_time}
    slicer = SquareSlicer(cursor_field=date_time, options=None, request_cursor_field=None)
    slicer.update_cursor(stream_slice=date_time_dict, last_record=date_time_dict)
    assert slicer.get_stream_state() == {date_time: "2022-09-05T10:10:10.000Z"}
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
                {"2022-09-05T10:10:10.000000Z": "2022-09-05T10:10:10.000000Z"},
                {'2022-09-05T10:10:10.000000Z': '2022-09-05T10:10:10.000Z'},
                [{"id": "some_id"}],
        ),
        (None, {}, []),
    ],
)
def test_sub_slicer(last_record, expected, records):
    date_time = "2022-09-05T10:10:10.000000Z"
    parent_slicer = SquareSlicer(cursor_field=date_time, options=None, request_cursor_field=None)
    SquareSlicer.read_records = MagicMock(return_value=records)
    slicer = SquareSubstreamSlicer(
        cursor_field=date_time,
        options=None,
        request_cursor_field=None,
        parent_stream=parent_slicer
    )
    stream_slice = next(slicer.stream_slices(SyncMode, {})) if records else {}
    slicer.update_cursor(stream_slice=stream_slice, last_record=last_record)
    assert slicer.get_stream_state() == expected


@pytest.mark.parametrize(
    "last_record, records, expected_data",
    [
        (
                {"2022-09-05T10:10:10.000000Z": "2022-09-05T10:10:10.000000Z"},
                [{"id": "some_id1"}],
                {'location_ids': ["some_id1"], 'start_date': '2022-09-05T10:10:10.000Z'}
        ),
        (
                {"2022-09-05T10:10:10.000000Z": "2022-09-05T10:10:10.000000Z"},
                [{"id": f"some_id{x}"} for x in range(11)],
                {'location_ids': [f"some_id{x}" for x in range(10)], 'start_date': '2022-09-05T10:10:10.000Z'}
        ),
    ],
)
def test_sub_slicer_request_body(last_record, records, expected_data):
    date_time = "2022-09-05T10:10:10.000000Z"
    parent_slicer = SquareSlicer(cursor_field=date_time, options=None, request_cursor_field=None)
    SquareSlicer.read_records = MagicMock(return_value=records)
    slicer = SquareSubstreamSlicer(
        cursor_field=date_time,
        options=None,
        request_cursor_field=None,
        parent_stream=parent_slicer
    )
    stream_slice = next(slicer.stream_slices(SyncMode, {})) if records else {}
    slicer.update_cursor(stream_slice=stream_slice, last_record=last_record)
    expected_request_body = {'location_ids': expected_data.get('location_ids'),
                             'query': {'filter': {'date_time_filter':
                                                      {'updated_at':
                                                           {'start_at': expected_data.get('start_date')}
                                                       }
                                                  },
                                       'sort': {'sort_field': 'UPDATED_AT', 'sort_order': 'ASC'}}}
    assert slicer.get_request_body_json(stream_state=slicer.get_stream_state(), stream_slice=stream_slice) == expected_request_body
