#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest import mock

import pendulum
import pytest
import responses
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from source_iterable.source import SourceIterable


@pytest.fixture
def session_mock():
    with mock.patch("airbyte_cdk.sources.streams.http.http.requests") as requests_mock:
        session_mock = mock.MagicMock()
        response_mock = mock.MagicMock()
        requests_mock.Session.return_value = session_mock
        session_mock.send.return_value = response_mock
        response_mock.status_code = 200
        yield session_mock


@responses.activate
def test_stream_correct(config):
    start_date = pendulum.parse("2020-01-01 00:00:00+00:00")
    end_date = pendulum.parse("2021-01-01 00:00:00+00:00")
    stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": start_date, "end_time": end_date})
    record_js = {"profileUpdatedAt": "2020-01-01 00:00:00 +00:00"}
    number_of_records = 10 ** 2
    resp_body = "\n".join([json.dumps(record_js)] * number_of_records)

    responses.add("GET", "https://api.iterable.com/api/export/data.json", body=resp_body)

    stream_name = "users"
    source_iterable = SourceIterable()
    stream = next(filter(lambda x: x.name == stream_name, source_iterable.streams(config=config)))
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=stream_slice, stream_state={}))

    assert len(records) == number_of_records
