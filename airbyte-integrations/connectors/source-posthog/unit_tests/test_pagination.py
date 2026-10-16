# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from source_posthog import SourcePosthog

from airbyte_cdk.models import SyncMode


CONFIG = {"api_key": "test", "base_url": "https://app.posthog.com", "start_date": "2026-09-01T00:00:00Z"}
BASE = "https://app.posthog.com/api/projects/42/"


def stream(name, **config):
    return next(s for s in SourcePosthog().streams({**CONFIG, **config}) if s.name == name)


import pytest


@pytest.mark.parametrize("page_size", [1000, 250, 10000])
def test_persons_follow_next_and_configure_page_size(requests_mock, page_size):
    url = BASE + "persons"
    requests_mock.get(url, json={"results": [{"id": "one"}], "next": url + "?offset=1&limit=100"})
    requests_mock.get(url + "?offset=1&limit=100", complete_qs=True, json={"results": [{"id": "two"}], "next": None})
    persons = stream("persons", persons_page_size=page_size)
    records = list(persons.read_records(SyncMode.full_refresh, stream_slice={"id": 42}))
    assert [r["id"] for r in records] == ["one", "two"]
    assert requests_mock.request_history[0].qs == {"limit": [str(page_size)]}


@pytest.mark.parametrize("next_url", ["https://other.example/api/projects/42/persons?offset=1", BASE + "events/?offset=1"])
def test_rejects_next_link_outside_endpoint(requests_mock, next_url):
    requests_mock.get(BASE + "persons", json={"results": [{"id": "one"}], "next": next_url})
    with pytest.raises(ValueError, match="outside the current endpoint"):
        list(stream("persons").read_records(SyncMode.full_refresh, stream_slice={"id": 42}))
    assert requests_mock.call_count == 1


def test_experiments_fetch_details_for_each_project(requests_mock):
    requests_mock.get("https://app.posthog.com/api/projects", json={"results": [{"id": 42}, {"id": 43}], "next": None})
    for project in [42, 43]:
        base = f"https://app.posthog.com/api/projects/{project}/experiments"
        requests_mock.get(base, json={"results": [{"id": project * 10}], "next": None})
        requests_mock.get(base + "?archived=true", json={"results": [{"id": project * 10 + 1}], "next": None})
        requests_mock.get(
            base + f"/{project * 10 + 1}/",
            json={
                "id": project * 10 + 1,
                "archived": True,
                "metrics": [{"kind": "ExperimentMetric"}],
                "parameters": {"feature_flag_variants": [{"key": "control"}, {"key": "test"}]},
            },
        )
        requests_mock.get(
            base + f"/{project * 10}/",
            json={
                "id": project * 10,
                "name": "Test",
                "metrics": [{"kind": "ExperimentMetric"}],
                "parameters": {"feature_flag_variants": [{"key": "control"}, {"key": "test"}]},
            },
        )
    experiments = stream("experiments")
    records = [
        record
        for part in experiments.stream_slices(sync_mode=SyncMode.full_refresh)
        for record in experiments.read_records(SyncMode.full_refresh, stream_slice=part)
    ]
    assert [r["id"] for r in records] == [420, 421, 430, 431]
    assert all(r["metrics"] == [{"kind": "ExperimentMetric"}] for r in records)
    assert all(len(r["parameters"]["feature_flag_variants"]) == 2 for r in records)


def test_rate_limit_respects_retry_after(requests_mock, mocker):
    sleep = mocker.patch("time.sleep")
    requests_mock.get(
        BASE + "persons",
        [
            {"status_code": 429, "headers": {"Retry-After": "17"}, "json": {"detail": "Throttled"}},
            {"json": {"results": [{"id": "one"}], "next": None}},
        ],
    )
    records = list(stream("persons").read_records(SyncMode.full_refresh, stream_slice={"id": 42}))
    assert [r["id"] for r in records] == ["one"]
    assert any(call.args[0] >= 17 for call in sleep.call_args_list)


def test_experiment_results_keep_cached_results_and_skip_uncomputed(requests_mock):
    requests_mock.get("https://app.posthog.com/api/projects", json={"results": [{"id": 42}], "next": None})
    requests_mock.get(BASE + "experiments", json={"results": [{"id": 1}, {"id": 2}], "next": None})
    requests_mock.get(BASE + "experiments?archived=true", json={"results": [], "next": None})
    result = {"id": "run-id", "status": "completed", "results": [{"metric_uuid": "conversion", "result": {"probability": 0.98}}]}
    requests_mock.get(BASE + "experiments/1/metrics_recalculation/latest/", json=result)
    requests_mock.get(BASE + "experiments/2/metrics_recalculation/latest/", status_code=404, json={"detail": "No results"})
    results = stream("experiment_results")
    records = [
        record
        for part in results.stream_slices(sync_mode=SyncMode.full_refresh)
        for record in results.read_records(SyncMode.full_refresh, stream_slice=part)
    ]
    assert [dict(record) for record in records] == [{**result, "project_id": 42, "experiment_id": 1}]
    assert all(request.method == "GET" for request in requests_mock.request_history)


def test_persons_are_last_without_changing_saved_catalog(mocker):
    import logging

    from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode
    from airbyte_cdk.sources.abstract_source import AbstractSource

    streams = {s.name: s for s in SourcePosthog().streams(CONFIG)}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=streams[name].as_airbyte_stream(),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
            for name in ["persons", "events", "experiments"]
        ]
    )
    read = mocker.patch.object(AbstractSource, "read", return_value=iter([]))
    list(SourcePosthog().read(logging.getLogger("test"), CONFIG, catalog))
    passed_catalog = read.call_args.args[2]
    assert [s.stream.name for s in passed_catalog.streams] == ["events", "experiments", "persons"]
    assert [s.stream.name for s in catalog.streams] == ["persons", "events", "experiments"]


def test_cursor_compares_instants_instead_of_timestamp_strings():
    events = stream("events")
    cursor = events.retriever.cursor
    later = {"timestamp": "2026-09-02T11:00:00Z"}
    earlier = {"timestamp": "2026-09-02T12:00:00+02:00"}
    assert cursor.is_greater_than_or_equal(later, earlier)
    cursor.set_initial_state({"42": earlier})
    cursor.close_slice({"project_id": "42"}, later)
    assert events.state == {"42": later}
