# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import _run_command, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_subdomain": "test-account", "api_username": "dummy", "api_password": "dummy"}
USERS_REQUEST = HttpRequest("https://test-account.sendsmaily.net/api/organizations/users.php", query_params={"limit": "250"})
NOT_FOUND_MESSAGE = (
    "Smaily returned 404 Not Found for the configured API subdomain. " "Check that the API subdomain matches an active Smaily account."
)
UNAUTHORIZED_MESSAGE = "Smaily rejected the API credentials. Check the API user username and password in the source configuration."


@pytest.mark.parametrize("status_code,message", [(404, NOT_FOUND_MESSAGE), (401, UNAUTHORIZED_MESSAGE)])
def test_read_configuration_error_without_retries(status_code: int, message: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(USERS_REQUEST, HttpResponse(body=f"<html>{status_code}</html>", status_code=status_code))
        catalog = CatalogBuilder().with_stream("users", SyncMode.full_refresh).build()

        output = read(get_source(CONFIG), CONFIG, catalog, expecting_exception=True)

        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == message
        http_mocker.assert_number_of_calls(USERS_REQUEST, 1)


def test_check_bad_subdomain(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(CONFIG))
    with HttpMocker() as http_mocker:
        http_mocker.get(USERS_REQUEST, HttpResponse(body="<html>404 Not Found</html>", status_code=404))

        output = _run_command(get_source(CONFIG), ["check", "--config", str(config_path)])

        status = output.connection_status_messages[0].connectionStatus
        assert status.status == Status.FAILED
        assert NOT_FOUND_MESSAGE in status.message
