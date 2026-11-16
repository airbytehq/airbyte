# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Guards for the 1.1.0 quota rework.

`videos` enumerates a channel's uploads playlist (`playlistItems.list`, 1 quota
unit, returns unlisted/private uploads to the owner) instead of `search.list`
(100 units, public only, capped at 500 results); `video` and the new
`video_engagement` batch 50 ids per `videos.list` call; every stream except
`channels` is incremental with a newest-first data-feed cursor; and exhausting
the daily quota fails immediately instead of retrying against a limit that only
resets at midnight Pacific.
"""

import json
import time
from unittest import TestCase, mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_CHANNEL = "UCxxxxxxxxxxxxxxxxxxxxxx"
_UPLOADS = "UUxxxxxxxxxxxxxxxxxxxxxx"
_CONFIG = {
    "credentials": {"auth_method": "api_key", "api_key": "test-key"},
    "channel_ids": [_CHANNEL],
}
_BASE = "https://www.googleapis.com/youtube/v3"
_UPLOADS_PARAMS = {"part": "snippet,status", "playlistId": _UPLOADS, "maxResults": "50", "key": "test-key"}


def _playlist_item(video_id: str, published_at: str, privacy: str) -> dict:
    return {
        "kind": "youtube#playlistItem",
        "etag": "e",
        "id": f"item-{video_id}",
        "snippet": {
            "publishedAt": published_at,
            "channelId": _CHANNEL,
            "title": f"Title {video_id}",
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
        },
        "status": {"privacyStatus": privacy},
    }


def _uploads_page(*items: dict, next_page_token: str = None) -> HttpResponse:
    body = {"items": list(items)}
    if next_page_token:
        body["nextPageToken"] = next_page_token
    return HttpResponse(body=json.dumps(body))


def _read(http_mocker: HttpMocker, stream: str, state=None):
    if stream != "channel_comments":
        # `videos` is a substream of `channels`: every read that goes through it first
        # resolves the uploads playlist id. `channel_comments` partitions straight off config.
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/channels", query_params="any query_parameters"),
            HttpResponse(body=json.dumps({"items": [{"id": _CHANNEL, "contentDetails": {"relatedPlaylists": {"uploads": _UPLOADS}}}]})),
        )
    catalog = CatalogBuilder().with_stream(stream, SyncMode.incremental).build()
    with mock.patch.object(time, "sleep"):
        return read(get_source(_CONFIG, catalog, state), config=_CONFIG, catalog=catalog, state=state)


class TestVideosStream(TestCase):
    @HttpMocker()
    def test_reads_uploads_playlist_including_unlisted_and_private(self, http_mocker: HttpMocker):
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/playlistItems", query_params=_UPLOADS_PARAMS),
            _uploads_page(
                _playlist_item("pub", "2026-03-03T00:00:00Z", "public"),
                _playlist_item("unl", "2026-02-02T00:00:00Z", "unlisted"),
                _playlist_item("prv", "2026-01-01T00:00:00Z", "private"),
            ),
        )

        output = _read(http_mocker, "videos")

        assert output.errors == [], output.get_formatted_error_message()
        records = [r.record.data for r in output.records]
        assert [r["videoId"] for r in records] == ["pub", "unl", "prv"]
        assert [r["privacyStatus"] for r in records] == ["public", "unlisted", "private"]
        assert records[0] == {
            "kind": "youtube#video",
            "videoId": "pub",
            "channelId": _CHANNEL,
            "title": "Title pub",
            "publishedAt": "2026-03-03T00:00:00Z",
            "privacyStatus": "public",
        }

    @HttpMocker()
    def test_incremental_stops_paginating_at_stored_cursor(self, http_mocker: HttpMocker):
        """The uploads playlist lists newest first: once a page contains an item older than
        the stored cursor, the next page must not be requested."""
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/playlistItems", query_params=_UPLOADS_PARAMS),
            _uploads_page(
                _playlist_item("new", "2026-05-05T00:00:00Z", "public"),
                _playlist_item("seen", "2026-03-03T00:00:00Z", "public"),
                _playlist_item("older", "2026-01-01T00:00:00Z", "public"),
                next_page_token="page2",
            ),
        )
        # Page 2 is deliberately not mocked: if the cursor failed to stop pagination, the
        # unmatched request would surface in `output.errors`.

        state = (
            StateBuilder()
            .with_stream_state(
                "videos",
                {
                    "states": [
                        {
                            "partition": {"parent_slice": {"channel_id": _CHANNEL}, "playlistId": _UPLOADS},
                            "cursor": {"publishedAt": "2026-03-03T00:00:00Z"},
                        }
                    ]
                },
            )
            .build()
        )
        output = _read(http_mocker, "videos", state)

        assert output.errors == [], output.get_formatted_error_message()
        # The cursor window is inclusive, so the boundary item is re-emitted (idempotent on
        # the primary key); anything older on the same page is dropped and page 2 is never fetched.
        assert [r.record.data["videoId"] for r in output.records] == ["new", "seen"]
        assert output.most_recent_state.stream_state.states[0]["cursor"]["publishedAt"] == "2026-05-05T00:00:00Z"


class TestBatchedVideoStreams(TestCase):
    def _mock_three_uploads(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(url=f"{_BASE}/playlistItems", query_params=_UPLOADS_PARAMS),
            _uploads_page(
                _playlist_item("a", "2026-03-03T00:00:00Z", "public"),
                _playlist_item("b", "2026-02-02T00:00:00Z", "unlisted"),
                _playlist_item("c", "2026-01-01T00:00:00Z", "private"),
            ),
        )

    @HttpMocker()
    def test_video_fetches_all_parent_ids_in_one_request(self, http_mocker: HttpMocker):
        self._mock_three_uploads(http_mocker)
        details = HttpRequest(
            url=f"{_BASE}/videos",
            query_params={"part": "snippet,contentDetails,statistics,player,status", "id": "a,b,c", "key": "test-key"},
        )
        http_mocker.get(
            details,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {"id": v, "snippet": {"publishedAt": f"2026-0{i}-0{i}T00:00:00Z", "title": v}, "statistics": {"viewCount": "1"}}
                            for i, v in ((3, "a"), (2, "b"), (1, "c"))
                        ]
                    }
                )
            ),
        )

        output = _read(http_mocker, "video")

        assert output.errors == [], output.get_formatted_error_message()
        http_mocker.assert_number_of_calls(details, 1)
        assert [r.record.data["videoId"] for r in output.records] == ["a", "b", "c"]
        assert output.records[0].record.data["title"] == "a"

    @HttpMocker()
    def test_video_engagement_snapshots_statistics(self, http_mocker: HttpMocker):
        self._mock_three_uploads(http_mocker)
        stats = HttpRequest(url=f"{_BASE}/videos", query_params={"part": "statistics", "id": "a,b,c", "key": "test-key"})
        http_mocker.get(
            stats,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {
                                "kind": "youtube#video",
                                "etag": "e",
                                "id": v,
                                "statistics": {"viewCount": str(n), "likeCount": "2", "commentCount": "0"},
                            }
                            for v, n in (("a", 10), ("b", 20), ("c", 30))
                        ]
                    }
                )
            ),
        )

        output = _read(http_mocker, "video_engagement")

        assert output.errors == [], output.get_formatted_error_message()
        http_mocker.assert_number_of_calls(stats, 1)
        records = [r.record.data for r in output.records]
        assert [(r["videoId"], r["viewCount"]) for r in records] == [("a", "10"), ("b", "20"), ("c", "30")]
        assert "statistics" not in records[0] and "id" not in records[0]
        # The cursor is the fetch time, so the checkpoint advances to this sync.
        assert output.most_recent_state.stream_state.state["datetime"] == records[0]["datetime"]


class TestCommentStreams(TestCase):
    @HttpMocker()
    def test_channel_comments_request_full_pages_newest_first_and_hoist_cursor(self, http_mocker: HttpMocker):
        threads = HttpRequest(
            url=f"{_BASE}/commentThreads",
            query_params={
                "part": "snippet,replies",
                "order": "time",
                "maxResults": "100",
                "allThreadsRelatedToChannelId": _CHANNEL,
                "key": "test-key",
            },
        )
        http_mocker.get(
            threads,
            HttpResponse(
                body=json.dumps(
                    {
                        "items": [
                            {
                                "snippet": {
                                    "channelId": _CHANNEL,
                                    "totalReplyCount": 0,
                                    "topLevelComment": {
                                        "id": "t1",
                                        "snippet": {"publishedAt": "2026-04-04T00:00:00Z", "textDisplay": "hi"},
                                    },
                                }
                            }
                        ]
                    }
                )
            ),
        )

        output = _read(http_mocker, "channel_comments")

        assert output.errors == [], output.get_formatted_error_message()
        record = output.records[0].record.data
        assert record["id"] == "t1"
        assert record["publishedAt"] == "2026-04-04T00:00:00Z"


class TestDailyQuota(TestCase):
    @HttpMocker()
    def test_quota_exceeded_fails_without_retrying(self, http_mocker: HttpMocker):
        """The daily quota resets at midnight Pacific; retrying inside the sync cannot succeed."""
        uploads = HttpRequest(url=f"{_BASE}/playlistItems", query_params=_UPLOADS_PARAMS)
        http_mocker.get(
            uploads,
            HttpResponse(
                body=json.dumps(
                    {"error": {"code": 403, "message": "quota", "errors": [{"reason": "quotaExceeded", "domain": "youtube.quota"}]}}
                ),
                status_code=403,
            ),
        )

        output = _read(http_mocker, "videos")

        http_mocker.assert_number_of_calls(uploads, 1)
        assert output.errors, "exhausting the daily quota must fail the sync"
        assert "midnight Pacific" in output.get_formatted_error_message()
