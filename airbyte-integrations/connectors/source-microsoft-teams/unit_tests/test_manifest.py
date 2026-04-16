# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Unit tests for the source-microsoft-teams manifest.yaml (v2.0.0 overhaul).

Validates:
1. Manifest parses and all expected streams are defined.
2. Removed legacy streams are absent.
3. Parent-child relationships are correctly wired.
4. Extra fields propagate parent IDs through deeply nested substreams.
5. Error handlers are present on substreams.
6. Pagination and record selectors use the shared OData components.
7. AddFields transformations inject parent partition IDs.
8. The spec section is properly structured.
"""

import pathlib
from typing import Any, Dict, List, Optional

import pytest
import yaml


MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "manifest.yaml"

# Streams that MUST be present after the overhaul
EXPECTED_STREAMS = [
    # Tier 1
    "users",
    "teams",
    "channels",
    "channel_messages",
    "channel_message_replies",
    "chats",
    "chat_messages",
    "team_members",
    # Tier 2
    "channel_members",
    "chat_members",
    "online_meetings",
    "meeting_transcripts",
    "meeting_attendance_reports",
    "tags",
    "tag_members",
    # Backward-compatible
    "groups",
    "group_members",
    "group_owners",
    "team_drives",
]

# Legacy streams that MUST be removed
REMOVED_STREAMS = [
    "conversations",
    "conversation_threads",
    "conversation_posts",
    "channel_tabs",
    "team_device_usage_report",
]

# Substreams and their expected parent stream name + partition field
SUBSTREAM_PARENTS = {
    "channels": ("teams", "team_id"),
    "channel_messages": ("channels", "channel_id"),
    "channel_message_replies": ("channel_messages", "message_id"),
    "chats": None,  # top-level
    "chat_messages": ("chats", "chat_id"),
    "chat_members": ("chats", "chat_id"),
    "team_members": ("teams", "team_id"),
    "channel_members": ("channels", "channel_id"),
    "online_meetings": ("users", "user_id"),
    "meeting_transcripts": ("online_meetings", "meeting_id"),
    "meeting_attendance_reports": ("online_meetings", "meeting_id"),
    "tags": ("teams", "team_id"),
    "tag_members": ("tags", "tag_id"),
    "group_members": ("groups", "group_id"),
    "group_owners": ("groups", "group_id"),
    "team_drives": ("teams", "team_id"),
}

# Deeply nested substreams that use extra_fields to carry parent IDs
EXTRA_FIELDS_EXPECTATIONS = {
    "channel_messages": [["teamId"]],
    "channel_message_replies": [["teamId"], ["channelId"]],
    "channel_members": [["teamId"]],
    "meeting_transcripts": [["userId"]],
    "meeting_attendance_reports": [["userId"]],
    "tag_members": [["teamId"]],
}

# Streams that should have AddFields transformations
ADDFIELDS_EXPECTATIONS = {
    "channels": ["teamId"],
    "channel_messages": ["teamId", "channelId"],
    "channel_message_replies": ["teamId", "channelId", "parentMessageId"],
    "chat_messages": ["chatId"],
    "chat_members": ["chatId"],
    "team_members": ["teamId"],
    "channel_members": ["teamId", "channelId"],
    "online_meetings": ["userId"],
    "meeting_transcripts": ["userId"],
    "meeting_attendance_reports": ["userId", "meetingId"],
    "tags": ["teamId"],
    "tag_members": ["teamId", "tagId"],
    "group_members": ["groupId"],
    "group_owners": ["groupId"],
    "team_drives": ["teamId"],
}


@pytest.fixture(scope="module")
def manifest() -> Dict[str, Any]:
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture(scope="module")
def stream_defs(manifest) -> Dict[str, Any]:
    return manifest["definitions"]["streams"]


def _get_stream_def(manifest: Dict, stream_name: str) -> Dict:
    return manifest["definitions"]["streams"][stream_name]


def _get_partition_router(stream_def: Dict) -> Optional[List]:
    retriever = stream_def.get("retriever", {})
    return retriever.get("partition_router")


def _get_parent_config(stream_def: Dict) -> Optional[Dict]:
    router = _get_partition_router(stream_def)
    if not router:
        return None
    for entry in router:
        if entry.get("type") == "SubstreamPartitionRouter":
            configs = entry.get("parent_stream_configs", [])
            if configs:
                return configs[0]
    return None


# ===== Structural tests =====


class TestManifestStructure:
    def test_manifest_parses(self, manifest):
        """The manifest.yaml must be valid YAML."""
        assert manifest is not None
        assert manifest["type"] == "DeclarativeSource"
        assert manifest["version"] == "4.3.0"

    def test_check_stream(self, manifest):
        """The check section must reference the users stream."""
        check = manifest["check"]
        assert check["type"] == "CheckStream"
        assert "users" in check["stream_names"]

    def test_definitions_section_exists(self, manifest):
        """The definitions section must exist with base components."""
        defs = manifest["definitions"]
        assert "base_requester" in defs
        assert "odata_paginator" in defs
        assert "odata_record_selector" in defs
        assert "permission_error_handler" in defs
        assert "streams" in defs


class TestStreamsPresence:
    @pytest.mark.parametrize("stream_name", EXPECTED_STREAMS)
    def test_expected_stream_exists(self, stream_defs, stream_name):
        """Every expected stream must be defined."""
        assert stream_name in stream_defs, f"Stream '{stream_name}' is missing from definitions"

    @pytest.mark.parametrize("stream_name", REMOVED_STREAMS)
    def test_removed_stream_absent(self, stream_defs, stream_name):
        """Legacy streams must not be present."""
        assert stream_name not in stream_defs, f"Legacy stream '{stream_name}' should be removed"

    def test_streams_section_references(self, manifest):
        """The top-level streams section must reference all expected streams."""
        streams_refs = manifest["streams"]
        ref_names = set()
        for entry in streams_refs:
            if "$ref" in entry:
                # Extract stream name from ref like "#/definitions/streams/users"
                ref_path = entry["$ref"]
                name = ref_path.split("/")[-1]
                ref_names.add(name)
        for expected in EXPECTED_STREAMS:
            assert expected in ref_names, f"Stream '{expected}' not in top-level streams list"

    def test_total_stream_count(self, stream_defs):
        """We expect exactly 19 streams after the overhaul."""
        assert len(stream_defs) == 19


# ===== Parent-child relationship tests =====


class TestSubstreamRelationships:
    @pytest.mark.parametrize(
        "stream_name,expected",
        [(name, parent_info) for name, parent_info in SUBSTREAM_PARENTS.items() if parent_info is not None],
    )
    def test_substream_parent(self, stream_defs, stream_name, expected):
        """Substreams must reference the correct parent stream."""
        parent_name, partition_field = expected
        stream_def = stream_defs[stream_name]
        parent_config = _get_parent_config(stream_def)
        assert parent_config is not None, f"'{stream_name}' has no partition router"
        assert (
            parent_config["partition_field"] == partition_field
        ), f"'{stream_name}' partition_field should be '{partition_field}', got '{parent_config.get('partition_field')}'"
        # Check parent stream reference
        parent_stream = parent_config["stream"]
        if "$ref" in parent_stream:
            ref_name = parent_stream["$ref"].split("/")[-1]
            assert ref_name == parent_name, f"'{stream_name}' parent should be '{parent_name}', got '{ref_name}'"

    def test_top_level_streams_have_no_partition_router(self, stream_defs):
        """Top-level streams (users, teams, groups, chats) should not have partition routers."""
        for name in ["users", "teams", "groups", "chats"]:
            stream_def = stream_defs[name]
            router = _get_partition_router(stream_def)
            assert router is None, f"Top-level stream '{name}' should not have a partition router"


# ===== Extra fields tests for deeply nested substreams =====


class TestExtraFields:
    @pytest.mark.parametrize(
        "stream_name,expected_extra_fields",
        list(EXTRA_FIELDS_EXPECTATIONS.items()),
    )
    def test_extra_fields_configured(self, stream_defs, stream_name, expected_extra_fields):
        """Deeply nested substreams must configure extra_fields on their parent config."""
        stream_def = stream_defs[stream_name]
        parent_config = _get_parent_config(stream_def)
        assert parent_config is not None, f"'{stream_name}' has no parent config"
        actual_extra = parent_config.get("extra_fields", [])
        assert actual_extra == expected_extra_fields, f"'{stream_name}' extra_fields should be {expected_extra_fields}, got {actual_extra}"


# ===== AddFields transformation tests =====


class TestAddFieldsTransformations:
    @pytest.mark.parametrize(
        "stream_name,expected_fields",
        list(ADDFIELDS_EXPECTATIONS.items()),
    )
    def test_addfields_present(self, stream_defs, stream_name, expected_fields):
        """Substreams must use AddFields to inject parent IDs into records."""
        stream_def = stream_defs[stream_name]
        transformations = stream_def.get("transformations", [])
        add_fields_found = []
        for t in transformations:
            if t.get("type") == "AddFields":
                for field in t.get("fields", []):
                    path = field.get("path", [])
                    if path:
                        add_fields_found.append(path[0])
        for expected in expected_fields:
            assert expected in add_fields_found, f"'{stream_name}' is missing AddFields for '{expected}'. Found: {add_fields_found}"


# ===== Error handler tests =====


class TestErrorHandlers:
    @pytest.mark.parametrize(
        "stream_name",
        [name for name, parent_info in SUBSTREAM_PARENTS.items() if parent_info is not None],
    )
    def test_substream_has_error_handler(self, stream_defs, stream_name):
        """All substreams should have an error handler for 403/404 responses."""
        stream_def = stream_defs[stream_name]
        requester = stream_def["retriever"]["requester"]
        error_handler = requester.get("error_handler")
        assert error_handler is not None, f"Substream '{stream_name}' is missing an error_handler"


# ===== Schema tests =====


class TestSchemas:
    @pytest.mark.parametrize("stream_name", EXPECTED_STREAMS)
    def test_schema_has_id_field(self, stream_defs, stream_name):
        """Every stream schema must have an 'id' field."""
        stream_def = stream_defs[stream_name]
        schema = stream_def["schema_loader"]["schema"]
        props = schema.get("properties", {})
        assert "id" in props, f"Schema for '{stream_name}' is missing 'id' property"

    @pytest.mark.parametrize("stream_name", EXPECTED_STREAMS)
    def test_schema_allows_additional_properties(self, stream_defs, stream_name):
        """All schemas must have additionalProperties: true to handle API changes gracefully."""
        stream_def = stream_defs[stream_name]
        schema = stream_def["schema_loader"]["schema"]
        assert schema.get("additionalProperties") is True, f"Schema for '{stream_name}' should have additionalProperties: true"

    @pytest.mark.parametrize("stream_name", EXPECTED_STREAMS)
    def test_stream_has_primary_key(self, stream_defs, stream_name):
        """Every stream must declare a primary key."""
        stream_def = stream_defs[stream_name]
        pk = stream_def.get("primary_key")
        assert pk is not None and len(pk) > 0, f"Stream '{stream_name}' is missing a primary_key"


# ===== Pagination tests =====


class TestPagination:
    def test_top_level_streams_use_odata_paginator(self, stream_defs):
        """Top-level streams (users, teams, groups) must use the OData paginator."""
        for name in ["users", "teams", "groups"]:
            stream_def = stream_defs[name]
            paginator = stream_def["retriever"]["paginator"]
            if "$ref" in paginator:
                assert paginator["$ref"] == "#/definitions/odata_paginator"
            else:
                strategy = paginator.get("pagination_strategy", {})
                assert strategy.get("type") == "CursorPagination"

    def test_team_drives_uses_no_pagination(self, stream_defs):
        """team_drives (single object per team) should use NoPagination."""
        stream_def = stream_defs["team_drives"]
        paginator = stream_def["retriever"]["paginator"]
        assert paginator.get("type") == "NoPagination"


# ===== API path tests =====


class TestApiPaths:
    def test_users_path(self, stream_defs):
        requester = stream_defs["users"]["retriever"]["requester"]
        assert "users" in requester.get("path", "")

    def test_teams_path(self, stream_defs):
        requester = stream_defs["teams"]["retriever"]["requester"]
        assert "teams" in requester.get("path", "")

    def test_channels_path(self, stream_defs):
        requester = stream_defs["channels"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "teams/" in path and "/channels" in path

    def test_channel_messages_path(self, stream_defs):
        requester = stream_defs["channel_messages"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "/channels/" in path and "/messages" in path

    def test_channel_message_replies_path(self, stream_defs):
        requester = stream_defs["channel_message_replies"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "/messages/" in path and "/replies" in path

    def test_chats_path(self, stream_defs):
        requester = stream_defs["chats"]["retriever"]["requester"]
        assert "chats" in requester.get("path", "")

    def test_chat_messages_path(self, stream_defs):
        requester = stream_defs["chat_messages"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "chats/" in path and "/messages" in path

    def test_team_members_path(self, stream_defs):
        requester = stream_defs["team_members"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "teams/" in path and "/members" in path

    def test_online_meetings_path(self, stream_defs):
        requester = stream_defs["online_meetings"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "users/" in path and "/onlineMeetings" in path

    def test_tags_path(self, stream_defs):
        requester = stream_defs["tags"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "teams/" in path and "/tags" in path

    def test_team_drives_path(self, stream_defs):
        requester = stream_defs["team_drives"]["retriever"]["requester"]
        path = requester.get("path", "")
        assert "groups/" in path and "/drive" in path


# ===== Spec tests =====


class TestSpec:
    def test_spec_exists(self, manifest):
        """The spec section must be present."""
        assert "spec" in manifest
        spec = manifest["spec"]
        assert spec["type"] == "Spec"

    def test_credentials_oneof(self, manifest):
        """The credentials field must have two auth options."""
        props = manifest["spec"]["connection_specification"]["properties"]
        creds = props["credentials"]
        assert "oneOf" in creds
        assert len(creds["oneOf"]) == 2
        auth_types = [item["properties"]["auth_type"]["const"] for item in creds["oneOf"]]
        assert "Client" in auth_types
        assert "Token" in auth_types

    def test_period_field_is_hidden(self, manifest):
        """The period field should be marked as hidden (deprecated)."""
        props = manifest["spec"]["connection_specification"]["properties"]
        period = props.get("period")
        assert period is not None, "period field should still exist (deprecated)"
        assert period.get("airbyte_hidden") is True, "period field should be marked as airbyte_hidden"

    def test_advanced_auth(self, manifest):
        """Advanced auth configuration must be present."""
        assert "advanced_auth" in manifest["spec"]
        auth = manifest["spec"]["advanced_auth"]
        assert auth["auth_flow_type"] == "oauth2.0"
        assert auth["predicate_value"] == "Client"


# ===== Base requester tests =====


class TestBaseRequester:
    def test_base_requester_url(self, manifest):
        req = manifest["definitions"]["base_requester"]
        assert req["url_base"] == "https://graph.microsoft.com/v1.0/"

    def test_base_requester_auth(self, manifest):
        req = manifest["definitions"]["base_requester"]
        auth = req["authenticator"]
        assert auth["type"] == "OAuthAuthenticator"
        assert auth["grant_type"] == "client_credentials"

    def test_base_requester_token_endpoint(self, manifest):
        req = manifest["definitions"]["base_requester"]
        auth = req["authenticator"]
        assert "login.microsoftonline.com" in auth["token_refresh_endpoint"]
        assert "oauth2/v2.0/token" in auth["token_refresh_endpoint"]


# ===== Metadata tests =====


class TestMetadata:
    def test_auto_import_schema(self, manifest):
        """All streams must be listed in metadata.autoImportSchema."""
        auto_import = manifest["metadata"]["autoImportSchema"]
        for stream_name in EXPECTED_STREAMS:
            assert stream_name in auto_import, f"Stream '{stream_name}' missing from autoImportSchema"
        for removed in REMOVED_STREAMS:
            assert removed not in auto_import, f"Removed stream '{removed}' should not be in autoImportSchema"
