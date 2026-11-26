# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import copy
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


MANIFEST_PATH = Path(__file__).parents[1] / "manifest.yaml"
BASE_URL = "https://graph.microsoft.com/v1.0/"
CONFIG = {
    "credentials": {"client_id": "fixture-client", "client_secret": "fixture-secret", "tenant_id": "fixture-tenant"},
    "period": "D7",
    "page_size": 2,
}
POSTS_PATH = "groups/group-1/conversations/conversation-1/threads/thread-1/posts"
REPORT_PATH = "reports/getTeamsDeviceUsageUserDetail(period='D7')"
PARENT_PATHS = {
    "groups": "groups",
    "conversations": "groups/group-1/conversations",
    "conversation_threads": "groups/group-1/conversations/conversation-1/threads",
}
POSTS = [
    {"id": "post-1", "threadId": "thread-1", "conversationId": "conversation-1", "body": {"content": "First post"}},
    {"id": "post-2", "threadId": "thread-1", "conversationId": "conversation-1", "body": {"content": "Second post"}},
]
REPORTS = [{"userId": "user-1", "usedWeb": "Yes", "reportPeriod": "7", "reportRefreshDate": "2026-11-01"}]


def restore_single_child_wrappers(node: Any) -> None:
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if key == "error_handler":
                node[key] = {"type": "".join(("Composite", "ErrorHandler")), "error_handlers": [value]}
            else:
                restore_single_child_wrappers(value)
    elif isinstance(node, list):
        for value in node:
            restore_single_child_wrappers(value)


@pytest.fixture
def manifests(tmp_path: Path) -> Iterator[Path]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    restore_single_child_wrappers(manifest)
    baseline = tmp_path / "baseline.yaml"
    baseline.write_text(yaml.safe_dump(manifest))
    return iter((baseline, MANIFEST_PATH))


def register_parents(http: requests_mock.Mocker) -> None:
    for name, record_id in (("groups", "group-1"), ("conversations", "conversation-1"), ("conversation_threads", "thread-1")):
        http.get(f"{BASE_URL}{PARENT_PATHS[name]}?$top=2", json={"value": [{"id": record_id}]})


def run_read(manifest: Path, stream: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(manifest), catalog=catalog, config=CONFIG, state=[])
    return read(source, CONFIG, catalog, expecting_exception=expecting_exception)


def records(output: EntrypointOutput) -> list[dict[str, Any]]:
    return [message.record.data for message in output.records if message.record is not None]


def states(output: EntrypointOutput) -> list[Any]:
    return [message.state.stream for message in output.state_messages if message.state is not None]


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    delays: list[float] = []
    monkeypatch.setattr("time.sleep", delays.append)
    return delays


@pytest.mark.parametrize(
    "stream,path,expected", [("conversation_posts", POSTS_PATH, POSTS), ("team_device_usage_report", REPORT_PATH, REPORTS)]
)
def test_complete_paginated_read_matches_wrapped_baseline(
    manifests: Iterator[Path], stream: str, path: str, expected: list[dict[str, Any]], sleeps: list[float]
) -> None:
    results = []
    for manifest in manifests:
        with requests_mock.Mocker() as http:
            register_parents(http)
            first_page = http.get(
                f"{BASE_URL}{path}?$top=2",
                json={"value": expected[:1], "@odata.nextLink": f"{BASE_URL}{path}?$skiptoken=next"},
            )
            last_page = http.get(f"{BASE_URL}{path}?$skiptoken=next", json={"value": expected[1:]})
            http.post(
                "https://login.microsoftonline.com/fixture-tenant/oauth2/v2.0/token",
                json={"access_token": "fixture-token", "expires_in": 3600},
            )
            output = run_read(manifest, stream)
            assert records(output) == expected
            assert output.errors == []
            assert output.state_messages
            assert first_page.call_count == last_page.call_count == 1
            if stream == "conversation_posts":
                for parent_path in PARENT_PATHS.values():
                    assert any(request.path == f"/v1.0/{parent_path}" for request in http.request_history)
            results.append((records(output), states(output)))
    assert results[0] == results[1]
    assert sleeps == []


@pytest.mark.parametrize(
    "stream,error_path,status,body,message",
    [
        *[("conversation_posts", POSTS_PATH, status, {}, "Some resources are not allowed to extract") for status in (403, 404, 503)],
        ("conversation_posts", POSTS_PATH, 400, {"App Only access is not allowed": "present"}, "Some resources are not allowed to extract"),
        ("conversation_posts", PARENT_PATHS["conversations"], 403, {}, "App only access is restricting some resources"),
        *[
            ("conversation_posts", PARENT_PATHS["conversation_threads"], status, {}, "Some resources not found for parent resources")
            for status in (403, 404)
        ],
        (
            "conversation_posts",
            PARENT_PATHS["conversation_threads"],
            400,
            {"App Only access is not allowed": "present"},
            "Some resources not found for parent resources",
        ),
        ("team_device_usage_report", REPORT_PATH, 400, {}, "Personal account not supported"),
    ],
)
def test_ignored_http_errors_match_wrapped_baseline(
    manifests: Iterator[Path], stream: str, error_path: str, status: int, body: dict[str, str], message: str, sleeps: list[float]
) -> None:
    results = []
    for manifest in manifests:
        with requests_mock.Mocker() as http:
            register_parents(http)
            error = http.get(f"{BASE_URL}{error_path}?$top=2", status_code=status, json=body)
            http.post(
                "https://login.microsoftonline.com/fixture-tenant/oauth2/v2.0/token",
                json={"access_token": "fixture-token", "expires_in": 3600},
            )
            output = run_read(manifest, stream)
            assert records(output) == []
            assert output.errors == []
            assert output.state_messages
            assert error.call_count >= 1
            assert any(message in log.log.message for log in output.logs if log.log is not None)
            results.append((records(output), states(output), error.call_count))
    assert results[0] == results[1]
    assert sleeps == []


@pytest.mark.parametrize(
    "stream,path,expected", [("conversation_posts", POSTS_PATH, POSTS), ("team_device_usage_report", REPORT_PATH, REPORTS)]
)
@pytest.mark.parametrize("status", [401, 429, 500])
def test_unrelated_errors_preserve_retry_budget_and_backoff(
    manifests: Iterator[Path], stream: str, path: str, expected: list[dict[str, Any]], status: int, sleeps: list[float]
) -> None:
    results = []
    for manifest in manifests:
        sleeps.clear()
        with requests_mock.Mocker() as http:
            register_parents(http)
            response = http.get(f"{BASE_URL}{path}?$top=2", status_code=status, json={"error": {"message": "Unrelated failure"}})
            http.post(
                "https://login.microsoftonline.com/fixture-tenant/oauth2/v2.0/token",
                json={"access_token": "fixture-token", "expires_in": 3600},
            )
            output = run_read(manifest, stream, expecting_exception=True)
            assert output.errors
            assert records(output) == []
            assert response.call_count == (1 if status == 401 else 6)
            assert len(sleeps) == (0 if status == 401 else 5)
            trace = output.errors[0].trace
            assert trace is not None and trace.error is not None
            results.append((states(output), copy.deepcopy(sleeps), trace.error.failure_type))
    assert results[0] == results[1]
