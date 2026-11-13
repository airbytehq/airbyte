# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
import json

import pytest
import test_product_dimension_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import REPORT_URL, RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


@pytest.fixture
def download_test():
    test = TestBulkStream()
    test.download_entity = "Keywords"
    test.setUp()
    yield test
    test.tearDown()


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["keywords", "product_dimension_performance_report_daily"])
@pytest.mark.parametrize(
    "headers,body,failure_type,message",
    [
        (
            {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
            "<Error><Code>AuthenticationFailed</Code><AuthenticationErrorDetail>"
            "Signature not valid in the specified time frame: Start [2024-05-06T00:00:00Z] - "
            "Expiry [2024-05-06T00:10:00Z] - Current [2024-05-06T00:11:00Z]"
            "</AuthenticationErrorDetail></Error>",
            FailureType.transient_error,
            "Bing Ads file download URL is expired.",
        ),
        (
            {},
            "",
            FailureType.config_error,
            "Forbidden. You don't have permission to access this resource.",
        ),
        (
            {"x-ms-error-code": "AuthorizationPermissionMismatch", "Content-Type": "application/xml"},
            "<Error><Code>AuthorizationPermissionMismatch</Code></Error>",
            FailureType.config_error,
            "Forbidden. You don't have permission to access this resource.",
        ),
    ],
)
def test_download_forbidden(download_test, stream_name, headers, body, failure_type, message):
    test = download_test
    if stream_name == "keywords":
        test.mock_user_query_api(response_template="user_query")
        test.mock_accounts_search_api(
            response_template="accounts_search_for_report",
            body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
        )
        test.mock_bulk_download_request()
        status = find_template(resource="bulk_status", execution_folder=__file__)
        status["ResultFileUrl"] = REPORT_URL
        test.http_mocker.post(
            RequestBuilder(resource="Bulk/v13/BulkDownloadStatus/Query", api="bulk")
            .with_body('{"RequestId": "TestDownloadRequestId"}')
            .build(),
            HttpResponse(json.dumps(status)),
        )
    else:
        report_test = test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
        report_test._http_mocker = test.http_mocker
        report_test.mock_report_apis()
    test.http_mocker.get(RequestBuilder().build_report_url(), HttpResponse(body, 403, headers))
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    config = {**test._config, "reports_start_date": "2024-01-01"}
    output = read_helper(config, catalog, expecting_exception=True)

    errors = [entry.trace.error for entry in output.errors if entry.trace.error.stream_descriptor]
    assert errors
    assert errors[0].failure_type == failure_type
    assert errors[0].message == message
