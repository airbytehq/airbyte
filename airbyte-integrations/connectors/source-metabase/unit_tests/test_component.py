#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from requests.exceptions import HTTPError
from source_metabase.components import MetabaseSessionTokenAuthenticator, get_new_session_token

options = {"hello": "world"}
instance_api_url = "https://airbyte.metabaseapp.com/api/"
username = "username"
password = "password"
session_token = "session_token"

input_instance_api_url = "{{ config['instance_api_url'] }}"
input_username = "{{ config['username'] }}"
input_password = "{{ config['password'] }}"
input_session_token = "{{ config['session_token'] }}"

config = {
    "instance_api_url": instance_api_url,
    "username": username,
    "password": password,
    "session_token": session_token,
}

config_session_token = {
    "instance_api_url": instance_api_url,
    "username": "",
    "password": "",
    "session_token": session_token,
}

config_username_password = {
    "instance_api_url": instance_api_url,
    "username": username,
    "password": password,
    "session_token": "",
}


def test_auth_header():
    auth_header = MetabaseSessionTokenAuthenticator(
        config=config,
        options=options,
        api_url=input_instance_api_url,
        username=input_username,
        password=input_password,
        session_token=input_session_token,
    ).auth_header
    assert auth_header == "X-Metabase-Session"


def test_get_token_valid_session(requests_mock):
    requests_mock.get(
        f"{config_session_token['instance_api_url']}user/current", json={"common_name": "common_name", "last_login": "last_login"}
    )

    token = MetabaseSessionTokenAuthenticator(
        config=config_session_token,
        options=options,
        api_url=input_instance_api_url,
        username=input_username,
        password=input_password,
        session_token=input_session_token,
    ).token
    assert token == "session_token"


def test_get_token_invalid_session_unauthorized():
    with pytest.raises(ConnectionError):
        _ = MetabaseSessionTokenAuthenticator(
            config=config_session_token,
            options=options,
            api_url=input_instance_api_url,
            username=input_username,
            password=input_password,
            session_token=input_session_token,
        ).token


def test_get_token_invalid_username_password_unauthorized():
    with pytest.raises(HTTPError):
        _ = MetabaseSessionTokenAuthenticator(
            config=config_username_password,
            options=options,
            api_url=input_instance_api_url,
            username=input_username,
            password=input_password,
            session_token=input_session_token,
        ).token


def test_get_token_username_password(requests_mock):
    requests_mock.post(f"{config['instance_api_url']}session", json={"id": "some session id"})

    token = MetabaseSessionTokenAuthenticator(
        config=config_username_password,
        options=options,
        api_url=input_instance_api_url,
        username=input_username,
        password=input_password,
        session_token=input_session_token,
    ).token
    assert token == "some session id"


def test_check_is_valid_session_token(requests_mock):
    requests_mock.get(f"{config['instance_api_url']}user/current", json={"common_name": "common_name", "last_login": "last_login"})

    assert MetabaseSessionTokenAuthenticator(
        config=config,
        options=options,
        api_url=input_instance_api_url,
        username=input_username,
        password=input_password,
        session_token=input_session_token,
    ).is_valid_session_token()


def test_check_is_valid_session_token_unauthorized():
    assert not MetabaseSessionTokenAuthenticator(
        config=config,
        options=options,
        api_url=input_instance_api_url,
        username=input_username,
        password=input_password,
        session_token=input_session_token,
    ).is_valid_session_token()


def test_get_new_session_token(requests_mock):
    requests_mock.post(f"{config['instance_api_url']}session", headers={"Content-Type": "application/json"}, json={"id": "some session id"})

    session_token = get_new_session_token(f'{config["instance_api_url"]}session', config["username"], config["password"])
    assert session_token == "some session id"
