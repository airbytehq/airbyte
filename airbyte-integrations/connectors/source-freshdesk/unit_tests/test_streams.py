#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import random
from typing import Any, MutableMapping

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from conftest import find_stream


def _read_full_refresh(stream_instance: Stream):
    records = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for slice in slices:
        records.extend(list(stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.full_refresh)))
    return records


def _read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    res = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=slice, stream_state=stream_state)
        for record in records:
            res.append(record)
    return res, stream_instance.state


@pytest.mark.parametrize(
    "stream_name, resource",
    [
        ("agents", "agents"),
        ("companies", "companies"),
        ("contacts", "contacts"),
        ("groups", "groups"),
        ("roles", "roles"),
        ("skills", "skills"),
        ("time_entries", "time_entries"),
        ("satisfaction_ratings", "surveys/satisfaction_ratings"),
        ("business_hours", "business_hours"),
        ("canned_response_folders", "canned_response_folders"),
        ("discussion_categories", "discussions/categories"),
        ("email_configs", "email_configs"),
        ("email_mailboxes", "email/mailboxes"),
        ("products", "products"),
        ("scenario_automations", "scenario_automations"),
        ("sla_policies", "sla_policies"),
        ("solution_categories", "solutions/categories"),
        ("ticket_fields", "ticket_fields"),
        ("surveys", "surveys"),
    ],
)
def test_full_refresh(stream_name, resource, config, requests_mock):
    stream = find_stream(stream_name, config)
    requests_mock.register_uri("GET", f"/api/v2/{resource}", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(25)])

    records = _read_full_refresh(stream)

    assert len(records) == 25


# skipped due to https://github.com/airbytehq/airbyte-internal-issues/issues/6314
@pytest.mark.skip
def test_full_refresh_conversations(authenticator, config, requests_mock):
    requests_mock.register_uri("GET", "/api/v2/tickets", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for i in range(5):
        requests_mock.register_uri("GET", f"/api/v2/tickets/{i}/conversations", json=[{"id": x} for x in range(10)])

    stream = find_stream("conversations", config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


def test_full_refresh_settings(config, requests_mock):
    json_resp = {"primary_language": "en", "supported_languages": [], "portal_languages": []}
    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", json=json_resp)

    stream = find_stream("settings", config)
    records = _read_full_refresh(stream)

    assert len(records) == 1
    assert dict(records[0]) == json_resp


# skipped due to https://github.com/airbytehq/airbyte-internal-issues/issues/6314
@pytest.mark.skip
@pytest.mark.parametrize(
    "stream_name, resource",
    [
        ("contacts", "contacts"),
        ("tickets", "tickets"),
        ("satisfaction_ratings", "surveys/satisfaction_ratings"),
    ],
)
def test_incremental(stream_name, resource, config, requests_mock):
    highest_updated_at = "2022-04-25T22:00:00Z"
    other_updated_at = "2022-04-01T00:00:00Z"
    highest_index = random.randint(0, 24)

    requests_mock.register_uri(
        "GET",
        f"/api/v2/{resource}",
        json=[{"id": x, "updated_at": highest_updated_at if x == highest_index else other_updated_at} for x in range(25)],
    )

    stream = find_stream(stream_name, config=config)
    records, state = _read_incremental(stream, {})

    assert len(records) == 25
    assert "updated_at" in state
    assert state["updated_at"] == highest_updated_at


@pytest.mark.parametrize(
    "stream_name, parent_path, sub_paths",
    [
        ("canned_responses", "canned_response_folders", [f"canned_response_folders/{x}/responses" for x in range(5)]),
        # ("conversations", "tickets", [f"tickets/{x}/conversations" for x in range(5)]), Disabled due to issue with caching
        ("discussion_forums", "discussions/categories", [f"discussions/categories/{x}/forums" for x in range(5)]),
        ("solution_folders", "solutions/categories", [f"solutions/categories/{x}/folders" for x in range(5)]),
    ],
)
def test_substream_full_refresh(requests_mock, stream_name, parent_path, sub_paths, authenticator, config):
    requests_mock.register_uri("GET", "/api/v2/" + parent_path, json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for sub_path in sub_paths:
        requests_mock.register_uri("GET", "/api/v2/" + sub_path, json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(10)])

    stream = find_stream(stream_name=stream_name, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


@pytest.mark.skip  # Disabled due to issue with caching
@pytest.mark.parametrize(
    "stream_name, parent_path, sub_paths, sub_sub_paths",
    [
        (
            "discussion_topics",
            "discussions/categories",
            [f"discussions/categories/{x}/forums" for x in range(5)],
            [f"discussions/forums/{x}/topics" for x in range(5)],
        ),
        (
            "solution_articles",
            "solutions/categories",
            [f"solutions/categories/{x}/folders" for x in range(5)],
            [f"solutions/folders/{x}/articles" for x in range(5)],
        ),
    ],
)
def test_full_refresh_with_two_sub_levels(requests_mock, stream_name, parent_path, sub_paths, sub_sub_paths, config):
    requests_mock.register_uri("GET", f"/api/v2/{parent_path}", json=[{"id": x} for x in range(5)])
    for sub_path in sub_paths:
        requests_mock.register_uri("GET", f"/api/v2/{sub_path}", json=[{"id": x} for x in range(5)])
        for sub_sub_path in sub_sub_paths:
            requests_mock.register_uri("GET", f"/api/v2/{sub_sub_path}", json=[{"id": x} for x in range(10)])

    stream = find_stream(stream_name=stream_name, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 250


@pytest.mark.skip  # Disabled due to issue with caching
def test_full_refresh_discussion_comments(requests_mock, authenticator, config):
    requests_mock.register_uri("GET", "/api/v2/discussions/categories", json=[{"id": x} for x in range(2)])
    for i in range(2):
        requests_mock.register_uri("GET", f"/api/v2/discussions/categories/{i}/forums", json=[{"id": x} for x in range(3)])
        for j in range(3):
            requests_mock.register_uri("GET", f"/api/v2/discussions/forums/{j}/topics", json=[{"id": x} for x in range(4)])
            for k in range(4):
                requests_mock.register_uri("GET", f"/api/v2/discussions/topics/{k}/comments", json=[{"id": x} for x in range(5)])

    stream = find_stream(stream_name="discussion_comments", config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 120
