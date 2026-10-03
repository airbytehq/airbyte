# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Pagination behavior of the incremental export paginators when `end_of_stream` is missing or explicit.

The manifest has three distinct `CursorPagination` strategies keyed on `end_of_stream`:
- `after_url_paginator` (tickets): cursor is `after_url`
- `end_of_stream_paginator` (organizations): cursor is `next_page`
- the inline paginator on `ticket_comments`: cursor is `next_page`

Each is covered by the same matrix: missing `end_of_stream`, explicit false, explicit true, and no cursor at all.
"""

import json
from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    OrganizationsRecordBuilder,
    OrganizationsResponseBuilder,
    TicketCommentsResponseBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"
_MISSING = object()


def _with_end_of_stream(response: HttpResponse, end_of_stream=_MISSING) -> HttpResponse:
    body = json.loads(response.body)
    if end_of_stream is _MISSING:
        body.pop("end_of_stream", None)
    else:
        body["end_of_stream"] = end_of_stream
    return HttpResponse(json.dumps(body), response.status_code)


def _without_cursor(response: HttpResponse) -> HttpResponse:
    body = json.loads(response.body)
    for key in ("end_of_stream", "after_url", "after_cursor", "next_page"):
        body.pop(key, None)
    return HttpResponse(json.dumps(body), response.status_code)


class _EndOfStreamPaginationTestCase(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])


@freezegun.freeze_time(_NOW.isoformat())
class TestAfterUrlPaginator(_EndOfStreamPaginationTestCase):
    """`after_url_paginator`, exercised through the `tickets` stream."""

    _BASE_URL = "https://d3v-airbyte.zendesk.com/api/v2/incremental/tickets/cursor.json"

    def _first_page(self, end_of_stream=_MISSING) -> HttpResponse:
        response = (
            TicketsResponseBuilder.tickets_response(self._BASE_URL, _A_CURSOR)
            .with_record(TicketsRecordBuilder.tickets_record().with_id(1))
            .with_pagination()
            .build()
        )
        return _with_end_of_stream(response, end_of_stream)

    def _mock_second_page(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(self._get_authenticator(self._config)).with_cursor(_A_CURSOR).build(),
            TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record().with_id(2)).build(),
        )

    def _first_page_request(self):
        return (
            ZendeskSupportRequestBuilder.tickets_endpoint(self._get_authenticator(self._config))
            .with_start_time(self._config["start_date"])
            .build()
        )

    @HttpMocker()
    def test_given_missing_end_of_stream_and_after_url_when_read_then_continue_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page())
        self._mock_second_page(http_mocker)

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert sorted(r.record.data["id"] for r in output.records) == [1, 2]

    @HttpMocker()
    def test_given_end_of_stream_false_and_after_url_when_read_then_continue_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page(end_of_stream=False))
        self._mock_second_page(http_mocker)

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert sorted(r.record.data["id"] for r in output.records) == [1, 2]

    @HttpMocker()
    def test_given_end_of_stream_true_and_after_url_when_read_then_stop_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page(end_of_stream=True))

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert [r.record.data["id"] for r in output.records] == [1]

    @HttpMocker()
    def test_given_no_end_of_stream_and_no_after_url_when_read_then_stop_pagination(self, http_mocker):
        response = TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record().with_id(1)).build()
        http_mocker.get(self._first_page_request(), _without_cursor(response))

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert [r.record.data["id"] for r in output.records] == [1]


@freezegun.freeze_time(_NOW.isoformat())
class TestEndOfStreamPaginator(_EndOfStreamPaginationTestCase):
    """`end_of_stream_paginator`, exercised through the `organizations` stream."""

    _BASE_URL = "https://d3v-airbyte.zendesk.com/api/v2/incremental/organizations"

    def _first_page(self, end_of_stream=_MISSING) -> HttpResponse:
        response = (
            OrganizationsResponseBuilder.organizations_response(self._BASE_URL, _A_CURSOR)
            .with_record(OrganizationsRecordBuilder.organizations_record().with_id(1))
            .with_pagination()
            .build()
        )
        return _with_end_of_stream(response, end_of_stream)

    def _first_page_request(self):
        return (
            ZendeskSupportRequestBuilder.organizations_endpoint(self._get_authenticator(self._config))
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build()
        )

    def _mock_second_page(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(self._get_authenticator(self._config)).with_cursor(_A_CURSOR).build(),
            OrganizationsResponseBuilder.organizations_response()
            .with_record(OrganizationsRecordBuilder.organizations_record().with_id(2))
            .build(),
        )

    @HttpMocker()
    def test_given_missing_end_of_stream_and_next_page_when_read_then_continue_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page())
        self._mock_second_page(http_mocker)

        output = read_stream("organizations", SyncMode.full_refresh, self._config)

        assert sorted(r.record.data["id"] for r in output.records) == [1, 2]

    @HttpMocker()
    def test_given_end_of_stream_false_and_next_page_when_read_then_continue_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page(end_of_stream=False))
        self._mock_second_page(http_mocker)

        output = read_stream("organizations", SyncMode.full_refresh, self._config)

        assert sorted(r.record.data["id"] for r in output.records) == [1, 2]

    @HttpMocker()
    def test_given_end_of_stream_true_and_next_page_when_read_then_stop_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page(end_of_stream=True))

        output = read_stream("organizations", SyncMode.full_refresh, self._config)

        assert [r.record.data["id"] for r in output.records] == [1]

    @HttpMocker()
    def test_given_no_end_of_stream_and_no_next_page_when_read_then_stop_pagination(self, http_mocker):
        response = (
            OrganizationsResponseBuilder.organizations_response()
            .with_record(OrganizationsRecordBuilder.organizations_record().with_id(1))
            .build()
        )
        http_mocker.get(self._first_page_request(), _without_cursor(response))

        output = read_stream("organizations", SyncMode.full_refresh, self._config)

        assert [r.record.data["id"] for r in output.records] == [1]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsPaginator(_EndOfStreamPaginationTestCase):
    """Inline paginator on the `ticket_comments` stream (one Comment child event per page in the template)."""

    _BASE_URL = "https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_events.json"

    def _first_page(self, end_of_stream=_MISSING) -> HttpResponse:
        response = TicketCommentsResponseBuilder.ticket_comments_response(self._BASE_URL, _A_CURSOR).with_pagination().build()
        return _with_end_of_stream(response, end_of_stream)

    def _first_page_request(self):
        return ZendeskSupportRequestBuilder.ticket_comments_endpoint(self._get_authenticator(self._config)).with_any_query_params().build()

    def _mock_second_page(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(self._get_authenticator(self._config))
            .with_cursor(_A_CURSOR)
            .with_include("comment_events")
            .with_per_page(100)
            .build(),
            TicketCommentsResponseBuilder.ticket_comments_response().build(),
        )

    @HttpMocker()
    def test_given_missing_end_of_stream_and_next_page_when_read_then_continue_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page())
        self._mock_second_page(http_mocker)

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_end_of_stream_false_and_next_page_when_read_then_continue_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page(end_of_stream=False))
        self._mock_second_page(http_mocker)

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_end_of_stream_true_and_next_page_when_read_then_stop_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), self._first_page(end_of_stream=True))

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_no_end_of_stream_and_no_next_page_when_read_then_stop_pagination(self, http_mocker):
        http_mocker.get(self._first_page_request(), _without_cursor(TicketCommentsResponseBuilder.ticket_comments_response().build()))

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1
