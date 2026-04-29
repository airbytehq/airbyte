#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json

import components
import pytest
import requests
from components import AmazonSPOauthAuthenticator, AmazonSPRdtAuthenticator


@pytest.fixture(autouse=True)
def reset_authenticator_instances():
    """Reset the module-level authenticator instances before and after each test."""
    components._authenticator_instances.clear()
    yield
    components._authenticator_instances.clear()


def _create_authenticator(cls=AmazonSPOauthAuthenticator, with_error_params=True):
    """
    Create an authenticator instance with optional refresh_token_error_* params,
    matching the manifest.yaml configuration.
    """
    auth = object.__new__(cls)
    if with_error_params:
        auth._refresh_token_error_status_codes = (400,)
        auth._refresh_token_error_key = "error"
        auth._refresh_token_error_values = ("invalid_grant",)
    else:
        auth._refresh_token_error_status_codes = ()
        auth._refresh_token_error_key = ""
        auth._refresh_token_error_values = ()
    return auth


def _create_http_error(status_code: int, body) -> requests.exceptions.HTTPError:
    """Create a requests.exceptions.HTTPError with a response carrying the given status and body."""
    response = requests.Response()
    response.status_code = status_code
    if isinstance(body, dict):
        response._content = json.dumps(body).encode("utf-8")
    else:
        response._content = body if isinstance(body, bytes) else body.encode("utf-8")
    return requests.exceptions.HTTPError(response=response)


@pytest.mark.parametrize(
    "cls,with_error_params,status_code,body,expected",
    [
        pytest.param(
            AmazonSPOauthAuthenticator,
            True,
            400,
            {"error": "invalid_grant", "error_description": "The request has an invalid grant parameter : refresh_token"},
            True,
            id="400_invalid_grant_classified_as_refresh_error",
        ),
        pytest.param(
            AmazonSPRdtAuthenticator,
            True,
            400,
            {"error": "invalid_grant", "error_description": "The request has an invalid grant parameter : refresh_token"},
            True,
            id="rdt_authenticator_inherits_classification",
        ),
        pytest.param(
            AmazonSPOauthAuthenticator,
            True,
            400,
            {"error": "invalid_client", "error_description": "Client authentication failed"},
            False,
            id="400_different_error_value_not_classified",
        ),
        pytest.param(
            AmazonSPOauthAuthenticator,
            True,
            401,
            {"error": "invalid_grant"},
            False,
            id="401_not_in_error_status_codes",
        ),
        pytest.param(
            AmazonSPOauthAuthenticator,
            True,
            400,
            {"message": "Bad Request"},
            False,
            id="400_missing_error_key_not_classified",
        ),
        pytest.param(
            AmazonSPOauthAuthenticator,
            True,
            400,
            b"not json",
            False,
            id="400_non_json_body_not_classified",
        ),
        pytest.param(
            AmazonSPOauthAuthenticator,
            False,
            400,
            {"error": "invalid_grant"},
            False,
            id="without_params_400_invalid_grant_not_classified",
        ),
    ],
)
def test_wrap_refresh_token_exception(cls, with_error_params, status_code, body, expected):
    """
    Verify _wrap_refresh_token_exception correctly identifies invalid-grant errors
    when refresh_token_error_* params are configured, matching the manifest.yaml fix.
    """
    auth = _create_authenticator(cls=cls, with_error_params=with_error_params)
    error = _create_http_error(status_code, body)
    assert auth._wrap_refresh_token_exception(error) is expected
