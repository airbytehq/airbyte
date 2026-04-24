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
        (200, {"ok": False, "error": "plan_upgrade_required"}, False, "Slack API error: plan_upgrade_required."),
        (
            400,
            "Bad request",
            False,
            "Got an exception while trying to set up the connection. Most probably, there are no users in the given Slack instance or your token is incorrect.",
        ),
        (
            403,
            "Forbidden",
            False,
            "Got an exception while trying to set up the connection. Most probably, there are no users in the given Slack instance or your token is incorrect.",
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
