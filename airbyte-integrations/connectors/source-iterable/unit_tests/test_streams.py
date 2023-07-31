#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pendulum
import pytest
import requests
import responses
from airbyte_cdk.models import SyncMode
from source_iterable.streams import (
    Campaigns,
    CampaignsMetrics,
    Channels,
    Events,
    Lists,
    ListUsers,
    MessageTypes,
    Metadata,
    Templates,
    Users,
)
from source_iterable.utils import dateutil_parse, read_full_refresh


@pytest.mark.parametrize(
    "stream,date,slice,expected_path",
    [
        (Lists, False, {}, "lists"),
        (Campaigns, False, {}, "campaigns"),
        (Channels, False, {}, "channels"),
        (Events, False, {}, "export/userEvents"),
        (MessageTypes, False, {}, "messageTypes"),
        (Metadata, False, {}, "metadata"),
        (ListUsers, False, {"list_id": 1}, "lists/getUsers?listId=1"),
        (CampaignsMetrics, True, {}, "campaigns/metrics"),
        (Templates, True, {}, "templates"),
    ],
)
def test_path(config, stream, date, slice, expected_path):
    args = {"authenticator": None}
    if date:
        args["start_date"] = "2019-10-10T00:00:00"

    assert stream(**args).path(stream_slice=slice) == expected_path


def test_campaigns_metrics_csv():
    csv_string = "a,b,c,d\n1, 2,,3\n6,,1, 2\n"
    output = [{"a": 1, "b": 2, "d": 3}, {"a": 6, "c": 1, "d": 2}]

    assert CampaignsMetrics._parse_csv_string_to_dict(csv_string) == output


@pytest.mark.parametrize(
    "url,id",
    [
        ("http://google.com?listId=1&another=another", 1),
        ("http://google.com?another=another", None),
    ],
)
def test_list_users_get_list_id(url, id):
    assert ListUsers._get_list_id(url) == id


def test_campaigns_metrics_request_params():
    stream = CampaignsMetrics(authenticator=None, start_date="2019-10-10T00:00:00")
    params = stream.request_params(stream_slice={"campaign_ids": "c101"}, stream_state=None)
    assert params == {"campaignId": "c101", "startDateTime": "2019-10-10T00:00:00"}


def test_events_request_params():
    stream = Events(authenticator=None)
    params = stream.request_params(stream_slice={"email": "a@a.a"}, stream_state=None)
    assert params == {"email": "a@a.a", "includeCustomEvents": "true"}


def test_templates_parse_response():
    stream = Templates(authenticator=None, start_date="2019-10-10T00:00:00")
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://api.iterable.com/api/1/foobar",
            json={"templates": [{"createdAt": "2022-01-01", "id": 1}]},
            status=200,
            content_type="application/json",
        )
        resp = requests.get("https://api.iterable.com/api/1/foobar")

        records = stream.parse_response(response=resp)

        assert list(records) == [{"id": 1, "createdAt": dateutil_parse("2022-01-01")}]


def test_list_users_parse_response():
    stream = ListUsers(authenticator=None)
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

    stream = CampaignsMetrics(authenticator=None, start_date="2019-10-10T00:00:00")
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
    stream = Lists(authenticator=None)
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
    stream = Lists(authenticator=None)
    assert stream.backoff_time(response=None) is None


def test_iterable_export_stream_backoff_time():
    stream = Users(authenticator=None, start_date="2019-10-10T00:00:00")
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
    stream = Users(authenticator=None, start_date="2019-10-10T00:00:00")
    state = stream.get_updated_state(
        current_stream_state=current_state,
        latest_record={"profileUpdatedAt": pendulum.parse(record_date)},
    )
    assert state == expected_state


@responses.activate
def test_stream_stops_on_401(mock_lists_resp):
    # no requests should be made after getting 401 error despite the multiple slices
    users_stream = ListUsers(authenticator=None)
    responses.add(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", json={}, status=401)
    slices = 0
    for slice_ in users_stream.stream_slices(sync_mode=SyncMode.full_refresh):
        slices += 1
        _ = list(users_stream.read_records(stream_slice=slice_, sync_mode=SyncMode.full_refresh))
    assert len(responses.calls) == 1
    assert slices > 1


@responses.activate
def test_listuser_stream_keep_working_on_500():
    users_stream = ListUsers(authenticator=None)

    msg_error = "An error occurred. Please try again later. If problem persists, please contact your CSM"
    generic_error1 = {"msg": msg_error, "code": "GenericError"}
    generic_error2 = {"msg": msg_error, "code": "Generic Error"}

    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1000}, {"id": 2000}, {"id": 3000}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1000", json=generic_error1, status=500)
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=2000", body="one@d1.com\ntwo@d1.com\nthree@d1.com")
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=3000", json=generic_error2, status=500)
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=3000", body="one@d2.com\ntwo@d2.com\nthree@d2.com")

    expected_records = [
        {'email': 'one@d1.com', 'listId': 2000},
        {'email': 'two@d1.com', 'listId': 2000},
        {'email': 'three@d1.com', 'listId': 2000},
        {'email': 'one@d2.com', 'listId': 3000},
        {'email': 'two@d2.com', 'listId': 3000},
        {'email': 'three@d2.com', 'listId': 3000},
    ]

    records = list(read_full_refresh(users_stream))
    assert records == expected_records


@responses.activate
def test_events_read_full_refresh():
    stream = Events(authenticator=None)
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body='user1\nuser2\nuser3\nuser4\nuser5\nuser6')

    def get_body(emails):
        return "\n".join([json.dumps({"email": email}) for email in emails]) + "\n"

    msg_error = "An error occurred. Please try again later. If problem persists, please contact your CSM"
    generic_error1 = {"msg": msg_error, "code": "GenericError"}
    generic_error2 = {"msg": msg_error, "code": "Generic Error"}

    responses.get("https://api.iterable.com/api/export/userEvents?email=user1&includeCustomEvents=true", body=get_body(["user1"]))

    responses.get("https://api.iterable.com/api/export/userEvents?email=user2&includeCustomEvents=true", json=generic_error1, status=500)
    responses.get("https://api.iterable.com/api/export/userEvents?email=user2&includeCustomEvents=true", body=get_body(["user2"]))

    responses.get("https://api.iterable.com/api/export/userEvents?email=user3&includeCustomEvents=true", body=get_body(["user3"]))

    responses.get("https://api.iterable.com/api/export/userEvents?email=user4&includeCustomEvents=true", json=generic_error1, status=500)

    responses.get("https://api.iterable.com/api/export/userEvents?email=user5&includeCustomEvents=true", json=generic_error2, status=500)
    responses.get("https://api.iterable.com/api/export/userEvents?email=user5&includeCustomEvents=true", json=generic_error2, status=500)
    responses.get("https://api.iterable.com/api/export/userEvents?email=user5&includeCustomEvents=true", body=get_body(["user5"]))

    m = responses.get("https://api.iterable.com/api/export/userEvents?email=user6&includeCustomEvents=true", json=generic_error2, status=500)

    records = list(read_full_refresh(stream))
    assert [r["email"] for r in records] == ['user1', 'user2', 'user3', 'user5']
    assert m.call_count == 3


def test_retry_read_timeout():
    stream = Lists(authenticator=None)
    stream._session.send = MagicMock(side_effect=requests.exceptions.ReadTimeout)
    with pytest.raises(requests.exceptions.ReadTimeout):
        list(read_full_refresh(stream))
    stream._session.send.call_args[1] == {'timeout': (60, 300)}
    assert stream._session.send.call_count == stream.max_retries + 1

    stream = Campaigns(authenticator=None)
    stream._session.send = MagicMock(side_effect=requests.exceptions.ConnectionError)
    with pytest.raises(requests.exceptions.ConnectionError):
        list(read_full_refresh(stream))
    stream._session.send.call_args[1] == {'timeout': (60, 300)}
    assert stream._session.send.call_count == stream.max_retries + 1
