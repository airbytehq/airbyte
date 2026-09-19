# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import calendar
import json
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import TicketCommentsResponseBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamFullRefresh(TestCase):
    """Test ticket_comments stream which uses incremental/ticket_events.json endpoint with custom extractor."""

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

    @HttpMocker()
    def test_given_one_page_when_read_ticket_comments_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        # Note: ticket_comments uses a custom extractor (ZendeskSupportExtractorEvents) that expects
        # ticket_events response format with nested child_events. Using with_any_query_params()
        # because the start_time parameter is dynamically calculated based on config start_date.
        # The template already has the correct nested structure, so we don't use .with_record().
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketCommentsResponseBuilder.ticket_comments_response().build(),
        )

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamIncremental(TestCase):
    """Test ticket_comments stream incremental sync."""

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

    @HttpMocker()
    def test_given_no_state_when_read_ticket_comments_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        # Note: Using with_any_query_params() because the start_time parameter is dynamically
        # calculated based on config start_date. The template already has the correct nested
        # structure, so we don't use .with_record().
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketCommentsResponseBuilder.ticket_comments_response().build(),
        )

        output = read_stream("ticket_comments", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_comments"

    @HttpMocker()
    def test_given_state_when_read_ticket_comments_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))

        # Note: Using with_any_query_params() because the start_time parameter is dynamically
        # calculated based on state cursor value. The template already has the correct nested
        # structure, so we don't use .with_record().
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketCommentsResponseBuilder.ticket_comments_response().build(),
        )

        state = StateBuilder().with_stream_state("ticket_comments", {"timestamp": str(int(state_cursor_value.timestamp()))}).build()

        output = read_stream("ticket_comments", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_comments"


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsPageSizeReduction(TestCase):
    """Zendesk answers a `ticket_events` page it cannot assemble in time with a 504.

    The connector re-issues that same page with a smaller `per_page` rather than repeating the identical
    request, which is the only thing that changes what the endpoint has to do.
    """

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

    def _request(self, per_page):
        return (
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(self._get_authenticator(self._config))
            .with_include("comment_events")
            .with_start_time(_START_DATE)
            .with_per_page(per_page)
            .build()
        )

    @staticmethod
    def _timed_out():
        return HttpResponse(json.dumps({"error": "Gateway timeout"}), 504)

    @HttpMocker()
    @patch("time.sleep")
    def test_given_a_page_times_out_when_read_then_request_it_again_at_a_smaller_page_size(self, _, http_mocker):
        http_mocker.get(self._request(100), self._timed_out())
        http_mocker.get(self._request(50), self._timed_out())
        http_mocker.get(self._request(25), TicketCommentsResponseBuilder.ticket_comments_response().build())

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        # HttpMocker fails the test if any of the three requests above was never made, so reaching this
        # point is what pins the 100 -> 50 -> 25 sequence.
        assert len(output.records) == 1

    @HttpMocker()
    @patch("time.sleep")
    def test_given_a_later_page_times_out_when_read_then_rewrite_the_page_size_inside_the_next_page_url(self, _, http_mocker):
        # Zendesk builds the next page itself and echoes the page size back inside that URL, so the reduced
        # size has to replace `per_page` there. Sent next to it the request would carry two, and the API
        # would keep serving the page it already could not assemble.
        start_time = calendar.timegm(_START_DATE.utctimetuple())
        next_page_url = f"https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_events.json?start_time={start_time}&per_page=100"

        http_mocker.get(
            self._request(100),
            TicketCommentsResponseBuilder.ticket_comments_response(url=next_page_url, cursor="second-page").with_pagination().build(),
        )
        http_mocker.get(self._second_page_request(100), self._timed_out())
        http_mocker.get(self._second_page_request(50), TicketCommentsResponseBuilder.ticket_comments_response().build())

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2

    def _second_page_request(self, per_page):
        return (
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(self._get_authenticator(self._config))
            .with_include("comment_events")
            .with_start_time(_START_DATE)
            .with_per_page(per_page)
            .with_cursor("second-page")
            .build()
        )
