#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

import pytest
import requests
import requests_mock
from requests.exceptions import HTTPError
from source_zendesk_support import SourceZendeskSupport
from source_zendesk_support.streams import Tags, TicketComments

CONFIG_FILE = "secrets/config.json"


@pytest.fixture(scope="module")
def prepare_stream_args():
    """Generates streams settings from a file"""
    with open(CONFIG_FILE, "r") as f:
        return SourceZendeskSupport.convert_config2stream_args(json.loads(f.read()))


@pytest.mark.parametrize(
    "header_name,header_value,expected",
    [
        # Retry-After > 0
        ("Retry-After", "123", 123),
        # Retry-Afte < 0
        ("Retry-After", "-123", None),
        # X-Rate-Limit > 0
        ("X-Rate-Limit", "100", 1.2),
        # X-Rate-Limit header < 0
        ("X-Rate-Limit", "-100", None),
        # Random header
        ("Fake-Header", "-100", None),
    ],
)
def test_backoff_cases(prepare_stream_args, header_name, header_value, expected):
    """Zendesk sends the header different value for backoff logic"""

    stream = Tags(**prepare_stream_args)
    with requests_mock.Mocker() as m:
        url = stream.url_base + stream.path()

        m.get(url, headers={header_name: header_value}, status_code=429)
        result = stream.backoff_time(requests.get(url))
        if expected:
            assert (result - expected) < 0.005
        else:
            assert result is None


@pytest.mark.parametrize(
    "status_code,expected_comment_count,expected_expection",
    [
        # success
        (200, 1, None),
        # not found ticket
        (404, 0, None),
        # some another code error.
        (403, 0, HTTPError),
    ],
)
def test_comments_not_found_ticket(prepare_stream_args, status_code, expected_comment_count, expected_expection):
    """Checks the case when some ticket is removed while sync of comments"""
    fake_id = 12345
    stream = TicketComments(**prepare_stream_args)
    with requests_mock.Mocker() as comment_mock:
        path = f"tickets/{fake_id}/comments.json"
        stream.path = Mock(return_value=path)
        url = stream.url_base + path
        comment_mock.get(
            url,
            status_code=status_code,
            json={
                "comments": [
                    {
                        "id": fake_id,
                        TicketComments.cursor_field: "2121-07-22T06:55:55Z",
                    }
                ]
            },
        )
        comments = stream.read_records(
            sync_mode=None,
            stream_slice={
                "id": fake_id,
            },
        )
        if expected_expection:
            with pytest.raises(expected_expection):
                next(comments)
        else:
            assert len(list(comments)) == expected_comment_count
