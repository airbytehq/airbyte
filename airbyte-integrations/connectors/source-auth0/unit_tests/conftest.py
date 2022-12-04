#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest


@pytest.fixture()
def url_base():
    """
    URL base for test
    """
    return "https://dev-yourOrg.us.auth0.com"


@pytest.fixture()
def api_url(url_base):
    """
    Just return API url based on url_base
    """
    return f"{url_base}/api/v2"


@pytest.fixture()
def oauth_config(url_base):
    """
    Credentials for oauth2.0 authorization
    """
    return {
        "credentials": {
            "auth_type": "oauth2_confidential_application",
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "audience": f"{url_base}/api/v2",
        },
        "base_url": url_base,
    }


@pytest.fixture()
def wrong_oauth_config_bad_credentials_record(url_base):
    """
    Malformed Credentials for oauth2.0 authorization
    credentials -> credential
    """
    return {
        "credential": {
            "auth_type": "oauth2.0",
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
        },
        "base_url": url_base,
    }


@pytest.fixture()
def wrong_oauth_config_bad_auth_type(url_base):
    """
    Wrong Credentials format for oauth2.0 authorization
    absent "auth_type" field
    """
    return {
        "credentials": {
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "base_url": url_base,
    }


@pytest.fixture()
def token_config(url_base):
    """
    Just test 'token'
    """
    return {
        "credentials": {"auth_type": "oauth2_access_token", "access_token": "test-token"},
        "base_url": url_base,
    }


@pytest.fixture()
def user_status_filter():
    statuses = ["ACTIVE", "DEPROVISIONED", "LOCKED_OUT", "PASSWORD_EXPIRED", "PROVISIONED", "RECOVERY", "STAGED", "SUSPENDED"]
    return " or ".join([f'status eq "{status}"' for status in statuses])


@pytest.fixture()
def users_instance():
    """
    Users instance object response
    """
    return {
        "blocked": False,
        "created_at": "2022-10-21T04:10:34.240Z",
        "email": "rodrick_waelchi73@yahoo.com",
        "email_verified": False,
        "family_name": "Kerluke",
        "given_name": "Nick",
        "identities": [
            {
                "user_id": "15164a44-8064-4ef9-ac31-fb08814da3f9",
                "connection": "Username-Password-Authentication",
                "provider": "auth0",
                "isSocial": False,
            }
        ],
        "name": "Linda Sporer IV",
        "nickname": "Marty",
        "picture": "https://secure.gravatar.com/avatar/15626c5e0c749cb912f9d1ad48dba440?s=480&r=pg&d=https%3A%2F%2Fssl.gstatic.com%2Fs2%2Fprofiles%2Fimages%2Fsilhouette80.png",
        "updated_at": "2022-10-21T04:10:34.240Z",
        "user_id": "auth0|15164a44-8064-4ef9-ac31-fb08814da3f9",
        "user_metadata": {},
        "app_metadata": {},
    }


@pytest.fixture()
def latest_record_instance():
    """
    Last Record instance object response
    """
    return {
        "id": "test_user_group_id",
        "created": "2022-07-18T07:58:11.000Z",
        "lastUpdated": "2022-07-18T07:58:11.000Z",
    }


@pytest.fixture()
def error_failed_to_authorize_with_provided_credentials():
    """
    Error raised when using incorrect oauth2.0 credentials
    """
    return "Failed to authenticate with the provided credentials"


@pytest.fixture()
def start_date():
    return pendulum.parse("2021-03-21T20:49:13Z")
