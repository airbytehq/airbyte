#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging

import pytest
import requests
from source_netsuite.constraints import META_PATH, RECORD_PATH
from source_netsuite.source import SourceNetsuite, _extract_netsuite_error


FAKE_CONFIG = {
    "realm": "12345-sb1",
    "consumer_key": "ck",
    "consumer_secret": "cs",
    "token_key": "tk",
    "token_secret": "ts",
    "start_datetime": "2024-01-01T00:00:00Z",
    "window_in_days": 30,
}

BASE_URL = "https://12345-sb1.suitetalk.api.netsuite.com"
METADATA_URL = BASE_URL + META_PATH


# ---------------------------------------------------------------------------
# _extract_netsuite_error
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "status_code,json_body,text,expected",
    [
        pytest.param(
            400,
            {
                "o:errorDetails": [
                    {
                        "o:errorCode": "INSUFFICIENT_PERMISSION",
                        "detail": "You do not have permission to access this record.",
                    }
                ]
            },
            None,
            "INSUFFICIENT_PERMISSION: You do not have permission to access this record.",
            id="structured_error_details",
        ),
        pytest.param(
            400,
            {"o:errorDetails": [{"o:errorCode": "USER_ERROR"}]},
            None,
            'USER_ERROR: {"o:errorDetails": [{"o:errorCode": "USER_ERROR"}]}',
            id="error_code_without_detail_falls_back_to_response_text",
        ),
        pytest.param(
            400,
            {"o:errorDetails": []},
            None,
            '{"o:errorDetails": []}',
            id="empty_error_details_list",
        ),
        pytest.param(
            400,
            {"someOtherKey": "value"},
            None,
            '{"someOtherKey": "value"}',
            id="no_error_details_key",
        ),
        pytest.param(
            500,
            None,
            "Internal Server Error",
            "Internal Server Error",
            id="non_json_response",
        ),
        pytest.param(
            400,
            None,
            "",
            "400",
            id="empty_text_falls_back_to_status_code",
        ),
    ],
)
def test_extract_netsuite_error(status_code, json_body, text, expected):
    response = requests.Response()
    response.status_code = status_code
    if json_body is not None:
        response._content = json.dumps(json_body).encode("utf-8")
        response.headers["Content-Type"] = "application/json"
    else:
        response._content = (text or "").encode("utf-8")
    assert _extract_netsuite_error(response) == expected


# ---------------------------------------------------------------------------
# check_connection — success scenarios
# ---------------------------------------------------------------------------
def test_check_connection_success_no_object_types(requests_mock):
    requests_mock.get(METADATA_URL, json={"items": [{"name": "contact"}]})

    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), FAKE_CONFIG)

    assert ok is True
    assert error is None


def test_check_connection_success_with_object_types(requests_mock):
    requests_mock.get(METADATA_URL, json={"items": []})
    requests_mock.get(BASE_URL + RECORD_PATH + "contact", json={"items": [], "totalResults": 0})

    config = {**FAKE_CONFIG, "object_types": ["Contact"]}
    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), config)

    assert ok is True
    assert error is None


# ---------------------------------------------------------------------------
# check_connection — metadata-catalog failures
# ---------------------------------------------------------------------------
def test_check_connection_metadata_http_error_with_structured_error(requests_mock):
    requests_mock.get(
        METADATA_URL,
        status_code=401,
        json={
            "o:errorDetails": [
                {
                    "o:errorCode": "INVALID_LOGIN_ATTEMPT",
                    "detail": "Invalid login attempt.",
                }
            ]
        },
    )

    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), FAKE_CONFIG)

    assert ok is False
    assert "INVALID_LOGIN_ATTEMPT" in error
    assert "Invalid login attempt." in error
    assert METADATA_URL in error


def test_check_connection_metadata_http_error_plain_text(requests_mock):
    requests_mock.get(METADATA_URL, status_code=403, text="Forbidden")

    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), FAKE_CONFIG)

    assert ok is False
    assert "Forbidden" in error


def test_check_connection_metadata_connection_error(requests_mock):
    requests_mock.get(METADATA_URL, exc=requests.exceptions.ConnectionError("DNS resolution failed"))

    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), FAKE_CONFIG)

    assert ok is False
    assert "Unable to reach NetSuite" in error
    assert "realm" in error.lower() or "Account ID" in error


# ---------------------------------------------------------------------------
# check_connection — object_type validation failures
# ---------------------------------------------------------------------------
def test_check_connection_duplicate_object_types(requests_mock):
    requests_mock.get(METADATA_URL, json={"items": []})

    config = {**FAKE_CONFIG, "object_types": ["Contact", "Contact"]}
    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), config)

    assert ok is False
    assert "Duplicate" in error
    assert "Contact" in error


def test_check_connection_object_type_permission_error(requests_mock):
    requests_mock.get(METADATA_URL, json={"items": []})
    requests_mock.get(
        BASE_URL + RECORD_PATH + "campaign",
        status_code=400,
        json={
            "o:errorDetails": [
                {
                    "o:errorCode": "INSUFFICIENT_PERMISSION",
                    "detail": "Permission Violation: You need the 'Lists -> Marketing Campaigns' permission.",
                }
            ]
        },
    )

    config = {**FAKE_CONFIG, "object_types": ["Campaign"]}
    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), config)

    assert ok is False
    assert "Campaign" in error
    assert "INSUFFICIENT_PERMISSION" in error
    assert "permissions" in error.lower()


def test_check_connection_object_type_plain_400_error(requests_mock):
    requests_mock.get(METADATA_URL, json={"items": []})
    requests_mock.get(
        BASE_URL + RECORD_PATH + "badrecord",
        status_code=400,
        text="Bad Request",
    )

    config = {**FAKE_CONFIG, "object_types": ["BadRecord"]}
    source = SourceNetsuite()
    ok, error = source.check_connection(logging.getLogger(), config)

    assert ok is False
    assert "BadRecord" in error
    assert "Bad Request" in error
