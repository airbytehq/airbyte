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

    rate_by_pattern = {}
    for policy in policies:
        for rate in policy["rates"]:
            interval = _parse_iso8601_duration(rate["interval"])
            assert interval <= _MAX_RATE_WINDOW, (
                f"api_budget window {rate['interval']} would let a request block past the "
                "3600s access-token lifetime; keep windows at PT1M or shorter"
            )
            assert interval < _TOKEN_LIFETIME
            for matcher in policy["matchers"]:
                rate_by_pattern[matcher["url_path_pattern"]] = (rate["limit"], rate["interval"])

    # Both cost tiers from the quota model must be covered at the documented
    # per-minute rates: the search.list tier and the other list endpoints.
    assert rate_by_pattern["/search"] == (3, "PT1M")
    assert rate_by_pattern["/(channels|playlistItems|videos|commentThreads)"] == (100, "PT1M")


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

        unauthorized_body = {
            "error": {
                "code": 401,
                "message": "Invalid Credentials",
                "errors": [{"reason": "authError"}],
            }
        }
        # Header matching is subset-based, so each mock only matches the request
        # carrying its token: the first attempt (expired token) gets the 401 and
        # the retried request must carry the refreshed token to get the 200.
        expired_token_request = HttpRequest(
            url=f"{_BASE}/channels",
            query_params="any query_parameters",
            headers={"Authorization": "Bearer first-token"},
        )
        http_mocker.get(expired_token_request, HttpResponse(body=json.dumps(unauthorized_body), status_code=401))
        refreshed_token_request = HttpRequest(
            url=f"{_BASE}/channels",
            query_params="any query_parameters",
            headers={"Authorization": "Bearer refreshed-token"},
        )
        http_mocker.get(
            refreshed_token_request,
            HttpResponse(body=json.dumps({"items": [{"id": "UCxxxxxxxxxxxxxxxxxxxxxx", "kind": "youtube#channel"}]})),
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
        http_mocker.assert_number_of_calls(expired_token_request, 1)
        http_mocker.assert_number_of_calls(refreshed_token_request, 1)


class TestVideosFromUploadsPlaylist(TestCase):
    @HttpMocker()
    def test_videos_and_children_use_paginated_uploads_playlist(self, http_mocker: HttpMocker):
        http_mocker.post(
            HttpRequest(url=_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body=json.dumps({"access_token": "test-token", "expires_in": 3600})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/channels", query_params="any query_parameters"),
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {
                                "id": "UC-test",
                                "contentDetails": {"relatedPlaylists": {"uploads": "UU-test"}},
                            }
                        ]
                    }
                )
            ),
        )
        first_playlist_request = HttpRequest(
            url=f"{_BASE}/playlistItems",
            query_params={"playlistId": "UU-test", "part": "snippet", "maxResults": "50"},
        )
        http_mocker.get(
            first_playlist_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [{"snippet": {"resourceId": {"kind": "youtube#video", "videoId": "video-1"}}}],
                        "nextPageToken": "page-2",
                    }
                )
            ),
        )
        second_playlist_request = HttpRequest(
            url=f"{_BASE}/playlistItems",
            query_params={
                "playlistId": "UU-test",
                "part": "snippet",
                "maxResults": "50",
                "pageToken": "page-2",
            },
        )
        http_mocker.get(
            second_playlist_request,
            HttpResponse(body=json.dumps({"items": [{"snippet": {"resourceId": {"kind": "youtube#video", "videoId": "video-2"}}}]})),
        )
        catalog = CatalogBuilder().with_stream("videos", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == [], output.get_formatted_error_message()
        video_ids = {record.record.data["videoId"] for record in output.records if record.record.stream == "videos"}
        assert video_ids == {"video-1", "video-2"}
        http_mocker.assert_number_of_calls(first_playlist_request, 1)
        http_mocker.assert_number_of_calls(second_playlist_request, 1)


class TestVideoChildrenFromUploadsPlaylist(TestCase):
    @HttpMocker()
    def test_video_child_receives_upload_playlist_video_id(self, http_mocker: HttpMocker):
        http_mocker.post(
            HttpRequest(url=_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body=json.dumps({"access_token": "test-token", "expires_in": 3600})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/channels", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU-test"}}}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/playlistItems", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"snippet": {"resourceId": {"videoId": "video-1"}}}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/videos", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"id": "video-1", "snippet": {"title": "One"}}]})),
        )

        catalog = CatalogBuilder().with_stream("video", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data["videoId"] for record in output.records] == ["video-1"]

    @HttpMocker()
    def test_deleted_video_returns_no_video_record_without_failing_sync(self, http_mocker: HttpMocker):
        http_mocker.post(
            HttpRequest(url=_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body=json.dumps({"access_token": "test-token", "expires_in": 3600})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/channels", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU-test"}}}]})),
        )
        playlist_request = HttpRequest(url=f"{_BASE}/playlistItems", query_params="any query_parameters")
        http_mocker.get(
            playlist_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {"snippet": {"resourceId": {"videoId": "video-ok"}}},
                            {"snippet": {"resourceId": {"videoId": "video-deleted"}}},
                        ]
                    }
                )
            ),
        )
        video_ok_request = HttpRequest(
            url=f"{_BASE}/videos",
            query_params={"id": "video-ok", "part": "snippet,contentDetails,statistics,player,status"},
        )
        http_mocker.get(
            video_ok_request,
            HttpResponse(body=json.dumps({"items": [{"id": "video-ok", "snippet": {"title": "OK"}}]})),
        )
        video_deleted_request = HttpRequest(
            url=f"{_BASE}/videos",
            query_params={"id": "video-deleted", "part": "snippet,contentDetails,statistics,player,status"},
        )
        http_mocker.get(
            video_deleted_request,
            HttpResponse(body=json.dumps({"items": []})),
        )

        catalog = CatalogBuilder().with_stream("video", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data["videoId"] for record in output.records] == ["video-ok"]
        http_mocker.assert_number_of_calls(playlist_request, 1)
        http_mocker.assert_number_of_calls(video_ok_request, 1)
        http_mocker.assert_number_of_calls(video_deleted_request, 1)

    @HttpMocker()
    def test_deleted_video_comments_are_ignored_without_dropping_valid_comments(self, http_mocker: HttpMocker):
        http_mocker.post(
            HttpRequest(url=_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body=json.dumps({"access_token": "test-token", "expires_in": 3600})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/channels", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU-test"}}}]})),
        )
        playlist_request = HttpRequest(url=f"{_BASE}/playlistItems", query_params="any query_parameters")
        http_mocker.get(
            playlist_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {"snippet": {"resourceId": {"videoId": "video-ok"}}},
                            {"snippet": {"resourceId": {"videoId": "video-deleted"}}},
                        ]
                    }
                )
            ),
        )
        comments_ok_request = HttpRequest(
            url=f"{_BASE}/commentThreads",
            query_params={"part": "snippet,replies", "videoId": "video-ok"},
        )
        http_mocker.get(
            comments_ok_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {
                                "snippet": {
                                    "videoId": "video-ok",
                                    "topLevelComment": {"id": "comment-ok"},
                                }
                            }
                        ]
                    }
                )
            ),
        )
        comments_deleted_request = HttpRequest(
            url=f"{_BASE}/commentThreads",
            query_params={"part": "snippet,replies", "videoId": "video-deleted"},
        )
        http_mocker.get(
            comments_deleted_request,
            HttpResponse(
                body=json.dumps(
                    {
                        "error": {
                            "code": 404,
                            "message": "Video not found",
                            "errors": [{"reason": "videoNotFound"}],
                        }
                    }
                ),
                status_code=404,
            ),
        )

        catalog = CatalogBuilder().with_stream("comments", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data["videoId"] for record in output.records] == ["video-ok"]
        assert [record.record.data["id"] for record in output.records] == ["comment-ok"]
        http_mocker.assert_number_of_calls(playlist_request, 1)
        http_mocker.assert_number_of_calls(comments_ok_request, 1)
        http_mocker.assert_number_of_calls(comments_deleted_request, 1)

    @HttpMocker()
    def test_comments_child_receives_upload_playlist_video_id(self, http_mocker: HttpMocker):
        http_mocker.post(
            HttpRequest(url=_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
            HttpResponse(body=json.dumps({"access_token": "test-token", "expires_in": 3600})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/channels", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU-test"}}}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/playlistItems", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"snippet": {"resourceId": {"videoId": "video-1"}}}]})),
        )
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/commentThreads", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"snippet": {"topLevelComment": {"id": "comment-1"}, "videoId": "video-1"}}]})),
        )

        catalog = CatalogBuilder().with_stream("comments", SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        assert output.errors == [], output.get_formatted_error_message()
        assert [record.record.data["videoId"] for record in output.records] == ["video-1"]
