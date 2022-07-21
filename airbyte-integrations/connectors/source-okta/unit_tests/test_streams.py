#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import time
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_okta.source import (
    CustomRoles,
    GroupMembers,
    GroupRoleAssignments,
    Groups,
    IncrementalOktaStream,
    Logs,
    OktaStream,
    UserRoleAssignments,
    Users,
)
from unit_tests import api_url, url_base


@pytest.fixture()
def users_instance():
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
def custom_role_instance():
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
def groups_instance():
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
def group_members_instance():
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
        "published": "2022-07-18T07:58:55.625Z",
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
def user_role_assignments_instance():
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
        "published": "2022-07-19T15:54:11.545Z",
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
def latest_record_instance():
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


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(OktaStream, "path", "v0/example_endpoint")
    mocker.patch.object(OktaStream, "primary_key", "test_primary_key")
    mocker.patch.object(OktaStream, "__abstractmethods__", set())
    mocker.patch.object(IncrementalOktaStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalOktaStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalOktaStream, "__abstractmethods__", set())


class TestStatusCodes:
    @pytest.mark.parametrize(
        ("http_status", "should_retry"),
        [
            (HTTPStatus.OK, False),
            (HTTPStatus.BAD_REQUEST, False),
            (HTTPStatus.TOO_MANY_REQUESTS, True),
            (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        ],
    )
    def test_should_retry(self, patch_base_class, http_status, should_retry):
        response_mock = MagicMock()
        response_mock.status_code = http_status
        stream = OktaStream(url_base=url_base)
        assert stream.should_retry(response_mock) == should_retry


class TestOktaStream:
    def test_okta_stream_request_params(self, patch_base_class):
        stream = OktaStream(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"limit": 200}
        assert stream.request_params(**inputs) == expected_params

    def test_okta_stream_parse_response(self, patch_base_class, requests_mock):
        stream = OktaStream(url_base=url_base)
        requests_mock.get(f"{api_url}", json=[{"a": 123}, {"b": "xx"}])
        resp = requests.get(f"{api_url}")
        inputs = {"response": resp, "stream_state": MagicMock()}
        expected_parsed_object = [{"a": 123}, {"b": "xx"}]
        assert list(stream.parse_response(**inputs)) == expected_parsed_object

    def test_okta_stream_backoff_time(self, patch_base_class):
        response_mock = requests.Response()
        stream = OktaStream(url_base=url_base)
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_okta_stream_incremental_request_params(self, patch_base_class):
        stream = IncrementalOktaStream(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"limit": 200}
        assert stream.request_params(**inputs) == expected_params

    def test_incremental_okta_stream_parse_response(self, patch_base_class, requests_mock):
        stream = IncrementalOktaStream(url_base=url_base)
        requests_mock.get(f"{api_url}", json=[{"a": 123}, {"b": "xx"}])
        resp = requests.get(f"{api_url}")
        inputs = {"response": resp, "stream_state": MagicMock()}
        expected_parsed_object = [{"a": 123}, {"b": "xx"}]
        assert list(stream.parse_response(**inputs)) == expected_parsed_object

    def test_incremental_okta_stream_backoff_time(self, patch_base_class):
        response_mock = MagicMock()
        stream = IncrementalOktaStream(url_base=url_base)
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_okta_stream_incremental_backoff_time_empty(self, patch_base_class):
        stream = IncrementalOktaStream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.status_code = 200
        expected_params = None
        inputs = {"response": response}
        assert stream.backoff_time(**inputs) == expected_params

    def test_okta_stream_incremental_back_off_now(self, patch_base_class):
        stream = IncrementalOktaStream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.status_code = requests.codes.TOO_MANY_REQUESTS
        response.headers = {"x-rate-limit-reset": int(time.time())}
        expected_params = (0, 2)
        inputs = {"response": response}
        get_backoff_time = stream.backoff_time(**inputs)
        assert expected_params[0] <= get_backoff_time <= expected_params[1]

    def test_okta_stream_incremental_get_updated_state(self, patch_base_class, latest_record_instance):
        stream = IncrementalOktaStream(url_base=url_base)
        stream._cursor_field = "lastUpdated"
        current_stream_state = {"lastUpdated": "2021-04-21T21:03:55.000Z"}
        update_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record_instance)
        expected_result = {"lastUpdated": "2022-07-18T07:58:11.000Z"}
        assert update_state == expected_result

    def test_okta_stream_http_method(self, patch_base_class):
        stream = OktaStream(url_base=url_base)
        expected_method = "GET"
        assert stream.http_method == expected_method


class TestNextPageToken:
    def test_next_page_token(self, patch_base_class, users_instance):
        stream = OktaStream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}?param1=test_value1&param2=test_value2"}}
        inputs = {"response": response}
        expected_token = {"param1": "test_value1", "param2": "test_value2"}
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_empty_params(self, patch_base_class, users_instance):
        stream = OktaStream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}}
        inputs = {"response": response}
        expected_token = {}
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_link_have_self_and_equal_next(self, patch_base_class, users_instance):
        stream = OktaStream(url_base=url_base)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}, "self": {"url": f"{api_url}"}}
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token


class TestStreamUsers:

    # Users
    def test_stream_users(self, requests_mock, patch_base_class, users_instance):
        stream = Users(url_base=url_base)
        record = users_instance
        requests_mock.get(f"{api_url}/users", json=[record])
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == [record]

    def test_users_request_params_out_of_next_page_token(self, patch_base_class):
        stream = Users(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"limit": 200}
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_request_params_have_next_cursor(self, patch_base_class):
        stream = Users(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"next_cursor": "123"}}
        expected_params = {"limit": 200, "next_cursor": "123"}
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_request_params_have_latest_entry(self, patch_base_class):
        stream = Users(url_base=url_base)
        inputs = {"stream_slice": None, "stream_state": {"lastUpdated": "some_date"}, "next_page_token": {"next_cursor": "123"}}
        expected_params = {"limit": 200, "next_cursor": "123", "filter": 'lastUpdated gt "some_date"'}
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_parse_response(self, requests_mock, patch_base_class, users_instance):
        stream = Users(url_base=url_base)
        expected_params = users_instance
        requests_mock.get(f"{api_url}", json=[users_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [expected_params]


class TestStreamCustomRoles:
    def test_custom_roles(self, requests_mock, patch_base_class, custom_role_instance):
        stream = CustomRoles(url_base=url_base)
        record = {"roles": [custom_role_instance]}
        requests_mock.get(f"{api_url}/iam/roles?limit=200", json=record)
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == record["roles"]

    def test_custom_roles_parse_response(self, requests_mock, patch_base_class, custom_role_instance):
        stream = CustomRoles(url_base=url_base)
        record = {"roles": [custom_role_instance]}
        expected_params = [custom_role_instance]
        requests_mock.get(f"{api_url}", json=record)
        r = requests.get(f"{api_url}")
        assert list(stream.parse_response(response=r)) == expected_params


class TestStreamGroups:
    def test_groups(self, requests_mock, patch_base_class, groups_instance):
        stream = Groups(url_base=url_base)
        record = [groups_instance]
        requests_mock.get(f"{api_url}/groups?limit=200", json=record)
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == record

    def test_groups_parse_response(self, requests_mock, patch_base_class, groups_instance):
        stream = Groups(url_base=url_base)
        record = [groups_instance]
        expected_params = [groups_instance]
        requests_mock.get(f"{api_url}", json=record)
        r = requests.get(f"{api_url}")
        assert list(stream.parse_response(response=r)) == expected_params


class TestStreamGroupMembers:
    def test_group_members(self, requests_mock, patch_base_class, group_members_instance):
        stream = GroupMembers(url_base=url_base)
        group_id = "test_group_id"
        record = [group_members_instance]
        requests_mock.get(f"{api_url}/groups/{group_id}/users?limit=200", json=record)
        inputs = {"sync_mode": SyncMode.incremental, "stream_state": {}, "stream_slice": {"group_id": group_id}}
        assert list(stream.read_records(**inputs)) == record

    def test_group_members_parse_response(self, requests_mock, patch_base_class, group_members_instance):
        stream = GroupMembers(url_base=url_base)
        record = [group_members_instance]
        expected_params = [group_members_instance]
        requests_mock.get(f"{api_url}", json=record)
        r = requests.get(f"{api_url}")
        assert list(stream.parse_response(response=r)) == expected_params

    def test_group_members_request_params_with_latest_entry(self, patch_base_class, group_members_instance):
        stream = GroupMembers(url_base=url_base)
        inputs = {
            "stream_slice": {"group_id": "some_group"},
            "stream_state": {"id": "some_test_id"},
            "next_page_token": {"next_cursor": "123"},
        }
        expected_params = {"limit": 200, "next_cursor": "123", "after": "some_test_id"}
        assert stream.request_params(**inputs) == expected_params

    def test_group_members_slice_stream(self, requests_mock, patch_base_class, group_members_instance, groups_instance):
        stream = GroupMembers(url_base=url_base)
        requests_mock.get(f"{api_url}/groups?limit=200", json=[groups_instance])
        expected_params = [{"group_id": "test_group_id"}]
        assert list(stream.stream_slices()) == expected_params

    def test_group_member_request_get_update_state(self, latest_record_instance):
        stream = GroupMembers(url_base=url_base)
        stream._cursor_field = "id"
        current_stream_state = {"id": "test_user_group_id"}
        update_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record_instance)
        expected_result = {"id": "test_user_group_id"}
        assert update_state == expected_result


class TestStreamGroupRoleAssignment:
    def test_group_role_assignments(self, requests_mock, patch_base_class, group_role_assignments_instance):
        stream = GroupRoleAssignments(url_base=url_base)
        record = [group_role_assignments_instance]
        group_id = "test_group_id"
        mock_address = f"{api_url}/groups/{group_id}/roles?limit=200"
        requests_mock.get(mock_address, json=record)
        inputs = {"sync_mode": SyncMode.full_refresh, "stream_state": {}, "stream_slice": {"group_id": group_id}}
        assert list(stream.read_records(**inputs)) == record

    def test_group_role_assignments_parse_response(self, requests_mock, patch_base_class, group_role_assignments_instance):
        stream = GroupRoleAssignments(url_base=url_base)
        record = [group_role_assignments_instance]
        expected_params = [group_role_assignments_instance]
        requests_mock.get(f"{api_url}", json=record)
        r = requests.get(f"{api_url}")
        assert list(stream.parse_response(response=r)) == expected_params

    def test_group_role_assignments_slice_stream(self, requests_mock, patch_base_class, group_members_instance, groups_instance):
        stream = GroupRoleAssignments(url_base=url_base)
        requests_mock.get(f"{api_url}/groups?limit=200", json=[groups_instance])
        expected_params = [{"group_id": "test_group_id"}]
        assert list(stream.stream_slices()) == expected_params


class TestStreamLogs:
    def test_logs(self, requests_mock, patch_base_class, logs_instance):
        stream = Logs(url_base=url_base)
        record = [logs_instance]
        requests_mock.get(f"{api_url}/logs?limit=200", json=record)
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == record

    def test_logs_parse_response(self, requests_mock, patch_base_class, logs_instance):
        stream = Logs(url_base=url_base)
        record = [logs_instance]
        expected_params = [logs_instance]
        requests_mock.get(f"{api_url}/logs?limit=200", json=record)
        r = requests.get(f"{api_url}/logs?limit=200")
        assert list(stream.parse_response(response=r)) == expected_params

    def test_logs_request_params_for_since(self, patch_base_class, logs_instance):
        stream = Logs(url_base=url_base)
        inputs = {"stream_state": {"published": "2022-07-19T15:54:11.545Z"}, "stream_slice": None}
        expected_params = {"limit": 200, "since": "2022-07-19T15:54:11.545Z"}
        assert stream.request_params(**inputs) == expected_params

    def test_logs_request_params_for_until(self, patch_base_class, logs_instance):
        stream = Logs(url_base=url_base)
        testing_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        inputs = {"stream_state": {"published": testing_date.isoformat()}, "stream_slice": None}
        expected_params = {"limit": 200, "since": testing_date.isoformat(), "until": testing_date.isoformat()}
        assert stream.request_params(**inputs) == expected_params


class TestStreamUserRoleAssignment:
    def test_user_role_assignments(self, requests_mock, patch_base_class, user_role_assignments_instance):
        stream = UserRoleAssignments(url_base=url_base)
        record = [user_role_assignments_instance]
        user_id = "test_user_id"
        mock_address = f"{api_url}/users/{user_id}/roles?limit=200"
        requests_mock.get(mock_address, json=record)
        inputs = {"sync_mode": SyncMode.full_refresh, "stream_state": {}, "stream_slice": {"user_id": user_id}}
        assert list(stream.read_records(**inputs)) == record

    def test_user_role_assignments_parse_response(self, requests_mock, patch_base_class, user_role_assignments_instance):
        stream = UserRoleAssignments(url_base=url_base)
        record = [user_role_assignments_instance]
        expected_params = [user_role_assignments_instance]
        requests_mock.get(f"{api_url}", json=record)
        r = requests.get(f"{api_url}")
        assert list(stream.parse_response(response=r)) == expected_params

    def test_user_role_assignments_slice_stream(self, requests_mock, patch_base_class, group_members_instance, users_instance):
        stream = UserRoleAssignments(url_base=url_base)
        requests_mock.get(f"{api_url}/users?limit=200", json=[users_instance])
        expected_params = [{"user_id": "test_user_id"}]
        assert list(stream.stream_slices()) == expected_params
