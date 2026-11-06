# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_bulk_stream
import test_product_dimension_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SIGNATURE_XML = (
    "<Error><Code>AuthenticationFailed</Code>"
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2024-05-06T00:00:00Z] - Expiry [2024-05-06T00:10:00Z] - "
    "Current [2024-05-06T00:20:00Z]</AuthenticationErrorDetail></Error>"
)
PERMISSION_XML = (
    "<Error><Code>AuthorizationPermissionMismatch</Code>"
    "<Message>This request is not authorized to perform this operation using this permission.</Message></Error>"
)


@pytest.mark.parametrize("stream_kind", ["report", "bulk"])
@pytest.mark.parametrize(
    "body,failure_type,message",
    [
        (EXPIRED_SIGNATURE_XML, "transient_error", "pre-signed download URL expired before download"),
        (PERMISSION_XML, "config_error", "Forbidden. You don't have permission to access this resource."),
    ],
    ids=["expired-signature", "permission-denied"],
)
@freeze_time("2024-05-06")
def test_download_403(stream_kind, body, failure_type, message):
    helper = (
        test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
        if stream_kind == "report"
        else test_bulk_stream.TestBulkStream()
    )
    helper.setUp()
    try:
        if stream_kind == "report":
            stream_name = helper.stream_name
            helper.mock_report_apis()
            request = RequestBuilder().build_report_url()
        else:
            stream_name = "app_install_ads"
            helper.download_entity = "AppInstallAds"
            helper.mock_user_query_api(response_template="user_query")
            helper.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            helper.mock_bulk_download_request()
            helper.mock_bulk_download_status_query()
            request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        helper.http_mocker.get(request, HttpResponse(body, 403, headers={"Content-Type": "application/xml"}))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(helper._config, catalog, expecting_exception=True)
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type.value == failure_type
        assert message in error.message
        assert not output.records
    finally:
        helper.tearDown()
