#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.utils import AirbyteTracedException


API_URL = "https://quickbooks.api.intuit.com"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
CONFIG = {
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "refresh-token",
    "access_token": "initial-token",
    "token_expiry_date": "2030-01-01T00:00:00Z",
    "realm_id": "realm-id",
    "start_date": "2026-08-01T00:00:00Z",
    "sandbox": False,
}


def _catalog():
    return CatalogBuilder().with_stream("accounts", SyncMode.incremental).build()


def _account(account_id):
    return {
        "Id": str(account_id),
        "MetaData": {"LastUpdatedTime": "2026-08-15T00:00:00Z"},
    }


def test_refreshes_access_token_and_retries_mid_sync(requests_mock, get_source):
    token_requests = []
    account_requests = []

    def token_callback(request, context):
        token_requests.append(request)
        context.status_code = 200
        return {
            "access_token": "new-token",
            "expires_in": 3600,
            "refresh_token": "rotated-refresh-token",
        }

    def account_callback(request, context):
        account_requests.append(request)
        if len(account_requests) == 1:
            context.status_code = 200
            return {"QueryResponse": {"Account": [_account(i) for i in range(5)]}}
        if len(account_requests) == 2:
            context.status_code = 401
            return {"Fault": {"type": "AuthenticationFault"}}
        context.status_code = 200
        return {"QueryResponse": {"Account": [_account(6)]}}

    requests_mock.post(TOKEN_URL, json=token_callback)
    requests_mock.get(f"{API_URL}/v3/company/realm-id/query", json=account_callback)

    output = read(get_source(CONFIG), config=CONFIG, catalog=_catalog())

    assert not output.errors
    assert [record.record.data["Id"] for record in output.records] == ["0", "1", "2", "3", "4", "6"]
    assert len(token_requests) == 1
    assert len(account_requests) == 3
    assert account_requests[0].headers["Authorization"] == "Bearer initial-token"
    assert account_requests[2].headers["Authorization"] == "Bearer new-token"


def test_fault_error_message_excludes_detail(requests_mock, get_source):
    requests_mock.get(
        f"{API_URL}/v3/company/realm-id/query",
        status_code=400,
        json={
            "Fault": {
                "Error": [{"Message": "m", "Detail": "d", "code": "4000"}],
                "type": "ValidationFault",
            }
        },
    )

    source = get_source(CONFIG)
    output = read(source, config=CONFIG, catalog=_catalog())

    assert output.errors
    message = output.errors[-1].trace.error.message
    assert "ValidationFault" in message
    assert "4000" in message

    response = requests.Response()
    response.status_code = 400
    response._content = json.dumps(
        {
            "Fault": {
                "Error": [{"Message": "m", "Detail": "d", "code": "4000"}],
                "type": "ValidationFault",
            }
        }
    ).encode()
    error_handler = source.streams(CONFIG)[0]._stream_partition_generator._partition_factory._retriever.requester.error_handler
    resolution = error_handler.interpret_response(response)
    assert resolution.error_message == ("QuickBooks API request failed. Fault type: ValidationFault, code: 4000, message: m")
    assert "Detail" not in resolution.error_message


def test_empty_fault_body_is_null_safe(requests_mock, get_source):
    requests_mock.get(
        f"{API_URL}/v3/company/realm-id/query",
        status_code=400,
        json={},
    )

    output = read(get_source(CONFIG), config=CONFIG, catalog=_catalog())

    assert output.errors
    assert "status code '400'" in output.errors[-1].trace.error.message

    response = requests.Response()
    response.status_code = 400
    response._content = b"[]"
    source = get_source(CONFIG)
    error_handler = source.streams(CONFIG)[0]._stream_partition_generator._partition_factory._retriever.requester.error_handler
    resolution = error_handler.interpret_response(response)
    assert "unknown" in resolution.error_message


def test_invalid_grant_is_a_config_error(requests_mock, get_source):
    requests_mock.post(
        TOKEN_URL,
        status_code=400,
        json={"error": "invalid_grant"},
    )

    source = get_source(CONFIG)
    authenticator = source.streams(CONFIG)[0]._stream_partition_generator._partition_factory._retriever.requester.authenticator

    with pytest.raises(AirbyteTracedException) as raised:
        authenticator.refresh_and_set_access_token()

    assert raised.value.failure_type == FailureType.config_error
    assert "re-authenticate" in raised.value.message.lower()


def test_token_expiry_date_is_optional_and_hidden(connector_path):
    import yaml

    manifest = yaml.safe_load((connector_path / "manifest.yaml").read_text())
    specification = manifest["spec"]["connection_specification"]

    assert "token_expiry_date" not in specification["required"]
    assert specification["properties"]["token_expiry_date"]["airbyte_hidden"] is True
