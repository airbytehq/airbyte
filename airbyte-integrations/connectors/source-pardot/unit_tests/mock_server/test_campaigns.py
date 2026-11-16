# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase
from urllib.parse import quote

import pytest

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import START_CURSOR
from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids, sent_queries, stream_state


_STREAM = "campaigns"
_PATH = "v5/objects/campaigns"
_FIELDS = "id,name,isDeleted,folderId,cost,parentCampaignId,createdById,updatedById,createdAt,updatedAt,salesforceId"


def _request(updated_at_from: str | list[str] = START_CURSOR) -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("deleted", "all")
        .with_query_param("orderBy", "updatedAt ASC")
        .with_query_param("updatedAtAfterOrEqualTo", updated_at_from)
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _campaign(campaign_id: int, updated_at: str = "2026-03-01T09:00:00-08:00") -> dict[str, Any]:
    return {
        "id": campaign_id,
        "name": f"Campaign {campaign_id}",
        "isDeleted": False,
        "folderId": 7,
        "cost": 1500,
        "parentCampaignId": 3,
        "createdById": 11,
        "updatedById": 11,
        "createdAt": "2026-02-01T08:00:00-08:00",
        "updatedAt": updated_at,
        "salesforceId": "701000000000001AAA",
    }


class TestCampaignsStream(TestCase):
    @HttpMocker()
    def test_first_sync_reads_two_pages_and_saves_the_start_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_campaign(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(
            _next_page_request().build(),
            page_response([_campaign(1001), _campaign(1002, updated_at="2026-03-01T09:00:05-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1003))
        assert output.records[0].record.data == _campaign(1)
        # A page that follows `nextPageUrl` sends `fields` and the page token, and no filter.
        assert sent_queries(http_mocker)[1] == f"fields={_FIELDS}&nextPageToken=page-2"
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        # Not the newest `updatedAt`. The first sync of every version 5 incremental stream saves the start date.
        assert stream_state(output) == {"updatedAt": START_CURSOR}

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        last_of_page = _campaign(1000, updated_at="2026-03-01T09:16:40-08:00")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_campaign(number) for number in range(1, 1000)] + [last_of_page]))
        http_mocker.get(
            _request(updated_at_from="2026-03-01T09:16:40-08:00").build(),
            page_response([_campaign(1001, updated_at="2026-03-01T09:16:41-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_second_sync_sends_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"updatedAt": "2026-03-01T09:00:05-12:00"}).build()
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request(updated_at_from="2026-03-01T09:00:05-12:00").build(),
            page_response([_campaign(1003, updated_at="2026-03-02T10:30:00-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert record_ids(output) == [1003]
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        # The saved value is the record's wall clock time with "-12:00" in place of its own offset.
        assert stream_state(output) == {"updatedAt": "2026-03-02T10:30:00-12:00"}


@pytest.mark.parametrize("offset", ["+01:00", "-08:00"])
def test_restart_sends_one_inclusive_filter_with_the_value_encoded(offset: str) -> None:
    # Past 100,000 records the API returns a full page with no page token, and the connector starts a new query from the
    # last record's cursor value.
    boundary = f"2026-03-01T09:16:40{offset}"
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(), page_response([_campaign(number) for number in range(1, 1000)] + [_campaign(1000, updated_at=boundary)])
        )
        http_mocker.get(_request(updated_at_from=boundary).build(), page_response([_campaign(1001, updated_at=boundary)]))

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1002))
        assert sent_queries(http_mocker)[-1] == (
            f"updatedAtAfterOrEqualTo={quote(boundary)}&limit=1000&fields={quote(_FIELDS)}&deleted=all&orderBy=updatedAt+ASC"
        )


def test_restart_reads_every_record_of_the_boundary_second() -> None:
    # The new query starts at the second of the page's last record: it reads that record again and every other record of that second.
    boundary = "2026-03-01T09:16:40-08:00"
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(), page_response([_campaign(number) for number in range(1, 1000)] + [_campaign(1000, updated_at=boundary)])
        )
        http_mocker.get(
            _request(updated_at_from=boundary).build(),
            page_response([_campaign(1000, updated_at=boundary), _campaign(1001, updated_at=boundary)]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1001)) + [1000, 1001]
