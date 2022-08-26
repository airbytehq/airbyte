#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest import mock

import pendulum
import pytest
import responses
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_iterable.api import Users
from source_iterable.iterable_streams import StreamSlice


@pytest.fixture
def session_mock():
    with mock.patch("airbyte_cdk.sources.streams.http.http.requests") as requests_mock:
        session_mock = mock.MagicMock()
        response_mock = mock.MagicMock()
        requests_mock.Session.return_value = session_mock
        session_mock.send.return_value = response_mock
        response_mock.status_code = 200
        yield session_mock


def test_send_email_stream(session_mock):
    stream = Users(start_date="2020", authenticator=NoAuth())
    stream_slice = StreamSlice(start_date=pendulum.parse("2020"), end_date=pendulum.parse("2021"))
    _ = list(stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=stream_slice, stream_state={}))

    assert session_mock.send.called
    send_args = session_mock.send.call_args[1]
    assert send_args.get("stream") is True


@responses.activate
def test_stream_correct():
    stream_slice = StreamSlice(start_date=pendulum.parse("2020"), end_date=pendulum.parse("2021"))
    record_js = {"profileUpdatedAt": "2020"}
    NUMBER_OF_RECORDS = 10**2
    resp_body = "\n".join([json.dumps(record_js)] * NUMBER_OF_RECORDS)
    responses.add("GET", "https://api.iterable.com/api/export/data.json", body=resp_body)
    stream = Users(start_date="2020", authenticator=NoAuth())
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=stream_slice, stream_state={}))
    assert len(records) == NUMBER_OF_RECORDS
