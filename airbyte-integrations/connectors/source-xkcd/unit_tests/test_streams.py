#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_xkcd.source import XkcdStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(XkcdStream, "path", "v0/example_endpoint")
    mocker.patch.object(XkcdStream, "primary_key", "test_primary_key")
    mocker.patch.object(XkcdStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = XkcdStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class):
    stream = XkcdStream()
    response = MagicMock()
    response.json.return_value = {
        "month": "10",
        "num": 2685,
        "link": "",
        "year": "2022",
        "news": "",
        "safe_title": "2045",
        "transcript": "",
        "alt": '"Sorry, doctor, I\'m going to have to come in on a different day--I have another appointment that would be really hard to move, in terms of the kinetic energy requirements."',
        "img": "https://imgs.xkcd.com/comics/2045.png",
        "title": "2045",
        "day": "14",
    }
    inputs = {"response": response}
    expected_token = {"next_token": 1}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = XkcdStream()
    response = MagicMock()
    response.json.return_value = {
        "month": "1",
        "num": 1,
        "link": "",
        "year": "2006",
        "news": "",
        "safe_title": "Barrel - Part 1",
        "transcript": "[[A boy sits in a barrel which is floating in an ocean.]]\nBoy: I wonder where I'll float next?\n[[The barrel drifts into the distance. Nothing else can be seen.]]\n{{Alt: Don't we all.}}",
        "alt": "Don't we all.",
        "img": "https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg",
        "title": "Barrel - Part 1",
        "day": "1",
    }
    inputs = {"response": response, "stream_state": None}
    expected_parsed_object = {
        "month": "1",
        "num": 1,
        "link": "",
        "year": "2006",
        "news": "",
        "safe_title": "Barrel - Part 1",
        "transcript": "[[A boy sits in a barrel which is floating in an ocean.]]\nBoy: I wonder where I'll float next?\n[[The barrel drifts into the distance. Nothing else can be seen.]]\n{{Alt: Don't we all.}}",
        "alt": "Don't we all.",
        "img": "https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg",
        "title": "Barrel - Part 1",
        "day": "1",
    }
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = XkcdStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = XkcdStream()
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
    stream = XkcdStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = XkcdStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
