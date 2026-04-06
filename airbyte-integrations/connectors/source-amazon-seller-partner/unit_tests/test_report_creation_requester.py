#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock, patch

import pytest
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
) -> dict:
    """Build a report object matching the Amazon SP-API Report schema."""
    return {
        "reportId": report_id,
        "reportType": report_type,
        "processingStatus": status,
        "dataStartTime": start_time,
        "dataEndTime": end_time,
        "marketplaceIds": marketplace_ids or ["ATVPDKIKX0DER"],
    }


def _make_requester() -> ReportCreationRequester:
    """Create a ReportCreationRequester instance with mocked internals for unit testing."""
    requester = object.__new__(ReportCreationRequester)

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
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
            )
            is True
        )

    def test_matching_dates_with_different_timezones(self):
        """Date-only comparison should match even if times differ."""
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
                "2023-01-01T05:00:00+05:00",
                "2023-01-30T12:00:00+00:00",
            )
            is True
        )

    def test_non_matching_start_date(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
                "2023-01-02T00:00:00Z",
                "2023-01-30T00:00:00Z",
            )
            is False
        )

    def test_non_matching_end_date(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
                "2023-01-01T00:00:00Z",
                "2023-01-31T00:00:00Z",
            )
            is False
        )

    def test_empty_report_start(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
                "",
                "2023-01-30T00:00:00Z",
            )
            is False
        )

    def test_empty_report_end(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
                "2023-01-01T00:00:00Z",
                "",
            )
            is False
        )

    def test_empty_requested_start(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "",
                "2023-01-30T00:00:00Z",
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
            )
            is False
        )

    def test_empty_requested_end(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "2023-01-01T00:00:00Z",
                "",
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
            )
            is False
        )

    def test_invalid_date_format(self):
        assert (
            ReportCreationRequester._date_ranges_match(
                "not-a-date",
                "2023-01-30T00:00:00Z",
                "2023-01-01T00:00:00Z",
                "2023-01-30T00:00:00Z",
            )
            is False
        )


class TestMarketplaceIdsMatch:
    """Tests for ReportCreationRequester._marketplace_ids_match static method."""

    def test_matching_single_marketplace(self):
        assert (
            ReportCreationRequester._marketplace_ids_match(
                ["ATVPDKIKX0DER"],
                ["ATVPDKIKX0DER"],
            )
            is True
        )

    def test_matching_multiple_marketplaces(self):
        assert (
            ReportCreationRequester._marketplace_ids_match(
                ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
                ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
            )
            is True
        )

    def test_matching_different_order(self):
        """Order shouldn't matter — sets should be compared."""
        assert (
            ReportCreationRequester._marketplace_ids_match(
                ["A2EUQ1WTGCTBG2", "ATVPDKIKX0DER"],
                ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
            )
            is True
        )

    def test_non_matching_marketplace(self):
        assert (
            ReportCreationRequester._marketplace_ids_match(
                ["ATVPDKIKX0DER"],
                ["A2EUQ1WTGCTBG2"],
            )
            is False
        )

    def test_empty_requested(self):
        assert (
            ReportCreationRequester._marketplace_ids_match(
                [],
                ["ATVPDKIKX0DER"],
            )
            is False
        )

    def test_empty_report(self):
        assert (
            ReportCreationRequester._marketplace_ids_match(
                ["ATVPDKIKX0DER"],
                [],
            )
            is False
        )

    def test_both_empty(self):
        assert ReportCreationRequester._marketplace_ids_match([], []) is False

    def test_subset_does_not_match(self):
        assert (
            ReportCreationRequester._marketplace_ids_match(
                ["ATVPDKIKX0DER"],
                ["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"],
            )
            is False
        )


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
        matching_report = _make_report(report_id="rpt-match", marketplace_ids=["ATVPDKIKX0DER"])
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

    def test_skips_fatal_report(self):
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

        assert result is None

    def test_skips_fatal_and_returns_next_valid_report(self):
        """If the first report is FATAL but a second matching report exists, return the second."""
        requester = _make_requester()
        fatal_report = _make_report(report_id="rpt-fatal", status="FATAL")
        valid_report = _make_report(report_id="rpt-valid", status="IN_PROGRESS")
        get_response = _make_get_reports_response([fatal_report, valid_report])
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
        assert result.json()["reportId"] == "rpt-valid"

    def test_skips_marketplace_mismatch(self):
        requester = _make_requester()
        report = _make_report(report_id="rpt-wrong-mp", marketplace_ids=["A2EUQ1WTGCTBG2"])
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
        matching_report = _make_report(report_id="rpt-existing")
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

    def test_skips_cancelled_and_returns_done_report(self):
        """When first report is CANCELLED, should skip it and find the DONE report."""
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        cancelled = _make_report(report_id="rpt-cancelled", status="CANCELLED")
        done = _make_report(report_id="rpt-done", status="DONE")
        get_response = _make_get_reports_response([cancelled, done])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-done"

    def test_skips_fatal_and_returns_done_report(self):
        """When first report is FATAL, should skip it and find the DONE report."""
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        fatal = _make_report(report_id="rpt-fatal", status="FATAL")
        done = _make_report(report_id="rpt-done", status="DONE")
        get_response = _make_get_reports_response([fatal, done])
        requester._http_client.send_request.return_value = (None, get_response)

        result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-done"

    def test_skips_marketplace_mismatch_in_send_request(self):
        """When report has different marketplace, should create new."""
        requester = _make_requester()
        requester._request_body_json.return_value = {
            "reportType": "GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL",
            "dataStartTime": "2023-01-01T00:00:00Z",
            "dataEndTime": "2023-01-30T00:00:00Z",
            "marketplaceIds": ["ATVPDKIKX0DER"],
        }
        wrong_mp = _make_report(report_id="rpt-wrong-mp", marketplace_ids=["A2EUQ1WTGCTBG2"])
        get_response = _make_get_reports_response([wrong_mp])
        requester._http_client.send_request.return_value = (None, get_response)

        create_response = _create_response(200, {"reportId": "rpt-new"})
        with patch.object(ReportCreationRequester.__bases__[0], "send_request", return_value=create_response):
            result = requester.send_request(stream_state=None, stream_slice=None)

        assert result is not None
        assert result.json()["reportId"] == "rpt-new"
