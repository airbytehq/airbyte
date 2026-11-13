# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime, timedelta, timezone

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "domain_id": "123456",
    "secret_key": "test-secret-key",
    "start_date": "2023-07-30T03:43:59.244Z",
}

_LAST_CLICKS_URL = "https://statistics.short.io/statistics/domain/123456/last_clicks"


def _click(index: int) -> dict:
    timestamp = datetime(2024, 1, 3, tzinfo=timezone.utc) - timedelta(seconds=index)
    return {"dt": timestamp.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "path": f"/{index}", "method": "GET", "human": True}


def _sync():
    catalog = CatalogBuilder().with_stream("clicks", SyncMode.full_refresh).build()
    source = get_source(config=_CONFIG)
    return read(source, _CONFIG, catalog)


@pytest.mark.parametrize("older_count", [0, 1, 29])
def test_clicks_paginates_with_inclusive_before_date(older_count: int) -> None:
    first_page = [_click(index) for index in range(30)]
    older_clicks = [_click(index) for index in range(30, 30 + older_count)]
    second_page = [first_page[-1], *older_clicks]
    expected_cursors = [None, first_page[-1]["dt"]]
    if len(second_page) == 30:
        expected_cursors.append(second_page[-1]["dt"])
    seen_cursors = set()

    def callback(request, context):
        before_date = request.json().get("beforeDate")
        assert before_date not in seen_cursors, f"Repeated beforeDate: {before_date}"
        seen_cursors.add(before_date)
        if before_date is None:
            return first_page
        if before_date == first_page[-1]["dt"]:
            return second_page
        if before_date == second_page[-1]["dt"]:
            return [second_page[-1]]
        context.status_code = 404
        return {"error": "Unexpected cursor"}

    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, json=callback)
        output = _sync()
        requests_made = mocker.request_history

    assert [request.json().get("beforeDate") for request in requests_made] == expected_cursors
    assert all(request.method == "POST" and request.json()["limit"] == 30 for request in requests_made)
    assert "beforeDate" not in requests_made[0].json()
    cursors = [request.json()["beforeDate"] for request in requests_made[1:]]
    assert all(newer > older for newer, older in zip(cursors, cursors[1:]))
    emitted = [record.record.data for record in output.records]
    expected = first_page + second_page
    if len(second_page) == 30:
        expected.append(second_page[-1])
    assert emitted == expected
    assert emitted.count(first_page[-1]) == 2
    assert all(emitted.count(click) <= 2 for click in first_page + older_clicks)


def test_clicks_terminates_on_full_page_of_boundary_records() -> None:
    first_page = [_click(index) for index in range(30)]
    second_page = [first_page[-1], *[{**_click(index), "dt": first_page[-1]["dt"]} for index in range(30, 59)]]
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, [{"json": first_page}, {"json": second_page}, {"status_code": 404}])
        output = _sync()
        assert len(mocker.request_history) == 2

    emitted = [record.record.data for record in output.records]
    assert emitted == first_page + second_page
    assert emitted.count(first_page[-1]) == 2


def test_clicks_terminates_on_full_first_page_with_same_timestamp() -> None:
    page = [{**_click(index), "dt": _click(0)["dt"]} for index in range(30)]
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, [{"json": page}, {"status_code": 404}])
        output = _sync()
        assert len(mocker.request_history) == 1

    assert [record.record.data for record in output.records] == page


@pytest.mark.parametrize("first_page", [[], [_click(index) for index in range(30)]])
def test_clicks_treats_not_found_as_no_records(first_page: list[dict]) -> None:
    responses = ([{"json": first_page}] if first_page else []) + [{"status_code": 404, "text": ""}]
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, responses)
        output = _sync()
        assert len(mocker.request_history) == (2 if first_page else 1)
        if first_page:
            assert mocker.request_history[-1].json()["beforeDate"] == first_page[-1]["dt"]

    assert [record.record.data for record in output.records] == first_page


def test_check_succeeds_when_clicks_returns_not_found() -> None:
    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.short.io/api/links", json={"links": []})
        mocker.post(_LAST_CLICKS_URL, status_code=404, text="")
        result = get_source(config=_CONFIG).check(logging.getLogger("test"), _CONFIG)
        assert mocker.call_count == 2

    assert result.status == Status.SUCCEEDED


@pytest.mark.parametrize("page", [[], [_click(0)], [_click(index) for index in range(29)]])
def test_clicks_terminates_on_short_first_page(page: list[dict]) -> None:
    with requests_mock.Mocker() as mocker:
        mocker.post(_LAST_CLICKS_URL, [{"json": page}, {"status_code": 404}])
        output = _sync()
        assert len(mocker.request_history) == 1

    assert [record.record.data for record in output.records] == page
