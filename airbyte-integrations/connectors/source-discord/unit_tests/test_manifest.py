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


# ---------------------------------------------------------------------------
# Behavioral test: CDK instantiation + discover
# ---------------------------------------------------------------------------


def test_manifest_instantiates_with_cdk():
    """Verify the CDK can parse and instantiate the manifest without errors."""
    from airbyte_cdk import YamlDeclarativeSource

    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
    assert source is not None


def test_discover_returns_all_streams():
    """Verify discover returns the expected set of streams."""
    from airbyte_cdk import YamlDeclarativeSource

    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
    catalog = source.discover(
        logger=None,
        config={"bot_token": "test-token"},
    )
    stream_names = sorted([s.name for s in catalog.streams])
    expected = sorted(
        [
            "audit_log",
            "channels",
            "current_user",
            "guilds",
            "members",
            "messages",
            "pinned_messages",
            "roles",
            "scheduled_events",
            "threads",
        ]
    )
    assert stream_names == expected


# ---------------------------------------------------------------------------
# Structural tests
# ---------------------------------------------------------------------------


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
            "current_user",
        ]
        stream_defs = manifest["definitions"]["streams"]

        for stream_name in expected_streams:
            assert (
                stream_name in stream_defs
            ), f"Stream '{stream_name}' not found in definitions"

        stream_refs = manifest["streams"]
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
        rate_limit_filter = [
            f for f in response_filters if 429 in f.get("http_codes", [])
        ]
        assert len(rate_limit_filter) == 1
        assert rate_limit_filter[0]["action"] == "RETRY"

    def test_error_handler_has_retry_on_server_error(self, manifest):
        requester = manifest["definitions"]["base_requester"]
        error_handler = requester["error_handler"]
        response_filters = error_handler["response_filters"]
        server_error_filter = [
            f
            for f in response_filters
            if any(
                code in f.get("http_codes", []) for code in [500, 502, 503]
            )
        ]
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
        forbidden_filter = [
            f for f in response_filters if 403 in f.get("http_codes", [])
        ]
        assert len(forbidden_filter) == 1
        assert forbidden_filter[0]["action"] == "IGNORE"


# ---------------------------------------------------------------------------
# Messages stream — P0-1 fix validation
# ---------------------------------------------------------------------------


class TestMessagesStream:
    """Test messages stream configuration."""

    def test_messages_pagination_uses_before_parameter(self, manifest):
        """P0-1: Messages must paginate with 'before' (descending walk),
        not 'after', because Discord returns newest-to-oldest."""
        messages = manifest["definitions"]["streams"]["messages"]
        paginator = messages["retriever"]["paginator"]
        page_token = paginator["page_token_option"]
        assert page_token["field_name"] == "before"

    def test_messages_pagination_has_no_initial_token(self, manifest):
        """P0-1: No initial_token needed — Discord defaults 'before' to now."""
        messages = manifest["definitions"]["streams"]["messages"]
        strategy = messages["retriever"]["paginator"]["pagination_strategy"]
        assert "initial_token" not in strategy

    def test_messages_partition_router_includes_channels_and_threads(
        self, manifest
    ):
        """P1-3: Messages must iterate over both channels and threads."""
        messages = manifest["definitions"]["streams"]["messages"]
        routers = messages["retriever"]["partition_router"]
        assert isinstance(routers, list), "partition_router should be a list"
        assert len(routers) == 2

        parent_refs = []
        for router in routers:
            cfg = router["parent_stream_configs"][0]
            parent_refs.append(
                cfg["stream"]["$ref"].split("/")[-1]
            )

        assert "channels" in parent_refs
        assert "threads" in parent_refs

    def test_messages_uses_permissive_requester(self, manifest):
        messages = manifest["definitions"]["streams"]["messages"]
        requester = messages["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/permissive_requester"

    def test_messages_injects_channel_id_transformation(self, manifest):
        """P1-6: Messages should inject channel_id into records."""
        messages = manifest["definitions"]["streams"]["messages"]
        transformations = messages.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["channel_id"] in field_paths

    def test_messages_schema_has_required_fields(self, manifest):
        schema = manifest["schemas"]["messages"]
        props = schema["properties"]
        for field in [
            "id",
            "channel_id",
            "content",
            "author",
            "timestamp",
            "attachments",
            "embeds",
        ]:
            assert field in props, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# Members stream — P0-2 / P0-3 fix validation
# ---------------------------------------------------------------------------


class TestMembersStream:
    """Test members stream configuration."""

    def test_members_primary_key_is_composite(self, manifest):
        """P0-2: PK must be (user_id, guild_id), not [user, id]."""
        members = manifest["definitions"]["streams"]["members"]
        pk = members["primary_key"]
        assert "user_id" in pk
        assert "guild_id" in pk

    def test_members_uses_base_requester_not_permissive(self, manifest):
        """P0-3: Members must use base_requester so 403 fails loudly
        (indicates missing GUILD_MEMBERS intent)."""
        members = manifest["definitions"]["streams"]["members"]
        requester = members["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/base_requester"

    def test_members_injects_guild_id_and_user_id(self, manifest):
        """P0-2 + P1-6: guild_id and user_id must be injected."""
        members = manifest["definitions"]["streams"]["members"]
        transformations = members.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["guild_id"] in field_paths
        assert ["user_id"] in field_paths

    def test_members_schema_has_guild_id_and_user_id(self, manifest):
        schema = manifest["schemas"]["members"]
        props = schema["properties"]
        assert "guild_id" in props
        assert "user_id" in props
        assert "user" in props
        assert "joined_at" in props


# ---------------------------------------------------------------------------
# Audit log — P0-3 fix validation
# ---------------------------------------------------------------------------


class TestAuditLogStream:
    """Test audit_log stream configuration."""

    def test_audit_log_uses_base_requester(self, manifest):
        """P0-3: audit_log must use base_requester so 403 fails loudly."""
        audit = manifest["definitions"]["streams"]["audit_log"]
        requester = audit["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/base_requester"

    def test_audit_log_pagination_uses_before(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        paginator = audit["retriever"]["paginator"]
        page_token = paginator["page_token_option"]
        assert page_token["field_name"] == "before"

    def test_audit_log_pagination_has_no_initial_token(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        strategy = audit["retriever"]["paginator"]["pagination_strategy"]
        assert "initial_token" not in strategy

    def test_audit_log_extracts_from_entries_field(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        extractor = audit["retriever"]["record_selector"]["extractor"]
        assert extractor["field_path"] == ["audit_log_entries"]

    def test_audit_log_injects_guild_id(self, manifest):
        audit = manifest["definitions"]["streams"]["audit_log"]
        transformations = audit.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["guild_id"] in field_paths


# ---------------------------------------------------------------------------
# Current user stream — P1-1
# ---------------------------------------------------------------------------


class TestCurrentUserStream:
    """Test current_user stream configuration."""

    def test_current_user_path(self, manifest):
        user = manifest["definitions"]["streams"]["current_user"]
        requester = user["retriever"]["requester"]
        assert requester["path"] == "/users/@me"

    def test_current_user_uses_base_requester(self, manifest):
        user = manifest["definitions"]["streams"]["current_user"]
        requester = user["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/base_requester"

    def test_current_user_no_pagination(self, manifest):
        user = manifest["definitions"]["streams"]["current_user"]
        paginator = user["retriever"]["paginator"]
        assert paginator["type"] == "NoPagination"

    def test_current_user_schema(self, manifest):
        schema = manifest["schemas"]["current_user"]
        props = schema["properties"]
        assert "id" in props
        assert "username" in props
        assert "email" in props


# ---------------------------------------------------------------------------
# Remaining streams — structural coverage
# ---------------------------------------------------------------------------


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


class TestChannelsStream:
    """Test channels stream configuration."""

    def test_channels_is_substream_of_guilds(self, manifest):
        channels = manifest["definitions"]["streams"]["channels"]
        partition_router = channels["retriever"]["partition_router"]
        assert partition_router["type"] == "SubstreamPartitionRouter"
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["parent_key"] == "id"
        assert parent_config["partition_field"] == "guild_id"

    def test_channels_no_pagination(self, manifest):
        channels = manifest["definitions"]["streams"]["channels"]
        paginator = channels["retriever"]["paginator"]
        assert paginator["type"] == "NoPagination"


class TestRolesStream:
    """Test roles stream configuration."""

    def test_roles_is_substream_of_guilds(self, manifest):
        roles = manifest["definitions"]["streams"]["roles"]
        partition_router = roles["retriever"]["partition_router"]
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["partition_field"] == "guild_id"

    def test_roles_injects_guild_id(self, manifest):
        roles = manifest["definitions"]["streams"]["roles"]
        transformations = roles.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["guild_id"] in field_paths

    def test_roles_schema_has_guild_id(self, manifest):
        schema = manifest["schemas"]["roles"]
        assert "guild_id" in schema["properties"]


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

    def test_threads_injects_guild_id(self, manifest):
        threads = manifest["definitions"]["streams"]["threads"]
        transformations = threads.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["guild_id"] in field_paths


class TestPinnedMessagesStream:
    """Test pinned_messages stream configuration."""

    def test_pinned_messages_is_substream_of_channels(self, manifest):
        pinned = manifest["definitions"]["streams"]["pinned_messages"]
        partition_router = pinned["retriever"]["partition_router"]
        parent_config = partition_router["parent_stream_configs"][0]
        assert parent_config["partition_field"] == "channel_id"

    def test_pinned_messages_injects_channel_id(self, manifest):
        pinned = manifest["definitions"]["streams"]["pinned_messages"]
        transformations = pinned.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["channel_id"] in field_paths


class TestScheduledEventsStream:
    """Test scheduled_events stream configuration."""

    def test_scheduled_events_uses_base_requester(self, manifest):
        events = manifest["definitions"]["streams"]["scheduled_events"]
        requester = events["retriever"]["requester"]
        assert requester["$ref"] == "#/definitions/base_requester"

    def test_scheduled_events_injects_guild_id(self, manifest):
        events = manifest["definitions"]["streams"]["scheduled_events"]
        transformations = events.get("transformations", [])
        field_paths = []
        for t in transformations:
            for f in t.get("fields", []):
                field_paths.append(f["path"])
        assert ["guild_id"] in field_paths


# ---------------------------------------------------------------------------
# Schemas — format:date-time on timestamps (P3-1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "schema_name,field_name",
    [
        pytest.param(
            "messages", "timestamp", id="messages.timestamp"
        ),
        pytest.param(
            "messages", "edited_timestamp", id="messages.edited_timestamp"
        ),
        pytest.param(
            "members", "joined_at", id="members.joined_at"
        ),
        pytest.param(
            "members", "premium_since", id="members.premium_since"
        ),
        pytest.param(
            "members",
            "communication_disabled_until",
            id="members.communication_disabled_until",
        ),
        pytest.param(
            "scheduled_events",
            "scheduled_start_time",
            id="scheduled_events.scheduled_start_time",
        ),
        pytest.param(
            "scheduled_events",
            "scheduled_end_time",
            id="scheduled_events.scheduled_end_time",
        ),
    ],
)
def test_timestamp_fields_have_date_time_format(
    manifest, schema_name, field_name
):
    """P3-1: ISO8601 timestamp fields must declare format: date-time."""
    field = manifest["schemas"][schema_name]["properties"][field_name]
    assert field.get("format") == "date-time", (
        f"{schema_name}.{field_name} is missing format: date-time"
    )


# ---------------------------------------------------------------------------
# General schema validation
# ---------------------------------------------------------------------------


class TestSchemas:
    """Test all schemas have valid structure."""

    def test_all_schemas_are_objects(self, manifest):
        for name, schema in manifest["schemas"].items():
            assert (
                schema["type"] == "object"
            ), f"Schema '{name}' is not of type object"
            assert (
                "properties" in schema
            ), f"Schema '{name}' has no properties"

    def test_all_schemas_allow_additional_properties(self, manifest):
        for name, schema in manifest["schemas"].items():
            assert schema.get("additionalProperties") is True, (
                f"Schema '{name}' does not allow additionalProperties"
            )

    def test_all_schemas_have_id_field(self, manifest):
        schemas_with_id = [
            "guilds",
            "channels",
            "messages",
            "roles",
            "threads",
            "scheduled_events",
            "audit_log",
            "current_user",
        ]
        for name in schemas_with_id:
            schema = manifest["schemas"][name]
            assert "id" in schema["properties"], (
                f"Schema '{name}' missing 'id' field"
            )
            assert schema["properties"]["id"]["type"] == "string"

    def test_nullable_fields_use_correct_format(self, manifest):
        """Verify nullable fields use type array syntax [type, 'null']."""
        for schema_name, schema in manifest["schemas"].items():
            for field_name, field_def in schema.get(
                "properties", {}
            ).items():
                if isinstance(field_def.get("type"), list):
                    assert "null" in field_def["type"], (
                        f"Schema '{schema_name}.{field_name}' "
                        f"has array type but no null"
                    )
