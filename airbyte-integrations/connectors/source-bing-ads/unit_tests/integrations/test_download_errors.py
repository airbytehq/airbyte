# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_app_install_ads_stream as bulk_tests
import test_product_dimension_performance_report as report_tests
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SAS_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<Error>
  <Code>AuthenticationFailed</Code>
  <Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.
RequestId:00000000-0000-0000-0000-000000000000
Time:2024-05-06T00:00:00.0000000Z</Message>
  <AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [Mon, 06 May 2024 00:00:00 GMT] - Expiry [Mon, 06 May 2024 00:10:00 GMT] - Current [Mon, 06 May 2024 00:20:00 GMT]</AuthenticationErrorDetail>
</Error>"""


@freeze_time("2024-05-06")
@pytest.mark.parametrize(
    "stream_test_class",
    [bulk_tests.TestAppInstallAdsStream, report_tests.TestProductDimensionPerformanceReportDailyStream],
    ids=["bulk", "report"],
)
@pytest.mark.parametrize(
    "body,failure_type",
    [
        (EXPIRED_SAS_RESPONSE, FailureType.transient_error),
        ("<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied.</Message></Error>", FailureType.config_error),
        ("", FailureType.config_error),
    ],
    ids=["expired", "permission_denied", "empty"],
)
def test_download_errors(stream_test_class, body, failure_type):
    stream_test = stream_test_class()
    stream_test.setUp()
    try:
        if isinstance(stream_test, bulk_tests.TestAppInstallAdsStream):
            stream_test.mock_user_query_api(response_template="user_query")
            stream_test.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            stream_test.mock_bulk_download_request()
            stream_test.mock_bulk_download_status_query()
            download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        else:
            stream_test.mock_report_apis()
            download_request = RequestBuilder().build_report_url()
        stream_test.http_mocker.get(download_request, HttpResponse(body, 403, headers={"Content-Type": "application/xml"}))
        catalog = CatalogBuilder().with_stream(stream_test.stream_name, SyncMode.full_refresh).build()
        output = read_helper(stream_test._config, catalog, expecting_exception=True)

        assert not output.records
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == failure_type
        if failure_type == FailureType.transient_error:
            assert error.message == (
                f"The Bing Ads download link for stream '{stream_test.stream_name}' expired before the file could be downloaded. "
                "The sync will retry."
            )
        else:
            assert "You don't have permission to access this resource." in error.message
    finally:
        stream_test.tearDown()
