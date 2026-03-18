#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from unittest.mock import MagicMock, patch

import jwt
import pytest
import responses
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from source_github.source import SourceGithub
from source_github.utils import generate_github_app_token

from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def _generate_test_rsa_key():
    """Generate a test RSA private key in PEM format."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


TEST_PEM_KEY = _generate_test_rsa_key()


@responses.activate
def test_generate_github_app_token_success():
    responses.add(
        responses.POST,
        "https://api.github.com/app/installations/12345/access_tokens",
        json={"token": "ghs_test_token_123", "expires_at": "2026-01-01T00:00:00Z"},
        status=201,
    )

    token = generate_github_app_token(
        app_id="99999",
        private_key=TEST_PEM_KEY,
        installation_id="12345",
    )

    assert token == "ghs_test_token_123"
    # Verify the JWT was sent correctly
    auth_header = responses.calls[0].request.headers["Authorization"]
    assert auth_header.startswith("Bearer ")
    decoded = jwt.decode(auth_header.split(" ")[1], options={"verify_signature": False})
    assert decoded["iss"] == "99999"
    assert "iat" in decoded
    assert "exp" in decoded


@responses.activate
def test_generate_github_app_token_custom_api_url():
    responses.add(
        responses.POST,
        "https://github.example.com/api/v3/app/installations/555/access_tokens",
        json={"token": "ghs_enterprise_token"},
        status=201,
    )

    token = generate_github_app_token(
        app_id="111",
        private_key=TEST_PEM_KEY,
        installation_id="555",
        api_url="https://github.example.com/api/v3",
    )

    assert token == "ghs_enterprise_token"


@responses.activate
def test_generate_github_app_token_bad_credentials():
    responses.add(
        responses.POST,
        "https://api.github.com/app/installations/12345/access_tokens",
        json={"message": "Bad credentials"},
        status=401,
    )

    with pytest.raises(AirbyteTracedException, match="Failed to generate GitHub App installation token"):
        generate_github_app_token(
            app_id="99999",
            private_key=TEST_PEM_KEY,
            installation_id="12345",
        )


@responses.activate
def test_generate_github_app_token_retries_on_5xx():
    responses.add(
        responses.POST,
        "https://api.github.com/app/installations/12345/access_tokens",
        json={"message": "Internal Server Error"},
        status=500,
    )
    responses.add(
        responses.POST,
        "https://api.github.com/app/installations/12345/access_tokens",
        json={"token": "ghs_after_retry"},
        status=201,
    )

    token = generate_github_app_token(
        app_id="99999",
        private_key=TEST_PEM_KEY,
        installation_id="12345",
    )

    assert token == "ghs_after_retry"
    assert len(responses.calls) == 2


def test_pem_newline_normalization():
    """Verify that literal \\n sequences are converted to real newlines."""
    # Take a real PEM key and replace newlines with literal \n
    mangled_key = TEST_PEM_KEY.replace("\n", "\\n")
    assert "\\n" in mangled_key

    # The function should normalize this internally — verify by checking JWT generation doesn't fail
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://api.github.com/app/installations/12345/access_tokens",
            json={"token": "ghs_normalized"},
            status=201,
        )
        token = generate_github_app_token(
            app_id="99999",
            private_key=mangled_key,
            installation_id="12345",
        )
        assert token == "ghs_normalized"


def test_get_access_token_github_app():
    """Verify that SourceGithub.get_access_token dispatches to GitHub App auth."""
    source = SourceGithub()
    config = {
        "credentials": {
            "private_key": TEST_PEM_KEY,
            "app_id": "99999",
            "installation_id": "12345",
        }
    }

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://api.github.com/app/installations/12345/access_tokens",
            json={"token": "ghs_from_source"},
            status=201,
        )
        title, token = source.get_access_token(config)
        assert title == "GitHub App"
        assert token == "ghs_from_source"


def test_get_access_token_missing_field():
    """Verify error when GitHub App config is missing required fields."""
    source = SourceGithub()
    config = {
        "credentials": {
            "private_key": TEST_PEM_KEY,
            # missing app_id and installation_id
        }
    }

    with pytest.raises(AirbyteTracedException, match="app_id"):
        source.get_access_token(config)
