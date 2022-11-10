#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import random
from typing import Any, MutableMapping
from unittest.mock import PropertyMock, patch

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_freshdesk.streams import (
    Agents,
    BusinessHours,
    CannedResponseFolders,
    CannedResponses,
    Companies,
    Contacts,
    Conversations,
    DiscussionCategories,
    DiscussionComments,
    DiscussionForums,
    DiscussionTopics,
    EmailConfigs,
    EmailMailboxes,
    Groups,
    Products,
    Roles,
    SatisfactionRatings,
    ScenarioAutomations,
    Settings,
    Skills,
    SlaPolicies,
    SolutionArticles,
    SolutionCategories,
    SolutionFolders,
    Surveys,
    TicketFields,
    Tickets,
    TimeEntries,
)


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
    "stream, resource",
    [
        (Agents, "agents"),
        (Companies, "companies"),
        (Contacts, "contacts"),
        (Groups, "groups"),
        (Roles, "roles"),
        (Skills, "skills"),
        (TimeEntries, "time_entries"),
        (SatisfactionRatings, "surveys/satisfaction_ratings"),
        (BusinessHours, "business_hours"),
        (CannedResponseFolders, "canned_response_folders"),
        (DiscussionCategories, "discussions/categories"),
        (EmailConfigs, "email_configs"),
        (EmailMailboxes, "email/mailboxes"),
        (Products, "products"),
        (ScenarioAutomations, "scenario_automations"),
        (SlaPolicies, "sla_policies"),
        (SolutionCategories, "solutions/categories"),
        (TicketFields, "ticket_fields"),
        (Surveys, "surveys"),
    ],
)
def test_full_refresh(stream, resource, authenticator, config, requests_mock):
    requests_mock.register_uri("GET", f"/api/v2/{resource}", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(25)])

    stream = stream(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 25


def test_full_refresh_conversations(authenticator, config, requests_mock):
    requests_mock.register_uri("GET", "/api/v2/tickets", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for i in range(5):
        requests_mock.register_uri("GET", f"/api/v2/tickets/{i}/conversations", json=[{"id": x} for x in range(10)])

    stream = Conversations(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


def test_full_refresh_settings(authenticator, config, requests_mock):
    json_resp = {"primary_language": "en", "supported_languages": [], "portal_languages": []}
    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", json=json_resp)

    stream = Settings(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 1
    assert records[0] == json_resp


@pytest.mark.parametrize(
    "stream, resource",
    [
        (Contacts, "contacts"),
        (Tickets, "tickets"),
        (SatisfactionRatings, "surveys/satisfaction_ratings"),
    ],
)
def test_incremental(stream, resource, authenticator, config, requests_mock):
    highest_updated_at = "2022-04-25T22:00:00Z"
    other_updated_at = "2022-04-01T00:00:00Z"
    highest_index = random.randint(0, 24)
    with patch(f"source_freshdesk.streams.{stream.__name__}.use_cache", new_callable=PropertyMock, return_value=False):
        requests_mock.register_uri(
            "GET",
            f"/api/v2/{resource}",
            json=[{"id": x, "updated_at": highest_updated_at if x == highest_index else other_updated_at} for x in range(25)],
        )

        stream = stream(authenticator=authenticator, config=config)
        records, state = _read_incremental(stream, {})

        assert len(records) == 25
        assert "updated_at" in state
        assert state["updated_at"] == highest_updated_at


@pytest.mark.parametrize(
    "stream_class, parent_path, sub_paths",
    [
        (CannedResponses, "canned_response_folders", [f"canned_response_folders/{x}/responses" for x in range(5)]),
        (Conversations, "tickets", [f"tickets/{x}/conversations" for x in range(5)]),
        (DiscussionForums, "discussions/categories", [f"discussions/categories/{x}/forums" for x in range(5)]),
        (SolutionFolders, "solutions/categories", [f"solutions/categories/{x}/folders" for x in range(5)]),
    ],
)
def test_substream_full_refresh(requests_mock, stream_class, parent_path, sub_paths, authenticator, config):
    requests_mock.register_uri("GET", "/api/v2/" + parent_path, json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for sub_path in sub_paths:
        requests_mock.register_uri("GET", "/api/v2/" + sub_path, json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(10)])

    stream = stream_class(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


@pytest.mark.parametrize(
    "stream_class, parent_path, sub_paths, sub_sub_paths",
    [
        (
            DiscussionTopics,
            "discussions/categories",
            [f"discussions/categories/{x}/forums" for x in range(5)],
            [f"discussions/forums/{x}/topics" for x in range(5)],
        ),
        (
            SolutionArticles,
            "solutions/categories",
            [f"solutions/categories/{x}/folders" for x in range(5)],
            [f"solutions/folders/{x}/articles" for x in range(5)],
        ),
    ],
)
def test_full_refresh_with_two_sub_levels(requests_mock, stream_class, parent_path, sub_paths, sub_sub_paths, authenticator, config):
    requests_mock.register_uri("GET", f"/api/v2/{parent_path}", json=[{"id": x} for x in range(5)])
    for sub_path in sub_paths:
        requests_mock.register_uri("GET", f"/api/v2/{sub_path}", json=[{"id": x} for x in range(5)])
        for sub_sub_path in sub_sub_paths:
            requests_mock.register_uri("GET", f"/api/v2/{sub_sub_path}", json=[{"id": x} for x in range(10)])

    stream = stream_class(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 250


def test_full_refresh_discussion_comments(requests_mock, authenticator, config):
    requests_mock.register_uri("GET", "/api/v2/discussions/categories", json=[{"id": x} for x in range(2)])
    for i in range(2):
        requests_mock.register_uri("GET", f"/api/v2/discussions/categories/{i}/forums", json=[{"id": x} for x in range(3)])
        for j in range(3):
            requests_mock.register_uri("GET", f"/api/v2/discussions/forums/{j}/topics", json=[{"id": x} for x in range(4)])
            for k in range(4):
                requests_mock.register_uri("GET", f"/api/v2/discussions/topics/{k}/comments", json=[{"id": x} for x in range(5)])

    stream = DiscussionComments(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 120
