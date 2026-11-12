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


AZURE_EXPIRED_LINK = (
    "<Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2024-05-06T00:00:00Z] - Expiry [2024-05-06T00:10:00Z] - Current [2024-05-06T01:00:00Z]"
    "</AuthenticationErrorDetail></Error>"
)


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "product_dimension_performance_report_daily"])
@pytest.mark.parametrize(
    "status,body,failure_type",
    [
        (403, AZURE_EXPIRED_LINK, FailureType.transient_error),
        (403, "<Error><Code>AuthorizationFailure</Code></Error>", FailureType.config_error),
        (403, "", FailureType.config_error),
        (
            403,
            "<Error><Code>AuthenticationFailed</Code>"
            "<AuthenticationErrorDetail>Signature did not match</AuthenticationErrorDetail></Error>",
            FailureType.config_error,
        ),
    ],
    ids=["expired", "other_forbidden", "empty_forbidden", "other_authentication_failure"],
)
def test_download_error(stream_name, status, body, failure_type):
    helper = (
        test_bulk_stream.TestBulkStream()
        if stream_name == "app_install_ads"
        else test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
    )
    helper.setUp()
    try:
        if stream_name == "app_install_ads":
            helper.download_entity = "AppInstallAds"
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
            download_request = RequestBuilder().build_report_url()
        helper.http_mocker.get(download_request, HttpResponse(body, status, headers={"Content-Type": "application/xml"}))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(helper._config, catalog, expecting_exception=True)
        helper.http_mocker.assert_number_of_calls(download_request, 1)
        error = next(message.trace.error for message in output.errors if message.trace.error.stream_descriptor)
        assert error.failure_type == failure_type, error.message
        if failure_type == FailureType.transient_error:
            assert error.message == "The Bing Ads download link expired before the file could be downloaded. The sync will retry."
        elif status == 403:
            assert "You don't have permission to access this resource" in error.message
    finally:
        helper.tearDown()
