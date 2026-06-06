# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the source-discord connector manifest."""

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

EXPOSED_STREAMS = sorted(
    [
        "channels",
        "guilds",
        "members",
        "messages",
        "roles",
        "scheduled_events",
        "threads",
    ]
)


@pytest.fixture
def manifest():
    """Load the connector manifest."""
    return yaml.safe_load(MANIFEST_PATH.read_text())


# ---------------------------------------------------------------------------
# Behavioral tests: CDK instantiation + discover
# ---------------------------------------------------------------------------


def test_manifest_instantiates_with_cdk():
    """Verify the CDK can parse and instantiate the manifest without errors."""
    from airbyte_cdk import YamlDeclarativeSource

    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
    assert source is not None


def test_discover_returns_expected_streams():
    """Verify discover returns exactly the expected exposed streams."""
    from airbyte_cdk import YamlDeclarativeSource

    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
    catalog = source.discover(
        logger=None,
        config={"bot_token": "test-token"},
    )
    stream_names = sorted([s.name for s in catalog.streams])
    assert stream_names == EXPOSED_STREAMS


# ---------------------------------------------------------------------------
# Messages partitioning — behavioral mock test (P0 fix)
# ---------------------------------------------------------------------------


def test_messages_partition_router_is_union_not_cartesian(manifest):
    """The messages partition_router must be a single SubstreamPartitionRouter
    with multiple ParentStreamConfigs (union), not a list of routers
    (which the CDK treats as a CartesianProductStreamSlicer)."""
    messages = manifest["definitions"]["streams"]["messages"]
    router = messages["retriever"]["partition_router"]
    assert isinstance(router, dict), "partition_router should be a dict (single router), not a list"
    assert router["type"] == "SubstreamPartitionRouter"
    parent_configs = router["parent_stream_configs"]
    parent_refs = [cfg["stream"]["$ref"].split("/")[-1] for cfg in parent_configs]
    assert "message_parent_channels" in parent_refs
    assert "threads" in parent_refs
    assert "archived_public_threads" in parent_refs
    assert "archived_private_threads" in parent_refs
    for cfg in parent_configs:
        assert cfg["partition_field"] == "channel_id"


def test_messages_stream_instantiates_with_cdk():
    """Verify the CDK can instantiate the messages stream and it is discoverable."""
    from airbyte_cdk import YamlDeclarativeSource

    source = YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
    catalog = source.discover(
        logger=None,
        config={"bot_token": "test-token"},
    )

    messages_stream_catalog = next(
        (stream for stream in catalog.streams if stream.name == "messages"),
        None,
    )
    assert messages_stream_catalog is not None

    streams = source.streams(config={"bot_token": "test-token"})
    messages_stream = next(
        (stream for stream in streams if stream.name == "messages"),
        None,
    )
    assert messages_stream is not None


# ---------------------------------------------------------------------------
# Manifest structure
# ---------------------------------------------------------------------------


def test_manifest_loads(manifest):
    """Verify manifest loads and is a DeclarativeSource."""
    assert manifest is not None
    assert manifest["type"] == "DeclarativeSource"


def test_manifest_version_present(manifest):
    """Verify manifest declares a version."""
    assert "version" in manifest
    assert manifest["version"] is not None


def test_check_stream_is_guilds(manifest):
    """Verify check stream uses guilds."""
    assert manifest["check"]["type"] == "CheckStream"
    assert "guilds" in manifest["check"]["stream_names"]


def test_exposed_streams_match_expected(manifest):
    """Verify top-level streams list matches the expected surface."""
    stream_refs = manifest["streams"]
    assert len(stream_refs) == len(EXPOSED_STREAMS)
    ref_names = sorted(ref["$ref"].split("/")[-1] for ref in stream_refs)
    assert ref_names == EXPOSED_STREAMS


def test_internal_streams_not_exposed(manifest):
    """current_user, archived thread streams, and filtered parent streams are internal."""
    ref_names = [ref["$ref"].split("/")[-1] for ref in manifest["streams"]]
    assert "current_user" not in ref_names
    assert "archived_public_threads" not in ref_names
    assert "archived_private_threads" not in ref_names
    assert "message_parent_channels" not in ref_names
    assert "archived_public_thread_parent_channels" not in ref_names
    assert "archived_private_thread_parent_channels" not in ref_names


def test_removed_streams_not_in_definitions(manifest):
    """pinned_messages and audit_log should be fully removed."""
    stream_defs = manifest["definitions"]["streams"]
    assert "pinned_messages" not in stream_defs
    assert "audit_log" not in stream_defs


def test_spec_has_required_fields(manifest):
    """Verify spec declares bot_token as required secret."""
    spec = manifest["spec"]
    assert spec["type"] == "Spec"
    conn_spec = spec["connection_specification"]
    assert "bot_token" in conn_spec["properties"]
    assert conn_spec["properties"]["bot_token"]["airbyte_secret"] is True
    assert "bot_token" in conn_spec["required"]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def test_authenticator_uses_bot_prefix(manifest):
    """Verify ApiKeyAuthenticator with Bot prefix."""
    auth = manifest["definitions"]["authenticator"]
    assert auth["type"] == "ApiKeyAuthenticator"
    assert "Bot" in auth["api_token"]
    assert "config['bot_token']" in auth["api_token"]
    inject = auth["inject_into"]
    assert inject["field_name"] == "Authorization"
    assert inject["inject_into"] == "header"


# ---------------------------------------------------------------------------
# Requester configuration
# ---------------------------------------------------------------------------


def test_base_requester_url(manifest):
    """Verify base URL targets Discord API v10."""
    requester = manifest["definitions"]["base_requester"]
    assert requester["url_base"] == "https://discord.com/api/v10"


def test_base_requester_retries_rate_limit(manifest):
    """Verify 429 responses trigger retry."""
    filters = manifest["definitions"]["base_requester"]["error_handler"]["response_filters"]
    rate_limit = [f for f in filters if 429 in f.get("http_codes", [])]
    assert len(rate_limit) == 1
    assert rate_limit[0]["action"] == "RETRY"


def test_base_requester_retries_server_errors(manifest):
    """Verify 5xx responses trigger retry."""
    filters = manifest["definitions"]["base_requester"]["error_handler"]["response_filters"]
    server_err = [f for f in filters if any(c in f.get("http_codes", []) for c in [500, 502, 503])]
    assert len(server_err) == 1
    assert server_err[0]["action"] == "RETRY"


def test_backoff_uses_retry_after_header(manifest):
    """Verify WaitTimeFromHeader backoff on Retry-After."""
    backoff = manifest["definitions"]["base_requester"]["error_handler"]["backoff_strategies"]
    assert any(s.get("header") == "Retry-After" for s in backoff)


def test_permissive_requester_ignores_403(manifest):
    """Verify permissive requester skips 403 (channel-level permission denied)."""
    filters = manifest["definitions"]["permissive_requester"]["error_handler"]["response_filters"]
    forbidden = [f for f in filters if 403 in f.get("http_codes", [])]
    assert len(forbidden) == 1
    assert forbidden[0]["action"] == "IGNORE"


# ---------------------------------------------------------------------------
# Messages stream
# ---------------------------------------------------------------------------


def test_messages_pagination_uses_before(manifest):
    """Messages paginate with `before` (newest-to-oldest)."""
    paginator = manifest["definitions"]["streams"]["messages"]["retriever"]["paginator"]
    assert paginator["page_token_option"]["field_name"] == "before"


def test_messages_pagination_has_no_initial_token(manifest):
    """No initial_token needed — Discord defaults `before` to now."""
    strategy = manifest["definitions"]["streams"]["messages"]["retriever"]["paginator"]["pagination_strategy"]
    assert "initial_token" not in strategy


def test_messages_uses_permissive_requester(manifest):
    """Messages uses permissive requester for graceful 403 skipping."""
    requester = manifest["definitions"]["streams"]["messages"]["retriever"]["requester"]
    assert requester["$ref"] == "#/definitions/permissive_requester"


def test_messages_injects_channel_id(manifest):
    """Messages should inject channel_id into records via AddFields."""
    transformations = manifest["definitions"]["streams"]["messages"].get("transformations", [])
    field_paths = [f["path"] for t in transformations for f in t.get("fields", [])]
    assert ["channel_id"] in field_paths


def test_messages_schema_has_required_fields(manifest):
    """Verify messages schema has core fields."""
    props = manifest["schemas"]["messages"]["properties"]
    for field in ["id", "channel_id", "content", "author", "timestamp", "attachments", "embeds"]:
        assert field in props, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# Members stream
# ---------------------------------------------------------------------------


def test_members_primary_key_is_composite(manifest):
    """PK must be (user_id, guild_id)."""
    pk = manifest["definitions"]["streams"]["members"]["primary_key"]
    assert "user_id" in pk
    assert "guild_id" in pk


def test_members_uses_base_requester(manifest):
    """Members uses base_requester so 403 fails loudly (missing GUILD_MEMBERS intent)."""
    requester = manifest["definitions"]["streams"]["members"]["retriever"]["requester"]
    assert requester["$ref"] == "#/definitions/base_requester"


def test_members_injects_guild_id_and_user_id(manifest):
    """guild_id and user_id must be injected."""
    transformations = manifest["definitions"]["streams"]["members"].get("transformations", [])
    field_paths = [f["path"] for t in transformations for f in t.get("fields", [])]
    assert ["guild_id"] in field_paths
    assert ["user_id"] in field_paths


def test_members_schema_has_key_fields(manifest):
    """Verify members schema has PK and core fields."""
    props = manifest["schemas"]["members"]["properties"]
    assert "guild_id" in props
    assert "user_id" in props
    assert "user" in props
    assert "joined_at" in props


# ---------------------------------------------------------------------------
# Guilds stream
# ---------------------------------------------------------------------------


def test_guilds_path(manifest):
    """Verify guilds path."""
    requester = manifest["definitions"]["streams"]["guilds"]["retriever"]["requester"]
    assert requester["path"] == "/users/@me/guilds"


def test_guilds_primary_key(manifest):
    """Verify guilds PK."""
    assert manifest["definitions"]["streams"]["guilds"]["primary_key"] == ["id"]


def test_guilds_pagination(manifest):
    """Verify guilds uses cursor pagination with after."""
    paginator = manifest["definitions"]["streams"]["guilds"]["retriever"]["paginator"]
    assert paginator["type"] == "DefaultPaginator"
    strategy = paginator["pagination_strategy"]
    assert strategy["type"] == "CursorPagination"
    assert strategy["page_size"] == 200
    assert strategy["initial_token"] == "0"
    assert paginator["page_token_option"]["field_name"] == "after"


# ---------------------------------------------------------------------------
# Channels stream
# ---------------------------------------------------------------------------


def test_channels_is_substream_of_guilds(manifest):
    """Verify channels is partitioned by guild_id from guilds."""
    router = manifest["definitions"]["streams"]["channels"]["retriever"]["partition_router"]
    assert router["type"] == "SubstreamPartitionRouter"
    parent = router["parent_stream_configs"][0]
    assert parent["parent_key"] == "id"
    assert parent["partition_field"] == "guild_id"


def test_channels_no_pagination(manifest):
    """Verify channels has no pagination (guild returns all channels)."""
    paginator = manifest["definitions"]["streams"]["channels"]["retriever"]["paginator"]
    assert paginator["type"] == "NoPagination"


# ---------------------------------------------------------------------------
# Roles stream
# ---------------------------------------------------------------------------


def test_roles_is_substream_of_guilds(manifest):
    """Verify roles is partitioned by guild_id."""
    router = manifest["definitions"]["streams"]["roles"]["retriever"]["partition_router"]
    parent = router["parent_stream_configs"][0]
    assert parent["partition_field"] == "guild_id"


def test_roles_injects_guild_id(manifest):
    """Verify guild_id is injected into role records."""
    transformations = manifest["definitions"]["streams"]["roles"].get("transformations", [])
    field_paths = [f["path"] for t in transformations for f in t.get("fields", [])]
    assert ["guild_id"] in field_paths


def test_roles_schema_has_guild_id(manifest):
    """Verify roles schema includes guild_id."""
    assert "guild_id" in manifest["schemas"]["roles"]["properties"]


# ---------------------------------------------------------------------------
# Threads stream
# ---------------------------------------------------------------------------


def test_threads_path_active(manifest):
    """Verify threads fetches active threads from guild."""
    requester = manifest["definitions"]["streams"]["threads"]["retriever"]["requester"]
    assert "threads/active" in requester["path"]


def test_threads_extracts_from_threads_field(manifest):
    """Verify DpathExtractor targets `threads` key in response."""
    extractor = manifest["definitions"]["streams"]["threads"]["retriever"]["record_selector"]["extractor"]
    assert extractor["field_path"] == ["threads"]


def test_threads_injects_guild_id(manifest):
    """Verify guild_id is injected into thread records."""
    transformations = manifest["definitions"]["streams"]["threads"].get("transformations", [])
    field_paths = [f["path"] for t in transformations for f in t.get("fields", [])]
    assert ["guild_id"] in field_paths


# ---------------------------------------------------------------------------
# Archived threads (internal streams for message fetching)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stream_name,expected_path_fragment",
    [
        pytest.param("archived_public_threads", "threads/archived/public", id="public"),
        pytest.param("archived_private_threads", "threads/archived/private", id="private"),
    ],
)
def test_archived_threads_definition(manifest, stream_name, expected_path_fragment):
    """Verify archived thread streams exist as internal definitions with correct path."""
    stream = manifest["definitions"]["streams"][stream_name]
    requester = stream["retriever"]["requester"]
    assert expected_path_fragment in requester["path"]
    extractor = stream["retriever"]["record_selector"]["extractor"]
    assert extractor["field_path"] == ["threads"]
    paginator = stream["retriever"]["paginator"]
    assert paginator["type"] == "DefaultPaginator"
    assert paginator["page_token_option"]["field_name"] == "before"


@pytest.mark.parametrize("stream_name", ["archived_public_threads", "archived_private_threads"])
def test_archived_threads_stop_on_has_more(manifest, stream_name):
    """Archived thread pagination uses has_more, not last_page_size."""
    strategy = manifest["definitions"]["streams"][stream_name]["retriever"]["paginator"]["pagination_strategy"]
    assert strategy["stop_condition"] == "{{ not response.get('has_more', False) }}"


# ---------------------------------------------------------------------------
# Private archived threads requester
# ---------------------------------------------------------------------------


def test_private_archived_threads_uses_failing_requester(manifest):
    """Private archived threads require MANAGE_THREADS, so 403 must fail loudly."""
    requester = manifest["definitions"]["streams"]["archived_private_threads"]["retriever"]["requester"]
    assert requester["$ref"] == "#/definitions/private_archived_threads_requester"


def test_private_archived_threads_requester_fails_on_403(manifest):
    """Verify missing MANAGE_THREADS does not silently skip private archived threads."""
    filters = manifest["definitions"]["private_archived_threads_requester"]["error_handler"]["response_filters"]
    forbidden = [f for f in filters if 403 in f.get("http_codes", [])]

    assert len(forbidden) == 1
    assert forbidden[0]["action"] == "FAIL"
    assert "MANAGE_THREADS" in forbidden[0]["error_message"]


def test_private_archived_threads_requester_preserves_retries(manifest):
    """Verify dedicated requester still retries rate limits and transient server errors."""
    filters = manifest["definitions"]["private_archived_threads_requester"]["error_handler"]["response_filters"]

    rate_limit = [f for f in filters if 429 in f.get("http_codes", [])]
    server_errors = [f for f in filters if any(code in f.get("http_codes", []) for code in [500, 502, 503])]

    assert rate_limit[0]["action"] == "RETRY"
    assert server_errors[0]["action"] == "RETRY"


# ---------------------------------------------------------------------------
# Filtered parent channel streams
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stream_name,expected_condition",
    [
        pytest.param(
            "message_parent_channels",
            "{{ record.get('type') in [0, 5] }}",
            id="message_parent_channels",
        ),
        pytest.param(
            "archived_public_thread_parent_channels",
            "{{ record.get('type') in [0, 5] }}",
            id="archived_public_thread_parent_channels",
        ),
        pytest.param(
            "archived_private_thread_parent_channels",
            "{{ record.get('type') == 0 }}",
            id="archived_private_thread_parent_channels",
        ),
    ],
)
def test_internal_parent_channel_filters(manifest, stream_name, expected_condition):
    """Internal parent channel streams filter to thread-capable channel types."""
    selector = manifest["definitions"]["streams"][stream_name]["retriever"]["record_selector"]
    assert selector["record_filter"]["condition"] == expected_condition


def test_archived_thread_streams_use_filtered_channel_parents(manifest):
    """Archived thread streams use type-filtered parent channels, not the raw channels stream."""
    public_parent = manifest["definitions"]["streams"]["archived_public_threads"]["retriever"]["partition_router"]["parent_stream_configs"][
        0
    ]
    private_parent = manifest["definitions"]["streams"]["archived_private_threads"]["retriever"]["partition_router"][
        "parent_stream_configs"
    ][0]

    assert public_parent["stream"]["$ref"] == "#/definitions/streams/archived_public_thread_parent_channels"
    assert private_parent["stream"]["$ref"] == "#/definitions/streams/archived_private_thread_parent_channels"


# ---------------------------------------------------------------------------
# Scheduled events stream
# ---------------------------------------------------------------------------


def test_scheduled_events_uses_base_requester(manifest):
    """Verify scheduled_events uses base_requester."""
    requester = manifest["definitions"]["streams"]["scheduled_events"]["retriever"]["requester"]
    assert requester["$ref"] == "#/definitions/base_requester"


def test_scheduled_events_injects_guild_id(manifest):
    """Verify guild_id is injected."""
    transformations = manifest["definitions"]["streams"]["scheduled_events"].get("transformations", [])
    field_paths = [f["path"] for t in transformations for f in t.get("fields", [])]
    assert ["guild_id"] in field_paths


# ---------------------------------------------------------------------------
# Schemas — format:date-time on timestamps
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "schema_name,field_name",
    [
        pytest.param("messages", "timestamp", id="messages.timestamp"),
        pytest.param("messages", "edited_timestamp", id="messages.edited_timestamp"),
        pytest.param("members", "joined_at", id="members.joined_at"),
        pytest.param("members", "premium_since", id="members.premium_since"),
        pytest.param("members", "communication_disabled_until", id="members.communication_disabled_until"),
        pytest.param("scheduled_events", "scheduled_start_time", id="scheduled_events.scheduled_start_time"),
        pytest.param("scheduled_events", "scheduled_end_time", id="scheduled_events.scheduled_end_time"),
    ],
)
def test_timestamp_fields_have_date_time_format(manifest, schema_name, field_name):
    """ISO8601 timestamp fields must declare format: date-time."""
    field = manifest["schemas"][schema_name]["properties"][field_name]
    assert field.get("format") == "date-time", f"{schema_name}.{field_name} missing format: date-time"


# ---------------------------------------------------------------------------
# General schema validation
# ---------------------------------------------------------------------------

EXPOSED_SCHEMA_NAMES = [
    "guilds",
    "channels",
    "messages",
    "members",
    "roles",
    "threads",
    "scheduled_events",
]

SCHEMAS_WITH_ID = [s for s in EXPOSED_SCHEMA_NAMES if s != "members"] + ["current_user"]


def test_all_exposed_schemas_are_objects(manifest):
    """Verify all exposed schemas have type object and properties."""
    for name in EXPOSED_SCHEMA_NAMES:
        schema = manifest["schemas"][name]
        assert schema["type"] == "object", f"Schema '{name}' is not of type object"
        assert "properties" in schema, f"Schema '{name}' has no properties"


def test_all_exposed_schemas_allow_additional_properties(manifest):
    """Verify additionalProperties: true on all exposed schemas."""
    for name in EXPOSED_SCHEMA_NAMES:
        schema = manifest["schemas"][name]
        assert schema.get("additionalProperties") is True, f"Schema '{name}' missing additionalProperties"


def test_schemas_with_id_have_string_id(manifest):
    """Verify id field is present and typed as string."""
    for name in SCHEMAS_WITH_ID:
        schema = manifest["schemas"][name]
        assert "id" in schema["properties"], f"Schema '{name}' missing 'id' field"
        assert schema["properties"]["id"]["type"] == "string"


def test_nullable_fields_use_correct_format(manifest):
    """Verify nullable fields use type array syntax [type, 'null']."""
    for schema_name in EXPOSED_SCHEMA_NAMES:
        for field_name, field_def in manifest["schemas"][schema_name].get("properties", {}).items():
            if isinstance(field_def.get("type"), list):
                assert "null" in field_def["type"], f"Schema '{schema_name}.{field_name}' has array type but no null"


def test_removed_schemas_not_present(manifest):
    """Verify audit_log schema is removed."""
    assert "audit_log" not in manifest["schemas"]
