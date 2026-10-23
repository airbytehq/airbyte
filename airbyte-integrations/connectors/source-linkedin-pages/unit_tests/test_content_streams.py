# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import requests_mock

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from conftest import get_source


_CONFIG = {
    "org_id": "12345678",
    "credentials": {"auth_method": "access_token", "access_token": "test_token"},
    "start_date": "2023-10-31T00:00:00Z",
    "time_granularity_type": "DAY",
}
_BASE_URL = "https://api.linkedin.com/rest"
_ORGANIZATION = "urn:li:organization:12345678"
_POST_URNS = ("urn:li:share:1", "urn:li:ugcPost:2")


def _read(stream_name: str, mode: SyncMode = SyncMode.full_refresh, state=None, config=None):
    config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, mode).build()
    source = get_source(config, state=state)
    return read(source, config=config, catalog=catalog, state=state)


def _assert_params(request, expected: dict[str, str]) -> None:
    assert parse_qs(urlsplit(request.url).query, keep_blank_values=True) == {key: [value] for key, value in expected.items()}


def _day_start_millis(day: date) -> int:
    return int(datetime.combine(day, time.min, timezone.utc).timestamp() * 1000)


def _posts_response(*posts: dict) -> dict:
    return {"elements": list(posts)}


def test_posts_paginates_with_exact_parameters_and_protocol_header():
    first_page = [{"id": f"urn:li:share:{index}"} for index in range(100)]
    second_page = [{"id": "urn:li:ugcPost:100"}]
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/posts",
            response_list=[{"json": _posts_response(*first_page)}, {"json": _posts_response(*second_page)}],
        )

        output = _read("posts")

        assert output.errors == [], output.get_formatted_error_message()
        assert len(output.records) == 101
        assert [request.path for request in mocker.request_history] == ["/rest/posts", "/rest/posts"]
        for request, start in zip(mocker.request_history, ("0", "100")):
            _assert_params(
                request,
                {
                    "author": _ORGANIZATION,
                    "q": "author",
                    "sortBy": "LAST_MODIFIED",
                    "start": start,
                    "count": "100",
                },
            )
            assert request.headers["X-Restli-Protocol-Version"] == "2.0.0"


def test_posts_incremental_cursor_filters_records_before_state():
    cursor = datetime(2026, 6, 1, tzinfo=timezone.utc)
    cursor_millis = int(cursor.timestamp() * 1000)
    state = StateBuilder().with_stream_state("posts", {"lastModifiedAt": cursor_millis}).build()
    records = [
        {"id": "too_old", "lastModifiedAt": cursor_millis - 8 * 24 * 60 * 60 * 1000},
        {"id": "old", "lastModifiedAt": cursor_millis - 24 * 60 * 60 * 1000},
        {"id": "new", "lastModifiedAt": cursor_millis + 24 * 60 * 60 * 1000},
        {"id": "newer", "lastModifiedAt": cursor_millis + 2 * 24 * 60 * 60 * 1000},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/posts", json=_posts_response(*records))

        output = _read("posts", SyncMode.incremental, state)

        assert output.errors == [], output.get_formatted_error_message()
        assert {record.record.data["id"] for record in output.records} == {"new", "newer"}
        _assert_params(
            mocker.request_history[0],
            {
                "author": _ORGANIZATION,
                "q": "author",
                "sortBy": "LAST_MODIFIED",
                "start": "0",
                "count": "100",
            },
        )


def _mock_posts_parent(mocker) -> None:
    mocker.get(f"{_BASE_URL}/posts", json=_posts_response(*({"id": urn} for urn in _POST_URNS)))


def test_post_comments_encodes_post_urns_adds_parent_and_ignores_deleted_post():
    encoded_urns = ("urn%3Ali%3Ashare%3A1", "urn%3Ali%3AugcPost%3A2")
    with requests_mock.Mocker() as mocker:
        _mock_posts_parent(mocker)
        mocker.get(
            f"{_BASE_URL}/socialActions/{encoded_urns[0]}/comments",
            json={"elements": [{"id": 1}]},
        )
        mocker.get(
            f"{_BASE_URL}/socialActions/{encoded_urns[1]}/comments",
            status_code=404,
            json={"message": "Post was deleted"},
        )

        output = _read("post_comments")

        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data for record in output.records] == [{"id": 1, "post_urn": _POST_URNS[0]}]
        comment_requests = [request for request in mocker.request_history if "/comments" in request.path]
        assert [urlsplit(request.url).path for request in comment_requests] == [
            f"/rest/socialActions/{encoded_urns[0]}/comments",
            f"/rest/socialActions/{encoded_urns[1]}/comments",
        ]
        for request in comment_requests:
            _assert_params(request, {"start": "0", "count": "100"})


def test_post_reactions_uses_literal_parentheses_and_adds_parent_urn():
    with requests_mock.Mocker() as mocker:
        _mock_posts_parent(mocker)
        for urn in _POST_URNS:
            encoded_urn = urn.replace(":", "%3A")
            mocker.get(
                f"{_BASE_URL}/reactions/(entity:{encoded_urn})",
                json={"elements": [{"id": f"reaction-{urn}", "reactionType": "LIKE"}]},
            )

        output = _read("post_reactions")

        assert output.errors == [], output.get_formatted_error_message()
        assert {record.record.data["post_urn"] for record in output.records} == set(_POST_URNS)
        assert {record.record.data["id"] for record in output.records} == {f"reaction-{urn}" for urn in _POST_URNS}
        reaction_requests = [request for request in mocker.request_history if "/reactions/" in request.path]
        assert [urlsplit(request.url).path for request in reaction_requests] == [
            f"/rest/reactions/(entity:{urn.replace(':', '%3A')})" for urn in _POST_URNS
        ]
        for request in reaction_requests:
            _assert_params(request, {"q": "entity", "start": "0", "count": "100"})


def test_page_statistics_requests_exact_parameters_and_returns_a_record():
    response_record = {
        "organization": _ORGANIZATION,
        "totalPageStatistics": {"views": {"allPageViews": 10}},
        "pageStatisticsBySeniority": [],
        "pageStatisticsByIndustryV2": [],
        "pageStatisticsByGeoCountry": [],
        "pageStatisticsByGeo": [],
        "pageStatisticsByTargetedContent": [],
        "pageStatisticsByStaffCountRange": [],
        "pageStatisticsByFunction": [],
    }
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/organizationPageStatistics", json={"elements": [response_record]})

        output = _read("page_statistics")

        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data for record in output.records] == [response_record]
        assert len(mocker.request_history) == 1
        _assert_params(
            mocker.request_history[0],
            {"q": "organization", "organization": _ORGANIZATION},
        )
        assert "X-Restli-Protocol-Version" not in mocker.request_history[0].headers


def _page_statistics_dates() -> tuple[int, int]:
    today = datetime.now(timezone.utc).date()
    start_day = max(date.fromisoformat(_CONFIG["start_date"][:10]), today - timedelta(days=365))
    end_day = today - timedelta(days=2)
    return _day_start_millis(start_day), _day_start_millis(end_day)


def test_page_statistics_time_bound_aligns_midnight_and_removes_time_range():
    start_millis, end_millis = _page_statistics_dates()
    record = {
        "organization": _ORGANIZATION,
        "totalPageStatistics": {"views": {"allPageViews": 10}},
        "pageStatisticsBySeniority": [],
        "pageStatisticsByIndustryV2": [],
        "pageStatisticsByGeoCountry": [],
        "pageStatisticsByGeo": [],
        "pageStatisticsByTargetedContent": [],
        "pageStatisticsByStaffCountRange": [],
        "pageStatisticsByFunction": [],
        "timeRange": {"start": start_millis, "end": end_millis},
    }
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/organizationPageStatistics", json={"elements": [record]})

        output = _read("page_statistics_time_bound", SyncMode.incremental)

        assert output.errors == [], output.get_formatted_error_message()
        assert len(output.records) == 1
        result = output.records[0].record.data
        assert result["timeRangeStart"] == start_millis
        assert result["timeRangeEnd"] == end_millis
        assert "timeRange" not in result
        assert len(mocker.request_history) == 1
        _assert_params(
            mocker.request_history[0],
            {
                "q": "organization",
                "organization": _ORGANIZATION,
                "timeIntervals.timeGranularityType": "DAY",
                "timeIntervals.timeRange.start": str(start_millis),
                "timeIntervals.timeRange.end": str(end_millis),
            },
        )
        assert "X-Restli-Protocol-Version" not in mocker.request_history[0].headers


def test_page_statistics_time_bound_ignores_same_day_resync_error():
    _, end_millis = _page_statistics_dates()
    state = StateBuilder().with_stream_state("page_statistics_time_bound", {"timeRangeEnd": end_millis}).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/organizationPageStatistics",
            status_code=400,
            json={"message": "Invalid timeIntervals parameter. End time must be greater than start time."},
        )

        output = _read("page_statistics_time_bound", SyncMode.incremental, state)

        assert output.errors == [], output.get_formatted_error_message()
        assert output.records == []
        assert mocker.request_history == []


def test_page_statistics_time_bound_ignores_month_granularity_error():
    _, end_millis = _page_statistics_dates()
    state_millis = end_millis - 5 * 24 * 60 * 60 * 1000
    state = StateBuilder().with_stream_state("page_statistics_time_bound", {"timeRangeEnd": state_millis}).build()
    config = {**_CONFIG, "time_granularity_type": "MONTH"}
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/organizationPageStatistics",
            status_code=400,
            json={
                "message": "Invalid timeIntervals parameter [...]. End time must be greater than start time by at least one multiple of the granularity type [MONTH].",
                "status": 400,
            },
        )

        output = _read("page_statistics_time_bound", SyncMode.incremental, state, config=config)

        assert output.errors == [], output.get_formatted_error_message()
        assert output.records == []
        assert len(mocker.request_history) == 1
        _assert_params(
            mocker.request_history[0],
            {
                "q": "organization",
                "organization": _ORGANIZATION,
                "timeIntervals.timeGranularityType": "MONTH",
                "timeIntervals.timeRange.start": str(state_millis),
                "timeIntervals.timeRange.end": str(end_millis),
            },
        )


def test_posts_403_is_a_config_error_with_scope_remediation():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/posts", status_code=403, json={"message": "Access denied"})

        output = _read("posts")

        assert output.errors
        assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        assert any("r_organization_social" in error.trace.error.message for error in output.errors)
        assert any("rw_organization_admin" in error.trace.error.message for error in output.errors)
