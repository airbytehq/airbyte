#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import yaml

from airbyte_cdk.models import Status

from .conftest import YAML_FILE_PATH, get_source, parametrized_configs


def get_stream_by_name(stream_name, config):
    streams = get_source(config, stream_name)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@parametrized_configs
def test_streams(conversations_list, config, is_valid):
    source = get_source(config)
    if is_valid:
        streams = source.streams(config)
        assert len(streams) == 5
    else:
        with pytest.raises(Exception) as exc_info:
            _ = source.streams(config)
        assert "The path from `authenticator_selection_path` is not found in the config." in repr(exc_info.value)


@pytest.mark.parametrize(
    "status_code, response, is_connection_successful, error_msg",
    (
        (200, {"members": [{"id": 1, "name": "Abraham"}]}, True, None),
        (200, {"ok": False, "error": "invalid_auth"}, False, "Slack API authentication/permission error: invalid_auth."),
        (200, {"ok": False, "error": "missing_scope"}, False, "Slack API authentication/permission error: missing_scope."),
        (200, {"ok": False, "error": "not_authed"}, False, "Slack API authentication/permission error: not_authed."),
        (200, {"ok": False, "error": "account_inactive"}, False, "Slack API authentication/permission error: account_inactive."),
        (200, {"ok": False, "error": "token_revoked"}, False, "Slack API authentication/permission error: token_revoked."),
        (200, {"ok": False, "error": "token_expired"}, False, "Slack API authentication/permission error: token_expired."),
        (200, {"ok": False, "error": "no_permission"}, False, "Slack API authentication/permission error: no_permission."),
        (200, {"ok": False, "error": "plan_upgrade_required"}, False, "Slack API returned an unrecognized error: plan_upgrade_required."),
        (
            400,
            "Bad request",
            False,
            "Slack API users request denied or malformed (HTTP 403/400).",
        ),
        (
            403,
            "Forbidden",
            False,
            "Slack API users request denied or malformed (HTTP 403/400).",
        ),
    ),
)
def test_check_connection(token_config, requests_mock, status_code, response, is_connection_successful, error_msg):
    requests_mock.register_uri("GET", "https://slack.com/api/users.list?limit=1000", status_code=status_code, json=response)
    source = get_source(token_config)
    connection_status = source.check(logger=logging.getLogger("airbyte"), config=token_config)
    success = connection_status.status == Status.SUCCEEDED
    assert success is is_connection_successful
    if not success:
        assert error_msg in connection_status.message


def test_oauth_scopes_contain_only_used_scopes():
    manifest = yaml.safe_load(YAML_FILE_PATH.read_text())
    oauth_spec = manifest["spec"]["advanced_auth"]["oauth_config_specification"]["oauth_connector_input_specification"]
    scopes = [entry["scope"] for entry in oauth_spec["scopes"]]

    expected_scopes = [
        "channels:history",
        "channels:join",
        "channels:read",
        "groups:read",
        "groups:history",
        "users:read",
    ]
    assert scopes == expected_scopes

    unused_scopes = {"im:history", "mpim:history", "im:read", "mpim:read"}
    assert unused_scopes.isdisjoint(set(scopes)), f"Found unused IM/MPIM scopes: {unused_scopes & set(scopes)}"


def test_stream_groups_serializes_substream_execution(token_config):
    """Verify stream_groups assigns block_simultaneous_read so substreams do not run concurrently."""
    source = get_source(token_config)
    streams = source.streams(token_config)
    groups_by_stream = {s.name: s.block_simultaneous_read for s in streams}

    assert groups_by_stream["users"] == "", "users should be ungrouped"
    assert groups_by_stream["channels"] == "channels_lock"
    assert groups_by_stream["channel_members"] == "channel_messages_lock"
    assert groups_by_stream["channel_messages"] == "channel_messages_lock"
    assert groups_by_stream["threads"] == "threads_lock"


def test_stream_groups_manifest_structure():
    """Verify the manifest declares stream_groups that serialize substream parent walks."""
    manifest = yaml.safe_load(YAML_FILE_PATH.read_text())
    groups = manifest["stream_groups"]

    assert "channels_lock" in groups
    assert "channel_messages_lock" in groups
    assert "threads_lock" in groups

    assert len(groups["channels_lock"]["streams"]) == 1
    assert len(groups["channel_messages_lock"]["streams"]) == 2
    assert len(groups["threads_lock"]["streams"]) == 1

    for group in groups.values():
        assert group["action"]["type"] == "BlockSimultaneousSyncsAction"


def test_stream_groups_no_parent_child_in_same_group():
    """Verify no stream shares a group with its parent to prevent deadlock.

    `channels` is a parent of `channel_members`, `channel_messages`, and
    (transitively) `threads`, so it must sit in its own group. `threads` depends
    on `channel_messages`, so they must also be in separate groups.
    """
    manifest = yaml.safe_load(YAML_FILE_PATH.read_text())
    groups = manifest["stream_groups"]

    def _stream_names(group_name):
        return {s["name"] for s in groups[group_name]["streams"]}

    channels_names = _stream_names("channels_lock")
    messages_names = _stream_names("channel_messages_lock")
    threads_names = _stream_names("threads_lock")

    assert channels_names.isdisjoint(messages_names), "channels must not share a group with its children"
    assert channels_names.isdisjoint(threads_names), "channels must not share a group with threads"
    assert messages_names.isdisjoint(threads_names), "channel_messages must not share a group with threads"


def test_stream_groups_covers_all_substreams():
    """Every substream that walks `channels` as a parent must be in a stream group."""
    manifest = yaml.safe_load(YAML_FILE_PATH.read_text())
    groups = manifest["stream_groups"]

    all_grouped_names = set()
    for group in groups.values():
        all_grouped_names.update(s["name"] for s in group["streams"])

    expected_grouped_streams = ["channels", "channel_members", "channel_messages", "threads"]
    for name in expected_grouped_streams:
        assert name in all_grouped_names, f"{name} should be covered by a stream group"
