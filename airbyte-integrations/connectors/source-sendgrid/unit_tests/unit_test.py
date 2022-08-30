#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock

import pendulum
import pytest
import requests
from airbyte_cdk.logger import AirbyteLogger
from source_sendgrid.source import SourceSendgrid
from source_sendgrid.streams import Messages, SendgridStream

FAKE_NOW = pendulum.DateTime(2022, 1, 1, tzinfo=pendulum.timezone("utc"))


@pytest.fixture(name="sendgrid_stream")
def sendgrid_stream_fixture(mocker) -> SendgridStream:
    # Wipe the internal list of abstract methods to allow instantiating the abstract class without implementing its abstract methods
    mocker.patch("source_sendgrid.streams.SendgridStream.__abstractmethods__", set())
    # Mypy yells at us because we're init'ing an abstract class
    return SendgridStream()  # type: ignore


@pytest.fixture()
def mock_pendulum_now(monkeypatch):
    pendulum_mock = unittest.mock.MagicMock(wraps=pendulum.now)
    pendulum_mock.return_value = FAKE_NOW
    monkeypatch.setattr(pendulum, "now", pendulum_mock)


def test_parse_response_gracefully_handles_nulls(mocker, sendgrid_stream: SendgridStream):
    response = requests.Response()
    mocker.patch.object(response, "json", return_value=None)
    mocker.patch.object(response, "request", return_value=MagicMock())
    assert [] == list(sendgrid_stream.parse_response(response))


def test_source_wrong_credentials():
    source = SourceSendgrid()
    status, error = source.check_connection(logger=AirbyteLogger(), config={"apikey": "wrong.api.key123"})
    assert not status


def test_messages_stream_request_params(mock_pendulum_now):
    start_time = 1558359830
    stream = Messages(start_time)
    state = {"last_event_time": 1558359000}
    request_params = stream.request_params(state)
    assert (
        request_params
        == "query=last_event_time%20BETWEEN%20TIMESTAMP%20%222019-05-20T13%3A30%3A00Z%22%20AND%20TIMESTAMP%20%222022-01-01T00%3A00%3A00Z%22&limit=1000"
    )
