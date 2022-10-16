#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
import responses
from source_lever_hiring.streams import LeverHiringStream


def setup_responses():
    responses.add(
        responses.GET,
        "https://api.sandbox.lever.co/v0/example_endpoint",
        json={
            "data": [
                {
                    "id": "fake_id",
                    "name": "fake_name",
                    "contact": "fake_contact",
                    "headline": "Airbyte",
                    "stage": "offer",
                    "confidentiality": "non-confidential",
                    "location": "Los Angeles, CA",
                    "origin": "referred",
                    "createdAt": 1628510997134,
                    "updatedAt": 1628542848755,
                    "isAnonymized": False,
                },
                {
                    "id": "fake_id_2",
                    "name": "fake_name_2",
                    "contact": "fake_contact_2",
                    "headline": "Airbyte",
                    "stage": "applicant-new",
                    "confidentiality": "non-confidential",
                    "location": "Los Angeles, CA",
                    "origin": "sourced",
                    "createdAt": 1628509001183,
                    "updatedAt": 1628542849132,
                    "isAnonymized": False,
                },
            ],
            "hasNext": True,
            "next": "%5B1628543173558%2C%227bf8c1ac-4a68-450f-bea0-a1e2c3f5aeaf%22%5D",
        },
    )


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(LeverHiringStream, "path", "v0/example_endpoint")
    mocker.patch.object(LeverHiringStream, "primary_key", "test_primary_key")
    mocker.patch.object(LeverHiringStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, test_full_refresh_config):
    stream = LeverHiringStream(**test_full_refresh_config)
    inputs = {
        "stream_slice": {"slice": "test_slice"},
        "stream_state": {"updatedAt": 1600000000000},
        "next_page_token": {"offset": "next_page_cursor"},
    }
    expected_params = {"limit": stream.page_size, "offset": "next_page_cursor"}
    assert stream.request_params(**inputs) == expected_params


@responses.activate
def test_next_page_token(patch_base_class, test_full_refresh_config):
    setup_responses()
    stream = LeverHiringStream(**test_full_refresh_config)
    inputs = {"response": requests.get("https://api.sandbox.lever.co/v0/example_endpoint")}
    expected_token = {"offset": "%5B1628543173558%2C%227bf8c1ac-4a68-450f-bea0-a1e2c3f5aeaf%22%5D"}
    assert stream.next_page_token(**inputs) == expected_token


@responses.activate
def test_parse_response(patch_base_class, test_full_refresh_config):
    setup_responses()
    stream = LeverHiringStream(**test_full_refresh_config)
    inputs = {"response": requests.get("https://api.sandbox.lever.co/v0/example_endpoint")}
    expected_parsed_object = {
        "id": "fake_id",
        "name": "fake_name",
        "contact": "fake_contact",
        "headline": "Airbyte",
        "stage": "offer",
        "confidentiality": "non-confidential",
        "location": "Los Angeles, CA",
        "origin": "referred",
        "createdAt": 1628510997134,
        "updatedAt": 1628542848755,
        "isAnonymized": False,
    }
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class, test_full_refresh_config):
    stream = LeverHiringStream(**test_full_refresh_config)
    inputs = {
        "stream_slice": {"slice": "test_slice"},
        "stream_state": {"updatedAt": 1600000000000},
        "next_page_token": {"offset": "next_page_cursor"},
    }
    assert stream.request_headers(**inputs) == {}


def test_http_method(patch_base_class, test_full_refresh_config):
    stream = LeverHiringStream(**test_full_refresh_config)
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
def test_should_retry(patch_base_class, http_status, should_retry, test_full_refresh_config):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = LeverHiringStream(**test_full_refresh_config)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class, test_full_refresh_config):
    response_mock = MagicMock()
    stream = LeverHiringStream(**test_full_refresh_config)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
