#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
from source_facebook_pages.source import SourceFacebookPages

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {"page_id": "1", "access_token": "token"}
ACCESS_TOKEN_URL = "https://graph.facebook.com/1?fields=access_token&access_token=token"
INSIGHTS_URL = "https://graph.facebook.com/v24.0/1/insights"
METRIC = {
    "id": "1/insights/page_post_engagements/day",
    "name": "page_post_engagements",
    "period": "day",
    "values": [
        {"value": 1, "end_time": "2024-05-31T07:00:00+0000"},
        {"value": 2, "end_time": "2024-06-01T07:00:00+0000"},
    ],
}


def _read(sync_mode, config, body, state=None):
    catalog = CatalogBuilder().with_stream("page_insights", sync_mode).build()
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(INSIGHTS_URL, json=body)
        output = read(SourceFacebookPages(catalog=catalog, config=config, state=state), config, catalog, state=state)
        queries = [parse_qs(urlparse(r.url).query) for r in m.request_history if urlparse(r.url).path == urlparse(INSIGHTS_URL).path]
    # Slices may be read concurrently, so order the requests by their window.
    return output, sorted(queries, key=lambda q: q.get("since", [""])[0])


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_page_insights_sends_no_date_range_without_start_date_or_state(sync_mode):
    output, queries = _read(sync_mode, CONFIG, {"data": [METRIC]})
    assert len(queries) == 1
    assert "since" not in queries[0] and "until" not in queries[0]
    assert len(output.records) == 1
    assert output.records[0].record.data["end_time"] == "2024-06-01T07:00:00+00:00"


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_page_insights_slices_from_start_date_in_90_day_windows(sync_mode):
    # start_date applies in both modes, as the spec describes.
    config = {**CONFIG, "start_date": "2024-01-01T00:00:00Z"}
    _, queries = _read(sync_mode, config, {"data": [METRIC]})
    assert len(queries) >= 2
    assert queries[0]["since"] == ["2024-01-01T00:00:00+0000"]
    assert queries[0]["until"] == ["2024-03-30T23:59:59+0000"]
    assert queries[1]["since"] == ["2024-03-31T00:00:00+0000"]
    assert all("since" in q and "until" in q for q in queries)


def test_page_insights_incremental_resumes_from_state_and_advances_cursor():
    state = StateBuilder().with_stream_state("page_insights", {"end_time": "2024-03-01T07:00:00+0000"}).build()
    output, queries = _read(SyncMode.incremental, CONFIG, {"data": [METRIC]}, state=state)
    assert len(queries) == 1
    # The two-day lookback re-reads the days before the saved cursor.
    assert queries[0]["since"] == ["2024-02-28T07:00:00+0000"]
    assert "until" in queries[0]
    assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"end_time": "2024-06-01T07:00:00+0000"}


def test_page_insights_incremental_rereads_current_day_when_cursor_is_ahead_of_now():
    # Meta stamps the newest daily point with the end of a day still in progress, so the saved
    # cursor can be later than the next sync's start time.
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    state = StateBuilder().with_stream_state("page_insights", {"end_time": tomorrow}).build()
    _, queries = _read(SyncMode.incremental, CONFIG, {"data": [METRIC]}, state=state)
    assert len(queries) == 1
    assert queries[0]["since"][0] < datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")


@pytest.mark.parametrize("values", [[], [{"value": 1}]], ids=["no_values", "point_without_end_time"])
def test_page_insights_record_without_end_time_is_kept(values):
    output, _ = _read(SyncMode.incremental, CONFIG, {"data": [{**METRIC, "values": values}]})
    assert len(output.records) == 1
    assert output.records[0].record.data.get("end_time") is None
