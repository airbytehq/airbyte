# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import test_bulk_stream
import test_product_dimension_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import REPORT_URL, RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.request import HttpRequest


@pytest.fixture(params=["app_install_ads", "product_dimension_performance_report_daily"])
def download_stream(request):
    if request.param == "app_install_ads":
        stream = test_bulk_stream.TestBulkStream()
        stream.download_entity = "AppInstallAds"
    else:
        stream = test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
    stream.setUp()
    try:
        if request.param == "app_install_ads":
            stream.mock_user_query_api("user_query")
            stream.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            stream.mock_bulk_download_request()
            stream.http_mocker.post(
                RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk")
                .with_body('{"RequestId": "TestDownloadRequestId"}')
                .build(),
                HttpResponse(json.dumps({"RequestStatus": "Completed", "ResultFileUrl": REPORT_URL}), 200),
            )
        else:
            stream.mock_report_apis()
        yield request.param, stream
    finally:
        stream.tearDown()


@freeze_time("2024-05-06")
@pytest.mark.parametrize("expired", [True, False], ids=["expired_signature", "permission_denied"])
@pytest.mark.parametrize("initial_status", [403, 429, 500])
def test_download_error_trace(download_stream, expired, initial_status):
    stream_name, stream = download_stream
    body = (
        "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>"
        "Signature not valid in the specified time frame: Start [2024-05-06T00:00:00Z] - "
        "Expiry [2024-05-06T00:10:00Z] - Current [2024-05-06T00:20:00Z]"
        "</AuthenticationErrorDetail></Error>"
        if expired
        else "<Error><Code>AuthorizationPermissionMismatch</Code></Error>"
    )
    responses = [
        HttpResponse(
            body,
            403,
            {"x-ms-error-code": "AuthenticationFailed" if expired else "AuthorizationPermissionMismatch"},
        )
    ]
    if initial_status != 403:
        responses.insert(0, HttpResponse("", initial_status))
    stream.http_mocker.get(HttpRequest(url=REPORT_URL), responses)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read_helper(stream._config, catalog, expecting_exception=True)

    assert not output.records
    error = output.errors[0].trace.error
    assert error.message == (
        "Bing Ads file download URL is expired." if expired else "Forbidden. You don't have permission to access this resource."
    )
    assert error.failure_type == (FailureType.transient_error if expired else FailureType.config_error)
