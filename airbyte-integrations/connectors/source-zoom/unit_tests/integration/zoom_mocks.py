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
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


BASE_URL = "https://api.zoom.us/v2"
PAGE_SIZE = "30"
USER_ID = "u1"

CONFIG = {
    "account_id": "test_account_id",
    "client_id": "test_client_id",
    "client_secret": "test_client_secret",
    "authorization_endpoint": "https://zoom.us/oauth/token",
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


def mock_users(http_mocker: HttpMocker) -> None:
    http_mocker.get(request("/users", paginated_query()), json_response({"users": [{"id": USER_ID}], "next_page_token": ""}))


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


def mock_webinars_parent_error(http_mocker: HttpMocker, response: HttpResponse) -> None:
    mock_token(http_mocker)
    mock_users(http_mocker)
    http_mocker.get(user_webinars_request(), response)


def read_stream(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(config=CONFIG),
        config=CONFIG,
        catalog=catalog,
        state=StateBuilder().build(),
        expecting_exception=expecting_exception,
    )


def records_data(output: EntrypointOutput) -> List[Dict[str, Any]]:
    return [message.record.data for message in output.records]


def assert_completed_without_errors(output: EntrypointOutput, stream_name: str) -> None:
    assert output.errors == []
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE


def assert_parent_400_is_skipped(stream_name: str) -> None:
    """A 400 on `GET /users/{id}/webinars` (e.g. code 3161, user not licensed) yields an empty, COMPLETE stream."""
    with HttpMocker() as http_mocker:
        mock_webinars_parent_error(
            http_mocker,
            zoom_error(3161, "User does not have the webinar feature enabled.", status_code=400),
        )
        output = read_stream(stream_name)

    assert_completed_without_errors(output, stream_name)
    assert output.records == []


def assert_parent_403_fails_with_config_error(stream_name: str) -> None:
    """A 403 on `GET /users/{id}/webinars` (e.g. missing scope) fails the stream as a config error."""
    with HttpMocker() as http_mocker:
        mock_webinars_parent_error(
            http_mocker,
            zoom_error(4711, "Invalid access token, does not contain scopes:[webinar:read:admin].", status_code=403),
        )
        output = read_stream(stream_name, expecting_exception=True)

    assert output.records == []
    assert AirbyteStreamStatus.INCOMPLETE in output.get_stream_statuses(stream_name)
    assert AirbyteStreamStatus.COMPLETE not in output.get_stream_statuses(stream_name)
    assert output.errors, "expected an error trace message"
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
