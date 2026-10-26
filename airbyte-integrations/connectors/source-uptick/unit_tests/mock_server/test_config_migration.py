# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server coverage for the `base_url` normalization in `spec.config_normalization_rules`.

Connections created before this rule existed may store `base_url` with an `http://` scheme, a
trailing slash, surrounding whitespace, or an API path. These tests run `check` and `read` with
such legacy configs and assert that every request is issued against the canonical
`https://<host>` URL, that the stored config is not rewritten (no CONTROL message), and that a
canonical config keeps working unchanged.
"""

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import _run_command, make_file, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


_STREAM = "servicegroups"
_CHECK_STREAM = "tasks"
_TOKEN_REQUEST = HttpRequest(
    url=UptickRequestBuilder.token_endpoint(),
    body="grant_type=password&client_id=test-client-id&client_secret=test-client-secret&username=test-user&password=test-password",
)
_TOKEN_RESPONSE = HttpResponse(body=json.dumps({"access_token": "tok", "expires_in": 3600}), status_code=200)
_LEGACY_BASE_URLS = [
    pytest.param("https://test-tenant.onuptick.com", id="canonical"),
    pytest.param("http://test-tenant.onuptick.com/", id="http_scheme_trailing_slash"),
    pytest.param("HTTP://test-tenant.onuptick.com//", id="uppercase_scheme_double_slash"),
    pytest.param("  https://test-tenant.onuptick.com  ", id="surrounding_whitespace"),
    pytest.param("https://test-tenant.onuptick.com/api/v2.15/", id="api_path"),
    pytest.param("test-tenant.onuptick.com", id="bare_host"),
]


def _page(stream: str, record_type: str, record_id: int) -> HttpResponse:
    record = {
        "type": record_type,
        "id": record_id,
        "attributes": {
            "created": "2026-01-01T00:00:00.000000+0000",
            "updated": "2026-01-02T00:00:00.000000+0000",
        },
        "relationships": {},
    }
    return HttpResponse(body=json.dumps({"data": [record], "links": {"next": None}}), status_code=200)


def _control_messages(stdout: str) -> list[dict]:
    messages = []
    for line in stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("type") == "CONTROL":
            messages.append(message)
    return messages


@pytest.mark.parametrize("base_url", _LEGACY_BASE_URLS)
def test_read_with_legacy_base_url_hits_canonical_host(base_url: Any) -> None:
    config = ConfigBuilder().with_base_url(base_url).with_password_credentials().build()
    catalog = CatalogBuilder().with_stream(_STREAM, SyncMode.full_refresh).build()
    page_request = UptickRequestBuilder.collection(_STREAM)
    stdout = StringIO()

    with HttpMocker() as http_mocker:
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        http_mocker.get(page_request, _page(_STREAM, "ServiceGroup", 1))

        with redirect_stdout(stdout):
            source = get_source(config=config)
            output = read(source, config=config, catalog=catalog, state=StateBuilder().build())

        http_mocker.assert_number_of_calls(_TOKEN_REQUEST, 1)
        http_mocker.assert_number_of_calls(page_request, 1)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == [1]
    assert output.get_stream_statuses(_STREAM)[-1].name == "COMPLETE"
    assert _control_messages(stdout.getvalue()) == []
    assert config["base_url"] == base_url


@pytest.mark.parametrize("base_url", _LEGACY_BASE_URLS)
def test_check_with_legacy_base_url_succeeds(base_url: Any, tmp_path: Path) -> None:
    config = ConfigBuilder().with_base_url(base_url).with_password_credentials().build()
    check_request = UptickRequestBuilder.collection(_CHECK_STREAM)
    stdout = StringIO()

    with HttpMocker() as http_mocker:
        http_mocker.post(_TOKEN_REQUEST, _TOKEN_RESPONSE)
        http_mocker.get(check_request, _page(_CHECK_STREAM, "Task", 1))

        with redirect_stdout(stdout):
            source = get_source(config=config)
            output = _run_command(source, ["check", "--config", make_file(tmp_path / "config.json", config)])

        http_mocker.assert_number_of_calls(check_request, 1)

    statuses = output.connection_status_messages
    assert len(statuses) == 1
    assert statuses[0].connectionStatus.status == Status.SUCCEEDED
    assert _control_messages(stdout.getvalue()) == []
