# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_bulk_stream
import test_hourly_reports
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


@pytest.fixture
def download_read():
    helper = test_bulk_stream.TestBulkStream()
    helper.download_entity = "AppInstallAds"
    helper.setUp()
    try:
        yield helper
    finally:
        helper.tearDown()


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["age_gender_audience_report_hourly", "app_install_ads"])
@pytest.mark.parametrize(
    "azure_message, failure_type",
    [
        (
            "Server failed to authenticate the request. Signature not valid in the specified time frame: "
            "Start [2024-05-06T00:00:00Z] - Expiry [2024-05-06T00:10:00Z] - Current [2024-05-06T00:11:00Z]",
            FailureType.transient_error,
        ),
        ("Server failed to authenticate the request. The MAC signature found in the HTTP request is not valid.", FailureType.config_error),
        ("", FailureType.config_error),
    ],
    ids=["expired-sas", "other-authentication-failure", "empty-body"],
)
def test_download_error_trace(download_read, stream_name, azure_message, failure_type):
    helper = download_read
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
        test_hourly_reports.TestAgeGenderAudienceReportHourlyStream.mock_report_apis(helper)
        download_request = RequestBuilder().build_report_url()

    body = (
        '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>' f"<Message>{azure_message}</Message></Error>"
        if azure_message
        else ""
    )
    helper.http_mocker.get(download_request, HttpResponse(body, 403, headers={"Content-Type": "application/xml"}))
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read_helper(helper._config, catalog, expecting_exception=True)

    assert not output.records
    errors = [message.trace.error for message in output.errors if message.trace.error.stream_descriptor]
    assert errors
    error = errors[0]
    assert error.stream_descriptor.name == stream_name
    assert error.failure_type == failure_type
    if failure_type == FailureType.transient_error:
        assert error.message == "The Bing Ads download link expired before the file could be downloaded. The sync will retry."
    else:
        assert error.message == "Forbidden. You don't have permission to access this resource."
