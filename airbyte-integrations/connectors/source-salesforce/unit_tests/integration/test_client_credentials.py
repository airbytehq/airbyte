# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from config_builder import ConfigBuilder
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from salesforce_job_response_builder import JobCreateResponseBuilder, JobInfoResponseBuilder
from source_salesforce.api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from integration.utils import create_base_url, given_client_credentials_authentication, given_stream, read


_A_FIELD_NAME = "a_field"
_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_DOMAIN_URL = "https://acme.my.salesforce.com"
_INSTANCE_URL = "https://instance.salesforce.com"
_BASE_URL = create_base_url(_INSTANCE_URL)
_JOB_ID = "a-job-id"
_REST_STREAM_NAME = UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS[0]
_BULK_STREAM_NAME = "a_stream_name"


def _config() -> ConfigBuilder:
    return ConfigBuilder().auth_type("ClientCredentials").domain_url(_DOMAIN_URL).client_id(_CLIENT_ID).client_secret(_CLIENT_SECRET)


def _assert_no_control_messages(output) -> None:
    assert output.get_message_by_types([Type.CONTROL]) == []


class ClientCredentialsReadTest(TestCase):
    @HttpMocker()
    def test_rest_full_refresh_read(self, http_mocker: HttpMocker) -> None:
        given_client_credentials_authentication(http_mocker, _DOMAIN_URL, _CLIENT_ID, _CLIENT_SECRET, _INSTANCE_URL)
        given_stream(http_mocker, _BASE_URL, _REST_STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/queryAll?q=SELECT+{_A_FIELD_NAME}+FROM+{_REST_STREAM_NAME}+"),
            HttpResponse(json.dumps({"records": [{_A_FIELD_NAME: "field_value"}]})),
        )

        output = read(_REST_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.records) == 1
        assert output.records[0].record.data == {_A_FIELD_NAME: "field_value"}
        _assert_no_control_messages(output)

    @HttpMocker()
    def test_bulk_full_refresh_read(self, http_mocker: HttpMocker) -> None:
        given_client_credentials_authentication(http_mocker, _DOMAIN_URL, _CLIENT_ID, _CLIENT_SECRET, _INSTANCE_URL)
        given_stream(http_mocker, _BASE_URL, _BULK_STREAM_NAME, SalesforceDescribeResponseBuilder().field(_A_FIELD_NAME))
        http_mocker.post(
            HttpRequest(
                f"{_BASE_URL}/jobs/query",
                body=json.dumps(
                    {
                        "operation": "queryAll",
                        "query": f"SELECT {_A_FIELD_NAME} FROM {_BULK_STREAM_NAME}",
                        "contentType": "CSV",
                        "columnDelimiter": "COMMA",
                        "lineEnding": "LF",
                    }
                ),
            ),
            JobCreateResponseBuilder().with_id(_JOB_ID).build(),
        )
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"),
            JobInfoResponseBuilder().with_id(_JOB_ID).with_state("JobComplete").build(),
        )
        http_mocker.get(
            HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}/results"),
            HttpResponse(f"{_A_FIELD_NAME}\nfield_value"),
        )
        http_mocker.delete(HttpRequest(f"{_BASE_URL}/jobs/query/{_JOB_ID}"), HttpResponse(""))

        output = read(_BULK_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.records) == 1
        assert output.records[0].record.data == {_A_FIELD_NAME: "field_value"}
        _assert_no_control_messages(output)
