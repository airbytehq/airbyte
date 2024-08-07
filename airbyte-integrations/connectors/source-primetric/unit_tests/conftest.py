#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pytest import fixture


@fixture
def config_pass():
    return { "client_id": "good", "client_secret": "good" }


@fixture
def assignments_url():
    return "https://api.primetric.com/beta/assignments"


@fixture
def auth_url():
    return "https://api.primetric.com/auth/token/"


@fixture
def auth_token():
    return { "access_token": "good", "expires_in": 3600 }
