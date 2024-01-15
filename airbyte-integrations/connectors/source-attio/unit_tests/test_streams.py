#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock
import requests

import pytest
from source_attio.source import (
    AttioStream,
    WorkspaceMembers,
)


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AttioStream, "primary_key", "test_primary_key")
    mocker.patch.object(AttioStream, "__abstractmethods__", set())


# ABSTRACT STREAM CLASS TESTS


def test_request_headers(patch_base_class):
    stream = AttioStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {
        # Auth handled by HttpAuthenticator
        "Content-Type": "application/json"
    }
    assert stream.request_headers(**inputs) == expected_headers


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
    stream = AttioStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = AttioStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


# STREAM TESTS


@pytest.mark.parametrize(
    ("response_data", "expected"),
    [
        ([], []),
        (
            [
                {
                    "id": {
                        "workspace_id": "1eb8b8be-2b16-4795-81d8-6cd004812f92",
                        "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    },
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                }
            ],
            [
                {
                    "workspace_id": "1eb8b8be-2b16-4795-81d8-6cd004812f92",
                    "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                }
            ],
        ),
        (
            [
                {
                    "id": {
                        "workspace_id": "1eb8b8be-2b16-4795-81d8-6cd004812f92",
                        "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    },
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                },
                {
                    "id": {
                        "workspace_id": "d7df08f9-d8bf-4136-bfa5-88ebb0374c0e",
                        "workspace_member_id": "26e027da-fcc7-4a47-b784-8c6cb93476e5",
                    },
                    "first_name": "Bob",
                    "last_name": "Booley",
                    "avatar_url": "https://assets.attio.com/avatars/2f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "bob@example.com",
                    "access_level": "admin",
                    "created_at": "2023-03-13T23:20:19.285000000Z",
                },
            ],
            [
                {
                    "workspace_id": "1eb8b8be-2b16-4795-81d8-6cd004812f92",
                    "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                },
                {
                    "workspace_id": "d7df08f9-d8bf-4136-bfa5-88ebb0374c0e",
                    "workspace_member_id": "26e027da-fcc7-4a47-b784-8c6cb93476e5",
                    "first_name": "Bob",
                    "last_name": "Booley",
                    "avatar_url": "https://assets.attio.com/avatars/2f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "bob@example.com",
                    "access_level": "admin",
                    "created_at": "2023-03-13T23:20:19.285000000Z",
                },
            ],
        ),
    ],
)
def test_workspace_member_parse(patch_base_class, requests_mock, response_data, expected):
    stream = WorkspaceMembers()
    response = MagicMock()
    response.json.return_value = {"data": response_data}
    inputs = {"response": response, "stream_slice": None, "stream_state": None, "next_page_token": None}
    parsed = stream.parse_response(**inputs)
    assert parsed == expected
