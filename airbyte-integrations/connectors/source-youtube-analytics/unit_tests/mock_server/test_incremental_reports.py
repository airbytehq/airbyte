#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""Mock server tests for incremental syncs of the report streams.

Incremental has to work on the `report` parent stream: it lists the daily report files for a
reporting job, and the child streams download whatever it hands back. If it returns all ~60
retained files, the children faithfully re-download all 60 and re-emit every row -- roughly
100k records and 64 MB per sync, every sync (airbytehq/oncall#13440).

The cursor is each file's `createTime`, and the floor reaches the API as `createdAfter`. Each
test's `createdAfter` matcher is therefore the real assertion: if the state migration does not
run, or writes the wrong key, the cursor falls back to its 1990 default and the outgoing request
does not match the mock, so `HttpMocker` fails the test.
"""

import json
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from _helpers import get_source
from mock_server.config import ConfigBuilder
from mock_server.request_builder import YoutubeAnalyticsRequestBuilder

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_NOW = "2026-09-09T00:00:00Z"
_STREAM_NAME = "channel_basic_a3"
_JOB_ID = "job-1"

# `report.incremental_sync.start_datetime` when the config sets no `testing_period`. A filter
# this old excludes nothing: YouTube retains report files for at most 60 days.
_DEFAULT_START_TIME = "1990-01-01T00:00:00.000000Z"

# Three report files, spread far enough apart that any off-by-one in the filter is visible.
# `startTime` is the 24-hour window of data inside the file (start of day Pacific, so 07:00Z);
# `createTime` is when YouTube generated the file, a day or two later.
_OLD = {"id": "r_old", "start_time": "2025-06-01T07:00:00Z", "create_time": "2025-06-03T00:00:00Z", "day": 20250601}
_SAME = {"id": "r_same", "start_time": "2025-11-07T07:00:00Z", "create_time": "2025-11-09T00:00:00Z", "day": 20251107}
_NEW = {"id": "r_new", "start_time": "2026-03-01T07:00:00Z", "create_time": "2026-03-03T00:00:00Z", "day": 20260301}

# A correction YouTube re-issued for the same day as `_SAME`: new id, newer `createTime`, but
# the SAME `startTime`. https://developers.google.com/youtube/reporting/v1/reports (Backfill data)
_BACKFILL = {"id": "r_backfill", "start_time": _SAME["start_time"], "create_time": "2026-04-01T00:00:00Z", "day": 20251107}

_ALL_REPORTS = [_OLD, _SAME, _NEW]


def _listing(report: Dict[str, Any]) -> Dict[str, Any]:
    """One entry of `GET /jobs/{id}/reports` -- metadata only, no rows."""
    return {
        "id": report["id"],
        "jobId": _JOB_ID,
        "startTime": report["start_time"],
        "endTime": report["start_time"],
        "createTime": report["create_time"],
        "downloadUrl": YoutubeAnalyticsRequestBuilder.download_url(report["id"]),
    }


def _reports_response(reports: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"reports": [_listing(report) for report in reports]}))


def _download_response(report: Dict[str, Any]) -> HttpResponse:
    """The file itself: CSV, decoded by `CustomDecoder`."""
    return HttpResponse(body=f"date,channel_id,views\n{report['day']},channel-1,1\n")


def _given_reports(http_mocker: HttpMocker, created_after: str, reports: List[Dict[str, Any]]) -> None:
    """Authenticate, resolve the reporting job, and list the files a correct API would return.

    The `jobs` response carries a job whose `reportTypeId` matches the stream under test, so
    `JobRequester` takes its read-only path and never POSTs to create one.
    """
    http_mocker.post(
        YoutubeAnalyticsRequestBuilder.token_request(), HttpResponse(body=json.dumps({"access_token": "token", "expires_in": 3600}))
    )
    http_mocker.get(
        YoutubeAnalyticsRequestBuilder.jobs_endpoint().build(),
        HttpResponse(body=json.dumps({"jobs": [{"id": _JOB_ID, "reportTypeId": _STREAM_NAME}]})),
    )
    http_mocker.get(
        YoutubeAnalyticsRequestBuilder.reports_endpoint(_JOB_ID).with_created_after(created_after).build(),
        _reports_response(reports),
    )


def _given_downloads(http_mocker: HttpMocker, reports: List[Dict[str, Any]]) -> None:
    """Mock exactly the downloads expected.

    Any file the connector downloads but is not listed here is an unmatched request, which
    `HttpMocker` fails -- so the omissions assert as strongly as the inclusions.
    """
    for report in reports:
        http_mocker.get(YoutubeAnalyticsRequestBuilder.download_endpoint(report["id"]).build(), _download_response(report))


def _read(state: Optional[List[AirbyteStateMessage]] = None) -> EntrypointOutput:
    config = ConfigBuilder().build()
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    return read(get_source(config=config, state=state), config=config, catalog=catalog, state=state)


def _state(stream_state: Dict[str, Any]) -> List[AirbyteStateMessage]:
    return StateBuilder().with_stream_state(_STREAM_NAME, stream_state).build()


def _report_state(output: EntrypointOutput) -> Dict[str, Any]:
    return output.most_recent_state.stream_state.parent_state["report"]


@freezegun.freeze_time(_NOW)
class TestIncrementalReports(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_every_retained_report_is_downloaded(self, http_mocker: HttpMocker):
        """A first sync must not filter anything out -- the fix's most obvious failure mode is over-correcting."""
        _given_reports(http_mocker, _DEFAULT_START_TIME, _ALL_REPORTS)
        _given_downloads(http_mocker, _ALL_REPORTS)

        output = _read()

        assert output.errors == []
        assert [record.record.data["date"] for record in output.records] == [report["day"] for report in _ALL_REPORTS]
        assert _report_state(output)["state"] == {"createTime": "2026-03-03T00:00:00.000000Z"}

    @HttpMocker()
    def test_given_migrated_state_when_read_then_only_newer_files_are_downloaded(self, http_mocker: HttpMocker):
        """The behaviour the customer was missing: a saved cursor actually narrows the listing."""
        _given_reports(http_mocker, "2025-11-09T00:00:00.000000Z", [_NEW])
        _given_downloads(http_mocker, [_NEW])

        output = _read(
            _state(
                {
                    "state": {"date": "20251107"},
                    "parent_state": {"report": {"state": {"createTime": "2025-11-09T00:00:00.000000Z"}}},
                }
            )
        )

        assert output.errors == []
        assert [record.record.data["date"] for record in output.records] == [_NEW["day"]]
        assert _report_state(output)["state"] == {"createTime": "2026-03-03T00:00:00.000000Z"}

    @HttpMocker()
    def test_given_legacy_low_code_state_when_read_then_cursor_is_rekeyed_and_applied(self, http_mocker: HttpMocker):
        """State written by 1.1.0 through 1.3.4 keyed the parent cursor on `date`.

        `ReportsStateMigration` re-keys it onto `createTime`. This is the test that proves the
        migration is wired into the stream rather than merely correct in isolation.

        The saved `lookback_window: 1` is the second half of it: the request floor comes out one
        second before the saved cursor, which is only possible if the migration carried the
        window through. Through 1.3.4 it wrote `lookback_window = 0` on every read, discarding
        the margin `GlobalSubstreamCursor` measures to catch files that appear mid-sync -- so
        this asserting `23:59:59` rather than `00:00:00` is the regression test for that.
        """
        _given_reports(http_mocker, "2025-11-08T23:59:59.000000Z", [_NEW])
        _given_downloads(http_mocker, [_NEW])

        output = _read(
            _state(
                {
                    "state": {"date": "20251107"},
                    "parent_state": {"report": {"state": {"date": "2025-11-09T00:00:00.000000Z"}, "lookback_window": 1}},
                }
            )
        )

        assert output.errors == []
        assert [record.record.data["date"] for record in output.records] == [_NEW["day"]]
        report_state = _report_state(output)
        assert report_state["state"] == {"createTime": "2026-03-03T00:00:00.000000Z"}
        # The legacy key is gone, so the next sync has nothing left to migrate.
        assert "date" not in report_state["state"]

    @HttpMocker()
    def test_given_pre_low_code_state_when_read_then_parent_cursor_is_seeded_from_the_child(self, http_mocker: HttpMocker):
        """Pre-1.1.0 state was a bare `%Y%m%d` day with no parent state at all.

        The day is a lower bound on the corresponding file's `createTime`, so seeding the parent
        with it re-lists a day or two of files rather than all 60.
        """
        _given_reports(http_mocker, "2025-11-07T00:00:00.000000Z", [_SAME, _NEW])
        _given_downloads(http_mocker, [_SAME, _NEW])

        output = _read(_state({"date": 20251107}))

        assert output.errors == []
        assert [record.record.data["date"] for record in output.records] == [_SAME["day"], _NEW["day"]]
        assert _report_state(output)["state"] == {"createTime": "2026-03-03T00:00:00.000000Z"}

    @HttpMocker()
    def test_given_reissued_report_when_read_then_the_correction_is_downloaded(self, http_mocker: HttpMocker):
        """The payoff of cursoring on `createTime` instead of `startTime`.

        `_BACKFILL` has the same `startTime` as a file already synced, so a `startTime` cursor
        would drop it -- equal, not greater -- and the correction would never land. Its
        `createTime` is newer, so a `createTime` cursor picks it up.
        """
        cursor = "2026-03-03T00:00:00.000000Z"  # `_NEW`'s createTime: everything through `_NEW` is synced.
        _given_reports(http_mocker, cursor, [_BACKFILL])
        _given_downloads(http_mocker, [_BACKFILL])

        output = _read(_state({"state": {"date": "20260301"}, "parent_state": {"report": {"state": {"createTime": cursor}}}}))

        assert output.errors == []
        # The row carries its own (old) date, so it lands as a correction to that day.
        assert [record.record.data["date"] for record in output.records] == [_BACKFILL["day"]]
        assert _report_state(output)["state"] == {"createTime": "2026-04-01T00:00:00.000000Z"}
