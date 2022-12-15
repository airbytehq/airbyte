#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
import requests_mock
from source_facebook_pages.components import AuthenticatorFacebookPageAccessToken


@pytest.fixture
def req_mock():
    with requests_mock.Mocker() as mock:
        yield mock


def test_facebook_url_params(req_mock):
    config = {
        "access_token": "initial_token",
        "page_id": "pageID"
    }
    options = config

    req_mock.get("https://graph.facebook.com/pageID", json={"access_token": "page_access_token"})
    authenticator = AuthenticatorFacebookPageAccessToken(config=config,
                                                         page_id=config.get("page_id"),
                                                         access_token=config.get("access_token"),
                                                         options=options)
    page_token = authenticator.generate_page_access_token()
    assert page_token == "page_access_token"
    prepared_request = requests.PreparedRequest()
    prepared_request.method = "GET"
    prepared_request.url = "https://graph.facebook.com/"
    assert "access_token=page_access_token" in authenticator(prepared_request).path_url
