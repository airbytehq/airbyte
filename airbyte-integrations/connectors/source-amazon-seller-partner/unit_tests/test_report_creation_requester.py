#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import requests
from components import ReportCreationRequester


def _create_response(status_code: int, json_body: dict) -> requests.Response:
    """Create a real requests.Response object with the given status code and JSON body."""
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(json_body).encode("utf-8")
    return response


def _make_get_reports_response(reports: list) -> requests.Response:
    """Create a GET /reports response containing the given list of report objects."""
    return _create_response(200, {"reports": reports})


def _make_report(
    report_id: str = "report-123",
    report_type: str = "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
    status: str = "DONE",
    start_time: str = "2023-01-01T00:00:00Z",
    end_time: str = "2023-01-30T00:00:00Z",
    marketplace_ids: list = None,
    created_time: str = "",
) -> dict:
    """Build a report object matching the Amazon SP-API Report schema."""
    report = {
        "reportId": report_id,
        "reportType": report_type,
        "processingStatus": status,
        "dataStartTime": start_time,
        "dataEndTime": end_time,
        "marketplaceIds": marketplace_ids if marketplace_ids is not None else ["ATVPDKIKX0DER"],
    }
    if created_time:
        report["createdTime"] = created_time
    return report


def _make_requester(config: dict = None) -> ReportCreationRequester:
    """Create a ReportCreationRequester instance with mocked internals for unit testing."""
    requester = object.__new__(ReportCreationRequester)

    # Set config — defaults to empty dict (max_done_report_age_hours defaults to 0 in component)
    requester.config = config or {}

    # Mock _request_body_json to return a controlled body
    requester._request_body_json = MagicMock()

    # Mock get_url_base
    requester.get_url_base = MagicMock(return_value="https://sellingpartnerapi-na.amazon.com")

    # Mock _join_url
    requester._join_url = MagicMock(return_value="https://sellingpartnerapi-na.amazon.com/reports/2021-06-30/reports")

    # Mock _request_headers
    requester._request_headers = MagicMock(return_value={"content-type": "application/json"})

    # Mock _http_client
    requester._http_client = MagicMock()

    return requester


class TestDateRangesMatch:
    """Tests for ReportCreationRequester._date_ranges_match static method."""

    def test_matching_dates(self):
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="2023-01-30T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is True

    def test_matching_dates_with_same_instant_different_timezones(self):
        """Same instant expressed in different timezones should match."""
        report = _make_report(start_time="2023-01-01T05:00:00+05:00", end_time="2023-01-30T05:00:00+05:00")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is True

    def test_non_matching_times_on_same_date(self):
        """Same date but different time-of-day should not match."""
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="2023-01-30T12:00:00+00:00")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is False

    def test_non_matching_start_date(self):
        report = _make_report(start_time="2023-01-02T00:00:00Z", end_time="2023-01-30T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is False

    def test_non_matching_end_date(self):
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="2023-01-31T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is False

    def test_empty_report_start(self):
        report = _make_report(start_time="", end_time="2023-01-30T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is False

    def test_empty_report_end(self):
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "2023-01-30T00:00:00Z", report) is False

    def test_empty_requested_start(self):
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="2023-01-30T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("", "2023-01-30T00:00:00Z", report) is False

    def test_empty_requested_end(self):
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="2023-01-30T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("2023-01-01T00:00:00Z", "", report) is False

    def test_invalid_date_format(self):
        report = _make_report(start_time="2023-01-01T00:00:00Z", end_time="2023-01-30T00:00:00Z")
        assert ReportCreationRequester._date_ranges_match("not-a-date", "2023-01-30T00:00:00Z", report) is False


class TestFetchReports:
    """Tests for ReportCreationRequester._fetch_reports query parameters."""

    def test_passes_page_size_and_marketplace_ids(self):
        """Verify _fetch_reports sends pageSize=100 and marketplaceIds as comma-separated string."""
        requester = _make_requester()
        get_response = _make_get_reports_response([_make_report()])
        requester._http_client.send_request.return_value = (None, get_response)

        requester._fetch_reports(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            marketplace_ids=["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
        )

        call_kwargs = requester._http_client.send_request.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert params["pageSize"] == 100
        assert params["marketplaceIds"] == "ATVPDKIKX0DER,A2EUQ1WTGCTBG2"
        assert params["reportTypes"] == "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL"

    def test_omits_marketplace_ids_when_empty(self):
        """When marketplace_ids is empty, marketplaceIds should not be in params."""
        requester = _make_requester()
        get_response = _make_get_reports_response([])
        requester._http_client.send_request.return_value = (None, get_response)

        requester._fetch_reports(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            marketplace_ids=[],
        )

        call_kwargs = requester._http_client.send_request.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert "marketplaceIds" not in params
        assert params["pageSize"] == 100

    def test_returns_empty_on_exception(self):
        requester = _make_requester()
        requester._http_client.send_request.side_effect = Exception("Network error")

        reports, response = requester._fetch_reports(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert reports == []
        assert response is None


class TestBuildSyntheticResponse:
    """Tests for ReportCreationRequester._build_synthetic_response static method."""

    def test_response_contains_report_id(self):
        report = _make_report(report_id="rpt-abc-123")
        original = _create_response(200, {"reports": [report]})

        synthetic = ReportCreationRequester._build_synthetic_response(report, original)

        assert synthetic.status_code == 200
        assert synthetic.json() == {"reportId": "rpt-abc-123"}

    def test_response_copies_headers(self):
        report = _make_report()
        original = _create_response(200, {"reports": [report]})
        original.headers["x-amzn-RequestId"] = "req-id-123"

        synthetic = ReportCreationRequester._build_synthetic_response(report, original)

        assert synthetic.headers["x-amzn-RequestId"] == "req-id-123"


class TestFindExistingReport:
    """Tests for ReportCreationRequester._find_existing_report."""

    def test_returns_matching_report(self):
        requester = _make_requester()
        matching_report = _make_report(report_id="rpt-match", status="IN_PROGRESS", marketplace_ids=["ATVPDKIKX0DER"])
        get_response = _make_get_reports_response([matching_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-match"

    def test_skips_cancelled_report(self):
        """CANCELLED reports should be skipped so a new report is created to retry."""
        requester = _make_requester()
        cancelled_report = _make_report(report_id="rpt-cancelled", status="CANCELLED")
        get_response = _make_get_reports_response([cancelled_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_reuses_fatal_report(self):
        """FATAL reports should be reused — status_mapping handles the behavior."""
        requester = _make_requester()
        fatal_report = _make_report(report_id="rpt-fatal", status="FATAL")
        get_response = _make_get_reports_response([fatal_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-fatal"

    def test_returns_first_matching_report(self):
        """API returns reports sorted by createdTime desc, so first match is returned."""
        requester = _make_requester()
        now = datetime.now(tz=timezone.utc)
        # API returns newest first
        ip_report = _make_report(
            report_id="rpt-ip",
            status="IN_PROGRESS",
            created_time=(now - timedelta(hours=1)).isoformat(),
        )
        fatal_report = _make_report(
            report_id="rpt-fatal",
            status="FATAL",
            created_time=(now - timedelta(hours=2)).isoformat(),
        )
        get_response = _make_get_reports_response([ip_report, fatal_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-ip"

    def test_skips_cancelled_but_returns_in_progress(self):
        """When both CANCELLED and IN_PROGRESS reports exist, CANCELLED is skipped and IN_PROGRESS is returned."""
        requester = _make_requester()
        now = datetime.now(tz=timezone.utc)
        cancelled_report = _make_report(
            report_id="rpt-cancelled",
            status="CANCELLED",
            created_time=(now - timedelta(hours=1)).isoformat(),
        )
        ip_report = _make_report(
            report_id="rpt-ip",
            status="IN_PROGRESS",
            created_time=(now - timedelta(hours=2)).isoformat(),
        )
        get_response = _make_get_reports_response([cancelled_report, ip_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-ip"

    def test_skips_date_range_mismatch(self):
        requester = _make_requester()
        report = _make_report(
            report_id="rpt-wrong-date",
            start_time="2023-02-01T00:00:00Z",
            end_time="2023-02-28T00:00:00Z",
        )
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_returns_none_when_no_reports(self):
        requester = _make_requester()
        get_response = _make_get_reports_response([])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_returns_none_on_http_error(self):
        requester = _make_requester()
        error_response = _create_response(500, {"error": "Internal Server Error"})
        requester._http_client.send_request.return_value = (None, error_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_returns_none_on_exception(self):
        requester = _make_requester()
        requester._http_client.send_request.side_effect = Exception("Network error")

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_reuses_in_progress_report(self):
        """Reports with IN_PROGRESS status should be reusable."""
        requester = _make_requester()
        report = _make_report(report_id="rpt-in-progress", status="IN_PROGRESS")
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-in-progress"

    def test_reuses_in_queue_report(self):
        """Reports with IN_QUEUE status should be reusable."""
        requester = _make_requester()
        report = _make_report(report_id="rpt-in-queue", status="IN_QUEUE")
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-in-queue"

    def test_skips_done_report_when_max_age_is_zero(self):
        """When max_done_report_age_hours is 0 (default), DONE reports should never be reused."""
        requester = _make_requester()  # default config, max_done_report_age_hours=0
        now = datetime.now(tz=timezone.utc)
        report = _make_report(report_id="rpt-done", status="DONE", created_time=now.isoformat())
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_skips_stale_done_report(self):
        """DONE reports older than max_done_report_age_hours should be skipped."""
        requester = _make_requester(config={"max_done_report_age_hours": 24})
        # Report created 48 hours ago
        old_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        report = _make_report(report_id="rpt-stale", status="DONE", created_time=old_time)
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_reuses_fresh_done_report_when_max_age_set(self):
        """DONE reports created within max_done_report_age_hours should be reusable."""
        requester = _make_requester(config={"max_done_report_age_hours": 24})
        # Use a very recent timestamp
        now = datetime.now(tz=timezone.utc)
        fresh_time = now.isoformat()
        report = _make_report(report_id="rpt-fresh", status="DONE", created_time=fresh_time)
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-fresh"

    def test_in_progress_report_not_subject_to_staleness(self):
        """IN_PROGRESS reports should not be subject to the staleness check even when max_age is 0."""
        requester = _make_requester()  # default config, max_done_report_age_hours=0
        old_time = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()
        report = _make_report(report_id="rpt-old-ip", status="IN_PROGRESS", created_time=old_time)
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-old-ip"

    def test_returns_first_match_from_api_sorted_results(self):
        """API returns reports sorted by createdTime desc; first match in list is returned."""
        requester = _make_requester(config={"max_done_report_age_hours": 24})
        now = datetime.now(tz=timezone.utc)
        newer_time = (now - timedelta(hours=1)).isoformat()
        older_time = (now - timedelta(hours=2)).isoformat()

        # API returns newest first
        newer_report = _make_report(report_id="rpt-newer", status="DONE", created_time=newer_time)
        older_report = _make_report(report_id="rpt-older", status="DONE", created_time=older_time)
        get_response = _make_get_reports_response([newer_report, older_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-newer"

    def test_done_report_without_created_time_is_still_usable_when_max_age_set(self):
        """DONE reports without createdTime should still be reusable when max_age > 0."""
        requester = _make_requester(config={"max_done_report_age_hours": 24})
        report = _make_report(report_id="rpt-no-time", status="DONE")
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-no-time"

    def test_done_report_without_created_time_skipped_when_max_age_is_zero(self):
        """DONE reports without createdTime should be skipped when max_age is 0."""
        requester = _make_requester()  # default config, max_done_report_age_hours=0
        report = _make_report(report_id="rpt-no-time", status="DONE")
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_reuses_done_report_with_custom_max_age(self):
        """DONE report created 3h ago should be reused when max_done_report_age_hours=6."""
        requester = _make_requester(config={"max_done_report_age_hours": 6})
        now = datetime.now(tz=timezone.utc)
        report = _make_report(
            report_id="rpt-3h",
            status="DONE",
            created_time=(now - timedelta(hours=3)).isoformat(),
        )
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-3h"

    def test_skips_done_report_exceeding_custom_max_age(self):
        """DONE report created 10h ago should be skipped when max_done_report_age_hours=6."""
        requester = _make_requester(config={"max_done_report_age_hours": 6})
        now = datetime.now(tz=timezone.utc)
        report = _make_report(
            report_id="rpt-10h",
            status="DONE",
            created_time=(now - timedelta(hours=10)).isoformat(),
        )
        get_response = _make_get_reports_response([report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is None

    def test_default_config_skips_done_but_reuses_in_progress(self):
        """With default config (max_age=0), DONE reports are skipped but IN_PROGRESS is reused."""
        requester = _make_requester()  # default config, max_done_report_age_hours=0
        now = datetime.now(tz=timezone.utc)
        done_report = _make_report(report_id="rpt-done", status="DONE", created_time=now.isoformat())
        ip_report = _make_report(
            report_id="rpt-ip",
            status="IN_PROGRESS",
            created_time=(now - timedelta(hours=1)).isoformat(),
        )
        get_response = _make_get_reports_response([done_report, ip_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester._find_existing_report(
            stream_state=None,
            stream_slice=None,
            report_type="GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            requested_start="2023-01-01T00:00:00Z",
            requested_end="2023-01-30T00:00:00Z",
            requested_marketplace_ids=["ATVPDKIKX0DER"],
        )

        assert result is not None
        assert result.json()["reportId"] == "rpt-ip"


class TestSendRequest:
    """Tests for ReportCreationRequester.send_request integration."""

    def test_reuses_existing_report_when_found(self):
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        matching_report = _make_report(report_id="rpt-existing", status="IN_PROGRESS")
        get_response = _make_get_reports_response([matching_report])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-existing"

    def test_creates_new_report_when_no_match(self):
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        # GET /reports returns empty list
        get_response = _make_get_reports_response([])
        requester._http_client.send_request.return_value = (None, get_response)

        # Mock super().send_request to return a creation response
        create_response = _create_response(200, {"reportId": "rpt-new"})
        with patch.object(ReportCreationRequester.__bases__[0], "send_request", return_value=create_response):
            result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-new"

    def test_creates_new_report_when_get_fails(self):
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        # GET /reports raises an exception
        requester._http_client.send_request.side_effect = Exception("Network error")

        # Mock super().send_request to return a creation response
        create_response = _create_response(200, {"reportId": "rpt-fallback"})
        with patch.object(ReportCreationRequester.__bases__[0], "send_request", return_value=create_response):
            result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-fallback"

    def test_creates_new_report_when_no_report_type(self):
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
        }

        # Mock super().send_request to return a creation response
        create_response = _create_response(200, {"reportId": "rpt-no-type"})
        with patch.object(ReportCreationRequester.__bases__[0], "send_request", return_value=create_response):
            result = requester.send_request(stream_state=None, stream_slice=None)

        # Should not call _http_client for GET since there's no report_type
        requester._http_client.send_request.assert_not_called()
        assert result is not None
        assert result.json()["reportId"] == "rpt-no-type"

    def test_creates_new_report_when_only_cancelled_exists(self):
        """CANCELLED reports should be skipped, causing a new report to be created."""
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        cancelled = _make_report(report_id="rpt-cancelled", status="CANCELLED")
        get_response = _make_get_reports_response([cancelled])
        requester._http_client.send_request.return_value = (None, get_response)

        create_response = _create_response(200, {"reportId": "rpt-new"})
        with patch.object(ReportCreationRequester.__bases__[0], "send_request", return_value=create_response):
            result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-new"

    def test_reuses_fatal_report_in_send_request(self):
        """FATAL reports should be reused — status_mapping handles the behavior."""
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        fatal = _make_report(report_id="rpt-fatal", status="FATAL")
        get_response = _make_get_reports_response([fatal])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-fatal"

    def test_passes_marketplace_ids_to_fetch_reports(self):
        """Verify that send_request passes marketplaceIds from body_json to _fetch_reports."""
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
        }
        # GET /reports returns empty — no match
        get_response = _make_get_reports_response([])
        requester._http_client.send_request.return_value = (None, get_response)

        create_response = _create_response(200, {"reportId": "rpt-new"})
        with patch.object(ReportCreationRequester.__bases__[0], "send_request", return_value=create_response):
            requester.send_request(stream_state=None, stream_slice=None)

        # Verify the GET /reports call included marketplaceIds
        call_kwargs = requester._http_client.send_request.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs[1].get("params", {}))
        assert params["marketplaceIds"] == "ATVPDKIKX0DER,A2EUQ1WTGCTBG2"
