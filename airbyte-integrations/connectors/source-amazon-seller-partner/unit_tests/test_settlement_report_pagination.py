#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""
Tests that the flat_file_settlement_v2_helper stream (the parent stream that lists
GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE reports via GET /reports/2021-06-30/reports)
sends `nextToken` as the *only* query parameter on paginated requests.

Amazon SP-API rejects a getReports call that combines nextToken with any other
parameter (400 InvalidInput: "NextToken cannot be specified with other input parameters").
"""

import pytest
import requests
from freezegun import freeze_time

from .conftest import get_source


BASE_CONFIG = {
    "refresh_token": "Atzr|IwEBIP-abc123",
    "lwa_app_id": "amzn1.application-oa2-client.abc123",
    "lwa_client_secret": "abc123",
    "aws_environment": "SANDBOX",
    "region": "US",
    "account_type": "Seller",
    "replication_start_date": "2025-05-01T00:00:00Z",
}

REPORTS_URL = "https://sandbox.sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports"
NEXT_TOKEN = "next-token-abc"


def _report(report_id: str) -> dict:
    return {
        "reportId": report_id,
        "reportType": "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE",
        "processingStatus": "DONE",
        "createdTime": "2025-05-02T00:00:00Z",
        "dataStartTime": "2025-05-01T00:00:00Z",
        "dataEndTime": "2025-05-02T00:00:00Z",
    }


@pytest.mark.parametrize("token_key", ["nextToken", "NextToken"])
@freeze_time("2025-06-15T12:00:00Z")
def test_settlement_helper_paginated_request_sends_only_next_token(requests_mock, mocker, token_key):
    # Bypass requests_cache so requests_mock can intercept all HTTP calls.
    mocker.patch(
        "requests_cache.CachedSession.send",
        lambda self, request, **kwargs: requests.Session.send(self, request, **kwargs),
    )
    requests_mock.post(
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
        status_code=200,
    )

    def reports_callback(request, context):
        context.status_code = 200
        if "nexttoken" in request.qs:
            return {"reports": [_report("report-2")]}
        return {"reports": [_report("report-1")], token_key: NEXT_TOKEN}

    requests_mock.get(REPORTS_URL, json=reports_callback)

    source = get_source(config=BASE_CONFIG, state=None)
    streams = source.streams(source._config)
    stream = next((s for s in streams if s.name == "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"), None)
    assert stream is not None, "Stream 'GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE' not found"

    partitions = [partition.to_slice() for partition in stream.generate_partitions()]
    assert sorted(p["reportId"] for p in partitions) == ["report-1", "report-2"]

    reports_requests = [r for r in requests_mock.request_history if r.url.startswith(REPORTS_URL) and r.method == "GET"]
    assert len(reports_requests) == 2, f"Expected exactly two getReports calls, got {len(reports_requests)}"

    first_request, second_request = reports_requests
    # requests_mock lowercases query parameter names and values
    assert first_request.qs["reporttypes"] == ["get_v2_settlement_report_data_flat_file"]
    assert first_request.qs["pagesize"] == ["100"]
    assert first_request.qs["createdsince"] == ["2025-05-01t00:00:00z"]
    assert "createduntil" in first_request.qs
    assert "nexttoken" not in first_request.qs

    assert second_request.qs == {
        "nexttoken": [NEXT_TOKEN.lower()]
    }, f"Paginated getReports request must send nextToken as the only query parameter, got: {second_request.qs}"
