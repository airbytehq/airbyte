# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the Pipedrive error handlers declared in `manifest.yaml`.

Pipedrive returns a JSON envelope `{"success": false, "error": "..."}` for most failures, but
repeated rate-limit abuse can also produce a Cloudflare HTML 403 with no JSON body. These tests
assert how each status code is classified (fail / ignore / retry / rate-limited), that the
user-facing messages include Pipedrive's `error` text when present, and that substreams skip a
single missing or inaccessible parent instead of failing the whole sync.
"""

import logging

import pytest
from _helpers import CONFIG, collection, deals_request, get_source, pipedrive_error, read_stream, request

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def _error_trace(output):
    """Return the stream-level error trace (the last trace is the aggregated 'streams did not sync' summary)."""
    assert output.errors, "expected the sync to emit an error trace message"
    return output.errors[0].trace.error


def test_401_fails_as_config_error_with_pipedrive_error_text() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(401, "unauthorized access"))

        output = read_stream("deals", expecting_exception=True)

        error = _error_trace(output)
        assert error.failure_type == FailureType.config_error
        assert "401: unauthorized access" in error.message
        assert "Personal preferences > API" in error.message
        http_mocker.assert_number_of_calls(deals, 1)


def test_check_with_invalid_token_returns_401_config_message() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(401, "unauthorized access"))

        status = get_source().check(logging.getLogger("airbyte"), CONFIG)

        assert status.status == Status.FAILED
        assert "Pipedrive rejected the API token (401: unauthorized access)" in status.message


def test_402_fails_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(402, "company account not open"))

        error = _error_trace(read_stream("deals", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "402: company account not open" in error.message
        assert "billing" in error.message


def test_403_fails_as_config_error_with_pipedrive_error_text() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, pipedrive_error(403, "You do not have permissions to do this."))

        error = _error_trace(read_stream("deals", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "403: You do not have permissions to do this." in error.message


def test_403_html_body_from_cloudflare_still_produces_readable_message() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            HttpResponse(body="<html><body>Access denied</body></html>", status_code=403, headers={"Content-Type": "text/html"}),
        )

        error = _error_trace(read_stream("deals", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "Pipedrive refused the request (403)." in error.message
        assert "Cloudflare" in error.message


def test_429_is_rate_limited_and_retried_after_ratelimit_reset() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            [
                pipedrive_error(429, "request over limit", headers={"x-ratelimit-reset": "2", "x-ratelimit-remaining": "0"}),
                collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]),
            ],
        )

        output = read_stream("deals")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1]
        http_mocker.assert_number_of_calls(deals, 2)
        assert output.is_in_logs("Pipedrive rate limit reached")


def test_429_exhausting_retries_fails_as_rate_limited() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            pipedrive_error(429, "request over limit", headers={"x-ratelimit-reset": "2"}),
        )

        output = read_stream("deals", expecting_exception=True)

        assert output.errors
        # max_retries: 10 -> 1 initial attempt + 10 retries; the CDK then gives up with its generic backoff exception,
        # so the Pipedrive-specific hint about the daily budget is surfaced through the logs.
        http_mocker.assert_number_of_calls(deals, 11)
        assert output.is_in_logs("daily API token budget")


@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
def test_5xx_is_retried(status_code: int) -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            [
                pipedrive_error(status_code, None),
                collection([{"id": 7, "update_time": "2024-02-01 00:00:00"}]),
            ],
        )

        output = read_stream("deals")

        assert not output.errors
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(deals, 2)


def _deal_products_request(deal_id: int):
    return request(f"v1/deals/{deal_id}/products")


@pytest.mark.parametrize(
    "status_code, error",
    [
        (403, "You do not have permissions to do this."),
        (404, "Deal not found"),
        (410, "Deal has been deleted"),
    ],
)
def test_deal_products_skips_missing_or_forbidden_parent_deal(status_code: int, error: str) -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(
            deals,
            collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}, {"id": 2, "update_time": "2024-02-01 00:00:00"}]),
        )
        missing_deal = _deal_products_request(1)
        http_mocker.get(missing_deal, pipedrive_error(status_code, error))
        http_mocker.get(_deal_products_request(2), collection([{"id": 20, "deal_id": 2, "product_id": 5}]))

        output = read_stream("deal_products")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [20]
        http_mocker.assert_number_of_calls(missing_deal, 1)
        assert output.is_in_logs(error)


def test_deal_products_still_fails_on_401() -> None:
    with HttpMocker() as http_mocker:
        deals = deals_request()
        http_mocker.get(deals, collection([{"id": 1, "update_time": "2024-02-01 00:00:00"}]))
        http_mocker.get(_deal_products_request(1), pipedrive_error(401, "unauthorized access"))

        error = _error_trace(read_stream("deal_products", expecting_exception=True))

        assert error.failure_type == FailureType.config_error
        assert "401: unauthorized access" in error.message


def _mail_threads_request(folder: str):
    return request("v1/mailbox/mailThreads", {"folder": folder})


def _mail_messages_request(thread_id: int):
    return request(f"v1/mailbox/mailThreads/{thread_id}/mailMessages")


def test_mail_skips_missing_parent_thread() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_mail_threads_request("inbox"), collection([{"id": 10}, {"id": 11}]))
        for folder in ("drafts", "sent", "archive"):
            http_mocker.get(_mail_threads_request(folder), collection([]))
        http_mocker.get(_mail_messages_request(10), pipedrive_error(404, "Mail thread not found"))
        http_mocker.get(_mail_messages_request(11), collection([{"id": 110, "mail_thread_id": 11}]))

        output = read_stream("mail")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [110]
