# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from io import BytesIO
from pathlib import Path

import pytest
import test_bulk_stream
import test_product_dimension_performance_report
import yaml
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from requests import Response

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models import CompositeErrorHandler
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_RESPONSE = (
    '<?xml version="1.0" encoding="utf-8"?>'
    "<Error><Code>AuthenticationFailed</Code>"
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame</AuthenticationErrorDetail></Error>"
)
FORBIDDEN_MESSAGE = "Forbidden. You don't have permission to access this resource."


@pytest.fixture(params=["bulk", "report"])
def download_stream(request):
    if request.param == "bulk":
        helper = test_bulk_stream.TestBulkStream()
        helper.download_entity = "AppInstallAds"
        helper.stream_name = "app_install_ads"
    else:
        helper = test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
    helper.setUp()
    try:
        if request.param == "bulk":
            helper.mock_user_query_api(response_template="user_query")
            helper.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            helper.mock_bulk_download_request()
            helper.mock_bulk_download_status_query()
            download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        else:
            helper.mock_report_apis()
            download_request = RequestBuilder(resource="").build_report_url()
        yield helper, download_request
    finally:
        helper.tearDown()


@freeze_time("2024-05-06")
@pytest.mark.parametrize(
    "body,headers,failure_type,message",
    [
        (
            EXPIRED_RESPONSE,
            {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
            FailureType.transient_error,
            "Bing Ads file download URL is expired.",
        ),
        ("", {}, FailureType.config_error, FORBIDDEN_MESSAGE),
        (
            "<Error><Code>AuthenticationFailed</Code><Message>Invalid signature.</Message></Error>",
            {"x-ms-error-code": "AuthenticationFailed"},
            FailureType.config_error,
            FORBIDDEN_MESSAGE,
        ),
        (
            "<Error><Code>AuthorizationPermissionMismatch</Code></Error>",
            {"x-ms-error-code": "AuthorizationPermissionMismatch"},
            FailureType.config_error,
            FORBIDDEN_MESSAGE,
        ),
    ],
    ids=["expired-sas", "plain-forbidden", "invalid-signature", "other-azure-forbidden"],
)
def test_download_error_trace(download_stream, body, headers, failure_type, message):
    helper, download_request = download_stream
    helper.http_mocker.get(download_request, HttpResponse(body, 403, headers))
    catalog = CatalogBuilder().with_stream(helper.stream_name, SyncMode.full_refresh).build()

    output = read_helper(helper._config, catalog, expecting_exception=True)

    assert not output.records
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == failure_type
    assert error.message == message
    if body:
        assert body in error.internal_message


@pytest.mark.parametrize(
    "status,body,action",
    [
        (200, "Id,Name\n1,Test", ResponseAction.SUCCESS),
        (200, "", ResponseAction.SUCCESS),
        (429, "", ResponseAction.RATE_LIMITED),
        (500, "", ResponseAction.RETRY),
    ],
)
def test_download_error_handler_preserves_default_actions(status, body, action):
    manifest = yaml.safe_load((Path(__file__).parents[2] / "manifest.yaml").read_text())
    handler = ModelToComponentFactory().create_component(
        CompositeErrorHandler, manifest["definitions"]["download_error_handler"], config={}
    )
    response = Response()
    response.status_code = status
    response.raw = BytesIO(body.encode())

    assert handler.interpret_response(response).response_action == action
    if status == 200:
        assert response.raw.read() == body.encode()
