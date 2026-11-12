# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_app_install_ads_stream
import test_hourly_reports
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SAS_RESPONSE = """<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>
<Message>Server failed to authenticate the request. Make sure the value of Authorization header is formed correctly including the signature.
RequestId:test-request-id
Time:2024-05-06T00:00:00Z</Message>
<AuthenticationErrorDetail>Signature not valid in the specified time frame: Start [2024-05-05T23:00:00Z] - Expiry [2024-05-05T23:10:00Z] - Current [2024-05-06T00:00:00Z]</AuthenticationErrorDetail></Error>"""


@pytest.fixture(params=["bulk", "report"])
def expired_download(request):
    if request.param == "bulk":
        stream = test_app_install_ads_stream.TestAppInstallAdsStream()
        download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
    else:
        stream = test_hourly_reports.TestAgeGenderAudienceReportHourlyStream()
        download_request = RequestBuilder(resource="").build_report_url()
    stream.setUp()
    try:
        if request.param == "bulk":
            stream.mock_user_query_api(response_template="user_query")
            stream.mock_accounts_search_api(
                response_template="accounts_search_for_report",
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
            )
            stream.mock_bulk_download_request()
            stream.mock_bulk_download_status_query()
        else:
            stream.mock_report_apis()
        stream.http_mocker.get(download_request, HttpResponse(EXPIRED_SAS_RESPONSE, 403, headers={"Content-Type": "application/xml"}))
        yield stream
    finally:
        stream.tearDown()


@freeze_time("2024-05-06")
def test_expired_download_emits_retryable_error(expired_download):
    stream = expired_download
    catalog = CatalogBuilder().with_stream(stream.stream_name, SyncMode.full_refresh).build()
    output = read_helper(stream._config, catalog, expecting_exception=True)

    errors = [trace.trace.error for trace in output.errors]
    assert errors
    assert errors[0].failure_type == FailureType.transient_error
    assert errors[0].message == (
        f"The Bing Ads download link for stream '{stream.stream_name}' expired before the file could be downloaded. The sync will retry."
    )
