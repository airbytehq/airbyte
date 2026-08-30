# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the `videos` search stream and the substreams partitioned by its records."""

from urllib.parse import parse_qs, urlparse

import requests_mock
from _helpers import read_stream


_CHANNEL_A = "UCJr72fY4cTaNZv7WPbvjaSw"
_CHANNEL_B = "UC8lxnUR_CzruT2KA6cb7p0Q"
_CONFIG = {
    "credentials": {"auth_method": "api_key", "api_key": "test-api-key"},
    "channel_ids": [_CHANNEL_A, _CHANNEL_B],
}
_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
_COMMENT_THREADS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

_SEARCH_RESULTS = {
    _CHANNEL_A: ["video-a1", "video-a2"],
    _CHANNEL_B: ["video-b1"],
}
_ALL_VIDEO_IDS = ["video-a1", "video-a2", "video-b1"]


def _query(request) -> dict:
    """Return the request's query parameters, preserving the case of the values."""
    return parse_qs(urlparse(request.url).query)


def _search_response(request, context) -> dict:
    channel_id = _query(request)["channelId"][0]
    return {
        "kind": "youtube#searchListResponse",
        "items": [
            {"kind": "youtube#searchResult", "etag": f"etag-{video_id}", "id": {"kind": "youtube#video", "videoId": video_id}}
            for video_id in _SEARCH_RESULTS[channel_id]
        ],
    }


def _mock_search(mocker) -> None:
    mocker.get(_SEARCH_URL, json=_search_response)


def _queries(mocker, path: str) -> list:
    return [_query(request) for request in mocker.request_history if request.path.lower() == path.lower()]


def test_videos_searches_one_channel_per_request_and_only_for_videos() -> None:
    with requests_mock.Mocker() as mocker:
        _mock_search(mocker)
        output = read_stream("videos", _CONFIG)

    expected_queries = [
        {"part": ["id"], "type": ["video"], "channelId": [channel_id], "maxResults": ["50"], "key": ["test-api-key"]}
        for channel_id in (_CHANNEL_A, _CHANNEL_B)
    ]
    assert sorted(_queries(mocker, "/youtube/v3/search"), key=lambda query: query["channelId"]) == sorted(
        expected_queries, key=lambda query: query["channelId"]
    )
    assert sorted(record.record.data["videoId"] for record in output.records) == _ALL_VIDEO_IDS
    assert all(record.record.data["kind"] == "youtube#video" for record in output.records)


def test_video_substream_partitions_on_video_ids() -> None:
    def videos_response(request, context) -> dict:
        video_id = _query(request)["id"][0]
        return {"items": [{"kind": "youtube#video", "id": video_id, "snippet": {"title": f"title-{video_id}"}}]}

    with requests_mock.Mocker() as mocker:
        _mock_search(mocker)
        mocker.get(_VIDEOS_URL, json=videos_response)
        output = read_stream("video", _CONFIG)

    assert sorted(query["id"][0] for query in _queries(mocker, "/youtube/v3/videos")) == _ALL_VIDEO_IDS
    assert sorted(record.record.data["videoId"] for record in output.records) == _ALL_VIDEO_IDS
    assert sorted(record.record.data["title"] for record in output.records) == [f"title-{video_id}" for video_id in _ALL_VIDEO_IDS]


def test_comments_substream_partitions_on_video_ids() -> None:
    def comment_threads_response(request, context) -> dict:
        video_id = _query(request)["videoId"][0]
        return {"items": [{"snippet": {"videoId": video_id, "totalReplyCount": 0}}]}

    with requests_mock.Mocker() as mocker:
        _mock_search(mocker)
        mocker.get(_COMMENT_THREADS_URL, json=comment_threads_response)
        output = read_stream("comments", _CONFIG)

    assert sorted(query["videoId"][0] for query in _queries(mocker, "/youtube/v3/commentThreads")) == _ALL_VIDEO_IDS
    assert sorted(record.record.data["videoId"] for record in output.records) == _ALL_VIDEO_IDS
