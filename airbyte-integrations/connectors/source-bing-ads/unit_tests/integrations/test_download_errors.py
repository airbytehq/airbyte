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


EXPIRED_XML = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request. Make sure the value of Authorization header "
    "is formed correctly including the signature.\nRequestId:test\nTime:2024-05-06T00:00:00Z</Message>"
    "<AuthenticationErrorDetail>{detail}</AuthenticationErrorDetail></Error>"
)


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["app_install_ads", "product_dimension_performance_report_hourly"])
@pytest.mark.parametrize(
    "body, failure_type",
    [
        (
            EXPIRED_XML.format(detail="Signed expiry time [2024-05-05] must be after signed start time [2024-05-06]"),
            FailureType.transient_error,
        ),
        (
            EXPIRED_XML.format(detail="Signature not valid in the specified time frame"),
            FailureType.transient_error,
        ),
        ("<Error><Code>AuthorizationFailure</Code><Message>Forbidden</Message></Error>", FailureType.config_error),
        ("", FailureType.config_error),
    ],
    ids=["expiry_before_start", "outside_time_frame", "other_forbidden", "empty_forbidden"],
)
def test_download_error(stream_name, body, failure_type):
    if stream_name == "app_install_ads":
        helper = test_bulk_stream.TestBulkStream()
        helper.download_entity = "AppInstallAds"
    else:
        helper = test_product_dimension_performance_report.TestProductDimensionPerformanceReportHourlyStream()
    helper.setUp()
    try:
        http_mocker = helper.http_mocker
        if stream_name == "app_install_ads":
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
        http_mocker.get(download_request, HttpResponse(body, 403))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

        output = read_helper(helper._config, catalog, expecting_exception=True)

        http_mocker.assert_number_of_calls(download_request, 1)
        assert not output.records
        stream_errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
        assert len(stream_errors) == 1
        assert stream_errors[0].failure_type == failure_type
        if failure_type == FailureType.transient_error:
            assert stream_errors[0].message == (
                "The Bing Ads download link expired before the file could be downloaded. The sync will retry."
            )
        else:
            assert stream_errors[0].message == ("Forbidden. You don't have permission to access this resource.")
    finally:
        helper.tearDown()
