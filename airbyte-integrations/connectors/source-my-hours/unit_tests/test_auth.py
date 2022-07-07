#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import responses
from source_my_hours.auth import MyHoursAuthenticator
from source_my_hours.constants import URL_BASE

DEFAULT_CONFIG = {"email": "john@doe.com", "password": "pwd"}


@responses.activate
def test_init(mocker):
    responses.add(responses.POST, f"{URL_BASE}/tokens/login", json={"accessToken": "at", "refreshToken": "rt", "expiresIn": 100})

    authenticator = MyHoursAuthenticator(email="email", password="password")
    authenticator._access_token
    assert authenticator._access_token == "at"


@responses.activate
def test_refresh(mocker):
    responses.add(responses.POST, f"{URL_BASE}/tokens/login", json={"accessToken": "at", "refreshToken": "rt", "expiresIn": 0})
    responses.add(responses.POST, f"{URL_BASE}/tokens/refresh", json={"accessToken": "at2", "refreshToken": "rt2", "expiresIn": 100})

    authenticator = MyHoursAuthenticator(email="email", password="password")
    access_token = authenticator.get_access_token()

    assert access_token == "at2"
    assert authenticator.refresh_token == "rt2"
