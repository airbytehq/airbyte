# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from requests import PreparedRequest
from requests_mock import Mocker

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


BASE_URL = "https://api.outreach.io"
CONFIG = {
    "client_id": "test-client",
    "client_secret": "test-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2024-01-01T00:00:00Z",
}
EXPIRED_TOKEN = {
    "id": "expiredAccessToken",
    "title": "Expired Access Token",
    "detail": "Please get a new access token and try again.",
}


def read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).resolve().parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
    )
    return read(source, CONFIG, catalog)


def page(record_id: int, next_page: str | None = None) -> dict:
    return {
        "data": [{"id": record_id, "attributes": {"updatedAt": "2024-01-02T00:00:00.000Z"}}],
        "links": {"next": next_page},
    }


@pytest.mark.parametrize(("stream_name", "page_size"), [("calls", "1000"), ("mailings", "100")])
def test_read_refreshes_expired_token_and_retries_same_page(stream_name: str, page_size: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    with Mocker() as http:
        tokens = http.post(
            f"{BASE_URL}/oauth/token",
            [
                {"json": {"access_token": "old-token", "expires_in": 7200}},
                {"json": {"access_token": "new-token", "expires_in": 7200}},
            ],
        )
        next_page = f"{BASE_URL}/api/v2/{stream_name}?page[after]=next-cursor"
        first = http.get(f"{BASE_URL}/api/v2/{stream_name}", json=page(1, next_page))
        page_attempts = []

        def next_page_response(request: PreparedRequest, context) -> dict:
            # The CDK mutates the prepared request's auth header when retrying.
            page_attempts.append((request.url, request.headers["Authorization"]))
            if len(page_attempts) == 1:
                context.status_code = 401
                return EXPIRED_TOKEN
            return page(2)

        second = http.get(next_page, json=next_page_response)

        output = read_stream(stream_name)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert tokens.call_count == 2
        assert first.call_count == 1
        assert second.call_count == 2
        assert first.last_request.headers["Authorization"] == "Bearer old-token"
        assert [authorization for _, authorization in page_attempts] == ["Bearer old-token", "Bearer new-token"]
        assert parse_qs(urlparse(first.last_request.url).query) == {
            "count": ["false"],
            "sort": ["updatedAt"],
            "page[size]": [page_size],
            "newFilterSyntax": ["true"],
            "filter[updatedAt][gte]": ["2024-01-01T00:00:00.000Z"],
        }
        assert page_attempts[0][0] == page_attempts[1][0]
        for request in tokens.request_history:
            assert parse_qs(request.text) == {
                "grant_type": ["refresh_token"],
                "refresh_token": ["test-refresh-token"],
                "client_id": ["test-client"],
                "client_secret": ["test-secret"],
            }


def test_read_fails_when_refreshed_token_is_also_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    with Mocker() as http:
        tokens = http.post(
            f"{BASE_URL}/oauth/token",
            [
                {"json": {"access_token": "old-token", "expires_in": 7200}},
                {"json": {"access_token": "new-token", "expires_in": 7200}},
            ],
        )
        endpoint = http.get(f"{BASE_URL}/api/v2/calls", status_code=401, json=EXPIRED_TOKEN)

        output = read_stream("calls")

        assert output.records == []
        assert endpoint.call_count == 2
        assert tokens.call_count == 2
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == "Refreshed OAuth access token is rejected by the API."


def test_read_does_not_retry_permission_errors() -> None:
    with Mocker() as http:
        tokens = http.post(f"{BASE_URL}/oauth/token", json={"access_token": "token", "expires_in": 7200})
        endpoint = http.get(f"{BASE_URL}/api/v2/calls", status_code=403, json={"id": "forbidden"})

        output = read_stream("calls")

        assert output.records == []
        assert endpoint.call_count == 1
        assert tokens.call_count == 1
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == (
            "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
        )
