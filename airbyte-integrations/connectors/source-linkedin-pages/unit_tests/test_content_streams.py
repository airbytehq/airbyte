# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import pytest
import requests_mock
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.state_builder import StateBuilder


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


def _posts_response(*posts: dict, start: int = 0, has_next: bool = False) -> dict:
    # LinkedIn's documented paging block: a "next" link marks that more posts follow, even after a short page.
    links = [{"rel": "next", "type": "application/json", "href": f"/rest/posts?q=author&start={start + 100}&count=100"}] if has_next else []
    return {"elements": list(posts), "paging": {"start": start, "count": 100, "links": links}}


def test_posts_paginates_with_exact_parameters_and_protocol_header():
    first_page = [{"id": f"urn:li:share:{index}"} for index in range(100)]
    second_page = [{"id": "urn:li:ugcPost:100"}]
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/posts",
            response_list=[
                {"json": _posts_response(*first_page, has_next=True)},
                {"json": _posts_response(*second_page, start=100)},
            ],
        )

        output = _read("posts")

        assert output.errors == [], output.get_formatted_error_message()
        assert len(output.records) == 101
        assert [request.path for request in mocker.request_history] == ["/rest/posts", "/rest/posts"]
        expected = {"author": _ORGANIZATION, "q": "author", "sortBy": "LAST_MODIFIED", "count": "100"}
        _assert_params(mocker.request_history[0], expected)
        _assert_params(mocker.request_history[1], {**expected, "start": "100"})
        for request in mocker.request_history:
            assert request.headers["X-Restli-Protocol-Version"] == "2.0.0"


def test_posts_follow_the_next_link_after_a_short_page():
    first_page = [{"id": f"urn:li:share:{index}"} for index in range(97)]
    second_page = [{"id": f"urn:li:share:{index}"} for index in range(100, 150)]
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/posts",
            response_list=[
                {"json": _posts_response(*first_page, has_next=True)},
                {"json": _posts_response(*second_page, start=100)},
            ],
        )

        output = _read("posts")

        assert output.errors == [], output.get_formatted_error_message()
        assert len(output.records) == 147
        assert len(mocker.request_history) == 2
        # The next page starts at start + requested count, not after the 97 posts returned.
        assert parse_qs(urlsplit(mocker.request_history[1].url).query)["start"] == ["100"]


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
        # Partitions run concurrently, so the request order is not fixed.
        assert sorted(urlsplit(request.url).path for request in comment_requests) == [
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
        assert sorted(urlsplit(request.url).path for request in reaction_requests) == sorted(
            f"/rest/reactions/(entity:{urn.replace(':', '%3A')})" for urn in _POST_URNS
        )
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


@freeze_time("2026-10-23T14:37:12Z")
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
        assert result["date"] == datetime.fromtimestamp(start_millis / 1000, timezone.utc).strftime("%Y-%m-%d")
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


@freeze_time("2026-10-23T14:37:12Z")
def test_page_statistics_time_bound_same_day_resync_requests_nothing():
    _, end_millis = _page_statistics_dates()
    state = StateBuilder().with_stream_state("page_statistics_time_bound", {"timeRangeEnd": end_millis}).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/organizationPageStatistics", json={"elements": []})

        output = _read("page_statistics_time_bound", SyncMode.incremental, state)

        assert output.errors == [], output.get_formatted_error_message()
        assert output.records == []
        assert mocker.request_history == []


@freeze_time("2026-10-23T14:37:12Z")
def test_page_statistics_time_bound_month_resume_inside_the_month_requests_nothing():
    # LinkedIn rejects a MONTH window that ends inside the month it starts in, so only complete months are requested.
    _, end_millis = _page_statistics_dates()
    state_millis = end_millis - 5 * 24 * 60 * 60 * 1000
    state = StateBuilder().with_stream_state("page_statistics_time_bound", {"timeRangeEnd": state_millis}).build()
    config = {**_CONFIG, "time_granularity_type": "MONTH"}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/organizationPageStatistics", json={"elements": []})

        output = _read("page_statistics_time_bound", SyncMode.incremental, state, config=config)

        assert output.errors == [], output.get_formatted_error_message()
        assert output.records == []
        assert mocker.request_history == []


def test_posts_403_is_a_config_error_with_scope_remediation():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/posts", status_code=403, json={"message": "Access denied"})

        output = _read("posts")

        assert output.errors
        assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        assert any("r_organization_social" in error.trace.error.message for error in output.errors)
        assert any("rw_organization_admin" in error.trace.error.message for error in output.errors)


@freeze_time("2026-10-23T14:37:12Z")
@pytest.mark.parametrize(
    "start_date, expected_ids",
    [
        pytest.param("2026-01-01T00:00:00Z", {"this_year"}, id="start_date"),
        pytest.param(None, {"this_year", "last_year"}, id="two_year_default"),
    ],
)
def test_posts_first_incremental_sync_drops_posts_before_start(start_date, expected_ids):
    config = {key: value for key, value in {**_CONFIG, "start_date": start_date}.items() if value is not None}
    posts = [
        {"id": "this_year", "lastModifiedAt": _day_start_millis(date(2026, 3, 1))},
        {"id": "last_year", "lastModifiedAt": _day_start_millis(date(2025, 3, 1))},
        {"id": "three_years_ago", "lastModifiedAt": _day_start_millis(date(2023, 3, 1))},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/posts", json=_posts_response(*posts))

        output = _read("posts", SyncMode.incremental, config=config)

    assert output.errors == [], output.get_formatted_error_message()
    assert {record.record.data["id"] for record in output.records} == expected_ids


@pytest.mark.parametrize(
    "stream_name, child_path",
    [
        ("post_comments", "/socialActions/urn%3Ali%3Ashare%3A1/comments"),
        ("post_reactions", "/reactions/(entity:urn%3Ali%3Ashare%3A1)"),
    ],
)
def test_child_streams_ignore_deleted_post_and_fail_403_as_config_error(stream_name, child_path):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/posts", json=_posts_response({"id": "urn:li:share:1"}))
        mocker.get(
            f"{_BASE_URL}{child_path}",
            [{"status_code": 404, "json": {"message": "Not found"}}, {"status_code": 403, "json": {"message": "Denied"}}],
        )

        deleted = _read(stream_name)
        denied = _read(stream_name)

    assert deleted.errors == [] and deleted.records == []
    assert denied.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in denied.errors)
    assert any("r_organization_social" in error.trace.error.message for error in denied.errors)


def test_new_streams_primary_keys_and_cursors():
    catalog = discover(get_source(_CONFIG), _CONFIG).catalog.catalog
    streams = {stream.name: stream for stream in catalog.streams}

    assert {
        name: (streams[name].source_defined_primary_key, streams[name].default_cursor_field)
        for name in ("posts", "post_comments", "post_reactions", "page_statistics", "page_statistics_time_bound")
    } == {
        "posts": ([["id"]], ["lastModifiedAt"]),
        "post_comments": ([["object"], ["id"]], None),
        "post_reactions": ([["id"]], None),
        "page_statistics": ([["organization"]], None),
        "page_statistics_time_bound": ([["organization"], ["timeRangeStart"], ["timeRangeEnd"]], ["timeRangeEnd"]),
    }


@freeze_time("2026-10-23T14:37:12Z")
def test_page_statistics_time_bound_drops_zero_length_month_bucket():
    september, october = 1788220800000, 1790812800000
    record = {"organization": _ORGANIZATION, "totalPageStatistics": {"views": {"allPageViews": {"pageViews": 3}}}}
    config = {**_CONFIG, "time_granularity_type": "MONTH"}
    state = StateBuilder().with_stream_state("page_statistics_time_bound", {"timeRangeEnd": september}).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/organizationPageStatistics",
            json={
                "elements": [
                    {**record, "timeRange": {"start": september, "end": october}},
                    # LinkedIn appends a zero-length bucket at the end of a MONTH window.
                    {**record, "timeRange": {"start": october, "end": october}},
                ]
            },
        )

        output = _read("page_statistics_time_bound", SyncMode.incremental, state, config=config)

    assert output.errors == [], output.get_formatted_error_message()
    assert [(r.record.data["timeRangeStart"], r.record.data["timeRangeEnd"]) for r in output.records] == [(september, october)]


@freeze_time("2026-10-23T14:37:12Z")
@pytest.mark.parametrize(
    "start_date, expected_posts",
    [
        pytest.param(None, ["mid", "new"], id="default_two_years"),
        pytest.param("2026-01-01T00:00:00Z", ["new"], id="start_date"),
    ],
)
@pytest.mark.parametrize("stream_name", ["post_comments", "post_reactions"])
def test_child_streams_request_only_posts_inside_the_window(stream_name, start_date, expected_posts):
    # Each child request costs quota, so posts last modified before the window must not be requested.
    config = {key: value for key, value in _CONFIG.items() if key != "start_date"}
    if start_date:
        config["start_date"] = start_date
    posts = [
        {"id": "urn:li:share:new", "lastModifiedAt": _day_start_millis(date(2026, 3, 1))},
        {"id": "urn:li:share:mid", "lastModifiedAt": _day_start_millis(date(2025, 3, 1))},
        {"id": "urn:li:share:old", "lastModifiedAt": _day_start_millis(date(2023, 3, 1))},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(requests_mock.ANY, json={"elements": [], "paging": {"start": 0, "count": 100, "links": []}})
        mocker.get(f"{_BASE_URL}/posts", json=_posts_response(*posts))

        output = _read(stream_name, config=config)

        child_paths = [urlsplit(request.url).path for request in mocker.request_history if not request.path.endswith("/posts")]

    assert output.errors == []
    requested_posts = sorted(name for name in ("new", "mid", "old") if any(f"urn%3Ali%3Ashare%3A{name}" in path for path in child_paths))
    assert requested_posts == expected_posts
