# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_budget_stream
import test_product_search_query_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_LINK_XML = (
    "<Error><Code>AuthenticationFailed</Code>"
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header "
    "is formed correctly including the signature.\nRequestId:test-request Time:2024-05-06T00:00:00Z</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2024-05-05T00:00:00Z] - Expiry [2024-05-05T00:10:00Z] - Current [2024-05-06T00:00:00Z]"
    "</AuthenticationErrorDetail></Error>"
)
PERMISSION_XML = (
    "<Error><Code>AuthorizationPermissionMismatch</Code>"
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)
DEFAULT_FORBIDDEN_MESSAGE = "Forbidden. You don't have permission to access this resource."


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["product_search_query_performance_report_daily", "budget"])
@pytest.mark.parametrize(
    "body,failure_type",
    [(EXPIRED_LINK_XML, FailureType.transient_error), (PERMISSION_XML, FailureType.config_error)],
    ids=["expired_link", "permission_denied"],
)
def test_download_error(stream_name, body, failure_type):
    base = (
        test_budget_stream.TestBudgetStream()
        if stream_name == "budget"
        else test_product_search_query_performance_report.TestProductSearchQueryPerformanceReportDailyStream()
    )
    base.setUp()
    try:
        config = base._config
        if stream_name == "budget":
            base.mock_user_query_api("user_query")
            base.mock_accounts_search_api(
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
                response_template="accounts_search_for_report",
            )
            base.mock_bulk_download_request()
            base.mock_bulk_download_status_query()
            download = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        else:
            base.mock_report_apis()
            download = RequestBuilder().build_report_url()
        base.http_mocker.get(download, HttpResponse(body, 403))

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(config, catalog, expecting_exception=True)

        base.http_mocker.assert_number_of_calls(download, 1)
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == failure_type
        expected_message = (
            f"The Bing Ads download link for stream '{stream_name}' expired before the file could be downloaded. The sync will retry."
            if failure_type == FailureType.transient_error
            else DEFAULT_FORBIDDEN_MESSAGE
        )
        assert error.message == expected_message
    finally:
        base.tearDown()
