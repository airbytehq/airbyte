#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, Mock, patch

import pendulum
import pytest
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_sendgrid.source import SourceSendgrid
from source_sendgrid.streams import (
    Blocks,
    Campaigns,
    Contacts,
    GlobalSuppressions,
    Lists,
    Messages,
    Segments,
    SendgridStream,
    SendgridStreamIncrementalMixin,
    SendgridStreamOffsetPagination,
    SuppressionGroupMembers,
    SuppressionGroups,
    Templates,
)

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


def test_streams():
    streams = SourceSendgrid().streams(config={"apikey": "wrong.api.key123", "start_time": FAKE_NOW})

    assert len(streams) == 15


@patch.multiple(SendgridStreamOffsetPagination, __abstractmethods__=set())
def test_pagination(mocker):
    stream = SendgridStreamOffsetPagination()
    state = {}
    response = requests.Response()
    mocker.patch.object(response, "json", return_value={None: 1})
    mocker.patch.object(response, "request", return_value=MagicMock())
    next_page_token = stream.next_page_token(response)
    request_params = stream.request_params(stream_state=state, next_page_token=next_page_token)
    assert request_params == {"limit": 50}


@patch.multiple(SendgridStreamIncrementalMixin, __abstractmethods__=set())
def test_stream_state():
    stream = SendgridStreamIncrementalMixin(start_time=FAKE_NOW)
    state = {}
    request_params = stream.request_params(stream_state=state)
    assert request_params == {"end_time": pendulum.now().int_timestamp, "start_time": FAKE_NOW}


@pytest.mark.parametrize(
    "stream_class, url , expected",
    (
        [Templates, "https://api.sendgrid.com/v3/templates", []],
        [Lists, "https://api.sendgrid.com/v3/marketing/lists", []],
        [Campaigns, "https://api.sendgrid.com/v3/marketing/campaigns", []],
        [Contacts, "https://api.sendgrid.com/v3/marketing/contacts", []],
        [Segments, "https://api.sendgrid.com/v3/marketing/segments", []],
        [Blocks, "https://api.sendgrid.com/v3/suppression/blocks", ["name", "id", "contact_count", "_metadata"]],
        [SuppressionGroupMembers, "https://api.sendgrid.com/v3/asm/suppressions", ["name", "id", "contact_count", "_metadata"]],
        [SuppressionGroups, "https://api.sendgrid.com/v3/asm/groups", ["name", "id", "contact_count", "_metadata"]],
        [GlobalSuppressions, "https://api.sendgrid.com/v3/suppression/unsubscribes", ["name", "id", "contact_count", "_metadata"]],
    ),
)
def test_read_records(
    stream_class,
    url,
    expected,
    requests_mock,
):
    try:
        stream = stream_class(start_time=FAKE_NOW)
    except TypeError:
        stream = stream_class()
    requests_mock.get("https://api.sendgrid.com/v3/marketing", json={})
    requests_mock.get(url, json={"name": "test", "id": "id", "contact_count": 20, "_metadata": {"self": "self"}})
    records = list(stream.read_records(sync_mode=SyncMode))

    assert records == expected


@pytest.mark.parametrize(
    "stream_class, expected",
    (
        [Templates, "templates"],
        [Lists, "marketing/lists"],
        [Campaigns, "marketing/campaigns"],
        [Contacts, "marketing/contacts"],
        [Segments, "marketing/segments"],
        [Blocks, "suppression/blocks"],
        [SuppressionGroupMembers, "asm/suppressions"],
        [SuppressionGroups, "asm/groups"],
        [GlobalSuppressions, "suppression/unsubscribes"],
    ),
)
def test_path(stream_class, expected):
    stream = stream_class(Mock())
    assert stream.path() == expected


@pytest.mark.parametrize(
    "stream_class, status, expected",
    (
        (Messages, 400, False),
        (SuppressionGroupMembers, 401, False),
    ),
)
def test_should_retry_on_permission_error(requests_mock, stream_class, status, expected):
    stream = stream_class(Mock())
    response_mock = MagicMock()
    response_mock.status_code = status
    assert stream.should_retry(response_mock) == expected
