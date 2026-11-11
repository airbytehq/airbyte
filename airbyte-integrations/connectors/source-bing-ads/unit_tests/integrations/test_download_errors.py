# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_bulk_stream as bulk_tests
import test_hourly_reports as report_tests
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.request import HttpRequest


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_kind", ["report", "bulk"])
@pytest.mark.parametrize(
    "body, expired",
    [
        (
            '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
            "<Message>Server failed to authenticate the request. Make sure the value of Authorization "
            "header is formed correctly including the signature.</Message>"
            "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
            "Start [Tue, 10 Nov 2026 10:00:00 GMT] - Expiry [Tue, 10 Nov 2026 10:10:00 GMT] - "
            "Current [Tue, 10 Nov 2026 10:11:00 GMT]</AuthenticationErrorDetail></Error>",
            True,
        ),
        ("<Error><Code>AuthenticationFailed</Code><Message>Server failed to authenticate the request.</Message></Error>", True),
        ("<Error><Message>Signature not valid in the specified time frame</Message></Error>", True),
        ("<Error><Code>AuthorizationPermissionMismatch</Code><Message>Permission denied</Message></Error>", False),
        ("", False),
    ],
    ids=["azure_expired_sas", "authentication_failed", "signature_time_frame", "other_forbidden", "empty_forbidden"],
)
def test_download_403(stream_kind, body, expired):
    with HttpMocker() as http_mocker:
        if stream_kind == "report":
            helper = report_tests.TestAgeGenderAudienceReportHourlyStream()
            stream_name = helper.stream_name
            download_request = RequestBuilder().build_report_url()
        else:
            helper = bulk_tests.TestBulkStream()
            helper.download_entity = "AppInstallAds"
            stream_name = "app_install_ads"
            download_request = HttpRequest("https://bulk.api.bingads.microsoft.com/path/to/bulk/resultquery/url")
        helper._http_mocker = http_mocker
        helper._auth_client(http_mocker)
        if stream_kind == "report":
            helper.mock_report_apis()
        else:
            helper.mock_user_query_api("user_query")
            helper.mock_accounts_search_api(
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
                response_template="accounts_search_for_report",
            )
            helper.mock_bulk_download_request()
            helper.mock_bulk_download_status_query()
        http_mocker.get(download_request, HttpResponse(body, 403, headers={"Content-Type": "application/xml"}))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(helper._config, catalog, expecting_exception=True)
        http_mocker.assert_number_of_calls(download_request, 1)
        errors = [trace.trace.error for trace in output.trace_messages if trace.trace.error]
        assert errors
        error = errors[0]
        print(f"DOWNLOAD ERROR: failure_type={error.failure_type.value}; message={error.message}")
        assert error.failure_type == (FailureType.transient_error if expired else FailureType.config_error)
        assert error.message == (
            "The Bing Ads download link expired before the file could be downloaded. The sync will retry."
            if expired
            else "Forbidden. You don't have permission to access this resource."
        )
