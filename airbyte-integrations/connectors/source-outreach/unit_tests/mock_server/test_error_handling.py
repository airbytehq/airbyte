# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

import freezegun

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .request_builder import OutreachRequestBuilder
from .response_builder import error_response, page_response, resource
from .utils import given_token, read_stream, record_ids


# The shared `base_requester` error handler is the same for every stream, so these tests run on `accounts` only.
_STREAM = "accounts"
_NOW = datetime(2026, 11, 11, 12, 0, 0, tzinfo=timezone.utc)


def _request() -> HttpRequest:
    return OutreachRequestBuilder.endpoint("/accounts").build()


def _accounts_page() -> HttpResponse:
    return page_response([resource(1, "account", {"name": "Acme", "updatedAt": "2024-01-02T03:04:05.000Z"})])


class _Clock:
    """Freezes time and turns every `time.sleep` into a jump of the frozen clock, recording the waits."""

    def __init__(self) -> None:
        self.sleeps: list[float] = []
        self._freezer = freezegun.freeze_time(_NOW)
        self._patch = patch("time.sleep", side_effect=self._sleep)

    def _sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        # A zero-second sleep still has to move the clock, or the rate limiter never sees its window expire.
        self._frozen_time.tick(max(seconds, 0.001))

    def __enter__(self) -> "_Clock":
        self._frozen_time = self._freezer.start()
        self._patch.start()
        return self

    def __exit__(self, *args) -> None:
        self._patch.stop()
        self._freezer.stop()


class TestErrorHandling(TestCase):
    @HttpMocker()
    def test_403_fails_as_config_error_with_the_scope_outreach_names(self, http_mocker: HttpMocker) -> None:
        # Body captured from a live 403 on a token without the stream's scope.
        given_token(http_mocker)
        http_mocker.get(
            _request(),
            error_response(
                403,
                "unauthorizedOauthScope",
                "Unauthorized OAuth Scope",
                "Your authorization does not include the required scope 'accounts.read'.",
            ),
        )

        output = read_stream(_STREAM, SyncMode.full_refresh, expecting_exception=True)

        assert output.records == []
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == (
            "Outreach denied access: Your authorization does not include the required scope 'accounts.read'. "
            "Re-authenticate the source and grant the missing scope, or deselect this stream."
        )

    @HttpMocker()
    def test_403_without_an_error_detail_still_fails_as_config_error(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        http_mocker.get(_request(), HttpResponse(body="{}", status_code=403))

        output = read_stream(_STREAM, SyncMode.full_refresh, expecting_exception=True)

        assert output.records == []
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert output.errors[0].trace.error.message == (
            "Outreach denied access: the token lacks a required OAuth scope. "
            "Re-authenticate the source and grant the missing scope, or deselect this stream."
        )

    @HttpMocker()
    def test_404_fails_as_system_error_without_a_retry(self, http_mocker: HttpMocker) -> None:
        # Body captured from a live 404. No list endpoint documents a benign 404, so the CDK default (fail) applies.
        # The single mocked response also proves the request is not retried.
        given_token(http_mocker)
        http_mocker.get(
            _request(),
            error_response(404, "resourceNotFound", "Resource Not Found", "Could not find 'prospect' with ID '999999999'."),
        )

        output = read_stream(_STREAM, SyncMode.full_refresh, expecting_exception=True)

        assert output.records == []
        assert output.errors[0].trace.error.failure_type == FailureType.system_error
        assert "404" in output.errors[0].trace.error.message

    @HttpMocker()
    def test_429_waits_until_the_epoch_in_retry_after_then_retries(self, http_mocker: HttpMocker) -> None:
        # Body from https://developers.outreach.io/api/getting-started/#rate-limiting. Outreach sends the reset time,
        # a Unix epoch, as `Retry-After`.
        given_token(http_mocker)
        http_mocker.get(
            _request(),
            [
                error_response(
                    429,
                    "rateLimitExceeded",
                    "Rate Limit Exceeded",
                    "You have exceeded your permitted rate limit of 10,000; please try again at 2026-11-11T12:00:42.",
                    # No `X-RateLimit-Remaining` header here, so the budget assertion below rests on the 429 status alone.
                    headers={"Retry-After": str(int(_NOW.timestamp()) + 42)},
                ),
                _accounts_page(),
            ],
        )

        with _Clock() as clock:
            output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1]
        # 42 seconds until the reset, plus the second the CDK adds to a header-based wait.
        assert clock.sleeps[0] == 43
        # The API budget also counts the 429 as a used-up hour: with no earlier requests in its moving window, the
        # retry is held until a full hour after the 429.
        assert round(sum(clock.sleeps)) == 3600

    @HttpMocker()
    def test_503_with_an_iso_retry_after_falls_back_to_exponential_backoff(self, http_mocker: HttpMocker) -> None:
        # Body from the Maintenance section of https://developers.outreach.io/api/getting-started/. The header strategy
        # reads epochs only, so this ISO-8601 `Retry-After` is left to the exponential strategy.
        given_token(http_mocker)
        http_mocker.get(
            _request(),
            [
                error_response(
                    503,
                    "scheduledServerMaintenance",
                    "Scheduled Server Maintenance",
                    "Scheduled server maintenance is under way; please try again at 2026-11-11T12:30:00",
                    headers={"Retry-After": "2026-11-11T12:30:00Z"},
                ),
                _accounts_page(),
            ],
        )

        with _Clock() as clock:
            output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1]
        # factor 5 on the first retry: 5 * 2^1, plus the second the CDK adds.
        assert [seconds for seconds in clock.sleeps if seconds] == [11]

    @HttpMocker()
    def test_api_budget_holds_the_next_request_when_outreach_reports_no_calls_left(self, http_mocker: HttpMocker) -> None:
        given_token(http_mocker)
        next_url = OutreachRequestBuilder.endpoint("/accounts").next_page_url("eyJzcCI6InVwZGF0ZWRBdCJ9")
        http_mocker.get(
            _request(),
            page_response(
                [resource(1, "account", {"name": "Acme", "updatedAt": "2024-01-02T03:04:05.000Z"})],
                next_url=next_url,
                headers={"X-RateLimit-Remaining": "0"},
            ),
        )
        http_mocker.get(
            HttpRequest(next_url),
            page_response([resource(2, "account", {"name": "Globex", "updatedAt": "2024-01-03T03:04:05.000Z"})]),
        )

        with _Clock() as clock:
            output = read_stream(_STREAM, SyncMode.full_refresh)

        assert not output.errors
        assert record_ids(output) == [1, 2]
        # The budget is 10,000 requests per moving hour, so a window reported as used up frees after one hour.
        assert round(sum(clock.sleeps)) == 3600
