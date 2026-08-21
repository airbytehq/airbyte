#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests_mock as req_mock
from source_asana.source import SourceAsana

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


def test_oauth_connector_input_specification_includes_default_scope():
    source = SourceAsana(catalog=None, config=None, state=None)

    spec = source.spec(None)
    oauth_spec = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification

    assert oauth_spec.scopes == [{"scope": "default"}]


def test_tasks_stream_reads_by_section():
    """Verify that tasks are fetched per section (not per project) to avoid Asana API result-set cap."""
    base_url = "https://app.asana.com/api/1.0"
    test_config = {
        "credentials": {
            "option_title": "PAT Credentials",
            "personal_access_token": "test-token",
        }
    }

    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="tasks",
                    json_schema={"type": "object"},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )

    with req_mock.Mocker() as m:
        # Mock workspaces
        m.get(
            f"{base_url}/workspaces",
            json={"data": [{"gid": "ws1", "resource_type": "workspace", "name": "Workspace 1"}]},
        )
        # Mock projects for workspace
        m.get(
            f"{base_url}/projects",
            json={"data": [{"gid": "proj1", "resource_type": "project", "name": "Project 1"}]},
        )
        # Mock sections for project
        m.get(
            f"{base_url}/projects/proj1/sections",
            json={
                "data": [
                    {"gid": "sec1", "resource_type": "section", "name": "Section 1"},
                    {"gid": "sec2", "resource_type": "section", "name": "Section 2"},
                ]
            },
        )
        # Mock tasks for each section
        m.get(
            f"{base_url}/sections/sec1/tasks",
            json={
                "data": [
                    {"gid": "task1", "resource_type": "task", "name": "Task in Section 1"},
                ]
            },
        )
        m.get(
            f"{base_url}/sections/sec2/tasks",
            json={
                "data": [
                    {"gid": "task2", "resource_type": "task", "name": "Task in Section 2"},
                ]
            },
        )

        source = SourceAsana(catalog=configured_catalog, config=test_config, state=None)
        messages = list(source.read(logger=None, config=test_config, catalog=configured_catalog, state={}))

        record_messages = [msg for msg in messages if msg.type == Type.RECORD]
        task_gids = {msg.record.data["gid"] for msg in record_messages}

        assert "task1" in task_gids, "Expected task from section 1"
        assert "task2" in task_gids, "Expected task from section 2"
        assert len(task_gids) == 2

        # Verify that requests went to section-based endpoints, not project-based
        requested_paths = [req.path for req in m.request_history]
        assert any("/sections/sec1/tasks" in p for p in requested_paths)
        assert any("/sections/sec2/tasks" in p for p in requested_paths)
        # No request to /tasks?project=... should have been made
        assert not any("project=" in (req.query or "") and req.path == "/api/1.0/tasks" for req in m.request_history)
