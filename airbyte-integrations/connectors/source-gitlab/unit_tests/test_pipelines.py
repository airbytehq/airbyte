#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from urllib.parse import parse_qs, urlparse

from .conftest import BASE_CONFIG, GROUPS_LIST_URL, get_source, get_stream_by_name


CONFIG = BASE_CONFIG | {"projects_list": ["p_1", "p_2"], "start_date": "2026-06-01T00:00:00Z"}

PIPELINES = {
    "p_1": {
        "<absent>": [{"id": 100, "source": "push"}],
        "parent_pipeline": [{"id": 101, "source": "parent_pipeline"}],
    },
    "p_2": {
        "<absent>": [{"id": 200, "source": "web"}],
        "parent_pipeline": [{"id": 201, "source": "parent_pipeline"}],
    },
}


def _source_param(request):
    return parse_qs(urlparse(request.url).query).get("source", ["<absent>"])[0]


def _mock_pipelines(requests_mock):
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    for project, by_source in PIPELINES.items():
        requests_mock.get(f"/api/v4/projects/{project}", json=[{"id": project}])
        for source, pipelines in by_source.items():
            requests_mock.get(
                f"/api/v4/projects/{project}/pipelines",
                json=pipelines,
                additional_matcher=lambda request, source=source: _source_param(request) == source,
            )


def _read_records(requests_mock, stream_name):
    _mock_pipelines(requests_mock)
    source = get_source(config=CONFIG)
    migrated_config = source.configure(config=CONFIG, temp_dir="/not/a/real/path")
    stream = get_stream_by_name(source=source, stream_name=stream_name, config=migrated_config)

    records = []
    for partition in stream.generate_partitions():
        records.extend(dict(record) for record in partition.read())
    return records


def _pipelines_requests(requests_mock):
    return [request for request in requests_mock.request_history if urlparse(request.url).path.endswith("/pipelines")]


def test_pipelines_reads_regular_and_child_pipelines(requests_mock):
    records = _read_records(requests_mock, "pipelines")

    assert sorted(record["id"] for record in records) == [100, 101, 200, 201]

    requests = sorted((urlparse(request.url).path, _source_param(request)) for request in _pipelines_requests(requests_mock))
    assert requests == [
        ("/api/v4/projects/p_1/pipelines", "<absent>"),
        ("/api/v4/projects/p_1/pipelines", "parent_pipeline"),
        ("/api/v4/projects/p_2/pipelines", "<absent>"),
        ("/api/v4/projects/p_2/pipelines", "parent_pipeline"),
    ]
    for request in _pipelines_requests(requests_mock):
        assert parse_qs(urlparse(request.url).query).keys() - {"source"} == {"per_page", "updated_after", "updated_before"}


def test_jobs_are_read_for_child_pipelines(requests_mock):
    requests_mock.get("/api/v4/projects/p_1/pipelines/100/jobs", json=[{"id": 1, "pipeline": {"id": 100}}])
    requests_mock.get("/api/v4/projects/p_1/pipelines/101/jobs", json=[{"id": 2, "pipeline": {"id": 101}}])
    requests_mock.get("/api/v4/projects/p_2/pipelines/200/jobs", json=[])
    requests_mock.get("/api/v4/projects/p_2/pipelines/201/jobs", json=[])

    records = _read_records(requests_mock, "jobs")

    assert sorted((record["id"], record["pipeline_id"], record["project_id"]) for record in records) == [
        (1, 100, "p_1"),
        (2, 101, "p_1"),
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
    requests_mock.get("/api/v4/projects/p_1/pipelines/100/bridges", json=[bridge])
    requests_mock.get("/api/v4/projects/p_1/pipelines/101/bridges", json=[])
    requests_mock.get("/api/v4/projects/p_2/pipelines/200/bridges", json=[])
    requests_mock.get("/api/v4/projects/p_2/pipelines/201/bridges", json=[])

    records = _read_records(requests_mock, "pipeline_trigger_jobs")

    assert records == [
        bridge
        | {
            "project_id": "p_1",
            "user_id": "u_1",
            "commit_id": "c_1",
            "pipeline_id": 100,
            "downstream_pipeline_id": 101,
        }
    ]
