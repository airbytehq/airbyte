# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import calendar
import json
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest import TestCase
from unittest.mock import patch

import freezegun
import yaml

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketCommentsResponseBuilder
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


_START_TIME = calendar.timegm(_START_DATE.replace(microsecond=0).timetuple())
_FAILURE_MESSAGE_START = "Zendesk kept timing out on the same page of ticket events even at the smallest page size."


def _comment_event(event_id: int, timestamp: int) -> Dict[str, Any]:
    created_at = _START_DATE.add(timedelta(seconds=timestamp - _START_TIME)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "id": event_id,
        "ticket_id": event_id,
        "timestamp": timestamp,
        "via_reference_id": None,
        "child_events": [
            {
                "id": event_id,
                "event_type": "Comment",
                "body": f"comment {event_id}",
                "public": True,
                "author_id": 1,
                "created_at": created_at,
            }
        ],
    }


def _events_page(event_ids: List[int], end_time: Optional[int], end_of_stream: bool) -> HttpResponse:
    """A ticket_events page. `end_time` is the `generated_timestamp` of the last event, as Zendesk returns it."""
    timestamp = end_time if end_time is not None else _START_TIME
    body: Dict[str, Any] = {
        "ticket_events": [_comment_event(event_id, timestamp) for event_id in event_ids],
        "count": len(event_ids),
        "end_of_stream": end_of_stream,
        # Kept to show that the paginator no longer follows it: requesting this URL would not match any mock.
        "next_page": f"https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_events.json?include=comment_events&per_page=999&start_time={timestamp}",
    }
    if end_time is not None:
        body["end_time"] = end_time
    return HttpResponse(json.dumps(body), 200)


def _gateway_timeout() -> HttpResponse:
    return ErrorResponseBuilder.response_with_status(504).build()


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsPagination(TestCase):
    """The next page is requested as `start_time=<end_time>`, and a 504 halves `per_page` for the same page.

    Every test stays under the 10 requests per minute that the `api_budget` allows on incremental endpoints,
    since time is frozen and the budget's window never moves.
    """

    def _config(self, page_size: Optional[Any] = None) -> Dict[str, Any]:
        config = (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )
        if page_size is not None:
            config["page_size"] = page_size
        return config

    def _request(self, config: Dict[str, Any], start_time: int, per_page: int):
        authenticator = ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])
        return (
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(authenticator)
            .with_include("comment_events")
            .with_per_page(per_page)
            .with_start_time(start_time)
            .build()
        )

    def _read(self, config: Dict[str, Any], expecting_exception: bool = False):
        with patch("time.sleep", return_value=None) as sleep:
            output = read_stream("ticket_comments", SyncMode.full_refresh, config, expecting_exception=expecting_exception)
        return output, sleep

    @staticmethod
    def _record_ids(output) -> List[int]:
        return [record.record.data["id"] for record in output.records]

    @HttpMocker()
    def test_given_two_pages_when_read_then_second_page_requested_with_start_time_from_end_time(self, http_mocker):
        """Exact query matching also proves no parameter is sent twice: the cursor's own `start_time` is not
        added next to the page token, and `include`/`per_page` are present exactly once on every page."""
        config = self._config(page_size=500)
        http_mocker.get(self._request(config, _START_TIME, 500), _events_page([1, 2], end_time=_START_TIME + 100, end_of_stream=False))
        http_mocker.get(self._request(config, _START_TIME + 100, 500), _events_page([3], end_time=_START_TIME + 200, end_of_stream=True))

        output, _ = self._read(config)

        assert self._record_ids(output) == [1, 2, 3]

    @HttpMocker()
    def test_given_page_size_missing_when_read_then_request_1000_per_page(self, http_mocker):
        config = self._config()
        http_mocker.get(self._request(config, _START_TIME, 1000), _events_page([1], end_time=_START_TIME + 100, end_of_stream=True))

        output, _ = self._read(config)

        assert self._record_ids(output) == [1]

    @HttpMocker()
    def test_given_stored_page_size_100_when_read_then_migrated_to_1000(self, http_mocker):
        """The read uses the migrated config, so the old default takes effect on the first sync after upgrade."""
        config = self._config(page_size=100)
        http_mocker.get(self._request(config, _START_TIME, 1000), _events_page([1], end_time=_START_TIME + 100, end_of_stream=True))

        output, _ = self._read(config)

        assert self._record_ids(output) == [1]

    @HttpMocker()
    def test_given_lowered_page_size_when_read_then_kept(self, http_mocker):
        config = self._config(page_size=50)
        http_mocker.get(self._request(config, _START_TIME, 50), _events_page([1], end_time=_START_TIME + 100, end_of_stream=True))

        output, _ = self._read(config)

        assert self._record_ids(output) == [1]

    @HttpMocker()
    def test_given_response_without_end_time_when_read_then_stop(self, http_mocker):
        """Without `end_time` there is no next page token, so the read ends instead of re-requesting the first page."""
        config = self._config()
        http_mocker.get(self._request(config, _START_TIME, 1000), _events_page([1], end_time=None, end_of_stream=False))

        output, _ = self._read(config)

        assert self._record_ids(output) == [1]

    @HttpMocker()
    def test_given_504_when_read_then_same_page_reissued_at_half_size_and_next_page_back_to_configured_size(self, http_mocker):
        config = self._config()
        http_mocker.get(self._request(config, _START_TIME, 1000), _events_page([1], end_time=_START_TIME + 100, end_of_stream=False))
        http_mocker.get(self._request(config, _START_TIME + 100, 1000), _gateway_timeout())
        http_mocker.get(self._request(config, _START_TIME + 100, 500), _events_page([2], end_time=_START_TIME + 200, end_of_stream=False))
        # AFTER_SUCCESSFUL_PAGE: the page after the reduced one goes back to the configured size.
        http_mocker.get(self._request(config, _START_TIME + 200, 1000), _events_page([3], end_time=_START_TIME + 300, end_of_stream=True))

        output, sleep = self._read(config)

        assert self._record_ids(output) == [1, 2, 3]
        assert any(call.args == (10,) for call in sleep.call_args_list), "the reduction waits backoff_seconds before re-issuing"

    @HttpMocker()
    def test_given_repeated_504_when_read_then_records_of_reissued_page_emitted_once(self, http_mocker):
        config = self._config(page_size=400)
        http_mocker.get(self._request(config, _START_TIME, 400), _gateway_timeout())
        http_mocker.get(self._request(config, _START_TIME, 200), _gateway_timeout())
        http_mocker.get(self._request(config, _START_TIME, 100), _events_page([1, 2], end_time=_START_TIME + 100, end_of_stream=False))
        http_mocker.get(self._request(config, _START_TIME + 100, 400), _events_page([3], end_time=_START_TIME + 200, end_of_stream=True))

        output, _ = self._read(config)

        assert self._record_ids(output) == [1, 2, 3]

    @HttpMocker()
    def test_given_504_down_to_one_record_per_page_when_read_then_fail_with_failure_message(self, http_mocker):
        """8 -> 4 -> 2 -> 1, then 3 retries at 1: 7 requests for the page before the stream fails."""
        config = self._config(page_size=8)
        for per_page in (8, 4, 2):
            http_mocker.get(self._request(config, _START_TIME, per_page), _gateway_timeout())
        http_mocker.get(self._request(config, _START_TIME, 1), [_gateway_timeout() for _ in range(4)])

        output, _ = self._read(config, expecting_exception=True)

        assert not output.records
        errors = [error.trace.error for error in output.errors]
        assert any(
            error.failure_type == FailureType.transient_error and _FAILURE_MESSAGE_START in (error.message or "") for error in errors
        ), errors


def _ticket_comments_page_size_reduction() -> Dict[str, Any]:
    manifest = yaml.safe_load((Path(__file__).parent.parent.parent / "manifest.yaml").read_text())
    return manifest["definitions"]["ticket_comments_stream"]["retriever"]["page_size_reduction"]


def test_page_size_reduction_can_reach_its_floor_from_the_largest_page_size():
    """The mock server cannot walk 1000 -> 1 within the api_budget, so check the arithmetic instead: an
    unbroken run of 504s must reach `minimum_page_size` before `max_attempts` runs out."""
    reduction = _ticket_comments_page_size_reduction()
    page_size, reductions = 1000, 0
    while page_size > reduction["minimum_page_size"]:
        page_size = max(reduction["minimum_page_size"], int(page_size // reduction["reduction_factor"]))
        reductions += 1

    assert reductions <= reduction["max_attempts"]
    assert reduction["reset_policy"] == "AFTER_SUCCESSFUL_PAGE"
