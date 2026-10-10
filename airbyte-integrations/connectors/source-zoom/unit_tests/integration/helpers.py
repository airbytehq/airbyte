# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Shared stubs for the webinar stream mock-server tests.

Every webinar stream reads the `users` -> `webinars_list_tmp` parent chain
(`GET /users` then `GET /users/{id}/webinars`) before calling its own endpoint,
so each test stubs the token endpoint, one user and two webinars. The second
webinar's UUID starts with `/` and contains `//`, which Zoom requires to be
double URL-encoded in `past_webinars` and `report/webinars` paths.
"""

from typing import List

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import ZoomRequestBuilder, double_encode_uuid, json_response, zoom_error


USER_ID = "u1"
WEBINAR_1 = {"id": 111, "uuid": "wPUYIy/pR2mPs5r9no2GmA==", "topic": "Webinar one", "host_id": USER_ID}
WEBINAR_2 = {"id": 222, "uuid": "/abc//d==", "topic": "Webinar two", "host_id": USER_ID}
WEBINARS = [WEBINAR_1, WEBINAR_2]
ENCODED_UUID_1 = double_encode_uuid(WEBINAR_1["uuid"])
ENCODED_UUID_2 = double_encode_uuid(WEBINAR_2["uuid"])


def read_stream(stream_name: str) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


def mock_parents(http_mocker: HttpMocker, webinars: List[dict] = WEBINARS) -> None:
    # Each requester in the parent chain fetches its own token, so never assert on the token call count.
    http_mocker.post(ZoomRequestBuilder.token(), json_response({"access_token": "test_access_token", "expires_in": 3599}))
    http_mocker.get(ZoomRequestBuilder.users(), json_response({"users": [{"id": USER_ID}], "next_page_token": ""}))
    http_mocker.get(ZoomRequestBuilder.user_webinars(USER_ID), json_response({"webinars": webinars, "next_page_token": ""}))


def mock_parent_error(http_mocker: HttpMocker, response: HttpResponse) -> None:
    http_mocker.post(ZoomRequestBuilder.token(), json_response({"access_token": "test_access_token", "expires_in": 3599}))
    http_mocker.get(ZoomRequestBuilder.users(), json_response({"users": [{"id": USER_ID}], "next_page_token": ""}))
    http_mocker.get(ZoomRequestBuilder.user_webinars(USER_ID), response)


def user_not_licensed_for_webinars() -> HttpResponse:
    return zoom_error(3161, "Your user account is not allowed webinar hosting and scheduling capabilities.", status_code=400)


def missing_permission() -> HttpResponse:
    return zoom_error(4711, "Invalid access token, does not contain permissions:[webinar:read:admin].", status_code=403)


def assert_parent_400_skips_stream(http_mocker: HttpMocker, stream_name: str) -> None:
    """A 400 (eg code 3161, user not licensed for webinars) on the webinar list ends the stream with no records."""
    mock_parent_error(http_mocker, user_not_licensed_for_webinars())

    output = read_stream(stream_name)

    assert output.errors == []
    assert output.records == []
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE


def assert_parent_403_fails_stream_with_config_error(http_mocker: HttpMocker, stream_name: str) -> None:
    """A 403 on the webinar list is a credentials/scope problem and must fail the stream as a config error."""
    mock_parent_error(http_mocker, missing_permission())

    output = read_stream(stream_name)

    assert output.records == []
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.INCOMPLETE
    assert output.errors, "expected an error trace message"
    assert output.errors[-1].trace.error.failure_type == FailureType.config_error


def record_data(output: EntrypointOutput) -> List[dict]:
    return [message.record.data for message in output.records]
