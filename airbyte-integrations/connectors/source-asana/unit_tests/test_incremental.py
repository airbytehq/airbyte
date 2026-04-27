#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""
Tests that guard against the `silent incremental` anti-pattern described in
`airbytehq/ai-skills` skill `add-incremental-stream-support`.

The `tasks` stream is declared incremental via a `modified_at` cursor. These
tests assert at the *call site* (the outgoing HTTP request) that:

1. `tasks` requests carry the `modified_since` query parameter derived from
   the cursor value.
2. Child streams (stories_compact, stories, attachments_compact, attachments)
   that route through the incremental `tasks` parent inherit the parent's
   `modified_since` filter on the parent fetch, even though the children
   themselves remain full-refresh (no `incremental_sync` block, no
   `incremental_dependency: true`).
"""

import logging
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml
from source_asana.source import SourceAsana

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
)


ASANA_API = "https://app.asana.com/api/1.0"
WORKSPACE_GID = "ws1"
PROJECT_GID = "proj1"
TASK_OLD_GID = "task_old"
TASK_NEW_GID = "task_new"
STATE_CURSOR = "2026-01-01T00:00:00Z"


def _config() -> Mapping[str, Any]:
    return {"credentials": {"option_title": "PAT Credentials", "personal_access_token": "TOKEN"}}


def _catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _state_for_tasks() -> list[AirbyteStateMessage]:
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="tasks"),
                stream_state=AirbyteStateBlob(
                    use_global_cursor=True,
                    state={"modified_at": STATE_CURSOR},
                    lookback_window=0,
                ),
            ),
        )
    ]


def _register_common_mocks(requests_mock) -> None:
    """Register Asana API mocks shared across all incremental-parent tests."""
    requests_mock.get(
        f"{ASANA_API}/workspaces",
        json={"data": [{"gid": WORKSPACE_GID}], "next_page": None},
    )
    requests_mock.get(
        f"{ASANA_API}/projects",
        json={"data": [{"gid": PROJECT_GID}], "next_page": None},
    )
    requests_mock.get(
        f"{ASANA_API}/tasks",
        json={
            "data": [
                {"gid": TASK_OLD_GID, "modified_at": "2025-06-01T00:00:00.000Z"},
                {"gid": TASK_NEW_GID, "modified_at": "2026-04-01T00:00:00.000Z"},
            ],
            "next_page": None,
        },
    )


def _find_task_request(requests_mock) -> Any:
    for req in requests_mock.request_history:
        if req.path == "/api/1.0/tasks":
            return req
    raise AssertionError(f"No request to /api/1.0/tasks found; saw: {[r.url for r in requests_mock.request_history]}")


def _read_records(source: SourceAsana, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: list) -> list:
    return list(source.read(logging.getLogger("airbyte"), dict(config), catalog, state))


def test_tasks_injects_modified_since_from_state(requests_mock):
    """Regression guard: the `modified_since` query parameter must be present on the outgoing `/tasks` request when state is supplied.

    Corresponds to the `silent incremental` anti-pattern in the skill: the cursor is declared but never injected.
    """
    _register_common_mocks(requests_mock)
    catalog = _catalog("tasks")
    source = SourceAsana(catalog=catalog, config=_config(), state=_state_for_tasks())
    _read_records(source, _config(), catalog, _state_for_tasks())

    task_req = _find_task_request(requests_mock)
    assert "modified_since" in task_req.qs, f"Expected `modified_since` in /tasks query string but got: {task_req.qs}"
    assert task_req.qs["modified_since"] == [
        STATE_CURSOR.lower()
    ], f"Expected modified_since={STATE_CURSOR}, got {task_req.qs['modified_since']}"


def test_tasks_uses_epoch_sentinel_when_no_state_or_start_date(requests_mock):
    """Without state or configured `start_date`, the manifest defaults to the epoch sentinel `1970-01-01T00:00:00Z`.

    Honors the user's full available history rather than silently capping the lookback window.
    """
    _register_common_mocks(requests_mock)
    catalog = _catalog("tasks")
    source = SourceAsana(catalog=catalog, config=_config(), state=[])
    _read_records(source, _config(), catalog, [])

    task_req = _find_task_request(requests_mock)
    assert "modified_since" in task_req.qs
    value = task_req.qs["modified_since"][0]
    assert value.startswith("1970-01-01"), value


def test_configured_start_date_injected_as_modified_since(requests_mock):
    """User-provided `config.start_date` must flow into `modified_since` at the call site."""
    _register_common_mocks(requests_mock)
    catalog = _catalog("tasks")
    config = dict(_config())
    config["start_date"] = "2024-05-01T00:00:00Z"
    source = SourceAsana(catalog=catalog, config=config, state=[])
    _read_records(source, config, catalog, [])

    task_req = _find_task_request(requests_mock)
    assert "modified_since" in task_req.qs
    value = task_req.qs["modified_since"][0]
    assert "2024-05-01" in value, value


@pytest.mark.parametrize(
    "child_stream_name",
    [
        pytest.param("stories_compact", id="stories_compact_inherits_from_tasks"),
        pytest.param("attachments_compact", id="attachments_compact_inherits_from_tasks"),
    ],
)
def test_child_stream_parent_is_incremental(child_stream_name, requests_mock):
    """Child streams that route through the incremental `tasks` parent must see `modified_since` on the parent `/tasks` request.

    The children themselves are full-refresh and the partition router does not
    set `incremental_dependency: true`. The parent's own `incremental_sync`
    block still applies on every parent fetch, so `modified_since` is injected
    from `start_datetime` on the call site.
    """
    _register_common_mocks(requests_mock)
    requests_mock.get(f"{ASANA_API}/tasks/{TASK_OLD_GID}/stories", json={"data": [], "next_page": None})
    requests_mock.get(f"{ASANA_API}/tasks/{TASK_NEW_GID}/stories", json={"data": [], "next_page": None})
    requests_mock.get(f"{ASANA_API}/attachments", json={"data": [], "next_page": None})

    catalog = _catalog(child_stream_name)
    source = SourceAsana(catalog=catalog, config=_config(), state=[])
    _read_records(source, _config(), catalog, [])

    task_req = _find_task_request(requests_mock)
    assert (
        "modified_since" in task_req.qs
    ), f"Expected parent `/tasks` fetch (triggered by child `{child_stream_name}`) to inject `modified_since`; got qs={task_req.qs}"


def test_manifest_tasks_stream_declares_incremental_sync():
    """Static guard on the manifest:

    - `tasks_stream` must declare `incremental_sync`.
    - `tasks_partition_router` must NOT set `incremental_dependency: true`.
      The four child streams that route through this parent are full-refresh
      and have no cursor of their own, so the flag would be inert. See the
      connector's `CONTRIBUTING.md` for the full rationale.
    - `incremental_sync_modified_at` must be wired up correctly.
    """
    manifest_path = Path(__file__).parent.parent / "source_asana" / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())

    tasks_stream = manifest["definitions"]["tasks_stream"]
    assert "incremental_sync" in tasks_stream, "tasks_stream must declare incremental_sync"

    tasks_router = manifest["definitions"]["tasks_partition_router"]
    parent = tasks_router["parent_stream_configs"][0]
    assert parent.get("incremental_dependency") is not True, (
        "tasks_partition_router parent_stream_configs[0] must NOT set "
        "`incremental_dependency: true`; the children are full-refresh and the "
        "flag would be inert. See CONTRIBUTING.md."
    )

    inc = manifest["definitions"]["incremental_sync_modified_at"]
    assert inc["cursor_field"] == "modified_at"
    assert inc["start_time_option"]["field_name"] == "modified_since"
    assert inc["start_time_option"]["inject_into"] == "request_parameter"
