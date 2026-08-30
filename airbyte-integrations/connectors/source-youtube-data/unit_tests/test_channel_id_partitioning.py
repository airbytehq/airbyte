# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlsplit

import pytest
import requests_mock
from _helpers import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_BASE_URL = "https://www.googleapis.com/youtube/v3"
_CHANNEL_IDS = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "UCBR8-60-B28hp2BmDPdntcQ",
]
_CONFIG = {
    "credentials": {"auth_method": "api_key", "api_key": "test-key"},
    "channel_ids": _CHANNEL_IDS,
}
_INVALID_CHANNEL_ERROR = {
    "error": {
        "code": 400,
        "message": "Request contains an invalid argument.",
        "errors": [
            {
                "message": "Request contains an invalid argument.",
                "domain": "global",
                "reason": "badRequest",
            }
        ],
        "status": "INVALID_ARGUMENT",
    }
}
_MISSING_CHANNEL_MESSAGE = (
    'The channel identified by the <code><a href="/youtube/v3/docs/commentThreads/list'
    '#allThreadsRelatedToChannelId">allThreadsRelatedToChannelId</a></code> parameter could not be found.'
)
_MISSING_CHANNEL_ERROR = {
    "error": {
        "code": 404,
        "message": _MISSING_CHANNEL_MESSAGE,
        "errors": [
            {
                "message": _MISSING_CHANNEL_MESSAGE,
                "domain": "youtube.commentThread",
                "reason": "channelNotFound",
                "location": "channelId",
                "locationType": "parameter",
            }
        ],
    }
}


def _read(stream_name: str, config: dict = _CONFIG):
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog)


def _query(request, key: str) -> list[str]:
    return parse_qs(urlsplit(request.url).query).get(key, [])


def _error_messages(output) -> str:
    assert output.errors
    trace = output.errors[-1].trace
    assert trace and trace.error
    assert trace.error.failure_type == FailureType.config_error
    return "\n".join([trace.error.message] + [message.log.message for message in output.logs if message.log])


def test_videos_partition_channel_ids_into_separate_requests():
    response = {
        "items": [
            {"id": {"kind": "youtube#video", "videoId": "video-1"}},
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/search", json=response)
        output = _read("videos")

    search_requests = [request for request in mocker.request_history if request.path == "/youtube/v3/search"]
    assert len(search_requests) == 2
    assert sorted(_query(request, "channelId")[0] for request in search_requests) == sorted(_CHANNEL_IDS)
    assert all(len(_query(request, "channelId")) == 1 for request in search_requests)
    assert [record.record.data["videoId"] for record in output.records] == ["video-1", "video-1"]


def test_channel_comments_partition_channel_ids_into_separate_requests():
    response = {"items": [{"snippet": {"channelId": _CHANNEL_IDS[0]}}]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/commentThreads", json=response)
        output = _read("channel_comments")

    comment_requests = [request for request in mocker.request_history if request.path.lower() == "/youtube/v3/commentthreads"]
    assert len(comment_requests) == 2
    assert sorted(_query(request, "allThreadsRelatedToChannelId")[0] for request in comment_requests) == sorted(_CHANNEL_IDS)
    assert all(len(_query(request, "allThreadsRelatedToChannelId")) == 1 for request in comment_requests)
    assert all(_query(request, "part") == ["snippet,replies"] for request in comment_requests)
    assert len(output.records) == 2


def test_videos_invalid_channel_id_is_a_config_error():
    config = {**_CONFIG, "channel_ids": ["gameinformer"]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/search", status_code=400, json=_INVALID_CHANNEL_ERROR)
        output = _read("videos", config)

    assert 'Channel ID in "channel_ids" is not a valid YouTube channel ID.' in _error_messages(output)


def test_channel_comments_missing_channel_is_a_config_error():
    config = {**_CONFIG, "channel_ids": ["gameinformer"]}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/commentThreads", status_code=404, json=_MISSING_CHANNEL_ERROR)
        output = _read("channel_comments", config)

    assert 'Channel ID in "channel_ids" does not match an existing YouTube channel.' in _error_messages(output)


@pytest.mark.parametrize(
    ("stream_name", "child_path", "child_response"),
    [
        (
            "video",
            "videos",
            {"items": [{"id": "video-1", "snippet": {}}]},
        ),
        (
            "comments",
            "commentThreads",
            {"items": [{"snippet": {"channelId": _CHANNEL_IDS[0]}}]},
        ),
    ],
)
def test_video_substreams_read_videos_from_each_channel(stream_name: str, child_path: str, child_response: dict):
    search_responses = [
        {"items": [{"id": {"kind": "youtube#video", "videoId": "video-1"}}]},
        {"items": [{"id": {"kind": "youtube#video", "videoId": "video-2"}}]},
    ]
    config = _CONFIG

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/search", [{"json": response} for response in search_responses])
        mocker.get(f"{_BASE_URL}/{child_path}", json=child_response)
        output = _read(stream_name, config)

    child_requests = [request for request in mocker.request_history if request.path.lower() == f"/youtube/v3/{child_path}".lower()]
    assert len(child_requests) == 2
    assert sorted(_query(request, "id" if stream_name == "video" else "videoId")[0] for request in child_requests) == [
        "video-1",
        "video-2",
    ]
    assert output.records
