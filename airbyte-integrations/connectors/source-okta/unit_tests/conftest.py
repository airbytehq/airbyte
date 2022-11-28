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
    return "https://test_domain.okta.com"


@pytest.fixture()
def api_url(url_base):
    """
    Just return API url based on url_base
    """
    return f"{url_base}"


@pytest.fixture()
def oauth_config():
    """
    Credentials for oauth2.0 authorization
    """
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "domain": "test_domain",
    }


@pytest.fixture()
def wrong_oauth_config_bad_credentials_record():
    """
    Malformed Credentials for oauth2.0 authorization
    credentials -> credential
    """
    return {
        "credential": {
            "auth_type": "oauth2.0",
            "client_secret": "test_client_secret",
            "client_id": "test_client_id",
            "refresh_token": "test_refresh_token",
        },
        "domain": "test_domain",
    }


@pytest.fixture()
def wrong_oauth_config_bad_auth_type():
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
        "domain": "test_domain",
    }


@pytest.fixture()
def token_config():
    """
    Just test 'token'
    """
    return {"token": "test_token", "start_date": "2021-03-21T20:49:13Z"}


@pytest.fixture()
def auth_token_config():
    """
    Credentials for Token Authorization connect
    """
    return {"start_date": "2021-03-21T20:49:13Z", "credentials": {"auth_type": "api_token", "api_token": "test_token"}}


@pytest.fixture()
def user_status_filter():
    statuses = ["ACTIVE", "DEPROVISIONED", "LOCKED_OUT", "PASSWORD_EXPIRED", "PROVISIONED", "RECOVERY", "STAGED", "SUSPENDED"]
    return " or ".join([f'status eq "{status}"' for status in statuses])


@pytest.fixture()
def users_instance(api_url):
    """
    Users instance object response
    """
    return {
        "id": "test_user_id",
        "status": "ACTIVE",
        "created": "2021-04-21T21:04:03.000Z",
        "activated": None,
        "statusChanged": "2021-04-21T21:41:18.000Z",
        "lastLogin": "2022-07-18T07:57:05.000Z",
        "lastUpdated": "2021-11-03T13:45:55.000Z",
        "passwordChanged": "2021-04-21T21:41:18.000Z",
        "type": {"id": "test_user_type"},
        "profile": {
            "firstName": "TestUser",
            "lastName": "Test",
            "mobilePhone": "+1 2342 2342424",
            "secondEmail": None,
            "login": "test@airbyte.io",
            "email": "test@airbyte.io",
        },
        "credentials": {
            "password": {},
            "emails": [{"value": "test@airbyte.io", "status": "VERIFIED", "type": "PRIMARY"}],
            "provider": {"type": "OKTA", "name": "OKTA"},
        },
        "_links": {"self": {"href": f"{api_url}/users/test_user_id"}},
    }


@pytest.fixture()
def custom_role_instance(api_url):
    """
    Custom Role instance object response
    """
    _id = "custom_role_id"
    return {
        "id": _id,
        "label": "custom role for test",
        "description": "custom role for test",
        "created": "2022-07-13T07:54:31.000Z",
        "lastUpdated": "2022-07-13T07:54:31.000Z",
        "_links": {
            "permissions": {"href": f"{api_url}/iam/roles/{_id}/permissions"},
            "self": {"href": f"{api_url}/iam/roles/{_id}"},
        },
    }


@pytest.fixture()
def permission_instance(api_url):
    """
    Custom Role instance object response
    """
    _role_id = "test_role_id"
    _id = "okta.users.read"
    return {
        "label": _id,
        "created": "2022-07-09T20:54:54.000Z",
        "lastUpdated": "2022-07-09T20:54:54.000Z",
        "_links": {
            "role": {"href": f"{api_url}/api/v1/iam/roles/{_role_id}"},
            "self": {"href": f"{api_url}/api/v1/iam/roles/{_role_id}/permissions/{_id}"},
        },
    }


@pytest.fixture()
def groups_instance(api_url):
    """
    Groups instance object response
    """
    _id = "test_group_id"
    return {
        "id": _id,
        "created": "2021-04-21T21:03:55.000Z",
        "lastUpdated": "2021-04-21T21:03:55.000Z",
        "lastMembershipUpdated": "2021-09-08T07:04:28.000Z",
        "objectClass": ["okta:user_group"],
        "type": "BUILT_IN",
        "profile": {"name": "Everyone", "description": "All users in your organization"},
        "_links": {
            "logo": [
                {"name": "medium", "href": "{https://test_static_image.png", "type": "image/png"},
                {"name": "large", "href": "https://test_other_static_image.png", "type": "image/png"},
            ],
            "users": {"href": f"{api_url}/groups/{_id}/users"},
            "apps": {"href": f"{api_url}/groups/{_id}/apps"},
        },
    }


@pytest.fixture()
def group_members_instance(api_url):
    """
    Group Members instance object response
    """
    _id = "test_user_id"
    return {
        "id": _id,
        "status": "ACTIVE",
        "created": "2021-04-21T21:04:03.000Z",
        "activated": None,
        "statusChanged": "2021-04-21T21:41:18.000Z",
        "lastLogin": "2022-07-18T07:57:05.000Z",
        "lastUpdated": "2021-11-03T13:45:55.000Z",
        "passwordChanged": "2021-04-21T21:41:18.000Z",
        "type": {"id": "test_user_type"},
        "profile": {
            "firstName": "test_user_first_name",
            "lastName": "test_user_last_name",
            "mobilePhone": "+1 234 56789012",
            "secondEmail": None,
            "login": "test@login.test",
            "email": "test@login.test",
        },
        "credentials": {
            "password": {},
            "emails": [{"value": "test@login.test", "status": "VERIFIED", "type": "PRIMARY"}],
            "provider": {"type": "OKTA", "name": "OKTA"},
        },
        "_links": {"self": {"href": f"{api_url}/users/{_id}"}},
    }


@pytest.fixture()
def group_role_assignments_instance():
    """
    Group Role Assignment instance object response
    """
    return {
        "actor": {
            "id": "test_user_id",
            "type": "User",
            "alternateId": "test@airbyte.io",
            "displayName": "test_user_first_name test_user_last_name",
            "detailEntry": None,
        },
        "client": {"userAgent": None, "zone": None, "device": None, "id": None, "ipAddress": None, "geographicalContext": None},
        "device": None,
        "authenticationContext": {
            "authenticationProvider": None,
            "credentialProvider": None,
            "credentialType": None,
            "issuer": None,
            "interface": None,
            "authenticationStep": 0,
            "externalSessionId": None,
        },
        "displayMessage": "Add assigned application to group",
        "eventType": "group.application_assignment.add",
        "outcome": {"result": "SUCCESS", "reason": None},
        "published": "2022-07-18T07:58:55Z",
        "securityContext": {"asNumber": None, "asOrg": None, "isp": None, "domain": None, "isProxy": None},
        "severity": "INFO",
        "debugContext": {"debugData": {"groupAppAssignmentId": "test_group_app_assignment_id"}},
        "legacyEventType": "group.application_assignment.add",
        "transaction": {"type": "JOB", "id": "test_transaction_id", "detail": {}},
        "uuid": "test_uuid",
        "version": "0",
        "request": {"ipChain": []},
        "target": [
            {"id": "test_user_group_id", "type": "UserGroup", "alternateId": "unknown", "displayName": "test-runner", "detailEntry": None},
            {
                "id": "test_app_instance_id",
                "type": "AppInstance",
                "alternateId": "Okta Admin Console",
                "displayName": "Okta Admin Console",
                "detailEntry": None,
            },
        ],
    }


@pytest.fixture()
def user_role_assignments_instance(api_url):
    """
    User Role Assignment instance object response
    """
    _user_id = "test_user_id"
    return {
        "id": _user_id,
        "label": "Super Organization Administrator",
        "type": "SUPER_ADMIN",
        "status": "ACTIVE",
        "created": "2021-04-21T21:04:03.000Z",
        "lastUpdated": "2021-04-21T21:04:03.000Z",
        "assignmentType": "USER",
        "_links": {"assignee": {"href": f"{api_url}/users/{_user_id}"}},
    }


@pytest.fixture()
def logs_instance():
    """
    Logs instance object response
    """
    return {
        "actor": {
            "id": "test_client_app_id",
            "type": "PublicClientApp",
            "alternateId": "test_client_app_id",
            "displayName": "Airbyte",
            "detailEntry": None,
        },
        "client": {
            "userAgent": {"rawUserAgent": "python-requests/2.28.1", "os": "Unknown", "browser": "UNKNOWN"},
            "zone": "None",
            "device": "Unknown",
            "id": None,
            "ipAddress": "0.0.0.0",
            "geographicalContext": {
                "city": "TestCity",
                "state": "Test State",
                "country": "Test Country",
                "postalCode": "31-008",
                "geolocation": {"lat": 0.0, "lon": 0.0},
            },
        },
        "device": None,
        "authenticationContext": {
            "authenticationProvider": None,
            "credentialProvider": None,
            "credentialType": None,
            "issuer": None,
            "interface": None,
            "authenticationStep": 0,
            "externalSessionId": "unknown",
        },
        "displayMessage": "OIDC access token is granted",
        "eventType": "app.oauth2.token.grant.access_token",
        "outcome": {"result": "SUCCESS", "reason": None},
        "published": "2022-07-19T15:54:11Z",
        "securityContext": {"asNumber": 0, "asOrg": "Test Org", "isp": "TestProvider", "domain": "test-domain.com", "isProxy": False},
        "severity": "INFO",
        "debugContext": {
            "debugData": {
                "clientAuthType": "client_secret_basic",
                "grantedScopes": "okta.users.read, okta.logs.read, okta.groups.read, okta.roles.read, offline_access",
                "requestId": "test_debug_request_id",
                "responseTime": "559",
                "dtHash": "test_dt_hash",
                "clientSecret": "test_client_secret",
                "requestUri": "/oauth2/v1/token",
                "requestedScopes": "",
                "threatSuspected": "False",
                "grantType": "refresh_token",
                "url": "/oauth2/v1/token?",
            }
        },
        "legacyEventType": "app.oauth2.token.grant.access_token_success",
        "transaction": {"type": "WEB", "id": "test_debug_request_id", "detail": {}},
        "uuid": "test_uuid",
        "version": "0",
        "request": {
            "ipChain": [
                {
                    "ip": "0.0.0.0",
                    "geographicalContext": {
                        "city": "TestCity",
                        "state": "Test State",
                        "country": "Test Country",
                        "postalCode": "31-008",
                        "geolocation": {"lat": 0.0, "lon": 0.0},
                    },
                    "version": "V4",
                    "source": None,
                }
            ]
        },
        "target": [
            {"id": "test_user_id", "type": "User", "alternateId": None, "displayName": None, "detailEntry": None},
            {
                "id": "test_id",
                "type": "access_token",
                "alternateId": None,
                "displayName": "Access Token",
                "detailEntry": {"expires": "2022-07-19T16:54:11.000Z", "subject": "test_user_id", "hash": "test_detail_entry_hash"},
            },
        ],
    }


@pytest.fixture()
def resource_set_instance(api_url):
    """
    Resource set object instance
    """
    _id = "iam5xyzmibarA6Afoo7"
    return {
        "id": _id,
        "label": "all users",
        "description": "all users",
        "created": "2022-07-09T20:58:41.000Z",
        "lastUpdated": "2022-07-09T20:58:41.000Z",
        "_links": {
            "bindings": {"href": f"{url_base}/iam/resource-sets/{_id}/bindings"},
            "self": {"href": f"{url_base}/iam/resource-sets/{_id}"},
            "resources": {"href": f"{url_base}/iam/resource-sets/{_id}/resources"},
        },
    }


@pytest.fixture()
def latest_record_instance(url_base, api_url):
    """
    Last Record instance object response
    """
    return {
        "id": "test_user_group_id",
        "created": "2022-07-18T07:58:11.000Z",
        "lastUpdated": "2022-07-18T07:58:11.000Z",
        "lastMembershipUpdated": "2022-07-18T07:58:11.000Z",
        "objectClass": ["okta:user_group"],
        "type": "OKTA_GROUP",
        "profile": {"name": "test-runner", "description": None},
        "_links": {
            "logo": [
                {"name": "medium", "href": f"{url_base}/path_to_images/okta-medium.filename.png", "type": "image/png"},
                {"name": "large", "href": f"{url_base}/path_to_images/okta-large.filename.png", "type": "image/png"},
            ],
            "users": {"href": f"{api_url}/groups/test_user_group_id/users"},
            "apps": {"href": f"{api_url}/groups/test_user_group_id/apps"},
        },
    }


@pytest.fixture()
def error_while_refreshing_access_token():
    """
    Error raised when using incorrect access token
    """
    return "Error while refreshing access token: 'access_token'"


@pytest.fixture()
def error_failed_to_authorize_with_provided_credentials():
    """
    Error raised when using incorrect oauth2.0 credentials
    """
    return "Failed to authenticate with the provided credentials"


@pytest.fixture()
def start_date():
    return pendulum.parse("2021-03-21T20:49:13Z")
