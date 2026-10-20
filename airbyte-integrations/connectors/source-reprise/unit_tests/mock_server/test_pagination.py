# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""DefaultPaginator + OffsetIncrement(page_size=10000, inject_on_first_request=true)."""

from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import (
    NOW,
    PAGE_SIZE,
    config,
    data_request,
    data_response,
    login_request,
    login_response,
)


_STREAM_NAME = "replay_change_feed"


def _record(index: int) -> dict:
    return {
        "entity_id": f"entity-{index}",
        "changed_at": "2026-08-20 01:00:00",
        "change_type": "updated",
        "entity_type": "replay",
        "ingested_at": "2026-08-20 01:00:00",
    }


def _read() -> object:
    return read(
        get_source(config=config()),
        config=config(),
        catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
    )


@freezegun.freeze_time(NOW)
class TestOffsetPagination(TestCase):
    @HttpMocker()
    def test_given_full_page_when_read_then_next_page_is_requested_with_offset_10000(self, http_mocker: HttpMocker) -> None:
        first_page = [_record(index) for index in range(PAGE_SIZE)]
        last_record = {**_record(PAGE_SIZE), "entity_id": "entity-final"}
        http_mocker.post(login_request(), login_response())
        # `offset=0` and `limit=10000` are both injected on the first request.
        http_mocker.get(data_request(_STREAM_NAME, offset=0), data_response(first_page))
        # A full page must be followed by exactly one more request at offset=page_size.
        http_mocker.get(data_request(_STREAM_NAME, offset=PAGE_SIZE), data_response([last_record]))

        output = _read()

        assert output.errors == []
        assert len(output.records) == PAGE_SIZE + 1
        assert output.records[0].record.data["entity_id"] == "entity-0"
        assert output.records[-1].record.data["entity_id"] == "entity-final"

    @HttpMocker()
    def test_given_short_page_when_read_then_pagination_stops(self, http_mocker: HttpMocker) -> None:
        # Only offset=0 is mocked. HttpMocker raises on any unmatched request, so a second
        # page request would fail this test.
        http_mocker.post(login_request(), login_response())
        http_mocker.get(data_request(_STREAM_NAME, offset=0), data_response([_record(0), _record(1), _record(2)]))

        output = _read()

        assert output.errors == []
        assert len(output.records) == 3
        assert [record.record.data["entity_id"] for record in output.records] == ["entity-0", "entity-1", "entity-2"]
