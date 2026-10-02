#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover as entrypoint_discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import _YAML_FILE_PATH, BASE_CONFIG, GROUPS_LIST_URL, get_source, get_stream_by_name


CONFIG = BASE_CONFIG | {"projects_list": ["p_1", "p_2"], "start_date": "2026-06-01T00:00:00Z"}

PROJECT_IDS = {"p_1": 11, "p_2": 22}

PIPELINES = {
    11: {
        "<absent>": [{"id": 100, "source": "push", "updated_at": "2026-06-10T00:00:00Z"}],
        "parent_pipeline": [{"id": 101, "source": "parent_pipeline", "updated_at": "2026-06-11T00:00:00Z"}],
    },
    22: {
        "<absent>": [{"id": 200, "source": "web", "updated_at": "2026-06-12T00:00:00Z"}],
        "parent_pipeline": [{"id": 201, "source": "parent_pipeline", "updated_at": "2026-06-13T00:00:00Z"}],
    },
}

CHILD_STREAMS = [
    ("pipelines_extended", "updated_at", "/pipelines/{id}"),
    ("jobs", "pipeline_updated_at", "/pipelines/{id}/jobs"),
    ("pipeline_trigger_jobs", "pipeline_updated_at", "/pipelines/{id}/bridges"),
]


def _source_param(request):
    return parse_qs(urlparse(request.url).query).get("source", ["<absent>"])[0]


def _mock_project_resolution(requests_mock):
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    for project_path, project_id in PROJECT_IDS.items():
        requests_mock.get(f"/api/v4/projects/{project_path}", json=[{"id": project_id, "path_with_namespace": project_path}])


def _mock_pipelines(requests_mock):
    _mock_project_resolution(requests_mock)
    for project_id, by_source in PIPELINES.items():
        for source, pipelines in by_source.items():
            requests_mock.get(
                f"/api/v4/projects/{project_id}/pipelines",
                json=pipelines,
                additional_matcher=lambda request, source=source: _source_param(request) == source,
            )


def _read_records(requests_mock, stream_name, state=None):
    _mock_pipelines(requests_mock)
    if state is None:
        source = get_source(config=CONFIG)
    else:
        source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=CONFIG, state=state, catalog=CatalogBuilder().build())
        source.write_config = Mock()
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name=stream_name, config=migrated_config)

    records = []
    for partition in stream.generate_partitions():
        records.extend(dict(record) for record in partition.read())
    return records


def _incremental_catalog(stream_name):
    return (
        CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(SyncMode.incremental)).build()
    )


def _read_incremental_stream(stream_name, state=None):
    catalog = _incremental_catalog(stream_name)
    state_messages = StateBuilder().with_stream_state(stream_name, state).build() if state is not None else StateBuilder().build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        config=CONFIG,
        state=state_messages,
        catalog=catalog,
    )
    source.write_config = Mock()
    output = entrypoint_read(source=source, config=CONFIG, catalog=catalog, state=state_messages)
    output.raise_if_errors()
    return output


def _all_pipeline_records():
    return {
        project_id: [pipeline for pipelines in by_source.values() for pipeline in pipelines] for project_id, by_source in PIPELINES.items()
    }


def _mock_child_endpoints(requests_mock, stream_name, pipelines_by_project):
    suffix_by_stream = {"pipelines_extended": "", "jobs": "/jobs", "pipeline_trigger_jobs": "/bridges"}
    for project_id, pipelines in pipelines_by_project.items():
        for pipeline in pipelines:
            endpoint = f"/api/v4/projects/{project_id}/pipelines/{pipeline['id']}"
            suffix = suffix_by_stream[stream_name]
            if suffix:
                requests_mock.get(
                    f"{endpoint}{suffix}",
                    json=[{"id": pipeline["id"] * 10, "pipeline": {"id": pipeline["id"]}}],
                )
            else:
                requests_mock.get(endpoint, json=pipeline)


def _pipeline_request_signature(request):
    params = parse_qs(urlparse(request.url).query)
    params.pop("updated_before", None)
    return (urlparse(request.url).path, tuple((key, tuple(values)) for key, values in sorted(params.items())))


def _expected_pipeline_request_signature(project_id, source, updated_after):
    params = {"per_page": ("50",), "updated_after": (updated_after,)}
    if source == "parent_pipeline":
        params["source"] = ("parent_pipeline",)
    return (f"/api/v4/projects/{project_id}/pipelines", tuple(sorted(params.items())))


def _mock_incremental_pipelines(requests_mock, response_by_partition):
    _mock_project_resolution(requests_mock)
    for (project_id, source, updated_after), pipelines in response_by_partition.items():
        requests_mock.get(
            f"/api/v4/projects/{project_id}/pipelines",
            json=pipelines,
            additional_matcher=lambda request, source=source, updated_after=updated_after: (
                _source_param(request) == source and parse_qs(urlparse(request.url).query).get("updated_after") == [updated_after]
            ),
        )


def _all_child_request_paths(requests_mock, stream_name):
    suffix_by_stream = {"pipelines_extended": None, "jobs": "/jobs", "pipeline_trigger_jobs": "/bridges"}
    return sorted(
        urlparse(request.url).path
        for request in requests_mock.request_history
        if "/pipelines/" in urlparse(request.url).path
        and (
            urlparse(request.url).path.endswith(suffix_by_stream[stream_name])
            if suffix_by_stream[stream_name]
            else not urlparse(request.url).path.endswith(("/jobs", "/bridges"))
        )
    )


@pytest.mark.parametrize(("stream_name", "cursor_field", "_child_path"), CHILD_STREAMS)
def test_pipeline_child_streams_discover_incremental(stream_name, cursor_field, _child_path):
    output = entrypoint_discover(source=get_source(config=CONFIG), config=CONFIG)
    output.raise_if_errors()
    streams = {stream.name: stream for stream in output.catalog.catalog.streams}

    stream = streams[stream_name]
    assert SyncMode.incremental in stream.supported_sync_modes
    assert stream.source_defined_cursor
    assert stream.default_cursor_field == [cursor_field]


@pytest.mark.parametrize(("stream_name", "cursor_field", "child_path"), CHILD_STREAMS)
def test_pipeline_child_stream_first_incremental_read(requests_mock, stream_name, cursor_field, child_path):
    _mock_pipelines(requests_mock)
    pipelines_by_project = _all_pipeline_records()
    _mock_child_endpoints(requests_mock, stream_name, pipelines_by_project)

    output = _read_incremental_stream(stream_name)

    expected_parent_requests = [
        _expected_pipeline_request_signature(project_id, source, CONFIG["start_date"])
        for project_id in PROJECT_IDS.values()
        for source in ("<absent>", "parent_pipeline")
    ]
    assert sorted(_pipeline_request_signature(request) for request in _pipelines_requests(requests_mock)) == sorted(
        expected_parent_requests
    )

    expected_children = sorted(
        f"/api/v4/projects/{project_id}{child_path.format(id=pipeline['id'])}"
        for project_id, pipelines in pipelines_by_project.items()
        for pipeline in pipelines
    )
    assert _all_child_request_paths(requests_mock, stream_name) == expected_children

    if stream_name in ("jobs", "pipeline_trigger_jobs"):
        records_by_pipeline = {
            record["pipeline_id"]: record["pipeline_updated_at"] for record in (message.record.data for message in output.records)
        }
        assert records_by_pipeline == {
            pipeline["id"]: pipeline["updated_at"] for pipelines in pipelines_by_project.values() for pipeline in pipelines
        }

    child_state = output.most_recent_state.stream_state.__dict__
    assert child_state["use_global_cursor"] is True
    parent_states = child_state["parent_state"]["pipelines"]["states"]
    assert all(set(state["cursor"]) == {"updated_at"} for state in parent_states)
    assert {
        (state["partition"]["id"], state["partition"]["pipeline_source"]): state["cursor"]["updated_at"] for state in parent_states
    } == {
        (project_id, "default" if source == "<absent>" else source): pipelines[0]["updated_at"]
        for project_id, by_source in PIPELINES.items()
        for source, pipelines in by_source.items()
    }


@pytest.mark.parametrize(("stream_name", "_cursor_field", "child_path"), CHILD_STREAMS)
def test_pipeline_child_stream_resumes_parent_partitions_from_state(requests_mock, stream_name, _cursor_field, child_path):
    parent_cursors = {
        (11, "default"): "2026-08-01T00:00:00Z",
        (11, "parent_pipeline"): "2026-08-02T00:00:00Z",
        (22, "default"): "2026-08-03T00:00:00Z",
        (22, "parent_pipeline"): "2026-08-04T00:00:00Z",
    }
    pipeline_parent_state = {
        "use_global_cursor": False,
        "state": {"updated_at": "2026-08-04T00:00:00Z"},
        "states": [
            {
                "partition": {
                    "id": project_id,
                    "parent_slice": {"id": project_path},
                    "pipeline_source": source,
                },
                "cursor": {"updated_at": cursor},
            }
            for project_path, project_id in PROJECT_IDS.items()
            for source in ("default", "parent_pipeline")
            for cursor in [parent_cursors[(project_id, source)]]
        ],
    }
    cursor_field = "pipeline_updated_at" if stream_name == "jobs" else "updated_at"
    child_state = {
        "use_global_cursor": True,
        "state": {cursor_field: "2026-08-04T00:00:00Z"},
        "parent_state": {"pipelines": pipeline_parent_state},
    }
    response_by_partition = {
        (11, "<absent>", parent_cursors[(11, "default")]): [{"id": 110, "source": "push", "updated_at": "2026-08-05T00:00:00Z"}],
        (11, "parent_pipeline", parent_cursors[(11, "parent_pipeline")]): [],
        (22, "<absent>", parent_cursors[(22, "default")]): [{"id": 210, "source": "web", "updated_at": "2026-08-06T00:00:00Z"}],
        (22, "parent_pipeline", parent_cursors[(22, "parent_pipeline")]): [],
    }
    _mock_incremental_pipelines(requests_mock, response_by_partition)
    pipelines_by_project = {
        11: response_by_partition[(11, "<absent>", parent_cursors[(11, "default")])],
        22: response_by_partition[(22, "<absent>", parent_cursors[(22, "default")])],
    }
    _mock_child_endpoints(requests_mock, stream_name, pipelines_by_project)

    output = _read_incremental_stream(stream_name, state=child_state)

    expected_parent_requests = [
        _expected_pipeline_request_signature(project_id, "<absent>" if source == "default" else source, cursor)
        for (project_id, source), cursor in parent_cursors.items()
    ]
    assert sorted(_pipeline_request_signature(request) for request in _pipelines_requests(requests_mock)) == sorted(
        expected_parent_requests
    )
    assert _all_child_request_paths(requests_mock, stream_name) == sorted(
        f"/api/v4/projects/{project_id}{child_path.format(id=pipeline_id)}" for project_id, pipeline_id in ((11, 110), (22, 210))
    )
    if stream_name in ("jobs", "pipeline_trigger_jobs"):
        assert {record.record.data["pipeline_updated_at"] for record in output.records} == {"2026-08-05T00:00:00Z", "2026-08-06T00:00:00Z"}


@pytest.mark.parametrize(("stream_name", "cursor_field", "_child_path"), CHILD_STREAMS)
def test_pipeline_child_stream_new_project_starts_from_parent_global_cursor(requests_mock, stream_name, cursor_field, _child_path):
    parent_cursors = {
        (11, "default"): "2026-08-01T00:00:00Z",
        (11, "parent_pipeline"): "2026-08-02T00:00:00Z",
    }
    parent_global_cursor = "2026-08-15T00:00:00Z"
    new_project_updated_after = "2026-08-14T23:59:59Z"
    pipeline_parent_state = {
        "use_global_cursor": False,
        "state": {"updated_at": parent_global_cursor},
        "lookback_window": 1,
        "states": [
            {
                "partition": {
                    "id": 11,
                    "parent_slice": {"id": "p_1"},
                    "pipeline_source": source,
                },
                "cursor": {"updated_at": cursor},
            }
            for (project_id, source), cursor in parent_cursors.items()
        ],
    }
    child_state = {
        "use_global_cursor": True,
        "state": {cursor_field: parent_global_cursor},
        "lookback_window": 1,
        "parent_state": {"pipelines": pipeline_parent_state},
    }

    _mock_project_resolution(requests_mock)
    for project_id in PROJECT_IDS.values():
        for source in ("<absent>", "parent_pipeline"):
            requests_mock.get(
                f"/api/v4/projects/{project_id}/pipelines",
                json=[],
                additional_matcher=lambda request, source=source: _source_param(request) == source,
            )

    output = _read_incremental_stream(stream_name, state=child_state)

    expected_parent_requests = [
        _expected_pipeline_request_signature(project_id, "<absent>" if source == "default" else source, cursor)
        for (project_id, source), cursor in parent_cursors.items()
    ] + [
        _expected_pipeline_request_signature(project_id, source, new_project_updated_after)
        for project_id in (22,)
        for source in ("<absent>", "parent_pipeline")
    ]
    assert sorted(_pipeline_request_signature(request) for request in _pipelines_requests(requests_mock)) == sorted(
        expected_parent_requests
    )
    assert output.records == []


@pytest.mark.parametrize(("stream_name", "_cursor_field", "child_path"), CHILD_STREAMS)
def test_pipeline_child_stream_from_full_refresh_sentinel_state(requests_mock, stream_name, _cursor_field, child_path):
    _mock_pipelines(requests_mock)
    pipelines_by_project = _all_pipeline_records()
    _mock_child_endpoints(requests_mock, stream_name, pipelines_by_project)

    output = _read_incremental_stream(stream_name, state={"__ab_no_cursor_state_message": True})

    expected_parent_requests = [
        _expected_pipeline_request_signature(project_id, source, CONFIG["start_date"])
        for project_id in PROJECT_IDS.values()
        for source in ("<absent>", "parent_pipeline")
    ]
    assert sorted(_pipeline_request_signature(request) for request in _pipelines_requests(requests_mock)) == sorted(
        expected_parent_requests
    )
    expected_children = sorted(
        f"/api/v4/projects/{project_id}{child_path.format(id=pipeline['id'])}"
        for project_id, pipelines in pipelines_by_project.items()
        for pipeline in pipelines
    )
    assert _all_child_request_paths(requests_mock, stream_name) == expected_children
    assert len(output.records) == 4


def _pipelines_requests(requests_mock):
    return [request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/pipelines")]


LEGACY_PIPELINES_STATE = {
    "use_global_cursor": False,
    "state": {"updated_at": "2026-08-15T00:00:00Z"},
    "states": [
        {"partition": {"id": 11, "parent_slice": {"id": "p_1"}}, "cursor": {"updated_at": "2026-08-01T00:00:00Z"}},
        {"partition": {"id": 22, "parent_slice": {"id": "p_2"}}, "cursor": {"updated_at": "2026-08-15T00:00:00Z"}},
    ],
}


def test_pipelines_state_migration_adds_explicit_source_partitions():
    # Imported lazily: test_config_migrations patches `airbyte_cdk.utils.is_cloud_environment`, which
    # only takes effect if `components` has not been imported before the patch is applied.
    from components import PipelinesSourcePartitionStateMigration

    migration = PipelinesSourcePartitionStateMigration(config=CONFIG)

    assert migration.should_migrate(LEGACY_PIPELINES_STATE)
    migrated = migration.migrate(LEGACY_PIPELINES_STATE)

    assert migrated == {
        "use_global_cursor": False,
        "state": {"updated_at": "2026-08-15T00:00:00Z"},
        "states": [
            {
                "partition": {"id": 11, "parent_slice": {"id": "p_1"}, "pipeline_source": "default"},
                "cursor": {"updated_at": "2026-08-01T00:00:00Z"},
            },
            {
                "partition": {"id": 11, "parent_slice": {"id": "p_1"}, "pipeline_source": "parent_pipeline"},
                "cursor": {"updated_at": "2026-06-01T00:00:00Z"},
            },
            {
                "partition": {"id": 22, "parent_slice": {"id": "p_2"}, "pipeline_source": "default"},
                "cursor": {"updated_at": "2026-08-15T00:00:00Z"},
            },
            {
                "partition": {"id": 22, "parent_slice": {"id": "p_2"}, "pipeline_source": "parent_pipeline"},
                "cursor": {"updated_at": "2026-06-01T00:00:00Z"},
            },
        ],
    }
    assert not migration.should_migrate(migrated)


def test_pipelines_migrates_per_project_state_to_default_source_partition(requests_mock):
    legacy_state = StateBuilder().with_stream_state("pipelines", LEGACY_PIPELINES_STATE).build()

    _read_records(requests_mock, "pipelines", state=legacy_state)

    requests = sorted(
        (urlparse(request.url).path, _source_param(request), parse_qs(urlparse(request.url).query)["updated_after"][0])
        for request in _pipelines_requests(requests_mock)
    )
    assert requests == [
        ("/api/v4/projects/11/pipelines", "<absent>", "2026-08-01T00:00:00Z"),
        ("/api/v4/projects/11/pipelines", "parent_pipeline", "2026-06-01T00:00:00Z"),
        ("/api/v4/projects/22/pipelines", "<absent>", "2026-08-15T00:00:00Z"),
        ("/api/v4/projects/22/pipelines", "parent_pipeline", "2026-06-01T00:00:00Z"),
    ]


def test_pipelines_reads_regular_and_child_pipelines(requests_mock):
    records = _read_records(requests_mock, "pipelines")

    assert sorted(record["id"] for record in records) == [100, 101, 200, 201]

    requests = sorted((urlparse(request.url).path, _source_param(request)) for request in _pipelines_requests(requests_mock))
    assert requests == [
        ("/api/v4/projects/11/pipelines", "<absent>"),
        ("/api/v4/projects/11/pipelines", "parent_pipeline"),
        ("/api/v4/projects/22/pipelines", "<absent>"),
        ("/api/v4/projects/22/pipelines", "parent_pipeline"),
    ]
    for request in _pipelines_requests(requests_mock):
        assert parse_qs(urlparse(request.url).query).keys() - {"source"} == {"per_page", "updated_after", "updated_before"}


def test_jobs_are_read_for_child_pipelines(requests_mock):
    requests_mock.get("/api/v4/projects/11/pipelines/100/jobs", json=[{"id": 1, "pipeline": {"id": 100}}])
    requests_mock.get("/api/v4/projects/11/pipelines/101/jobs", json=[{"id": 2, "pipeline": {"id": 101}}])
    requests_mock.get("/api/v4/projects/22/pipelines/200/jobs", json=[])
    requests_mock.get("/api/v4/projects/22/pipelines/201/jobs", json=[])

    records = _read_records(requests_mock, "jobs")

    assert sorted((record["id"], record["pipeline_id"], record["project_id"]) for record in records) == [
        (1, 100, 11),
        (2, 101, 11),
    ]


def test_pipeline_trigger_jobs_stream(requests_mock):
    bridge = {
        "id": 7,
        "name": "trigger-child",
        "stage": "deploy",
        "status": "success",
        "user": {"id": "u_1"},
        "commit": {"id": "c_1"},
        "pipeline": {"id": 100},
        "downstream_pipeline": {"id": 101, "status": "success"},
    }
    requests_mock.get("/api/v4/projects/11/pipelines/100/bridges", json=[bridge])
    requests_mock.get("/api/v4/projects/11/pipelines/101/bridges", json=[])
    requests_mock.get("/api/v4/projects/22/pipelines/200/bridges", json=[])
    requests_mock.get("/api/v4/projects/22/pipelines/201/bridges", json=[])

    records = _read_records(requests_mock, "pipeline_trigger_jobs")

    assert records == [
        bridge
        | {
            "project_id": 11,
            "user_id": "u_1",
            "commit_id": "c_1",
            "pipeline_id": 100,
            "pipeline_updated_at": "2026-06-10T00:00:00Z",
            "downstream_pipeline_id": 101,
        }
    ]
