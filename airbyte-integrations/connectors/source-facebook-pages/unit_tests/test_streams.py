#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_facebook_pages.source import SourceFacebookPages

from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors


@pytest.mark.parametrize("error_code", (400, 429, 500))
def test_retries(mocker, requests_mock, error_code):
    mocker.patch("time.sleep")
    requests_mock.get("https://graph.facebook.com/1?fields=access_token&access_token=token", json={"access_token": "access"})
    requests_mock.get("https://graph.facebook.com/v24.0/1", [{"status_code": error_code}, {"json": {"data": {}}}])
    source = SourceFacebookPages()
    stream = source.streams({"page_id": 1, "access_token": "token"})[0]
    for slice_ in stream.stream_slices(sync_mode="full_refresh"):
        list(stream.read_records(sync_mode="full_refresh", stream_slice=slice_))
    assert requests_mock.call_count >= 3


@pytest.mark.parametrize(
    "error_message, expected_airbyte_message",
    (
        (
            "This application has not been approved to use this API",
            "The application used to create the Facebook access token has not been approved to use this API. Possibly, some of the requested fields require additional scopes/permissions. The Airbyte OAuth App is being in process of requesting needed scopes. In the meantime, we suggest you use your own access token with the necessary permissions.",
        ),
        ("Tried accessing nonexisting field", "Request contains invalid/deprecated field."),
    ),
)
def test_error_handling_with_error_messages(error_message, expected_airbyte_message, requests_mock):
    requests_mock.get("https://graph.facebook.com/1?fields=access_token&access_token=token", json={"access_token": "access"})
    requests_mock.get("https://graph.facebook.com/v24.0/1", status_code=400, json={"message": error_message})
    source = SourceFacebookPages()
    stream = source.streams({"page_id": 1, "access_token": "token"})[0]
    with pytest.raises(MessageRepresentationAirbyteTracedErrors) as err:
        for slice_ in stream.stream_slices(sync_mode="full_refresh"):
            list(stream.read_records(sync_mode="full_refresh", stream_slice=slice_))

    assert expected_airbyte_message in str(err.value)
