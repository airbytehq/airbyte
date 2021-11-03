#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from unittest import mock

import pytest
import responses
from airbyte_cdk.models import SyncMode
from source_iterable.api import EmailSend


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
    stream = EmailSend(start_date="2020", api_key="")
    _ = list(stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=[], stream_state={}))

    assert session_mock.send.called
    send_args = session_mock.send.call_args[1]
    assert send_args.get("stream") is True


@responses.activate
def test_stream_correct():
    record_js = {"createdAt": "2020"}
    NUMBER_OF_RECORDS = 10 ** 2
    resp_body = "\n".join([json.dumps(record_js)] * NUMBER_OF_RECORDS)
    responses.add("GET", "https://api.iterable.com/api/export/data.json", body=resp_body)
    stream = EmailSend(start_date="2020", api_key="")
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=[], stream_state={}))
    assert len(records) == NUMBER_OF_RECORDS
