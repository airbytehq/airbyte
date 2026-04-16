#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""
Tests that the settlement report streams use a 2-minute buffer on the 90-day lookback
(P89DT23H58M instead of P90D) to prevent 400 errors caused by network latency
when the Amazon SP-API rejects createdSince values more than 90 days old at the
time the request is received. This mirrors the PT2M buffer pattern used on
end_datetime in other streams.

See: https://github.com/airbytehq/airbyte/issues/76265
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
import requests
import yaml
from freezegun import freeze_time

from .conftest import get_source


BASE_CONFIG = {
    "refresh_token": "Atzr|IwEBIP-abc123",
    "lwa_app_id": "amzn1.application-oa2-client.abc123",
    "lwa_client_secret": "abc123",
    "aws_environment": "SANDBOX",
    "region": "US",
    "account_type": "Seller",
}

FROZEN_NOW = "2025-06-15T12:00:00Z"
FROZEN_NOW_DT = datetime(2025, 6, 15, 12, 0, 0)
# P89DT23H58M = 90 days minus 2 minutes
EXPECTED_BUFFERED_START = (FROZEN_NOW_DT - timedelta(days=89, hours=23, minutes=58)).strftime("%Y-%m-%dT%H:%M:%SZ")

MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _load_manifest():
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "definition_path",
    [
        pytest.param(
            ("definitions", "streams", "get_v2_settlement_report_data_flat_file"),
            id="main_stream",
        ),
        pytest.param(
            ("definitions", "flat_file_settlement_v2_helper"),
            id="helper_stream",
        ),
    ],
)
def test_manifest_settlement_definitions_use_buffered_duration_not_p90d(definition_path):
    """
    Verify that the manifest YAML for both settlement-related stream definitions
    uses P89DT23H58M (not P90D) in the start_datetime expression. This is a
    2-minute buffer matching the PT2M pattern used on end_datetime in other
    streams, preventing the race condition where network latency causes the
    SP-API to reject createdSince values computed as exactly 90 days ago.
    """
    manifest = _load_manifest()
    stream_def = manifest
    for key in definition_path:
        stream_def = stream_def[key]

    start_datetime_expr = stream_def["incremental_sync"]["start_datetime"]["datetime"]

    assert "P89DT23H58M" in start_datetime_expr, (
        f"Definition '{'/'.join(definition_path)}' should use P89DT23H58M in start_datetime, "
        f"but the expression is: {start_datetime_expr}"
    )
    assert "P90D" not in start_datetime_expr, (
        f"Definition '{'/'.join(definition_path)}' should NOT use P90D in start_datetime (race condition risk), "
        f"but the expression is: {start_datetime_expr}"
    )


@freeze_time(FROZEN_NOW)
@pytest.mark.parametrize(
    "config_override,expected_start",
    [
        pytest.param(
            {},
            EXPECTED_BUFFERED_START,
            id="no_start_date_defaults_to_90d_minus_2min",
        ),
        pytest.param(
            {"replication_start_date": "2020-01-01T00:00:00Z"},
            EXPECTED_BUFFERED_START,
            id="old_start_date_clamped_to_90d_minus_2min",
        ),
        pytest.param(
            {"replication_start_date": "2025-05-01T00:00:00Z"},
            "2025-05-01T00:00:00Z",
            id="recent_start_date_used_as_is",
        ),
    ],
)
def test_settlement_helper_stream_start_datetime(config_override, expected_start, requests_mock, mocker):
    """
    Test that the flat_file_settlement_v2_helper stream (which is the parent stream
    that makes the createdSince API call) computes the correct start_datetime based
    on config. This stream uses P89DT23H58M (90 days minus 2 minutes) to prevent
    the SP-API from rejecting createdSince values due to network latency.
    """
    # Bypass requests_cache so that parametrized cases sharing the same resolved URL
    # (e.g. no_start_date and old_start_date_clamped both clamp to the same createdSince)
    # are not served from cache, which would bypass requests_mock and leave request_history empty.
    mocker.patch(
        "requests_cache.CachedSession.send",
        lambda self, request, **kwargs: requests.Session.send(self, request, **kwargs),
    )
    requests_mock.post(
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
        status_code=200,
    )
    # Mock the reports API to return an empty list so the parent stream can be read
    requests_mock.get(
        "https://sandbox.sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports",
        json={"reports": []},
        status_code=200,
    )

    config = {**BASE_CONFIG, **config_override}
    source = get_source(config=config, state=None)
    streams = source.streams(source._config)

    # GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE is the exposed stream backed by the helper
    stream = next((s for s in streams if s.name == "GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE"), None)
    assert stream is not None, "Stream 'GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE' not found"

    # Generate partitions to trigger the parent stream's slice calculation
    list(map(lambda partition: partition.to_slice(), stream.generate_partitions()))

    # Verify the parent request was made with the correct createdSince parameter (89 days ago, not 90).
    history = requests_mock.request_history
    reports_requests = [r for r in history if "reports/2021-06-30/reports" in r.url and r.method == "GET"]
    assert len(reports_requests) > 0, "Expected at least one request to the reports API"

    first_request = reports_requests[0]
    created_since = first_request.qs.get("createdsince", [None])[0]
    assert created_since is not None, "Expected createdSince parameter in the reports API request"
    # requests_mock lowercases query parameter values, so compare case-insensitively
    assert created_since.lower() == expected_start.lower(), (
        f"Expected createdSince={expected_start}, got createdSince={created_since}. "
        f"The 2-minute buffer (P89DT23H58M) prevents the SP-API 400 error race condition."
    )
