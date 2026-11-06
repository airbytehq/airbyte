# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_hourly_reports
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from test_bulk_stream import TestBulkStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_LINK_MESSAGE = (
    "The download link expired before the file could be downloaded. Please retry the sync to obtain a fresh link; a retry should succeed."
)
EXPIRED_SAS = (
    "<Error><Code>AuthenticationFailed</Code>"
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2026-11-05T00:00:00Z] - Expiry [2026-11-05T00:10:00Z] - Current [2026-11-05T00:11:00Z]"
    "</AuthenticationErrorDetail></Error>"
)


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_kind", ["report", "bulk"])
@pytest.mark.parametrize(
    "body,failure_type,message",
    [
        pytest.param(EXPIRED_SAS, "transient_error", EXPIRED_LINK_MESSAGE, id="expired-sas"),
        pytest.param(
            "<Error><Code>AuthorizationPermissionMismatch</Code><Message>This request is not authorized.</Message></Error>",
            "config_error",
            "Forbidden. You don't have permission",
            id="permission-denied",
        ),
        pytest.param("", "config_error", "Forbidden. You don't have permission", id="empty-body"),
        pytest.param(
            "<Error><Code>AuthenticationFailed</Code><Message>Invalid signature.</Message></Error>",
            "config_error",
            "Forbidden. You don't have permission",
            id="other-authentication-failure",
        ),
    ],
)
def test_download_error_classification(stream_kind, body, failure_type, message):
    helper = test_hourly_reports.TestAgeGenderAudienceReportHourlyStream() if stream_kind == "report" else TestBulkStream()
    helper.setUp()
    try:
        if stream_kind == "report":
            helper.mock_report_apis()
            stream_name = helper.stream_name
            download_request = RequestBuilder().build_report_url()
        else:
            helper.download_entity = "AppInstallAds"
            helper.mock_user_query_api("user_query")
            helper.mock_accounts_search_api(
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
                response_template="accounts_search_for_report",
            )
            helper.mock_bulk_download_request()
            helper.mock_bulk_download_status_query()
            stream_name = "app_install_ads"
            download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        helper.http_mocker.get(download_request, HttpResponse(body, 403, headers={"Content-Type": "application/xml"}))
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(helper._config, catalog, expecting_exception=True)
        errors = [trace.trace.error for trace in output.errors]
        assert errors
        assert errors[0].failure_type.value == failure_type
        assert message in errors[0].message
    finally:
        helper.tearDown()
