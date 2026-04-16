# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the source-discord connector manifest."""

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture
def manifest():
    """Load the connector manifest."""
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def config():
    """Return a sample config."""
    return {"bot_token": "test-bot-token-12345"}


class TestManifestStructure:
    """Test the manifest YAML structure."""

    def test_manifest_loads(self, manifest):
        assert manifest is not None
        assert manifest["type"] == "DeclarativeSource"

    def test_manifest_version(self, manifest):
        assert "version" in manifest
        assert manifest["version"] is not None

    def test_check_stream_defined(self, manifest):
        assert manifest["check"]["type"] == "CheckStream"
        assert "guilds" in manifest["check"]["stream_names"]

    def test_all_expected_streams_present(self, manifest):
        expected_streams = [
            "guilds",
            "channels",
            "messages",
            "members",
            "roles",
            "threads",
            "pinned_messages",
            "scheduled_events",
            "audit_log",
        ]
        stream_refs = manifest["streams"]
        stream_defs = manifest["definitions"]["streams"]

        for stream_name in expected_streams:
            assert stream_name in stream_defs, f"Stream '{stream_name}' not found in definitions"

        assert len(stream_refs) == len(expected_streams)

    def test_spec_has_required_fields(self, manifest):
        spec = manifest["spec"]
        assert spec["type"] == "Spec"
        conn_spec = spec["connection_specification"]
        assert "bot_token" in conn_spec["properties"]
        assert conn_spec["properties"]["bot_token"]["airbyte_secret"] is True
        assert "bot_token" in conn_spec["required"]


class TestAuthenticator:
    """Test authentication configuration."""

    def test_authenticator_type(self, manifest):
        auth = manifest["definitions"]["authenticator"]
        assert auth["type"] == "ApiKeyAuthenticator"
        assert "Bot" in auth["api_token"]
        assert "config['bot_token']" in auth["api_token"]

    def test_auth_header_injection(self, manifest):
        auth = manifest["definitions"]["authenticator"]
        inject = auth["inject_into"]
        assert inject["field_name"] == "Authorization"
        assert inject["inject_into"] == "header"


class TestBaseRequester:
    """Test base requester configuration."""

    def test_base_url(self, manifest):
        requester = manifest["definitions"]["base_requester"]
        assert requester["url_base"] == "https://discord.com/api/v10"

    def test_error_handler_has_retry_on_rate_limit(self, manifest):
        requester = manifest["definitions"]["base_requester"]
        error_handler = requester["error_handler"]
        response_filters = error_handler["response_filters"]
        rate_limit_filter = [f for f in response_filters if 429 in f.get("http_codes", [])]
        assert len(rate_limit_filter) == 1
        assert rate_limit_filter[0]["action"] == "RETRY"

    def test_error_handler_has_retry_on_server_error(self, manifest):
        requester = manifest["definitions"]["base_requester"]
        error_handler = requester["error_handler"]
        response_filters = error_handler["response_filters"]
        server_error_filter = [f for f in response_filters if any(code in f.get("http_codes", []) for code in [500, 502, 503])]
        assert len(server_error_filter) == 1
        assert server_error_filter[0]["action"] == "RETRY"

    def test_backoff_strategy_uses_retry_after_header(self, manifest):
        requester = manifest["definitions"]["base_requester"]
        error_handler = requester["error_handler"]
        backoff = error_handler["backoff_strategies"]
        assert any(s.get("header") == "Retry-After" for s in backoff)

    def test_permissive_requester_ignores_403(self, manifest):
        requester = manifest["definitions"]["permissive_requester"]
        error_handler = requester["error_handler"]
        response_filters = error_handler["response_filters"]
        forbidden_filter = [f for f in response_filters if 403 in f.get("http_codes", [])]
        assert len(forbidden_filter) == 1
        assert forbidden_filter[0]["action"] == "IGNORE"


class TestGuildsStream:
    """Test guilds stream configuration."""

    def test_guilds_path(self, manifest):
        guilds = manifest["definitions"]["streams"]["guilds"]
        requester = guilds["retriever"]["requester"]
        assert requester["path"] == "/users/@me/guilds"

    def test_guilds_primary_key(self, manifest):
        guilds = manifest["definitions"]["streams"]["guilds"]
        assert guilds["primary_key"] == ["id"]

    def test_guilds_pagination(self, manifest):
        guilds = manifest["definitions"]["streams"]["guilds"]
        paginator = guilds["retriever"]["paginator"]
        assert paginator["type"] == "DefaultPaginator"
        strategy = paginator["pagination_strategy"]
        assert strategy["type"] == "CursorPagination"
        assert strategy["page_size"] == 200
        assert strategy["initial_token"] == "0"

    def test_guilds_pagination_uses_after_param(self, manifest):
        guilds = manifest["definitions"]["streams"]["guilds"]
        paginator = guilds["retriever"]["paginator"]
        page_token = paginator["page_token_option"]
        assert page_token["field_name"] == "after"
        assert page_token["inject_into"] == "request_parameter"

    def test_guilds_schema_has_required_fields(self, manifest):
        schema = manifest["schemas"]["guilds"]
        props = schema["properties"]
        assert "id" in props
        assert "name" in props
        assert "features" in props


class TestChannelsStream:
    """Test channels stream configuration."""

    def test_channels_is_substream_of_guilds(self, manifest):
        channels = manifest["definitions"]["streams"]["channels"]
        partition_router = channels["retriever"]["partition_router"]
        assert partition_router["type"] == "SubstreamPartitionRouter"
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["parent_key"] == "id"
        assert parent_config["partition_field"] == "guild_id"

    def test_channels_path_uses_guild_id_partition(self, manifest):
        channels = manifest["definitions"]["streams"]["channels"]
        requester = channels["retriever"]["requester"]
        assert "stream_partition['guild_id']" in requester["path"]
        assert "/guilds/" in requester["path"]
        assert "/channels" in requester["path"]

    def test_channels_no_pagination(self, manifest):
        channels = manifest["definitions"]["streams"]["channels"]
        paginator = channels["retriever"]["paginator"]
        assert paginator["type"] == "NoPagination"

    def test_channels_schema_has_required_fields(self, manifest):
        schema = manifest["schemas"]["channels"]
        props = schema["properties"]
        assert "id" in props
        assert "type" in props
        assert "name" in props
        assert "guild_id" in props


class TestMessagesStream:
    """Test messages stream configuration."""

    def test_messages_is_substream_of_channels(self, manifest):
        messages = manifest["definitions"]["streams"]["messages"]
        partition_router = messages["retriever"]["partition_router"]
        assert partition_router["type"] == "SubstreamPartitionRouter"
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["parent_key"] == "id"
        assert parent_config["partition_field"] == "channel_id"

    def test_messages_path_uses_channel_id_partition(self, manifest):
        messages = manifest["definitions"]["streams"]["messages"]
        requester = messages["retriever"]["requester"]
        assert "stream_partition['channel_id']" in requester["path"]
        assert "/channels/" in requester["path"]
        assert "/messages" in requester["path"]

    def test_messages_pagination(self, manifest):
        messages = manifest["definitions"]["streams"]["messages"]
        paginator = messages["retriever"]["paginator"]
        assert paginator["type"] == "DefaultPaginator"
        strategy = paginator["pagination_strategy"]
        assert strategy["type"] == "CursorPagination"
        assert strategy["page_size"] == 100
        assert strategy["initial_token"] == "0"

    def test_messages_uses_after_parameter(self, manifest):
        messages = manifest["definitions"]["streams"]["messages"]
        paginator = messages["retriever"]["paginator"]
        page_token = paginator["page_token_option"]
        assert page_token["field_name"] == "after"

    def test_messages_uses_permissive_requester(self, manifest):
        messages = manifest["definitions"]["streams"]["messages"]
        requester = messages["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/permissive_requester"

    def test_messages_schema_has_required_fields(self, manifest):
        schema = manifest["schemas"]["messages"]
        props = schema["properties"]
        assert "id" in props
        assert "channel_id" in props
        assert "content" in props
        assert "author" in props
        assert "timestamp" in props
        assert "attachments" in props
        assert "embeds" in props


class TestMembersStream:
    """Test members stream configuration."""

    def test_members_is_substream_of_guilds(self, manifest):
        members = manifest["definitions"]["streams"]["members"]
        partition_router = members["retriever"]["partition_router"]
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["partition_field"] == "guild_id"

    def test_members_pagination(self, manifest):
        members = manifest["definitions"]["streams"]["members"]
        paginator = members["retriever"]["paginator"]
        strategy = paginator["pagination_strategy"]
        assert strategy["page_size"] == 1000
        assert strategy["initial_token"] == "0"
        assert "user" in strategy["cursor_value"]

    def test_members_uses_permissive_requester(self, manifest):
        members = manifest["definitions"]["streams"]["members"]
        requester = members["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/permissive_requester"

    def test_members_schema_has_user_field(self, manifest):
        schema = manifest["schemas"]["members"]
        props = schema["properties"]
        assert "user" in props
        assert "roles" in props
        assert "joined_at" in props


class TestRolesStream:
    """Test roles stream configuration."""

    def test_roles_is_substream_of_guilds(self, manifest):
        roles = manifest["definitions"]["streams"]["roles"]
        partition_router = roles["retriever"]["partition_router"]
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["partition_field"] == "guild_id"

    def test_roles_no_pagination(self, manifest):
        roles = manifest["definitions"]["streams"]["roles"]
        paginator = roles["retriever"]["paginator"]
        assert paginator["type"] == "NoPagination"

    def test_roles_schema_has_required_fields(self, manifest):
        schema = manifest["schemas"]["roles"]
        props = schema["properties"]
        assert "id" in props
        assert "name" in props
        assert "permissions" in props
        assert "color" in props


class TestThreadsStream:
    """Test threads stream configuration."""

    def test_threads_path(self, manifest):
        threads = manifest["definitions"]["streams"]["threads"]
        requester = threads["retriever"]["requester"]
        assert "threads/active" in requester["path"]

    def test_threads_extracts_from_threads_field(self, manifest):
        threads = manifest["definitions"]["streams"]["threads"]
        extractor = threads["retriever"]["record_selector"]["extractor"]
        assert extractor["field_path"] == ["threads"]

    def test_threads_is_substream_of_guilds(self, manifest):
        threads = manifest["definitions"]["streams"]["threads"]
        partition_router = threads["retriever"]["partition_router"]
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["partition_field"] == "guild_id"


class TestPinnedMessagesStream:
    """Test pinned_messages stream configuration."""

    def test_pinned_messages_is_substream_of_channels(self, manifest):
        pinned = manifest["definitions"]["streams"]["pinned_messages"]
        partition_router = pinned["retriever"]["partition_router"]
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["partition_field"] == "channel_id"

    def test_pinned_messages_path(self, manifest):
        pinned = manifest["definitions"]["streams"]["pinned_messages"]
        requester = pinned["retriever"]["requester"]
        assert "/pins" in requester["path"]

    def test_pinned_messages_no_pagination(self, manifest):
        pinned = manifest["definitions"]["streams"]["pinned_messages"]
        paginator = pinned["retriever"]["paginator"]
        assert paginator["type"] == "NoPagination"

    def test_pinned_messages_reuses_messages_schema(self, manifest):
        pinned = manifest["definitions"]["streams"]["pinned_messages"]
        schema_ref = pinned["schema_loader"]["schema"]["$ref"]
        assert schema_ref == "#/schemas/messages"


class TestScheduledEventsStream:
    """Test scheduled_events stream configuration."""

    def test_scheduled_events_path(self, manifest):
        events = manifest["definitions"]["streams"]["scheduled_events"]
        requester = events["retriever"]["requester"]
        assert "scheduled-events" in requester["path"]

    def test_scheduled_events_schema_has_required_fields(self, manifest):
        schema = manifest["schemas"]["scheduled_events"]
        props = schema["properties"]
        assert "id" in props
        assert "name" in props
        assert "scheduled_start_time" in props
        assert "status" in props


class TestAuditLogStream:
    """Test audit_log stream configuration."""

    def test_audit_log_path(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        requester = audit["retriever"]["requester"]
        assert "audit-logs" in requester["path"]

    def test_audit_log_extracts_from_entries_field(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        extractor = audit["retriever"]["record_selector"]["extractor"]
        assert extractor["field_path"] == ["audit_log_entries"]

    def test_audit_log_pagination_uses_before(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        paginator = audit["retriever"]["paginator"]
        page_token = paginator["page_token_option"]
        assert page_token["field_name"] == "before"

    def test_audit_log_pagination_config(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        paginator = audit["retriever"]["paginator"]
        strategy = paginator["pagination_strategy"]
        assert strategy["page_size"] == 100
        assert "initial_token" not in strategy or strategy.get("initial_token") is None


class TestSchemas:
    """Test all schemas have valid structure."""

    def test_all_schemas_are_objects(self, manifest):
        for name, schema in manifest["schemas"].items():
            assert schema["type"] == "object", f"Schema '{name}' is not of type object"
            assert "properties" in schema, f"Schema '{name}' has no properties"

    def test_all_schemas_allow_additional_properties(self, manifest):
        for name, schema in manifest["schemas"].items():
            assert schema.get("additionalProperties") is True, f"Schema '{name}' does not allow additionalProperties"

    def test_all_schemas_have_id_field(self, manifest):
        schemas_with_id = [
            "guilds",
            "channels",
            "messages",
            "roles",
            "threads",
            "scheduled_events",
            "audit_log",
        ]
        for name in schemas_with_id:
            schema = manifest["schemas"][name]
            assert "id" in schema["properties"], f"Schema '{name}' missing 'id' field"
            assert schema["properties"]["id"]["type"] == "string"

    def test_nullable_fields_use_correct_format(self, manifest):
        """Verify nullable fields use type array syntax [type, 'null']."""
        for schema_name, schema in manifest["schemas"].items():
            for field_name, field_def in schema.get("properties", {}).items():
                if isinstance(field_def.get("type"), list):
                    assert "null" in field_def["type"], f"Schema '{schema_name}.{field_name}' has array type but no null"
