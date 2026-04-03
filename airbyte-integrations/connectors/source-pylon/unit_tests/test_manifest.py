"""
Unit tests for source-pylon manifest configuration.

Validates that the issues stream correctly uses POST /issues/search
with updated_at cursor field and body_json injection for pagination.
"""

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture()
def manifest():
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Issues stream: endpoint and HTTP method
# ---------------------------------------------------------------------------


def test_issues_stream_uses_post_method(manifest):
    """The issues stream must use POST /issues/search instead of GET /issues."""
    issues = manifest["definitions"]["streams"]["issues"]
    requester = issues["retriever"]["requester"]
    assert requester["http_method"] == "POST"
    assert requester["path"] == "issues/search"


# ---------------------------------------------------------------------------
# Issues stream: cursor field
# ---------------------------------------------------------------------------


def test_issues_stream_cursor_field_is_updated_at(manifest):
    """The issues stream must use updated_at as cursor field."""
    issues = manifest["definitions"]["streams"]["issues"]
    assert issues["incremental_sync"]["cursor_field"] == "updated_at"


# ---------------------------------------------------------------------------
# Issues stream: request body filter
# ---------------------------------------------------------------------------


def test_issues_stream_has_request_body_json_filter(manifest):
    """The issues stream must send a filter in the request body."""
    issues = manifest["definitions"]["streams"]["issues"]
    requester = issues["retriever"]["requester"]
    assert "request_body_json" in requester
    assert "filter" in requester["request_body_json"]


def test_issues_stream_filter_uses_updated_at(manifest):
    """The request body filter must reference the updated_at field."""
    issues = manifest["definitions"]["streams"]["issues"]
    filter_template = issues["retriever"]["requester"]["request_body_json"]["filter"]
    assert "updated_at" in filter_template
    assert "time_is_after" in filter_template
    assert "time_is_before" in filter_template


def test_issues_stream_filter_references_stream_interval(manifest):
    """The filter must use stream_interval for start/end times."""
    issues = manifest["definitions"]["streams"]["issues"]
    filter_template = issues["retriever"]["requester"]["request_body_json"]["filter"]
    assert "stream_interval.start_time" in filter_template
    assert "stream_interval.end_time" in filter_template


def test_issues_stream_filter_has_and_operator(manifest):
    """The filter must use the 'and' operator to combine time conditions."""
    issues = manifest["definitions"]["streams"]["issues"]
    filter_template = issues["retriever"]["requester"]["request_body_json"]["filter"]
    assert '"operator": "and"' in filter_template


def test_issues_stream_no_start_end_time_options(manifest):
    """The issues stream must NOT have start_time_option/end_time_option."""
    issues = manifest["definitions"]["streams"]["issues"]
    incremental_sync = issues["incremental_sync"]
    assert "start_time_option" not in incremental_sync
    assert "end_time_option" not in incremental_sync


# ---------------------------------------------------------------------------
# Issues paginator: body_json injection
# ---------------------------------------------------------------------------


def test_issues_paginator_uses_body_json(manifest):
    """The issues paginator must inject cursor and limit into the request body."""
    paginator = manifest["definitions"]["issues_paginator"]
    assert paginator["page_token_option"]["inject_into"] == "body_json"
    assert paginator["page_token_option"]["field_name"] == "cursor"
    assert paginator["page_size_option"]["inject_into"] == "body_json"
    assert paginator["page_size_option"]["field_name"] == "limit"


def test_issues_paginator_strategy(manifest):
    """The issues paginator must use CursorPagination with page_size 999."""
    paginator = manifest["definitions"]["issues_paginator"]
    strategy = paginator["pagination_strategy"]
    assert strategy["type"] == "CursorPagination"
    assert strategy["page_size"] == 999


# ---------------------------------------------------------------------------
# Issues schema: updated_at field
# ---------------------------------------------------------------------------


def test_issues_schema_has_updated_at(manifest):
    """The issues schema must include the updated_at field."""
    schema = manifest["schemas"]["issues"]
    assert "updated_at" in schema["properties"]
    assert schema["properties"]["updated_at"]["type"] == ["null", "string"]


def test_issues_schema_retains_created_at(manifest):
    """The issues schema must still include the created_at field."""
    schema = manifest["schemas"]["issues"]
    assert "created_at" in schema["properties"]


# ---------------------------------------------------------------------------
# Non-issues streams: unchanged
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("accounts", id="accounts"),
        pytest.param("contacts", id="contacts"),
        pytest.param("tags", id="tags"),
        pytest.param("teams", id="teams"),
        pytest.param("users", id="users"),
    ],
)
def test_other_streams_still_use_get(manifest, stream_name):
    """Non-issues streams must still use GET."""
    stream = manifest["definitions"]["streams"][stream_name]
    requester = stream["retriever"]["requester"]
    assert requester["http_method"] == "GET", f"{stream_name} should still use GET"


def test_cursor_paginator_still_uses_request_parameter(manifest):
    """The shared cursor_paginator (for GET streams) must still use request_parameter."""
    paginator = manifest["definitions"]["cursor_paginator"]
    assert paginator["page_token_option"]["inject_into"] == "request_parameter"


# ---------------------------------------------------------------------------
# Substream compatibility: issue_messages and issue_threads
# ---------------------------------------------------------------------------


def test_issue_messages_uses_issues_parent(manifest):
    """issue_messages must still use issues as parent stream."""
    stream = manifest["definitions"]["streams"]["issue_messages"]
    partition_router = stream["retriever"]["partition_router"]
    assert partition_router["parent_stream_configs"][0]["stream"]["$ref"] == "#/definitions/streams/issues"


def test_issue_threads_uses_issues_parent(manifest):
    """issue_threads must still use issues as parent stream."""
    stream = manifest["definitions"]["streams"]["issue_threads"]
    partition_router = stream["retriever"]["partition_router"]
    assert partition_router["parent_stream_configs"][0]["stream"]["$ref"] == "#/definitions/streams/issues"
