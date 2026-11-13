# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_bulk_stream
import test_product_dimension_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SIGNATURE = """<?xml version="1.0" encoding="utf-8"?>
<Error><Code>AuthenticationFailed</Code>
<Message>Server failed to authenticate the request.</Message>
<AuthenticationErrorDetail>Signature not valid in the specified time frame:
Start [Thu, 12 Nov 2026 00:00:00 GMT] - Expiry [Thu, 12 Nov 2026 00:10:00 GMT] - Current [Thu, 12 Nov 2026 00:11:00 GMT]
</AuthenticationErrorDetail></Error>"""


@pytest.mark.parametrize("stream_kind", ["bulk", "report"])
@pytest.mark.parametrize(
    "body,headers,failure_type,message",
    [
        pytest.param(
            EXPIRED_SIGNATURE,
            {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
            FailureType.transient_error,
            "Bing Ads file download URL is expired.",
            id="expired-signature",
        ),
        pytest.param(
            "Forbidden",
            {},
            FailureType.config_error,
            "You don't have permission to access this resource.",
            id="plain-forbidden",
        ),
        pytest.param(
            EXPIRED_SIGNATURE,
            {},
            FailureType.config_error,
            "You don't have permission to access this resource.",
            id="missing-azure-header",
        ),
        pytest.param(
            "",
            {"x-ms-error-code": "AuthenticationFailed"},
            FailureType.config_error,
            "You don't have permission to access this resource.",
            id="empty-body",
        ),
        pytest.param(
            "<Error><Code>AuthenticationFailed</Code><Message>Signature did not match.</Message></Error>",
            {"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"},
            FailureType.config_error,
            "You don't have permission to access this resource.",
            id="other-authentication-failure",
        ),
    ],
)
@freeze_time("2024-05-06")
def test_download_error_trace(stream_kind, body, headers, failure_type, message):
    if stream_kind == "bulk":
        helper = test_bulk_stream.TestBulkStream()
        helper.download_entity = "Budgets"
        stream_name = "budget"
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
    else:
        helper = test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
        stream_name = helper.stream_name
        download_request = RequestBuilder().build_report_url()

    helper.setUp()
    try:
        if stream_kind == "bulk":
            helper.mock_user_query_api(response_template="user_query")
            helper.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            helper.mock_bulk_download_request()
            helper.mock_bulk_download_status_query()
        else:
            helper.mock_report_apis()

        helper.http_mocker.get(download_request, HttpResponse(body, 403, headers))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(helper._config, catalog, expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == failure_type
        if failure_type == FailureType.transient_error:
            assert output.errors[0].trace.error.message == message
        else:
            assert message in output.errors[0].trace.error.message
        assert not output.records
    finally:
        helper.tearDown()
