#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json

import pytest
import requests
import responses
from source_iterable.source import SourceIterable
from source_iterable.streams import Campaigns, CampaignsMetrics, Templates
from source_iterable.utils import dateutil_parse

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice


def test_campaigns_metrics_csv():
    csv_string = "a,b,c,d\n1, 2,,3\n6,,1, 2\n"
    output = [{"a": 1, "b": 2, "d": 3}, {"a": 6, "c": 1, "d": 2}]
    assert CampaignsMetrics._parse_csv_string_to_dict(csv_string) == output


def test_campaigns_metrics_request_params():
    stream = CampaignsMetrics(authenticator=None, start_date="2019-10-10T00:00:00")
    params = stream.request_params(stream_slice={"campaign_ids": "c101"}, stream_state=None)
    assert params == {"campaignId": "c101", "startDateTime": "2019-10-10T00:00:00"}


@responses.activate
def test_stream_stops_on_401(config):
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}, {"id": 2}]})
    users_stream = next(filter(lambda x: x.name == "list_users", SourceIterable().streams(config=config)))
    responses.add(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", json={}, status=401)
    responses.add(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=2", json={}, status=401)
    slices = 0
    with pytest.raises(AirbyteTracedException):
        for slice_ in users_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            slices += 1
            _ = list(users_stream.read_records(stream_slice=slice_, sync_mode=SyncMode.full_refresh))


@responses.activate
def test_listuser_stream_keep_working_on_500(config):
    stream = next(filter(lambda x: x.name == "list_users", SourceIterable().streams(config=config)))

    msg_error = "An error occurred. Please try again later. If problem persists, please contact your CSM"
    generic_error1 = {"msg": msg_error, "code": "GenericError"}
    generic_error2 = {"msg": msg_error, "code": "Generic Error"}

    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1000}, {"id": 2000}, {"id": 3000}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1000", json=generic_error1, status=500)
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1000", body="one@d1.com\ntwo@d1.com\nthree@d1.com")
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=2000", body="one@d1.com\ntwo@d1.com\nthree@d1.com")
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=3000", json=generic_error2, status=500)
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=3000", body="one@d2.com\ntwo@d2.com\nthree@d2.com")

    expected_records = [
        {"email": "one@d1.com", "listId": 1000},
        {"email": "two@d1.com", "listId": 1000},
        {"email": "three@d1.com", "listId": 1000},
        {"email": "one@d1.com", "listId": 2000},
        {"email": "two@d1.com", "listId": 2000},
        {"email": "three@d1.com", "listId": 2000},
        {"email": "one@d2.com", "listId": 3000},
        {"email": "two@d2.com", "listId": 3000},
        {"email": "three@d2.com", "listId": 3000},
    ]
    stream_slices = [
        StreamSlice(partition={"list_id": 1000}, cursor_slice={}),
        StreamSlice(partition={"list_id": 2000}, cursor_slice={}),
        StreamSlice(partition={"list_id": 3000}, cursor_slice={}),
    ]
    records = []
    for stream_slice in stream_slices:
        slice_records = list(
            map(lambda record: record.data, stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        )
        records.extend(slice_records)
    assert records == expected_records


@responses.activate
def test_events_read_full_refresh(config):
    stream = next(filter(lambda x: x.name == "events", SourceIterable().streams(config=config)))

    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body="user1\nuser2\nuser3\nuser4")

    def get_body(emails):
        return "\n".join([json.dumps({"email": email}) for email in emails]) + "\n"

    responses.get("https://api.iterable.com/api/export/userEvents?email=user1&includeCustomEvents=true", body=get_body(["user1"]))
    responses.get("https://api.iterable.com/api/export/userEvents?email=user2&includeCustomEvents=true", body=get_body(["user2"]))
    responses.get("https://api.iterable.com/api/export/userEvents?email=user3&includeCustomEvents=true", body=get_body(["user3"]))
    responses.get("https://api.iterable.com/api/export/userEvents?email=user4&includeCustomEvents=true", body=get_body(["user4"]))

    stream_slices = [
        StreamSlice(partition={"email": "user1", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
        StreamSlice(partition={"email": "user2", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
        StreamSlice(partition={"email": "user3", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
        StreamSlice(partition={"email": "user4", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
    ]

    records = []
    for stream_slice in stream_slices:
        slice_records = list(
            map(lambda record: record.data, stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        )
        records.extend(slice_records)

    assert [r["email"] for r in records] == ["user1", "user2", "user3", "user4"]


@responses.activate
@pytest.mark.limit_memory("20 MB")
def test_events_memory_limit(config, large_events_response):
    lines_in_response, file_path = large_events_response
    stream = next(filter(lambda x: x.name == "events", SourceIterable().streams(config=config)))

    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1", body="user1\nuser2\nuser3\nuser4")

    def get_body():
        return open(file_path, "rb", buffering=30)

    responses.get("https://api.iterable.com/api/export/userEvents?email=user1&includeCustomEvents=true", body=get_body())
    responses.get("https://api.iterable.com/api/export/userEvents?email=user2&includeCustomEvents=true", body=get_body())
    responses.get("https://api.iterable.com/api/export/userEvents?email=user3&includeCustomEvents=true", body=get_body())
    responses.get("https://api.iterable.com/api/export/userEvents?email=user4&includeCustomEvents=true", body=get_body())

    stream_slices = [
        StreamSlice(partition={"email": "user1", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
        StreamSlice(partition={"email": "user2", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
        StreamSlice(partition={"email": "user3", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
        StreamSlice(partition={"email": "user4", "parent_slice": {"list_id": 111111, "parent_slice": {}}}, cursor_slice={}),
    ]

    counter = 0
    for stream_slice in stream_slices:
        for _ in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
            counter += 1
    assert counter == lines_in_response * len(stream_slices)


@responses.activate
def test_campaigns_metric_slicer(config):
    responses.get("https://api.iterable.com/api/campaigns", json={"campaigns": [{"id": 1}]})
    responses.get(
        "https://api.iterable.com/api/campaigns/metrics?campaignId=1&startDateTime=2019-10-10T00%3A00%3A00",
        json={"id": 1, "Total Email Sends": 1},
    )

    stream = CampaignsMetrics(authenticator=None, start_date="2019-10-10T00:00:00")
    expected = [{"campaign_ids": [1]}]

    assert list(stream.stream_slices(sync_mode=SyncMode.full_refresh)) == expected


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


@pytest.mark.parametrize(
    "stream,date,slice,expected_path",
    [
        (Campaigns, False, {}, "campaigns"),
        (CampaignsMetrics, True, {}, "campaigns/metrics"),
        (Templates, True, {}, "templates"),
    ],
)
def test_path(config, stream, date, slice, expected_path):
    args = {"authenticator": None}
    if date:
        args["start_date"] = "2019-10-10T00:00:00"

    assert stream(**args).path(stream_slice=slice) == expected_path


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
