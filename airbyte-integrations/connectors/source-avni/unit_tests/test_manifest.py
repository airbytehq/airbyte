# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import pytest
import requests_mock
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.auth import token_provider
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "username": "avni-user@example.org",
    "password": "avni-password",
    "start_date": "2000-06-23T01:30:00.000Z",
}
_IDP_URL = "https://app.avniproject.org/idp-details"
_COGNITO_URL = "https://cognito-idp.ap-south-1.amazonaws.com/"
_DATA_URLS = {
    "subjects": "https://app.avniproject.org/api/subjects",
    "program_enrolments": "https://app.avniproject.org/api/programEnrolments",
    "program_encounters": "https://app.avniproject.org/api/programEncounters",
    "encounters": "https://app.avniproject.org/api/encounters",
}
_CLIENT_ID = "avni-cognito-client-id"
_ID_TOKEN = "tok"
_LOGIN_ERROR = "Avni login failed: check your username and password."


def _record(stream_name: str, index: int, timestamp: str) -> dict:
    return {
        "ID": f"{stream_name}-{index:03}",
        "External ID": f"external-{index:03}",
        "Voided": False,
        "audit": {"Last modified at": timestamp},
    }


def _timestamp(index: int) -> str:
    value = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=index)
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _configure_auth(mocker, status_code: int = 200, body: dict | None = None):
    mocker.get(_IDP_URL, json={"cognito": {"clientId": _CLIENT_ID}})
    mocker.post(
        _COGNITO_URL,
        status_code=status_code,
        json=body or {"AuthenticationResult": {"IdToken": _ID_TOKEN}},
    )


def _read_stream(stream_names: list[str], state=None):
    config = dict(_CONFIG)
    catalog_builder = CatalogBuilder()
    for stream_name in stream_names:
        catalog_builder.with_stream(stream_name, SyncMode.incremental)
    catalog = catalog_builder.build()
    state_messages = state if state is not None else StateBuilder().build()
    return read(
        get_source(config=config, state=state_messages),
        config=config,
        catalog=catalog,
        state=state_messages,
    )


def _requests(mocker, url: str) -> list:
    return [request for request in mocker.request_history if request.url.startswith(url)]


def _query_params(request) -> dict:
    return {
        key: values[0] if len(values) == 1 else values
        for key, values in sorted(parse_qs(urlsplit(request.url).query, keep_blank_values=True).items())
    }


def _state_by_stream(output) -> dict:
    result = {}
    for message in output.state_messages:
        stream_state = message.state.stream
        result[stream_state.stream_descriptor.name] = vars(stream_state.stream_state)
    return result


def test_login_uses_idp_details_and_exact_cognito_request():
    with requests_mock.Mocker() as mocker:
        _configure_auth(mocker)
        mocker.get(_DATA_URLS["subjects"], json={"content": [_record("subject", 1, _timestamp(1))]})

        output = _read_stream(["subjects"])

    assert output.errors == []
    idp_requests = _requests(mocker, _IDP_URL)
    cognito_requests = _requests(mocker, _COGNITO_URL)
    assert [request.method for request in idp_requests] == ["GET"]
    assert [request.url for request in idp_requests] == [_IDP_URL]
    assert [request.method for request in cognito_requests] == ["POST"]
    cognito_request = cognito_requests[0]
    assert cognito_request.url == _COGNITO_URL
    assert cognito_request.headers["X-Amz-Target"] == "AWSCognitoIdentityProviderService.InitiateAuth"
    assert cognito_request.headers["Content-Type"] == "application/x-amz-json-1.1"
    assert cognito_request.json() == {
        "AuthFlow": "USER_PASSWORD_AUTH",
        "ClientId": _CLIENT_ID,
        "AuthParameters": {
            "USERNAME": _CONFIG["username"],
            "PASSWORD": _CONFIG["password"],
        },
    }


@pytest.mark.parametrize(
    ("stream_name", "sample_record"),
    [
        ("subjects", _record("subject", 1, "2024-05-01T00:00:00.000Z")),
        ("program_enrolments", _record("enrolment", 1, "2024-05-02T00:00:00.000Z")),
        ("program_encounters", _record("program-encounter", 1, "2024-05-03T00:00:00.000Z")),
        ("encounters", _record("encounter", 1, "2024-05-04T00:00:00.000Z")),
    ],
)
def test_stream_uses_legacy_data_request_and_adds_cursor(stream_name: str, sample_record: dict):
    with requests_mock.Mocker() as mocker:
        _configure_auth(mocker)
        mocker.get(_DATA_URLS[stream_name], json={"content": [sample_record]})

        output = _read_stream([stream_name])

    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data == {
        **sample_record,
        "last_modified_at": sample_record["audit"]["Last modified at"],
    }
    data_requests = _requests(mocker, _DATA_URLS[stream_name])
    assert len(data_requests) == 1
    assert data_requests[0].url.split("?", maxsplit=1)[0] == _DATA_URLS[stream_name]
    assert data_requests[0].headers["auth-token"] == _ID_TOKEN
    assert _query_params(data_requests[0]) == {
        "lastModifiedDateTime": "2000-06-23T01:30:00.000000Z",
        "size": "100",
    }


def test_subjects_page_increment_reads_101_records_with_cached_authentication():
    page_zero = [_record("subject", index, _timestamp(index)) for index in range(100)]
    page_one = [_record("subject", 100, _timestamp(100))]

    def page_response(request, context):
        page = int(request.qs.get("page", ["0"])[0])
        return json.dumps({"content": [page_zero, page_one][page]})

    with requests_mock.Mocker() as mocker:
        _configure_auth(mocker)
        mocker.get(_DATA_URLS["subjects"], text=page_response)

        output = _read_stream(["subjects"])

    assert output.errors == []
    assert len(output.records) == 101
    data_requests = _requests(mocker, _DATA_URLS["subjects"])
    assert len(data_requests) == 2
    assert [_query_params(request) for request in data_requests] == [
        {"lastModifiedDateTime": "2000-06-23T01:30:00.000000Z", "size": "100"},
        {"lastModifiedDateTime": "2000-06-23T01:30:00.000000Z", "page": "1", "size": "100"},
    ]
    assert [request.headers["auth-token"] for request in data_requests] == [_ID_TOKEN, _ID_TOKEN]
    assert len(_requests(mocker, _COGNITO_URL)) == 1
    assert len(_requests(mocker, _IDP_URL)) == 1


def test_authentication_refreshes_after_four_minutes(monkeypatch):
    current_time = [datetime(2024, 1, 1, tzinfo=timezone.utc)]
    monkeypatch.setattr(token_provider, "ab_datetime_now", lambda: current_time[0])
    page_zero = [_record("subject", index, _timestamp(index)) for index in range(100)]
    page_one = [_record("subject", 100, _timestamp(100))]

    def page_response(request, context):
        page = int(request.qs.get("page", ["0"])[0])
        if page == 0:
            current_time[0] += timedelta(minutes=4, seconds=1)
        return json.dumps({"content": [page_zero, page_one][page]})

    with requests_mock.Mocker() as mocker:
        _configure_auth(mocker)
        mocker.get(_DATA_URLS["subjects"], text=page_response)

        output = _read_stream(["subjects"])

    assert output.errors == []
    assert len(output.records) == 101
    data_requests = _requests(mocker, _DATA_URLS["subjects"])
    assert len(data_requests) == 2
    assert len(_requests(mocker, _COGNITO_URL)) == 2
    assert len(_requests(mocker, _IDP_URL)) == 1


def test_legacy_stream_state_is_used_for_requests_and_advances_to_latest_record():
    stream_names = list(_DATA_URLS)
    state_builder = StateBuilder()
    expected_cursors = {}
    with requests_mock.Mocker() as mocker:
        _configure_auth(mocker)
        for index, stream_name in enumerate(stream_names, start=1):
            state_builder.with_stream_state(
                stream_name,
                {"last_modified_at": "2024-01-01T00:00:00.000Z"},
            )
            sample = _record(stream_name, index, f"2024-05-{index:02}T00:00:00.000Z")
            expected_cursors[stream_name] = sample["audit"]["Last modified at"]
            mocker.get(_DATA_URLS[stream_name], json={"content": [sample]})

        output = _read_stream(stream_names, state=state_builder.build())

    assert output.errors == []
    for stream_name in stream_names:
        data_requests = _requests(mocker, _DATA_URLS[stream_name])
        assert len(data_requests) == 1
        assert _query_params(data_requests[0]) == {
            "lastModifiedDateTime": "2024-01-01T00:00:00.000000Z",
            "size": "100",
        }
        assert data_requests[0].headers["auth-token"] == _ID_TOKEN
    emitted_state = _state_by_stream(output)
    assert {stream_name: emitted_state[stream_name]["last_modified_at"] for stream_name in stream_names} == {
        stream_name: datetime.fromisoformat(cursor.replace("Z", "+00:00")).isoformat(timespec="microseconds").replace("+00:00", "Z")
        for stream_name, cursor in expected_cursors.items()
    }


@pytest.mark.parametrize(
    "error_body",
    [
        {"__type": "UserNotFoundException", "message": "User does not exist"},
        {"__type": "NotAuthorizedException", "message": "Incorrect username or password"},
    ],
)
def test_cognito_400_returns_config_error(error_body: dict):
    with requests_mock.Mocker() as mocker:
        _configure_auth(mocker, status_code=400, body=error_body)

        output = _read_stream(["subjects"])

    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert _LOGIN_ERROR in output.errors[0].trace.error.message
