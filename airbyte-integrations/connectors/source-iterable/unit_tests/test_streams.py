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
from source_iterable.streams import Campaigns, CampaignsMetrics, Templates
from source_iterable.utils import dateutil_parse
from source_iterable.source import SourceIterable
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
    for slice_ in users_stream.stream_slices(sync_mode=SyncMode.full_refresh):
        slices += 1
        _ = list(users_stream.read_records(stream_slice=slice_, sync_mode=SyncMode.full_refresh))
    assert len(responses.calls) == 2
    assert slices >= 1

@responses.activate
def test_listuser_stream(config):
    stream = next(filter(lambda x: x.name == "list_users", SourceIterable().streams(config=config)))
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1000}, {"id": 2000}]})
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=1000", body="one@d1.com\ntwo@d1.com\nthree@d1.com")
    responses.get("https://api.iterable.com/api/lists/getUsers?listId=2000", body="one@d2.com\ntwo@d2.com\nthree@d2.com")
    expected_records = [
        {"email": "one@d1.com", "listId": 1000},
        {"email": "two@d1.com", "listId": 1000},
        {"email": "three@d1.com", "listId": 1000},
        {"email": "one@d2.com", "listId": 2000},
        {"email": "two@d2.com", "listId": 2000},
        {"email": "three@d2.com", "listId": 2000},
    ]
    stream_slices = [
        StreamSlice(partition={"list_id": 1000}, cursor_slice={}),
        StreamSlice(partition={"list_id": 2000}, cursor_slice={})
    ]
    records = []
    for stream_slice in stream_slices:
        slice_records = list(map(lambda record: record.data, stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
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
        StreamSlice(partition={'email': 'user1', 'parent_slice': {'list_id': 111111, 'parent_slice': {}}}, cursor_slice={}),
        StreamSlice(partition={'email': 'user2', 'parent_slice': {'list_id': 111111, 'parent_slice': {}}}, cursor_slice={}),
        StreamSlice(partition={'email': 'user3', 'parent_slice': {'list_id': 111111, 'parent_slice': {}}}, cursor_slice={}),
        StreamSlice(partition={'email': 'user4', 'parent_slice': {'list_id': 111111, 'parent_slice': {}}}, cursor_slice={}),
    ]

    records = []
    for stream_slice in stream_slices:
        slice_records = list(map(lambda record: record.data, stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)))
        records.extend(slice_records)

    assert [r["email"] for r in records] == ["user1", "user2", "user3", "user4"]
