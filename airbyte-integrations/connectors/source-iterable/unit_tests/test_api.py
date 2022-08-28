#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
import requests
import responses
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_iterable.api import Campaigns, CampaignsMetrics, Channels, Events, Lists, ListUsers, MessageTypes, Metadata, Templates, Users


@pytest.fixture(name="config")
def config_fixture():
    config = {"api_key": 123, "start_date": "2019-10-10T00:00:00"}
    return config


@pytest.mark.parametrize(
    "stream,expected_path",
    [
        (Lists, "lists"),
        (Campaigns, "campaigns"),
        (Channels, "channels"),
        (Events, "export/userEvents"),
        (MessageTypes, "messageTypes"),
        (Metadata, "metadata"),
    ],
)
def test_path(config, stream, expected_path):
    assert stream(authenticator=NoAuth()).path() == expected_path


@pytest.mark.parametrize(
    "stream,expected_path",
    [
        (CampaignsMetrics, "campaigns/metrics"),
        (Templates, "templates"),
    ],
)
def test_path2(config, stream, expected_path):
    assert stream(authenticator=NoAuth(), start_date="2019-10-10T00:00:00").path() == expected_path


def test_campaigns_metrics_csv():
    csv_string = """a,b,c,d
1, 2,, 3
6,, 1, 2
"""

    output = [{"a": 1, "b": 2, "d": 3}, {"a": 6, "c": 1, "d": 2}]

    assert CampaignsMetrics._parse_csv_string_to_dict(csv_string) == output


def test_list_users_get_list_id():
    url = "http://google.com?listId=1&another=another"
    ListUsers._get_list_id(url) == 1


def test_campaigns_metrics_request_params():
    s = CampaignsMetrics(authenticator=NoAuth(), start_date="2019-10-10T00:00:00")
    params = s.request_params(stream_slice={"campaign_ids": "c101"}, stream_state=None)
    assert params == {"campaignId": "c101", "startDateTime": "2019-10-10T00:00:00"}


def test_events_request_params():
    s = Events(authenticator=NoAuth())
    params = s.request_params(stream_slice={"email": "a@a.a"}, stream_state=None)
    assert params == {"email": "a@a.a", "includeCustomEvents": "true"}


def test_templates_parse_response():
    stream = Templates(authenticator=NoAuth(), start_date="2019-10-10T00:00:00")
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.iterable.com/api/1/foobar",
            json={"templates": [{"createdAt": "2022", "id": 1}]},
            status=200,
            content_type="application/json",
        )
        resp = requests.get("https://api.iterable.com/api/1/foobar")

        records = stream.parse_response(response=resp)

        assert list(records) == [{"id": 1, "createdAt": pendulum.parse("2022", strict=False)}]


def test_list_users_parse_response():
    stream = ListUsers(authenticator=NoAuth())
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.iterable.com/lists/getUsers?listId=100",
            body="user100",
            status=200,
            content_type="application/json",
        )
        resp = requests.get("https://api.iterable.com/lists/getUsers?listId=100")

        records = stream.parse_response(response=resp)

        assert list(records) == [{"email": "user100", "listId": 100}]


def test_campaigns_metrics_parse_response():

    stream = CampaignsMetrics(authenticator=NoAuth(), start_date="2019-10-10T00:00:00")
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.iterable.com/lists/getUsers?listId=100",
            body="""a,b,c,d
1, 2,, 3
6,, 1, 2
""",
            status=200,
            content_type="application/json",
        )
        resp = requests.get("https://api.iterable.com/lists/getUsers?listId=100")

        records = stream.parse_response(response=resp)

        assert list(records) == [
            {"data": {"a": 1, "b": 2, "d": 3}},
            {"data": {"a": 6, "c": 1, "d": 2}},
        ]


def test_iterable_stream_parse_response():
    stream = Lists(authenticator=NoAuth())
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.iterable.com/lists/getUsers?listId=100",
            json={"lists": [{"id": 1}, {"id": 2}]},
            status=200,
            content_type="application/json",
        )
        resp = requests.get("https://api.iterable.com/lists/getUsers?listId=100")

        records = stream.parse_response(response=resp)

        assert list(records) == [{"id": 1}, {"id": 2}]


def test_iterable_stream_backoff_time():
    stream = Lists(authenticator=NoAuth())
    assert stream.backoff_time(response=None) == stream.BACKOFF_TIME_CONSTANT


def test_iterable_export_stream_backoff_time():
    stream = Users(authenticator=NoAuth(), start_date="2019-10-10T00:00:00")
    assert stream.backoff_time(response=None) is None


@pytest.mark.parametrize(
    "current_state,record_date,expected_state",
    [
        ({}, "2022", {"profileUpdatedAt": "2022-01-01T00:00:00+00:00"}),
        ({"profileUpdatedAt": "2020-01-01T00:00:00+00:00"}, "2022", {"profileUpdatedAt": "2022-01-01T00:00:00+00:00"}),
        ({"profileUpdatedAt": "2022-01-01T00:00:00+00:00"}, "2020", {"profileUpdatedAt": "2022-01-01T00:00:00+00:00"}),
    ],
)
def test_get_updated_state(current_state, record_date, expected_state):
    stream = Users(authenticator=NoAuth(), start_date="2019-10-10T00:00:00")
    state = stream.get_updated_state(
        current_stream_state=current_state,
        latest_record={"profileUpdatedAt": pendulum.parse(record_date)},
    )
    assert state == expected_state
