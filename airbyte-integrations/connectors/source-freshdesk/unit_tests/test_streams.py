#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import random
from typing import Any, MutableMapping

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from source_freshdesk.streams import (
    Agents,
    Companies,
    Contacts,
    Conversations,
    Groups,
    Roles,
    SatisfactionRatings,
    Skills,
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
    ],
)
def test_full_refresh(stream, resource, authenticator, config, requests_mock):
    requests_mock.register_uri("GET", f"/api/{resource}", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(25)])

    stream = stream(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 25


def test_full_refresh_conversations(authenticator, config, requests_mock):
    requests_mock.register_uri("GET", "/api/tickets", json=[{"id": x, "updated_at": "2022-05-05T00:00:00Z"} for x in range(5)])
    for i in range(5):
        requests_mock.register_uri("GET", f"/api/tickets/{i}/conversations", json=[{"id": x} for x in range(10)])

    stream = Conversations(authenticator=authenticator, config=config)
    records = _read_full_refresh(stream)

    assert len(records) == 50


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
    highest_index = random.randint(0, 25)
    requests_mock.register_uri(
        "GET",
        f"/api/{resource}",
        json=[{"id": x, "updated_at": highest_updated_at if x == highest_index else other_updated_at} for x in range(25)],
    )

    stream = stream(authenticator=authenticator, config=config)
    records, state = _read_incremental(stream, {})

    assert len(records) == 25
    assert "updated_at" in state
    assert state["updated_at"] == highest_updated_at
