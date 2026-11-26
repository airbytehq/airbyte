# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-qualtrics` covering the manifest behaviors that are easy to regress:

- the Client Credentials login (HTTP Basic, form body with `grant_type` and the configured or default
  `scope`) and the `Bearer` token it hands to the data requests
- the API token path, which sends `X-API-TOKEN` and never calls the token endpoint
- `surveys` pagination through the full `result.nextPage` URL, stopping on a null `nextPage`
- `survey_details` and `survey_response_schemas` reading one request per survey, the latter with the
  parent `survey_id` added as the primary key
- a rejected login or a rejected data request failing as `config_error` without retries, on the parent
  and on the per-survey streams
- a deleted survey (404) being skipped, and an empty survey list producing no records and no errors
- 429 handling: `Retry-After` when sent, exponential backoff otherwise
- the declared schemas: typed scalars, date-time formats, and complex fields left open
"""

import base64
import logging
import time
from urllib.parse import parse_qs

import pytest
import requests_mock
from _helpers import (
    ACCESS_TOKEN,
    API_TOKEN_CONFIG,
    DEFAULT_SCOPE,
    OAUTH_CONFIG,
    SURVEYS_PATH,
    SURVEYS_URL,
    TOKEN_PATH,
    TOKEN_RESPONSE,
    TOKEN_URL,
    get_source,
    query_params,
    read_stream,
    record_ids,
    requests_to,
    response_schema,
    stream_schema,
    survey,
    survey_detail,
    surveys_page,
)

from airbyte_cdk.models import FailureType, Status


def test_client_credentials_login_and_bearer_token():
    """Reading a stream logs in once with HTTP Basic client credentials and a form body, then sends `Bearer <token>`."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        output = read_stream("surveys")

    assert record_ids(output) == ["SV_1"]

    logins = requests_to(mocker.request_history, TOKEN_PATH)
    assert len(logins) == 1, f"expected exactly one login request, got {len(logins)}"
    login = logins[0]
    assert login.method == "POST"
    authorization = login.headers["Authorization"]
    assert authorization.startswith("Basic ")
    assert base64.b64decode(authorization.removeprefix("Basic ")).decode() == "test_client_id:test_client_secret"
    form = parse_qs(login.text)
    assert form["grant_type"] == ["client_credentials"]
    assert form["scope"] == [DEFAULT_SCOPE], f"login must request the default scope, got {form.get('scope')}"

    data_requests = requests_to(mocker.request_history, SURVEYS_PATH)
    assert len(data_requests) == 1
    assert data_requests[0].headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"
    assert data_requests[0].headers["Accept"] == "application/json"
    assert "X-API-TOKEN" not in data_requests[0].headers


def test_configured_scope_is_requested():
    """A custom `scope` replaces the default in the token request."""
    config = {**OAUTH_CONFIG, "credentials": {**OAUTH_CONFIG["credentials"], "scope": "manage:all"}}
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        output = read_stream("surveys", config=config)

    assert record_ids(output) == ["SV_1"]
    assert parse_qs(requests_to(mocker.request_history, TOKEN_PATH)[0].text)["scope"] == ["manage:all"]


def test_api_token_path_skips_the_token_endpoint():
    """With an API token, every request carries `X-API-TOKEN` and the token endpoint is never called."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        output = read_stream("surveys", config=API_TOKEN_CONFIG)

    assert record_ids(output) == ["SV_1"]
    assert requests_to(mocker.request_history, TOKEN_PATH) == []
    data_requests = requests_to(mocker.request_history, SURVEYS_PATH)
    assert len(data_requests) == 1
    assert data_requests[0].headers["X-API-TOKEN"] == "test-api-token"
    assert "Authorization" not in data_requests[0].headers


def test_surveys_pagination_follows_next_page_url():
    """The second request goes to the full `result.nextPage` URL, and a null `nextPage` ends the read."""
    next_url = f"{SURVEYS_URL}?offset=100"
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1"), survey("SV_2")], next_page=next_url))
        mocker.get(next_url, json=surveys_page([survey("SV_3")]))
        output = read_stream("surveys")

    assert record_ids(output) == ["SV_1", "SV_2", "SV_3"]
    data_requests = requests_to(mocker.request_history, SURVEYS_PATH)
    assert len(data_requests) == 2, f"expected 2 paginated requests, got {len(data_requests)}"
    assert query_params(data_requests[0]) == {}
    assert query_params(data_requests[1]) == {"offset": "100"}
    # One token serves both pages.
    assert len(requests_to(mocker.request_history, TOKEN_PATH)) == 1
    assert all(request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}" for request in data_requests)


def test_survey_details_reads_one_request_per_survey():
    """`survey_details` partitions over `surveys` and extracts `result` of `GET /surveys/{id}`."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1"), survey("SV_2")]))
        mocker.get(f"{SURVEYS_URL}/SV_1", json=survey_detail("SV_1"))
        mocker.get(f"{SURVEYS_URL}/SV_2", json=survey_detail("SV_2"))
        output = read_stream("survey_details")

    assert record_ids(output) == ["SV_1", "SV_2"]
    detail = output.records[0].record.data
    assert detail["responseCounts"] == {"auditable": 3, "generated": 0, "deleted": 0}
    assert "QID1" in detail["questions"]
    detail_requests = requests_to(mocker.request_history, f"{SURVEYS_PATH}/SV_1") + requests_to(mocker.request_history, f"{SURVEYS_PATH}/SV_2")
    assert len(detail_requests) == 2
    assert all(request.headers["Accept"] == "application/json" for request in detail_requests)
    # The parent and the child stream each hold their own authenticator, so each logs in once, and the
    # child's token is reused across both partitions (a lost `expiration_duration` would make it three).
    # Qualtrics' OAuth guide says requesting a new token does not invalidate earlier ones.
    assert len(requests_to(mocker.request_history, TOKEN_PATH)) == 2


def test_survey_response_schemas_adds_survey_id():
    """Each schema document is read from `GET /surveys/{id}/response-schema` and keyed by the parent survey id."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        mocker.get(f"{SURVEYS_URL}/SV_1/response-schema", json=response_schema("SV_1"))
        output = read_stream("survey_response_schemas")

    assert record_ids(output, key="survey_id") == ["SV_1"]
    record = output.records[0].record.data
    assert record["$id"] == "http://qualtrics.com/API/v3/surveys/SV_1/response-schema"
    assert isinstance(record["survey_id"], str)
    assert record["required"] == ["values", "displayedFields", "displayedValues", "labels", "responseId"]
    assert "responseId" in record["properties"]
    schema_requests = requests_to(mocker.request_history, f"{SURVEYS_PATH}/SV_1/response-schema")
    assert len(schema_requests) == 1
    assert schema_requests[0].headers["Accept"] == "application/json"


def test_check_uses_surveys():
    """`check` succeeds off the `surveys` stream."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json=TOKEN_RESPONSE)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        status = get_source(OAUTH_CONFIG).check(logging.getLogger("test_check_uses_surveys"), OAUTH_CONFIG)

    assert status.status == Status.SUCCEEDED, f"expected a successful check, got {status}"
    assert requests_to(mocker.request_history, SURVEYS_PATH), "check must exercise the surveys stream"


@pytest.mark.parametrize("status_code", [400, 401])
def test_rejected_login_is_a_config_error(status_code):
    """A rejected client ID or secret fails as `config_error` with the connector's message, without retries."""
    with requests_mock.Mocker() as mocker:
        mocker.post(TOKEN_URL, json={"error": "invalid_client"}, status_code=status_code)
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        output = read_stream("surveys")

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, errors[0].failure_type
    assert "Qualtrics rejected the client ID or client secret" in errors[0].message, errors[0].message
    assert len(requests_to(mocker.request_history, TOKEN_PATH)) == 1, "login errors must not be retried"
    assert requests_to(mocker.request_history, SURVEYS_PATH) == []


@pytest.mark.parametrize("status_code", [401, 403])
def test_rejected_data_request_is_a_config_error(status_code):
    """A 401 or 403 on a data request fails as `config_error` with the connector's message, without retries."""
    body = {"meta": {"httpStatus": f"{status_code}", "error": {"errorMessage": "Unrecognized X-API-TOKEN.", "errorCode": "AUTH_6.0"}}}
    with requests_mock.Mocker() as mocker:
        mocker.get(SURVEYS_URL, json=body, status_code=status_code)
        output = read_stream("surveys", config=API_TOKEN_CONFIG)

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, errors[0].failure_type
    assert "Qualtrics rejected the credentials" in errors[0].message, errors[0].message
    assert len(requests_to(mocker.request_history, SURVEYS_PATH)) == 1, "auth errors must not be retried"


def test_declared_schemas():
    """Scalars are typed, dates carry `date-time`, complex fields stay open objects or arrays."""
    surveys = stream_schema("surveys")["properties"]
    assert surveys["id"] == {"type": "string"}
    assert surveys["lastModified"] == {"type": ["null", "string"], "format": "date-time"}
    assert surveys["isActive"] == {"type": ["null", "boolean"]}

    details = stream_schema("survey_details")["properties"]
    assert details["lastModifiedDate"] == {"type": ["null", "string"], "format": "date-time"}
    assert details["questions"]["type"] == ["null", "object"]
    assert details["questions"]["additionalProperties"] is True
    assert details["flow"]["type"] == ["null", "array"]
    assert details["responseCounts"]["properties"]["auditable"] == {"type": ["null", "integer"]}

    schemas = stream_schema("survey_response_schemas")["properties"]
    assert schemas["survey_id"] == {"type": "string"}
    assert schemas["required"]["type"] == ["null", "array"]
    assert schemas["properties"]["type"] == ["null", "object"]


def test_check_fails_with_the_connector_message_on_401():
    """A rejected credential makes `check` fail and surface the connector's own message."""
    body = {"meta": {"httpStatus": "401", "error": {"errorMessage": "Unrecognized X-API-TOKEN.", "errorCode": "AUTH_6.0"}}}
    with requests_mock.Mocker() as mocker:
        mocker.get(SURVEYS_URL, json=body, status_code=401)
        status = get_source(API_TOKEN_CONFIG).check(logging.getLogger("test_check_fails"), API_TOKEN_CONFIG)

    assert status.status == Status.FAILED, status
    assert "Qualtrics rejected the credentials" in (status.message or ""), status.message


@pytest.mark.parametrize("stream_name, suffix", [("survey_details", ""), ("survey_response_schemas", "/response-schema")])
def test_rejected_child_request_is_a_config_error(stream_name, suffix):
    """A 403 on a per-survey request fails as `config_error` with the connector's message, without retries."""
    body = {"meta": {"httpStatus": "403", "error": {"errorMessage": "Insufficient permission.", "errorCode": "AUTH_13.0"}}}
    with requests_mock.Mocker() as mocker:
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_1")]))
        mocker.get(f"{SURVEYS_URL}/SV_1{suffix}", json=body, status_code=403)
        output = read_stream(stream_name, config=API_TOKEN_CONFIG)

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, errors[0].failure_type
    assert "Qualtrics rejected the credentials" in errors[0].message, errors[0].message
    assert len(requests_to(mocker.request_history, f"{SURVEYS_PATH}/SV_1{suffix}")) == 1, "auth errors must not be retried"


@pytest.mark.parametrize("stream_name, suffix", [("survey_details", ""), ("survey_response_schemas", "/response-schema")])
def test_deleted_survey_is_skipped(stream_name, suffix):
    """A survey that returns 404 is skipped and the other surveys are still read."""
    body = {"meta": {"httpStatus": "404", "error": {"errorMessage": "Survey not found.", "errorCode": "SV_0"}}}
    with requests_mock.Mocker() as mocker:
        mocker.get(SURVEYS_URL, json=surveys_page([survey("SV_gone"), survey("SV_1")]))
        mocker.get(f"{SURVEYS_URL}/SV_gone{suffix}", json=body, status_code=404)
        mocker.get(f"{SURVEYS_URL}/SV_1{suffix}", json=survey_detail("SV_1") if not suffix else response_schema("SV_1"))
        output = read_stream(stream_name, config=API_TOKEN_CONFIG)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert len(output.records) == 1
    assert len(requests_to(mocker.request_history, f"{SURVEYS_PATH}/SV_gone{suffix}")) == 1, "a 404 must not be retried"


@pytest.mark.parametrize("stream_name", ["surveys", "survey_details", "survey_response_schemas"])
def test_empty_survey_list_produces_no_records_and_no_errors(stream_name):
    """A brand without surveys syncs cleanly: one list request, nothing else."""
    with requests_mock.Mocker() as mocker:
        mocker.get(SURVEYS_URL, json=surveys_page([]))
        output = read_stream(stream_name, config=API_TOKEN_CONFIG)

    assert output.records == []
    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert len(requests_to(mocker.request_history, SURVEYS_PATH)) == 1


def test_429_waits_for_retry_after_then_succeeds(monkeypatch):
    """A 429 with `Retry-After` is retried after that many seconds and the read completes."""
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    with requests_mock.Mocker() as mocker:
        mocker.get(
            SURVEYS_URL,
            [
                {"status_code": 429, "headers": {"Retry-After": "7"}, "json": {"meta": {"httpStatus": "429"}}},
                {"status_code": 200, "json": surveys_page([survey("SV_1")])},
            ],
        )
        output = read_stream("surveys", config=API_TOKEN_CONFIG)

    assert record_ids(output) == ["SV_1"]
    assert len(requests_to(mocker.request_history, SURVEYS_PATH)) == 2
    assert any(seconds >= 7 for seconds in sleeps), f"expected a wait of at least 7 seconds, got {sleeps}"


def test_429_without_retry_after_backs_off_and_succeeds(monkeypatch):
    """Without `Retry-After`, a 429 falls through to exponential backoff and the read still completes."""
    sleeps = []
    monkeypatch.setattr(time, "sleep", lambda seconds: sleeps.append(seconds))
    with requests_mock.Mocker() as mocker:
        mocker.get(
            SURVEYS_URL,
            [
                {"status_code": 429, "json": {"meta": {"httpStatus": "429"}}},
                {"status_code": 500, "json": {"meta": {"httpStatus": "500"}}},
                {"status_code": 200, "json": surveys_page([survey("SV_1")])},
            ],
        )
        output = read_stream("surveys", config=API_TOKEN_CONFIG)

    assert record_ids(output) == ["SV_1"]
    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert len(requests_to(mocker.request_history, SURVEYS_PATH)) == 3
    assert sleeps, "expected the connector to wait between retries"
