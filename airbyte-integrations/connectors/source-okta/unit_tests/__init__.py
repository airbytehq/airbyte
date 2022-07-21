#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

url_base = "https://test_domain.com"
api_url = f"{url_base}"


def oauth_config():
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "domain": "test_domain",
    }


def wrong_oauth_config_bad_credentials_record():
    return {
        "credential": {
            "auth_type": "oauth2.0",
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "domain": "test_domain",
    }


def wrong_oauth_config_bad_auth_type():
    return {
        "credentials": {
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "domain": "test_domain",
    }


def token_config():
    return {"token": "test_token"}


def auth_token_config():
    return {"credentials": {"auth_type": "api_token", "api_token": "test_token"}}
