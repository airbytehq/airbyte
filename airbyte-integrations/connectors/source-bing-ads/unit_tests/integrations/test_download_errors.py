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


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_kind", ["bulk", "report"])
@pytest.mark.parametrize("expired", [True, False], ids=["expired_sas", "permission_denied"])
def test_download_error_classification(stream_kind, expired):
    test = (
        test_bulk_stream.TestBulkStream()
        if stream_kind == "bulk"
        else test_product_dimension_performance_report.TestProductDimensionPerformanceReportDailyStream()
    )
    test.setUp()
    try:
        if stream_kind == "bulk":
            test.download_entity = "AppInstallAds"
            stream_name = "app_install_ads"
            test.mock_user_query_api(response_template="user_query")
            test.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            test.mock_bulk_download_request()
            test.mock_bulk_download_status_query()
            request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        else:
            stream_name = test.stream_name
            test.mock_report_apis()
            request = RequestBuilder().build_report_url()

        code = "AuthenticationFailed" if expired else "AuthorizationPermissionMismatch"
        message = (
            "Signature not valid in the specified time frame: Start [2024-05-06] - Expiry [2024-05-06] - Current [2024-05-07]"
            if expired
            else "This request is not authorized to perform this operation using this permission."
        )
        test.http_mocker.get(
            request,
            HttpResponse(
                f'<?xml version="1.0" encoding="utf-8"?><Error><Code>{code}</Code><Message>{message}</Message></Error>',
                403,
                headers={"x-ms-error-code": code, "Content-Type": "application/xml"},
            ),
        )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(test._config, catalog, expecting_exception=True)

        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type.value == ("transient_error" if expired else "config_error")
        assert error.message == (
            "Bing Ads file download URL is expired." if expired else "Forbidden. You don't have permission to access this resource."
        )
    finally:
        test.tearDown()
