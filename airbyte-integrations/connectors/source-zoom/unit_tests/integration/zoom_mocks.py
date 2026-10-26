# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared stubs for the source-zoom webinar mock-server tests.

Every webinar stream is a child of `GET /users/{id}/webinars` (itself a child of `GET /users`):

* id-keyed streams build their path from the webinar `id` and inject `webinar_id`;
* uuid-keyed streams build their path from the webinar `uuid`, which Zoom requires to be
  double URL-encoded when it begins with `/` or contains `//`, and inject `webinar_uuid`.

The parent list returns two webinars over two pages so every test also exercises the parent
pagination; `WEBINAR_2` has a UUID that begins with `/` and contains `//`.
"""

import json
from functools import lru_cache
from typing import Any, Dict, List, Mapping, Optional

from jsonschema import Draft7Validator

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.models.outcome import ExpectedOutcome
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


BASE_URL = "https://api.zoom.us/v2"
PAGE_SIZE = "30"
USER_ID = "u1"

CONFIG = {
    "credentials": {
        "auth_type": "server_to_server",
        "account_id": "test_account_id",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_endpoint": "https://zoom.us/oauth/token",
    }
}

WEBINAR_1 = {"id": 81111111111, "uuid": "wPUYIy/pR2mPs5r9no2GmA==", "topic": "Webinar one"}
WEBINAR_2 = {"id": 82222222222, "uuid": "/abc//d==", "topic": "Webinar two"}
WEBINARS = [WEBINAR_1, WEBINAR_2]
ENCODED_UUIDS = {
    WEBINAR_1["uuid"]: "wPUYIy%252FpR2mPs5r9no2GmA%253D%253D",
    WEBINAR_2["uuid"]: "%252Fabc%252F%252Fd%253D%253D",
}

_TOKEN_REQUEST = HttpRequest(
    url="https://zoom.us/oauth/token",
    query_params={"grant_type": "account_credentials", "account_id": "test_account_id"},
)
_WEBINARS_NEXT_PAGE_TOKEN = "webinars-page-2"

# Pre-existing drift: `AddFields` injects `webinar_id` from `stream_partition.parent_id` (an int) while these
# schemas declare it `["null", "string"]`. Fixing it changes the emitted type, so it is a separate, breaking change.
# Remove a stream from this map once its schema and `AddFields` agree.
KNOWN_SCHEMA_DRIFT = {
    "webinar_registrants": {"webinar_id"},
    "webinar_polls": {"webinar_id"},
    "webinar_registration_questions": {"webinar_id"},
    "webinar_tracking_sources": {"webinar_id"},
}


def json_response(body: Any, status_code: int = 200) -> HttpResponse:
    return HttpResponse(json.dumps(body), status_code=status_code)


def zoom_error(code: int, message: str, status_code: int) -> HttpResponse:
    return json_response({"code": code, "message": message}, status_code=status_code)


def request(path: str, query_params: Optional[Mapping[str, str]] = None) -> HttpRequest:
    return HttpRequest(url=f"{BASE_URL}{path}", query_params=query_params)


def paginated_query(next_page_token: Optional[str] = None) -> Dict[str, str]:
    params = {"page_size": PAGE_SIZE}
    if next_page_token:
        params["next_page_token"] = next_page_token
    return params


def user_webinars_request(next_page_token: Optional[str] = None) -> HttpRequest:
    return request(f"/users/{USER_ID}/webinars", paginated_query(next_page_token))


def mock_token(http_mocker: HttpMocker) -> None:
    # Each requester in a stream's parent chain may fetch its own token, so never assert on the call count.
    http_mocker.post(_TOKEN_REQUEST, json_response({"access_token": "test_access_token", "expires_in": 3599}))


def mock_users(http_mocker: HttpMocker, users: Optional[List[Dict[str, Any]]] = None) -> HttpRequest:
    users_request = request("/users", paginated_query())
    http_mocker.get(
        users_request,
        json_response({"users": users if users is not None else [{"id": USER_ID}], "next_page_token": ""}),
    )
    return users_request


def mock_webinar_parents(http_mocker: HttpMocker) -> None:
    """Stub the token, users and the two-page webinars list (one webinar per page)."""
    mock_token(http_mocker)
    mock_users(http_mocker)
    http_mocker.get(
        user_webinars_request(),
        json_response({"webinars": [WEBINAR_1], "next_page_token": _WEBINARS_NEXT_PAGE_TOKEN}),
    )
    http_mocker.get(
        user_webinars_request(_WEBINARS_NEXT_PAGE_TOKEN),
        json_response({"webinars": [WEBINAR_2], "next_page_token": ""}),
    )


def mock_webinars_parent_error(http_mocker: HttpMocker, response: HttpResponse) -> HttpRequest:
    """Stub the token and users, fail `GET /users/{id}/webinars` with `response`, and return that request."""
    mock_token(http_mocker)
    mock_users(http_mocker)
    parent_request = user_webinars_request()
    http_mocker.get(parent_request, response)
    return parent_request


def read_stream(
    stream_name: str,
    expected_outcome: ExpectedOutcome = ExpectedOutcome.EXPECT_SUCCESS,
    config: Optional[Dict[str, Any]] = None,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[Any]] = None,
) -> EntrypointOutput:
    read_config = config if config is not None else CONFIG
    read_state = state if state is not None else StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        get_source(config=read_config, state=read_state),
        config=read_config,
        catalog=catalog,
        state=read_state,
        expected_outcome=expected_outcome,
    )


@lru_cache(maxsize=None)
def _stream_schema_validators() -> Dict[str, Draft7Validator]:
    catalog = discover(get_source(config=CONFIG), CONFIG).catalog.catalog
    return {stream.name: Draft7Validator(stream.json_schema) for stream in catalog.streams}


def records_data(output: EntrypointOutput) -> List[Dict[str, Any]]:
    return [message.record.data for message in output.records]


def assert_records_match_schema(output: EntrypointOutput, stream_name: str) -> None:
    """Every record validates against the discovered schema, except the fields listed in `KNOWN_SCHEMA_DRIFT`."""
    validator = _stream_schema_validators()[stream_name]
    known_drift = KNOWN_SCHEMA_DRIFT.get(stream_name, set())
    drifted_fields = set()
    for record in records_data(output):
        for error in validator.iter_errors(record):
            field = error.absolute_path[0] if error.absolute_path else None
            assert field in known_drift, f"{stream_name} record does not match its schema: {error.message}"
            drifted_fields.add(field)
    if output.records:
        assert drifted_fields == known_drift, f"{stream_name} no longer drifts on {known_drift - drifted_fields}; update KNOWN_SCHEMA_DRIFT"


def assert_completed_without_errors(output: EntrypointOutput, stream_name: str) -> None:
    assert output.errors == []
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE
    assert_records_match_schema(output, stream_name)


def assert_failed_with_config_error(output: EntrypointOutput, stream_name: str) -> None:
    assert output.records == []
    assert AirbyteStreamStatus.INCOMPLETE in output.get_stream_statuses(stream_name)
    assert AirbyteStreamStatus.COMPLETE not in output.get_stream_statuses(stream_name)
    assert output.errors, "expected an error trace message"
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)


_WEBINAR_PLAN_MISSING = zoom_error(
    200,
    "Webinar plan is missing. You must subscribe to the webinar plan and enable webinar for this user in order to perform this action.",
    status_code=400,
)
# Zoom reports a token missing a required scope as HTTP 400, code 4711.
MISSING_SCOPE = zoom_error(4711, "Invalid access token, does not contain scopes:[webinar:read:admin].", status_code=400)


def assert_parent_400_is_skipped(stream_name: str, response: HttpResponse = _WEBINAR_PLAN_MISSING) -> None:
    """A 400 on `GET /users/{id}/webinars` (by default code 200, no webinar plan) yields an empty, COMPLETE stream."""
    with HttpMocker() as http_mocker:
        parent_request = mock_webinars_parent_error(http_mocker, response)
        output = read_stream(stream_name)
        # The context-manager form of HttpMocker does not check that every mock was called.
        http_mocker.assert_number_of_calls(parent_request, 1)

    assert_completed_without_errors(output, stream_name)
    assert output.records == []


def assert_parent_unhandled_403_fails_with_config_error(stream_name: str) -> None:
    """A 403 on `GET /users/{id}/webinars`, which no handler in the manifest covers, fails the stream as a config error."""
    with HttpMocker() as http_mocker:
        parent_request = mock_webinars_parent_error(http_mocker, zoom_error(200, "No permission.", status_code=403))
        output = read_stream(stream_name, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)
        http_mocker.assert_number_of_calls(parent_request, 1)

    assert output.records == []
    assert AirbyteStreamStatus.INCOMPLETE in output.get_stream_statuses(stream_name)
    assert AirbyteStreamStatus.COMPLETE not in output.get_stream_statuses(stream_name)
    assert output.errors, "expected an error trace message"
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
