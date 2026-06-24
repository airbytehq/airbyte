#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time

import jwt
import pytest
import requests_mock as req_mock
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from source_salesforce.api import Salesforce


@pytest.fixture(scope="module")
def rsa_private_key_pem():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem.decode()


@pytest.fixture
def jwt_config(rsa_private_key_pem):
    return {
        "client_id": "fake_client_id",
        "is_sandbox": False,
        "start_date": "2021-01-01T00:00:00Z",
        "auth_type": "JWT",
        "private_key": rsa_private_key_pem,
        "username": "testuser@example.com",
    }


@pytest.fixture
def client_config():
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "is_sandbox": False,
        "start_date": "2021-01-01T00:00:00Z",
        "auth_type": "Client",
    }


class TestJWTLogin:
    def test_jwt_login_sends_correct_grant_type(self, jwt_config):
        sf = Salesforce(**jwt_config)
        with req_mock.Mocker() as m:
            m.post(
                "https://login.salesforce.com/services/oauth2/token",
                json={"access_token": "jwt_token_123", "instance_url": "https://myinstance.salesforce.com"},
            )
            sf.login()

            assert sf.access_token == "jwt_token_123"
            assert sf.instance_url == "https://myinstance.salesforce.com"

            request_body = m.last_request.text
            assert "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer" in request_body
            assert "assertion=" in request_body

    def test_jwt_login_jwt_claims_are_correct(self, jwt_config, rsa_private_key_pem):
        sf = Salesforce(**jwt_config)
        with req_mock.Mocker() as m:
            m.post(
                "https://login.salesforce.com/services/oauth2/token",
                json={"access_token": "jwt_token_123", "instance_url": "https://myinstance.salesforce.com"},
            )
            sf.login()

            request_body = m.last_request.text
            from urllib.parse import unquote_plus

            params = dict(param.split("=", 1) for param in request_body.split("&"))
            assertion = unquote_plus(params["assertion"])

            decoded = jwt.decode(assertion, options={"verify_signature": False}, algorithms=["RS256"])
            assert decoded["iss"] == "fake_client_id"
            assert decoded["sub"] == "testuser@example.com"
            assert decoded["aud"] == "https://login.salesforce.com"
            assert "exp" in decoded
            assert decoded["exp"] - time.time() <= 300

    def test_jwt_login_sandbox_uses_test_url(self, jwt_config, rsa_private_key_pem):
        jwt_config["is_sandbox"] = True
        sf = Salesforce(**jwt_config)
        with req_mock.Mocker() as m:
            m.post(
                "https://test.salesforce.com/services/oauth2/token",
                json={"access_token": "sandbox_token", "instance_url": "https://test.salesforce.com"},
            )
            sf.login()

            assert sf.access_token == "sandbox_token"
            assert sf.instance_url == "https://test.salesforce.com"

            request_body = m.last_request.text
            from urllib.parse import unquote_plus

            params = dict(param.split("=", 1) for param in request_body.split("&"))
            assertion = unquote_plus(params["assertion"])
            decoded = jwt.decode(assertion, options={"verify_signature": False}, algorithms=["RS256"])
            assert decoded["aud"] == "https://test.salesforce.com"

    def test_client_login_still_works(self, client_config):
        sf = Salesforce(**client_config)
        with req_mock.Mocker() as m:
            m.post(
                "https://login.salesforce.com/services/oauth2/token",
                json={"access_token": "client_token", "instance_url": "https://myinstance.salesforce.com"},
            )
            sf.login()

            assert sf.access_token == "client_token"
            request_body = m.last_request.text
            assert "grant_type=refresh_token" in request_body
            assert "client_id=fake_client_id" in request_body
            assert "client_secret=fake_client_secret" in request_body
            assert "refresh_token=fake_refresh_token" in request_body

    def test_jwt_login_refreshes_token_on_each_call(self, jwt_config):
        sf = Salesforce(**jwt_config)
        with req_mock.Mocker() as m:
            m.post(
                "https://login.salesforce.com/services/oauth2/token",
                [
                    {"json": {"access_token": "token_1", "instance_url": "https://myinstance.salesforce.com"}},
                    {"json": {"access_token": "token_2", "instance_url": "https://myinstance.salesforce.com"}},
                ],
            )
            sf.login()
            assert sf.access_token == "token_1"

            sf.login()
            assert sf.access_token == "token_2"

    def test_default_auth_type_is_client(self):
        sf = Salesforce(
            client_id="cid",
            client_secret="csec",
            refresh_token="rtok",
            is_sandbox=False,
        )
        assert sf.auth_type == "Client"

    def test_jwt_auth_type_stored(self, jwt_config):
        sf = Salesforce(**jwt_config)
        assert sf.auth_type == "JWT"
        assert sf.private_key == jwt_config["private_key"]
        assert sf.username == "testuser@example.com"
