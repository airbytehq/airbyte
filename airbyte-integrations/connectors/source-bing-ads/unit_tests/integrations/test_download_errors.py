# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import test_bulk_stream
import test_product_search_query_performance_report
from freezegun import freeze_time
from protocol_helpers import read_helper
from request_builder import RequestBuilder

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpResponse


EXPIRED_SIGNATURE = (
    '<?xml version="1.0" encoding="utf-8"?><Error><Code>AuthenticationFailed</Code>'
    "<Message>Server failed to authenticate the request.</Message>"
    "<AuthenticationErrorDetail>Signature not valid in the specified time frame: "
    "Start [2026-01-01] - Expiry [2026-01-02] - Current [2026-01-03]"
    "</AuthenticationErrorDetail></Error>"
)


@freeze_time("2024-05-06")
@pytest.mark.parametrize("stream_name", ["keywords", "product_search_query_performance_report_daily"])
@pytest.mark.parametrize("expired", [True, False], ids=["expired_signature", "plain_forbidden"])
def test_download_error(stream_name, expired):
    base = (
        test_bulk_stream.TestBulkStream()
        if stream_name == "keywords"
        else test_product_search_query_performance_report.TestProductSearchQueryPerformanceReportDailyStream()
    )
    base.setUp()
    try:
        if stream_name == "keywords":
            base.mock_user_query_api("user_query")
            base.mock_accounts_search_api(
                body=b'{"PageInfo": {"Index": 0, "Size": 1000}, "Predicates": [{"Field": "UserId", "Operator": "Equals", "Value": "123456789"}], "ReturnAdditionalFields": "TaxCertificate,AccountMode"}',
                response_template="accounts_search_for_report",
            )
            base.download_entity = "Keywords"
            base.mock_bulk_download_request()
            base.mock_bulk_download_status_query()
            download_request = RequestBuilder(resource="path/to/bulk/resultquery/url", api="bulk").build()
        else:
            base.mock_report_apis()
            download_request = RequestBuilder(resource="").build_report_url()
        base.http_mocker.get(
            download_request,
            HttpResponse(
                EXPIRED_SIGNATURE if expired else "Forbidden",
                403,
                headers={"x-ms-error-code": "AuthenticationFailed", "Content-Type": "application/xml"} if expired else {},
            ),
        )
        config = base._config
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read_helper(config, catalog, expecting_exception=True)
        errors = [message.trace.error for message in output.errors]
        assert errors
        expected_failure = FailureType.transient_error if expired else FailureType.config_error
        expected_message = (
            "Bing Ads file download URL is expired."
            if expired
            else "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource."
        )
        assert any(error.failure_type == expected_failure and expected_message in error.message for error in errors), errors
        assert not output.records
    finally:
        base.tearDown()
