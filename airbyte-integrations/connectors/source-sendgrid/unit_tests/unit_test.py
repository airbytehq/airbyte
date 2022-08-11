#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import unittest

import pendulum
import pytest
import requests
from airbyte_cdk.logger import AirbyteLogger
from source_sendgrid.source import SourceSendgrid

FAKE_NOW = pendulum.DateTime(2022, 1, 1, tzinfo=pendulum.timezone("utc"))


@pytest.fixture()
def mock_pendulum_now(monkeypatch):
    pendulum_mock = unittest.mock.MagicMock(wraps=pendulum.now)
    pendulum_mock.return_value = FAKE_NOW
    monkeypatch.setattr(pendulum, "now", pendulum_mock)


def get_stream(stream_name):
    source = SourceSendgrid()
    streams = source.streams({})

    return [s for s in streams if s.name == stream_name][0]


def create_response():
    response = requests.Response()
    response_body = {}
    response.status_code = 200
    response._content = json.dumps(response_body).encode("utf-8")
    return response


def test_parse_response_gracefully_handles_nulls():
    response = create_response()
    assert [] == list(get_stream("contacts").retriever.parse_response(response, stream_slice={}, stream_state={}))


def test_source_wrong_credentials():
    source = SourceSendgrid()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"apikey": "wrong.api.key123"})
    assert not status


def test_messages_stream_request_params(mock_pendulum_now):
    stream = get_stream("messages")
    state = {"last_event_time": 1558359000}
    expected_params = {
        "query": 'last_event_time BETWEEN TIMESTAMP "2019-05-20T06:30:00Z" AND TIMESTAMP "2021-12-31T16:00:00Z"',
        "limit": 1000,
    }
    request_params = stream.retriever.request_params(
        stream_state=state, stream_slice={"start_time": "2019-05-20T06:30:00Z", "end_time": "2021-12-31T16:00:00Z"}
    )
    assert request_params == expected_params
