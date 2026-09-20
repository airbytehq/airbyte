# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards for the three behavioural fixes this connector needed after Goldcast's API update.

Each test targets one of them, and each fails if that fix is reverted:

1. list endpoints now wrap records in a `results` envelope
2. list endpoints now paginate on `limit`/`offset` — before, only the first page was ever read
3. `webinars` resolves its parent from webinar-type events only, instead of every event
"""

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_CONFIG = {"access_key": "test_access_key"}
_BASE = "https://customapi.goldcast.io"
_EVENTS_URL = f"{_BASE}/event/"
_PAGE_SIZE = 100


def _event(index: int) -> dict:
    return {"id": f"evt-{index:04d}", "title": f"Event {index}", "event_type": "Webinar"}


def _envelope(records: list, count: int = None) -> HttpResponse:
    """The shape every Goldcast list endpoint now returns."""
    body = {"count": count if count is not None else len(records), "next": None, "previous": None, "results": records}
    return HttpResponse(body=json.dumps(body))


def _read(stream: str):
    return read(
        get_source(_CONFIG),
        config=_CONFIG,
        catalog=CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build(),
    )


class TestGoldcastApiFormat(TestCase):
    @HttpMocker()
    def test_records_are_extracted_from_the_results_envelope(self, http_mocker: HttpMocker):
        """A reverted extractor would emit the envelope object itself rather than the records."""
        http_mocker.get(
            HttpRequest(url=_EVENTS_URL, query_params={"limit": str(_PAGE_SIZE)}),
            _envelope([_event(1), _event(2)]),
        )

        output = _read("events")

        assert len(output.records) == 2
        assert {record.record.data["id"] for record in output.records} == {"evt-0001", "evt-0002"}

    @HttpMocker()
    def test_offset_pagination_reads_past_the_first_page(self, http_mocker: HttpMocker):
        """This is the data-loss half of the bug: without a paginator only the first page was read."""
        full_page = [_event(i) for i in range(_PAGE_SIZE)]
        http_mocker.get(
            HttpRequest(url=_EVENTS_URL, query_params={"limit": str(_PAGE_SIZE)}),
            _envelope(full_page, count=_PAGE_SIZE + 1),
        )
        http_mocker.get(
            HttpRequest(url=_EVENTS_URL, query_params={"limit": str(_PAGE_SIZE), "offset": str(_PAGE_SIZE)}),
            _envelope([_event(9999)], count=_PAGE_SIZE + 1),
        )

        output = _read("events")

        assert len(output.records) == _PAGE_SIZE + 1
        assert "evt-9999" in {record.record.data["id"] for record in output.records}

    @HttpMocker()
    def test_webinars_parent_is_scoped_to_webinar_events(self, http_mocker: HttpMocker):
        """Resolving the parent from every event is what made the webinars detail endpoint fail."""
        http_mocker.get(
            HttpRequest(url=_EVENTS_URL, query_params={"event_type": "Webinar", "limit": str(_PAGE_SIZE)}),
            _envelope([_event(1)]),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/event/webinars/evt-0001"),
            HttpResponse(body=json.dumps({"id": "web-0001", "event": "evt-0001", "title": "Webinar 1"})),
        )

        output = _read("webinars")

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "web-0001"

    @HttpMocker()
    def test_event_members_paginates_within_its_parent_partition(self, http_mocker: HttpMocker):
        """`event_members` carries its partition in the URL's own query string, so the paginator has to
        add `limit`/`offset` alongside `event=` rather than replace it."""
        http_mocker.get(
            HttpRequest(url=_EVENTS_URL, query_params={"limit": str(_PAGE_SIZE)}),
            _envelope([_event(1)]),
        )
        members_url = f"{_BASE}/event/event-members"
        full_page = [{"id": f"mem-{i:04d}", "event": "evt-0001"} for i in range(_PAGE_SIZE)]
        http_mocker.get(
            HttpRequest(url=members_url, query_params={"event": "evt-0001", "limit": str(_PAGE_SIZE)}),
            _envelope(full_page, count=_PAGE_SIZE + 1),
        )
        http_mocker.get(
            HttpRequest(
                url=members_url,
                query_params={"event": "evt-0001", "limit": str(_PAGE_SIZE), "offset": str(_PAGE_SIZE)},
            ),
            _envelope([{"id": "mem-9999", "event": "evt-0001"}], count=_PAGE_SIZE + 1),
        )

        output = _read("event_members")

        assert len(output.records) == _PAGE_SIZE + 1
        assert "mem-9999" in {record.record.data["id"] for record in output.records}
