# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


CHANNELS = [
    {"id": "C1", "name": "team-alpha", "is_member": True},
    {"id": "C2", "name": "team-beta", "is_member": True},
    {"id": "C3", "name": "team-external", "is_member": True, "is_ext_shared": True},
    {"id": "C4", "name": "general", "is_member": True},
    {"id": "C5", "name": "Team-upper", "is_member": True},
]


def read_stream(config, name):
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(name)).build()
    return read(get_source(config, name), config=config, catalog=catalog)


@pytest.mark.parametrize(
    "filters, expected",
    [
        ({"channel_filter": ["team-*"]}, ["C1", "C2", "C3"]),
        ({"channel_filter": ["team-bet?"]}, ["C2"]),
        ({"channel_filter": ["team-alpha", "general"]}, ["C1", "C4"]),
        ({"channel_filter": ["team-*"], "channel_exclude_filter": ["team-b*", "team-external"]}, ["C1"]),
        ({"channel_exclude_filter": ["team-*"]}, ["C4", "C5"]),
        ({"include_external_shared_channels": False}, ["C1", "C2", "C4", "C5"]),
        ({}, ["C1", "C2", "C3", "C4", "C5"]),
        ({"channel_filter": [], "channel_exclude_filter": []}, ["C1", "C2", "C3", "C4", "C5"]),
        ({"channel_filter": ["missing-*"]}, []),
        ({"channel_exclude_filter": ["*"]}, []),
    ],
)
def test_channels_selection(requests_mock, token_config, filters, expected):
    token_config.pop("channel_filter")
    token_config.update(filters)
    requests_mock.get("https://slack.com/api/conversations.list", json={"ok": True, "channels": CHANNELS})

    output = read_stream(token_config, "channels")

    assert [record.record.data["id"] for record in output.records] == expected
    assert not output.errors


def test_message_partitions_join_only_selected_channels(requests_mock, token_config):
    token_config.update(
        channel_filter=["team-*"],
        channel_exclude_filter=["team-beta"],
        include_external_shared_channels=False,
        join_channels=True,
    )
    channels = [dict(channel, is_member=False) for channel in CHANNELS]
    channels.extend(
        [
            {"id": "C6", "name": "team-archived", "is_member": False, "is_archived": True},
            {"id": "C7", "name": "team-member", "is_member": True},
        ]
    )
    requests_mock.get("https://slack.com/api/conversations.list", json={"ok": True, "channels": channels})
    joins = requests_mock.post("https://slack.com/api/conversations.join", json={"ok": True})
    history = requests_mock.get("https://slack.com/api/conversations.history", json={"ok": True, "messages": []})

    output = read_stream(token_config, "channel_messages")

    assert [request.json()["channel"] for request in joins.request_history] == ["C1"]
    assert {request.qs["channel"][0].upper() for request in history.request_history} == {"C1", "C7"}
    assert not output.errors
