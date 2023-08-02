#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
def clients_instance():
    """
    Clients instance object response
    """
    return {
        "client_id": "AaiyAPdpYdesoKnqjj8HJqRn4T5titww",
        "tenant": "",
        "name": "My application",
        "description": "",
        "global": False,
        "client_secret": "MG_TNT2ver-SylNat-_VeMmd-4m0Waba0jr1troztBniSChEw0glxEmgEi2Kw40H",
        "app_type": "",
        "logo_uri": "",
        "is_first_party": False,
        "oidc_conformant": False,
        "callbacks": ["http://localhost/callback"],
        "allowed_origins": [""],
        "web_origins": [""],
        "client_aliases": [""],
        "allowed_clients": [""],
        "allowed_logout_urls": ["http://localhost/logoutCallback"],
        "oidc_backchannel_logout": {"backchannel_logout_urls": [""]},
        "grant_types": [""],
        "jwt_configuration": {"lifetime_in_seconds": 36000, "secret_encoded": True, "scopes": {}, "alg": "HS256"},
        "signing_keys": ["object"],
        "encryption_key": {"pub": "", "cert": "", "subject": ""},
        "sso": False,
        "sso_disabled": False,
        "cross_origin_authentication": False,
        "cross_origin_loc": "",
        "custom_login_page_on": True,
        "custom_login_page": "",
        "custom_login_page_preview": "",
        "form_template": "",
        "addons": {
            "aws": {"principal": "", "role": "", "lifetime_in_seconds": 0},
            "azure_blob": {
                "accountName": "",
                "storageAccessKey": "",
                "containerName": "",
                "blobName": "",
                "expiration": 0,
                "signedIdentifier": "",
                "blob_read": False,
                "blob_write": False,
                "blob_delete": False,
                "container_read": False,
                "container_write": False,
                "container_delete": False,
                "container_list": False,
            },
            "azure_sb": {"namespace": "", "sasKeyName": "", "sasKey": "", "entityPath": "", "expiration": 0},
            "rms": {"url": ""},
            "mscrm": {"url": ""},
            "slack": {"team": ""},
            "sentry": {"org_slug": "", "base_url": ""},
            "box": {},
            "cloudbees": {},
            "concur": {},
            "dropbox": {},
            "echosign": {"domain": ""},
            "egnyte": {"domain": ""},
            "firebase": {"secret": "", "private_key_id": "", "private_key": "", "client_email": "", "lifetime_in_seconds": 0},
            "newrelic": {"account": ""},
            "office365": {"domain": "", "connection": ""},
            "salesforce": {"entity_id": ""},
            "salesforce_api": {"clientid": "", "principal": "", "communityName": "", "community_url_section": ""},
            "salesforce_sandbox_api": {"clientid": "", "principal": "", "communityName": "", "community_url_section": ""},
            "samlp": {
                "mappings": {},
                "audience": "",
                "recipient": "",
                "createUpnClaim": False,
                "mapUnknownClaimsAsIs": False,
                "passthroughClaimsWithNoMapping": False,
                "mapIdentities": False,
                "signatureAlgorithm": "",
                "digestAlgorithm": "",
                "issuer": "",
                "destination": "",
                "lifetimeInSeconds": 0,
                "signResponse": False,
                "nameIdentifierFormat": "",
                "nameIdentifierProbes": [""],
                "authnContextClassRef": "",
            },
            "layer": {"providerId": "", "keyId": "", "privateKey": "", "principal": "", "expiration": 0},
            "sap_api": {
                "clientid": "",
                "usernameAttribute": "",
                "tokenEndpointUrl": "",
                "scope": "",
                "servicePassword": "",
                "nameIdentifierFormat": "",
            },
            "sharepoint": {"url": "", "external_url": [""]},
            "springcm": {"acsurl": ""},
            "wams": {"masterkey": ""},
            "wsfed": {},
            "zendesk": {"accountName": ""},
            "zoom": {"account": ""},
            "sso_integration": {"name": "", "version": ""},
        },
        "token_endpoint_auth_method": "none",
        "client_metadata": {},
        "mobile": {
            "android": {"app_package_name": "", "sha256_cert_fingerprints": []},
            "ios": {"team_id": "", "app_bundle_identifier": ""},
        },
        "initiate_login_uri": "",
        "native_social_login": {"apple": {"enabled": False}, "facebook": {"enabled": False}},
        "refresh_token": {
            "rotation_type": "non-rotating",
            "expiration_type": "non-expiring",
            "leeway": 0,
            "token_lifetime": 0,
            "infinite_token_lifetime": False,
            "idle_token_lifetime": 0,
            "infinite_idle_token_lifetime": False,
        },
        "organization_usage": "deny",
        "organization_require_behavior": "no_prompt",
        "client_authentication_methods": {"private_key_jwt": {"credentials": ["object"]}}
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
