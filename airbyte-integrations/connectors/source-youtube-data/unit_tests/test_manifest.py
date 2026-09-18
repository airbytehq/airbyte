# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards for the two halves of the 401-on-large-channel fix (oncall#13549).

The `video` substream issues one `videos.list` call per video. With hourly
api_budget windows, a channel with more videos than the budget allowed per
window blocked inside the limiter for up to an hour after the OAuth header was
attached, so the request went out with an expired access token and failed with
HTTP 401. These tests pin both parts of the fix:

1. every api_budget rate window is short enough that the blocking wait stays
   far below the 3600-second OAuth access-token lifetime, and
2. a 401 response triggers REFRESH_TOKEN_THEN_RETRY — the token is refreshed
   and the request retried — instead of failing as a config error.
"""

import json
import re
import time
from datetime import timedelta
from pathlib import Path
from unittest import TestCase, mock

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"

# The YouTube Data API v3 grants OAuth access tokens with a 3600-second lifetime.
_TOKEN_LIFETIME = timedelta(seconds=3600)
# The api_budget windows must keep the worst-case blocking wait far below that
# lifetime; per-minute windows bound it to about one minute.
_MAX_RATE_WINDOW = timedelta(minutes=1)

_CONFIG = {
    "credentials": {
        "auth_method": "oauth2.0",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "refresh_token": "test-refresh-token",
    },
    "channel_ids": ["UCxxxxxxxxxxxxxxxxxxxxxx"],
}
_BASE = "https://www.googleapis.com/youtube/v3"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
# The OAuthAuthenticator form-encodes its refresh args in this fixed order
# (grant_type, client credentials, refresh_token, scopes); HttpRequest body
# matching compares the encoded form verbatim.
_TOKEN_REQUEST_BODY = (
    "grant_type=refresh_token"
    "&client_id=test-client-id"
    "&client_secret=test-client-secret"
    "&refresh_token=test-refresh-token"
    "&scopes=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.force-ssl"
)

_INTERVAL_PATTERN = re.compile(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def _parse_iso8601_duration(value: str) -> timedelta:
    """Parses the restricted ISO-8601 durations used in manifest api_budget rates (PT..H..M..S)."""
    match = _INTERVAL_PATTERN.match(value)
    if not match:
        raise ValueError(f"Unsupported duration format: {value!r}")
    hours, minutes, seconds = (int(group) if group else 0 for group in match.groups())
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def _manifest() -> dict:
    return yaml.safe_load(_MANIFEST_PATH.read_text())


def _base_requester_filters(manifest: dict) -> list:
    error_handlers = manifest["definitions"]["base_requester"]["error_handler"]["error_handlers"]
    return [f for handler in error_handlers for f in handler.get("response_filters", [])]


def test_api_budget_windows_bounded_below_token_lifetime():
    policies = _manifest()["api_budget"]["policies"]

    matched_patterns = set()
    for policy in policies:
        for rate in policy["rates"]:
            interval = _parse_iso8601_duration(rate["interval"])
            assert interval <= _MAX_RATE_WINDOW, (
                f"api_budget window {rate['interval']} would let a request block past the "
                "3600s access-token lifetime; keep windows at PT1M or shorter"
            )
            assert interval < _TOKEN_LIFETIME
        for matcher in policy["matchers"]:
            matched_patterns.add(matcher["url_path_pattern"])

    # Both cost tiers from the quota model must be covered: the 100-unit
    # search.list and the 1-unit list endpoints.
    assert "/search" in matched_patterns
    assert "/(channels|videos|commentThreads)" in matched_patterns


def test_401_filter_uses_refresh_token_then_retry():
    filters_401 = [
        response_filter for response_filter in _base_requester_filters(_manifest()) if 401 in response_filter.get("http_codes", [])
    ]
    assert len(filters_401) == 1
    assert filters_401[0]["action"] == "REFRESH_TOKEN_THEN_RETRY"
    assert filters_401[0]["failure_type"] == "config_error"


class Test401RefreshesTokenAndRetries(TestCase):
    @HttpMocker()
    def test_401_refreshes_token_and_retries(self, http_mocker: HttpMocker):
        """A 401 mid-sync must refresh the OAuth token and retry, not fail as config_error.

        Reverts to FAIL action on the manifest's 401 filter to see this fail.
        """
        token_request = HttpRequest(url=_TOKEN_URL, body=_TOKEN_REQUEST_BODY)
        http_mocker.post(
            token_request,
            [
                HttpResponse(body=json.dumps({"access_token": "first-token", "expires_in": 3600})),
                HttpResponse(body=json.dumps({"access_token": "refreshed-token", "expires_in": 3600})),
            ],
        )

        channels_request = HttpRequest(
            url=f"{_BASE}/channels",
            query_params="any query_parameters",
        )
        unauthorized_body = {
            "error": {
                "code": 401,
                "message": "Invalid Credentials",
                "errors": [{"reason": "authError"}],
            }
        }
        http_mocker.get(
            channels_request,
            [
                HttpResponse(body=json.dumps(unauthorized_body), status_code=401),
                HttpResponse(body=json.dumps({"items": [{"id": "UCxxxxxxxxxxxxxxxxxxxxxx", "kind": "youtube#channel"}]})),
            ],
        )

        catalog = CatalogBuilder().with_stream("channels", SyncMode.full_refresh).build()
        # Skip real backoff sleeps so the retry is fast.
        with mock.patch.object(time, "sleep"):
            output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "UCxxxxxxxxxxxxxxxxxxxxxx"
        assert output.errors == [], output.get_formatted_error_message()
        # One token fetch for the initial request, one for the post-401 refresh.
        http_mocker.assert_number_of_calls(token_request, 2)
        http_mocker.assert_number_of_calls(channels_request, 2)
