# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


TOKEN_URL = "https://api.outreach.io/oauth/token"
MAILINGS_URL = "https://api.outreach.io/api/v2/mailings"
NEXT_PAGE_URL = MAILINGS_URL + "?page%5Bafter%5D=cursor-1"
EXPIRED_TOKEN = {
    "id": "expiredAccessToken",
    "title": "Expired Access Token",
    "detail": "Please get a new access token and try again.",
}


def token_response(number):
    return {"access_token": f"access-{number}", "refresh_token": f"refresh-{number}", "expires_in": 7200}


def page(record_id, next_page=None):
    return {
        "data": [{"id": record_id, "attributes": {"updatedAt": "2024-01-02T00:00:00.000Z"}}],
        "links": {"next": next_page},
    }


def read_mailings(config):
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(Path(__file__).resolve().parents[2] / "manifest.yaml"), config=config, catalog=catalog)
    return read(source, config, catalog)


def test_expired_token_on_second_page_refreshes_and_preserves_records(requests_mock, config):
    requests_mock.post(TOKEN_URL, [{"json": token_response(1)}, {"json": token_response(2)}])
    sent_requests = []

    def mailing_response(request, context):
        sent_requests.append((request.url, request.headers["Authorization"]))
        if "page[after]" not in parse_qs(urlparse(request.url).query):
            return page(1, NEXT_PAGE_URL)
        if request.headers["Authorization"] == "Bearer access-1":
            context.status_code = 401
            return EXPIRED_TOKEN
        return page(2)

    requests_mock.get(re.compile(r"https://api\.outreach\.io/api/v2/mailings\?"), json=mailing_response)

    output = read_mailings(config)

    assert not output.errors, output.get_formatted_error_message()
    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert len(sent_requests) == 3
    token_requests = [request for request in requests_mock.request_history if request.method == "POST"]
    assert [parse_qs(request.text) for request in token_requests] == [
        {"grant_type": ["refresh_token"], "client_id": ["test-client"], "client_secret": ["test-secret"], "refresh_token": ["refresh-0"]},
        {"grant_type": ["refresh_token"], "client_id": ["test-client"], "client_secret": ["test-secret"], "refresh_token": ["refresh-1"]},
    ]
    assert [auth for _, auth in sent_requests] == ["Bearer access-1", "Bearer access-1", "Bearer access-2"]
    assert [urlparse(url).path for url, _ in sent_requests] == ["/api/v2/mailings"] * 3
    assert [parse_qs(urlparse(url).query) for url, _ in sent_requests] == [
        {
            "count": ["false"],
            "sort": ["updatedAt"],
            "page[size]": ["100"],
            "newFilterSyntax": ["true"],
            "filter[updatedAt][gte]": ["2024-01-01T00:00:00.000Z"],
        },
        {
            "page[after]": ["cursor-1"],
            "count": ["false"],
            "sort": ["updatedAt"],
            "page[size]": ["100"],
            "newFilterSyntax": ["true"],
            "filter[updatedAt][gte]": ["2024-01-01T00:00:00.000Z"],
        },
        {
            "page[after]": ["cursor-1"],
            "count": ["false"],
            "sort": ["updatedAt"],
            "page[size]": ["100"],
            "newFilterSyntax": ["true"],
            "filter[updatedAt][gte]": ["2024-01-01T00:00:00.000Z"],
        },
    ]


def test_rotated_refresh_token_is_saved_for_the_next_read(requests_mock, config, capsys):
    refresh = requests_mock.post(TOKEN_URL, [{"json": token_response(1)}, {"json": token_response(2)}])
    requests_mock.get(MAILINGS_URL, json=page(1))
    first = read_mailings(config)
    assert not first.errors, first.get_formatted_error_message()
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    saved_configs = [message["control"]["connectorConfig"]["config"] for message in messages if message["type"] == "CONTROL"]
    assert saved_configs, "No CONNECTOR_CONFIG message persisted the rotated refresh token"
    saved = saved_configs[-1]
    assert saved["refresh_token"] == "refresh-1"
    assert saved["access_token"] == "access-1"
    assert saved["token_expiry_date"]
    saved["token_expiry_date"] = "2020-01-01T00:00:00Z"

    second = read_mailings(saved)

    assert not second.errors, second.get_formatted_error_message()
    assert [record.record.data["id"] for record in second.records] == [1]
    assert refresh.call_count == 2
    assert parse_qs(refresh.last_request.text)["refresh_token"] == ["refresh-1"]


@pytest.mark.parametrize(
    "status,expected_requests,expected_refreshes,message",
    [
        (401, 2, 2, "Refreshed OAuth access token is rejected by the API."),
        (403, 1, 1, "Forbidden"),
    ],
)
def test_rejected_credentials_fail_with_bounded_requests(requests_mock, config, status, expected_requests, expected_refreshes, message):
    refresh = requests_mock.post(TOKEN_URL, json=token_response(1))
    rejected = requests_mock.get(MAILINGS_URL, status_code=status, json=EXPIRED_TOKEN)

    output = read_mailings(config)

    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert message in error.message
    assert rejected.call_count == expected_requests
    assert refresh.call_count == expected_refreshes
    assert output.records == []
