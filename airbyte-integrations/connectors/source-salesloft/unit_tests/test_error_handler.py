# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_CONFIG = {"credentials": {"auth_type": "api_key", "api_key": "test-key"}, "start_date": "2024-01-01T00:00:00Z"}
_REQUEST = HttpRequest(
    url="https://api.salesloft.com/v2/activities/emails",
    query_params=ANY_QUERY_PARAMS,
    headers={"Authorization": "Bearer test-key"},
)
_ERROR_MESSAGE = (
    "Scoped Fields require a Premier Salesloft Plan - Requested "
    "scoped field(s) could not be returned, required scope access not included"
)


def _read_emails(expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("emails_scoped_fields", SyncMode.full_refresh).build()
    return read(get_source(), _CONFIG, catalog, expecting_exception=expecting_exception)


class TestSalesloftErrorHandler(TestCase):
    @HttpMocker()
    def test_missing_scope_fails_with_configured_message(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REQUEST, HttpResponse(body=json.dumps({"error": "required scope access not included"}), status_code=403))

        output = _read_emails(expecting_exception=True)

        assert output.errors
        assert any(_ERROR_MESSAGE in error.trace.error.message for error in output.errors)
        assert not output.records
        http_mocker.assert_number_of_calls(_REQUEST, 1)

    @HttpMocker()
    def test_normal_response_yields_records(self, http_mocker: HttpMocker) -> None:
        record = {"id": 1, "subject": "Test email", "body": "Hello"}
        http_mocker.get(
            _REQUEST, HttpResponse(body=json.dumps({"data": [record], "metadata": {"paging": {"next_page": None}}}), status_code=200)
        )

        output = _read_emails()

        assert [message.record.data for message in output.records] == [record]
        assert not output.errors

    @HttpMocker()
    def test_empty_response_yields_no_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_REQUEST, HttpResponse(body=json.dumps({"data": [], "metadata": {"paging": {"next_page": None}}}), status_code=200))

        output = _read_emails()

        assert not output.records
        assert not output.errors


def test_requester_uses_default_error_handler() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    handler = manifest["definitions"]["streams"]["emails_scoped_fields"]["retriever"]["requester"]["error_handler"]

    assert handler["type"] == "DefaultErrorHandler"
