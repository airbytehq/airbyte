# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_app_install_ad_labels_stream as bulk_scenarios
import test_hourly_reports as report_scenarios
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SAS_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    '<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly '
    'including the signature.\nRequestId:test-request\nTime:2024-05-06T00:00:00Z</Message>'
    '<AuthenticationErrorDetail>Signature not valid in the specified time frame: '
    'Start [2024-05-05T23:00:00Z] - Expiry [2024-05-05T23:10:00Z] - Current [2024-05-06T00:00:00Z]'
    '</AuthenticationErrorDetail></Error>'
)


@pytest.mark.parametrize(
    "scenario_class",
    [report_scenarios.TestAdPerformanceReportHourlyStream, bulk_scenarios.TestAppInstallAdLabelsStream],
    ids=["report", "bulk"],
)
@pytest.mark.parametrize(
    "body",
    [EXPIRED_SAS_BODY, "", "<Error><Code>AuthorizationFailure</Code></Error>"],
    ids=["expired", "empty", "permission"],
)
@freeze_time("2024-05-06")
def test_download_forbidden(scenario_class, body):
    scenario = scenario_class()
    scenario.setUp()
    try:
        if scenario_class is report_scenarios.TestAdPerformanceReportHourlyStream:
            scenario.mock_report_apis()
            download_request = RequestBuilder(resource="").build_report_url()
        else:
            scenario.mock_user_query_api(response_template="user_query")
            scenario.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            scenario.mock_bulk_download_request()
            scenario.mock_bulk_download_status_query()
            download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        scenario.http_mocker.get(download_request, HttpResponse(body, 403))
        catalog = CatalogBuilder().with_stream(scenario.stream_name, SyncMode.full_refresh).build()
        output = read_helper(scenario._config, catalog, expecting_exception=True)
        scenario.http_mocker.assert_number_of_calls(download_request, 1)
        errors = [trace.trace.error for trace in output.errors]
        assert errors
        error = errors[0]
        assert error.failure_type.value == "transient_error"
        assert error.message == (
            "The Bing Ads file download link was rejected (HTTP 403), most likely because it expired before the download started. "
            "The sync will retry."
        )
    finally:
        scenario.tearDown()
