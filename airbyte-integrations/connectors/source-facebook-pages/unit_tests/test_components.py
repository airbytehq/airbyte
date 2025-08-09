#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os

import pytest
import requests
import requests_mock


def test_field_transformation(components_module):
    CustomFieldTransformation = components_module.CustomFieldTransformation
    with (
        open(f"{os.path.dirname(__file__)}/initial_record.json", "r") as initial_record,
        open(f"{os.path.dirname(__file__)}/transformed_record.json", "r") as transformed_record,
    ):
        initial_record = json.loads(initial_record.read())
        transformed_record = json.loads(transformed_record.read())
        record_transformation = CustomFieldTransformation(config={}, parameters={"name": "page"})
        # print("-------------------------------------")
        # print(initial_record)
        # print("-------------------------------------")
        assert transformed_record == record_transformation.transform(initial_record)


@pytest.fixture
def req_mock():
    with requests_mock.Mocker() as mock:
        yield mock


def test_facebook_url_params(components_module, req_mock):
    AuthenticatorFacebookPageAccessToken = components_module.AuthenticatorFacebookPageAccessToken
    config = {"access_token": "initial_token", "page_id": "pageID"}
    parameters = config

    req_mock.get("https://graph.facebook.com/pageID", json={"access_token": "page_access_token"})
    authenticator = AuthenticatorFacebookPageAccessToken(
        config=config, page_id=config.get("page_id"), access_token=config.get("access_token"), parameters=parameters
    )
    page_token = authenticator.generate_page_access_token()
    assert page_token == "page_access_token"
    prepared_request = requests.PreparedRequest()
    prepared_request.method = "GET"
    prepared_request.url = "https://graph.facebook.com/"
    assert "access_token=page_access_token" in authenticator(prepared_request).path_url


# @pytest.mark.parametrize("error_code", (400, 429, 500))
# def test_retries(components_module, mocker, requests_mock, error_code):
#     SourceFacebookPages = components_module.SourceFacebookPages
#     mocker.patch("time.sleep")
#     requests_mock.get("https://graph.facebook.com/1?fields=access_token&access_token=token", json={"access_token": "access"})
#     requests_mock.get("https://graph.facebook.com/v21.0/1", [{"status_code": error_code}, {"json": {"data": {}}}])
#     source = SourceFacebookPages()
#     stream = source.streams({"page_id": 1, "access_token": "token"})[0]
#     for slice_ in stream.stream_slices(sync_mode="full_refresh"):
#         list(stream.read_records(sync_mode="full_refresh", stream_slice=slice_))
#     assert requests_mock.call_count == 3
