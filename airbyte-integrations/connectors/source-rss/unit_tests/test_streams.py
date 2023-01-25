#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import time
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_rss.source import RssStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(RssStream, "path", "v0/example_endpoint")
    mocker.patch.object(RssStream, "primary_key", "test_primary_key")
    mocker.patch.object(RssStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = RssStream()
    # TODO: replace this with your input parameters
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    # TODO: replace this with your expected request parameters
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = RssStream()
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = RssStream()

    class SampleResponse:
        text = """""
                <?xml version="1.0" encoding="utf-8" ?>
                <rss version="2.0">
                    <channel>
                        <item>
                            <title>Test Title</title>
                            <link>http://testlink</link>
                            <description>Test Description</description>
                            <pubDate>Fri, 28 Oct 2022 11:16 EDT</pubDate>
                        </item>
                    </channel>
                </rss>
                """

    expected_parsed_object = {
        "title": "Test Title",
        "link": "http://testlink",
        "description": "Test Description",
        "published": "2022-10-28T15:16:00+00:00",
    }

    assert next(stream.parse_response(response=SampleResponse(), stream_state={})) == expected_parsed_object

    # test that the local timezone doesn't impact how this is computed
    os.environ['TZ'] = 'Africa/Accra'
    time.tzset()
    assert next(stream.parse_response(response=SampleResponse(), stream_state={})) == expected_parsed_object
    os.environ['TZ'] = 'Asia/Tokyo'
    time.tzset()
    assert next(stream.parse_response(response=SampleResponse(), stream_state={})) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = RssStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = RssStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = RssStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = RssStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
