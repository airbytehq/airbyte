#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import time
from abc import ABC
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
    Permissions,
    UserRoleAssignments,
    Users,
)


@pytest.fixture
def patch_base_class(mocker):
    """
    Base patcher for used streams
    """
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
    def test_should_retry(self, patch_base_class, http_status, should_retry, url_base, start_date):
        response_mock = MagicMock()
        response_mock.status_code = http_status
        stream = OktaStream(url_base=url_base, start_date=start_date)
        assert stream.should_retry(response_mock) == should_retry


class TestOktaStream:
    def test_okta_stream_request_params(self, patch_base_class, url_base, start_date):
        stream = OktaStream(url_base=url_base, start_date=start_date)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"limit": 200}
        assert stream.request_params(**inputs) == expected_params

    def test_okta_stream_parse_response(self, patch_base_class, requests_mock, url_base, api_url, start_date):
        stream = OktaStream(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[{"a": 123}, {"b": "xx"}])
        resp = requests.get(f"{api_url}")
        inputs = {"response": resp, "stream_state": MagicMock()}
        expected_parsed_object = [{"a": 123}, {"b": "xx"}]
        assert list(stream.parse_response(**inputs)) == expected_parsed_object

    def test_okta_stream_backoff_time(self, patch_base_class, url_base, start_date):
        response_mock = requests.Response()
        stream = OktaStream(url_base=url_base, start_date=start_date)
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_okta_stream_incremental_request_params(self, patch_base_class, url_base, start_date):
        stream = IncrementalOktaStream(url_base=url_base, start_date=start_date)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"filter": 'None gt "2021-03-21T20:49:13.000Z"', "limit": 200}
        assert stream.request_params(**inputs) == expected_params

    def test_incremental_okta_stream_parse_response(self, patch_base_class, requests_mock, url_base, api_url, start_date):
        stream = IncrementalOktaStream(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[{"a": 123}, {"b": "xx"}])
        resp = requests.get(f"{api_url}")
        inputs = {"response": resp, "stream_state": MagicMock()}
        expected_parsed_object = [{"a": 123}, {"b": "xx"}]
        assert list(stream.parse_response(**inputs)) == expected_parsed_object

    def test_incremental_okta_stream_backoff_time(self, patch_base_class, url_base, start_date):
        response_mock = MagicMock()
        stream = IncrementalOktaStream(url_base=url_base, start_date=start_date)
        expected_backoff_time = None
        assert stream.backoff_time(response_mock) == expected_backoff_time

    def test_okta_stream_incremental_backoff_time_empty(self, patch_base_class, url_base, start_date):
        stream = IncrementalOktaStream(url_base=url_base, start_date=start_date)
        response = MagicMock(requests.Response)
        response.status_code = 200
        expected_params = None
        inputs = {"response": response}
        assert stream.backoff_time(**inputs) == expected_params

    def test_okta_stream_incremental_back_off_now(self, patch_base_class, url_base, start_date):
        stream = IncrementalOktaStream(url_base=url_base, start_date=start_date)
        response = MagicMock(requests.Response)
        response.status_code = requests.codes.TOO_MANY_REQUESTS
        response.headers = {"x-rate-limit-reset": int(time.time())}
        expected_params = (0, 2)
        inputs = {"response": response}
        get_backoff_time = stream.backoff_time(**inputs)
        assert expected_params[0] <= get_backoff_time <= expected_params[1]

    def test_okta_stream_incremental_get_updated_state(self, patch_base_class, latest_record_instance, url_base, start_date):
        class TestIncrementalOktaStream(IncrementalOktaStream, ABC):
            def __init__(self, url_base: str, *args, **kwargs):
                super().__init__(url_base, *args, **kwargs)
                self._cursor_field = None

            @property
            def cursor_field(self) -> str:
                return self._cursor_field

        stream = TestIncrementalOktaStream(url_base=url_base, start_date=start_date)
        stream._cursor_field = "lastUpdated"

        current_stream_state = {"lastUpdated": "2021-04-21T21:03:55.000Z"}
        update_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record_instance)
        expected_result = {"lastUpdated": "2022-07-18T07:58:11.000Z"}
        assert update_state == expected_result

    def test_okta_stream_http_method(self, patch_base_class, url_base, start_date):
        stream = OktaStream(url_base=url_base, start_date=start_date)
        expected_method = "GET"
        assert stream.http_method == expected_method


class TestNextPageToken:
    def test_next_page_token(self, patch_base_class, users_instance, url_base, api_url, start_date):
        stream = OktaStream(url_base=url_base, start_date=start_date)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}?param1=test_value1&param2=test_value2"}}
        inputs = {"response": response}
        expected_token = {"param1": "test_value1", "param2": "test_value2"}
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_empty_params(self, patch_base_class, users_instance, url_base, api_url, start_date):
        stream = OktaStream(url_base=url_base, start_date=start_date)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}}
        inputs = {"response": response}
        expected_token = {}
        result = stream.next_page_token(**inputs)
        assert result == expected_token

    def test_next_page_token_link_have_self_and_equal_next(self, patch_base_class, users_instance, url_base, api_url, start_date):
        stream = OktaStream(url_base=url_base, start_date=start_date)
        response = MagicMock(requests.Response)
        response.links = {"next": {"url": f"{api_url}"}, "self": {"url": f"{api_url}"}}
        inputs = {"response": response}
        expected_token = None
        result = stream.next_page_token(**inputs)
        assert result == expected_token


class TestStreamUsers:
    def test_stream_users(self, requests_mock, patch_base_class, users_instance, url_base, api_url, start_date):
        stream = Users(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/users", json=[users_instance])
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == [users_instance]

    def test_users_request_params_out_of_next_page_token(self, patch_base_class, url_base, user_status_filter, start_date):
        stream = Users(url_base=url_base, start_date=start_date)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
        expected_params = {"limit": 200, "filter": f'lastUpdated gt "2021-03-21T20:49:13.000Z" and ({user_status_filter})'}
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_request_params_have_next_cursor(self, patch_base_class, url_base, user_status_filter, start_date):
        stream = Users(url_base=url_base, start_date=start_date)
        inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"next_cursor": "123"}}
        expected_params = {
            "limit": 200,
            "next_cursor": "123",
            "filter": f'lastUpdated gt "2021-03-21T20:49:13.000Z" and ({user_status_filter})',
        }
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_request_params_have_latest_entry(self, patch_base_class, url_base, user_status_filter, start_date):
        stream = Users(url_base=url_base, start_date=start_date)
        inputs = {"stream_slice": None, "stream_state": {"lastUpdated": "some_date"}, "next_page_token": {"next_cursor": "123"}}
        expected_params = {"limit": 200, "next_cursor": "123", "filter": f'lastUpdated gt "some_date" and ({user_status_filter})'}
        assert stream.request_params(**inputs) == expected_params

    def test_users_source_parse_response(self, requests_mock, patch_base_class, users_instance, url_base, api_url, start_date):
        stream = Users(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[users_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [users_instance]


class TestStreamCustomRoles:
    def test_custom_roles(self, requests_mock, patch_base_class, custom_role_instance, url_base, api_url, start_date):
        stream = CustomRoles(url_base=url_base, start_date=start_date)
        record = {"roles": [custom_role_instance]}
        requests_mock.get(f"{api_url}/iam/roles?limit=200", json=record)
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == record["roles"]

    def test_custom_roles_parse_response(self, requests_mock, patch_base_class, custom_role_instance, url_base, api_url, start_date):
        stream = CustomRoles(url_base=url_base, start_date=start_date)
        record = {"roles": [custom_role_instance]}
        requests_mock.get(f"{api_url}", json=record)
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [custom_role_instance]


class TestStreamPermissions:
    def test_permissions(self, requests_mock, patch_base_class, permission_instance, url_base, api_url, start_date):
        stream = Permissions(url_base=url_base, start_date=start_date)
        record = {"permissions": [permission_instance]}
        role_id = "test_role_id"
        requests_mock.get(f"{api_url}/iam/roles/{role_id}/permissions", json=record)
        inputs = {"sync_mode": SyncMode.full_refresh, "stream_state": {}, "stream_slice": {"role_id": role_id}}
        assert list(stream.read_records(**inputs)) == record["permissions"]

    def test_permissions_parse_response(self, requests_mock, patch_base_class, permission_instance, url_base, api_url, start_date):
        stream = Permissions(url_base=url_base, start_date=start_date)
        record = {"permissions": [permission_instance]}
        requests_mock.get(f"{api_url}", json=record)
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [permission_instance]


class TestStreamGroups:
    def test_groups(self, requests_mock, patch_base_class, groups_instance, url_base, api_url, start_date):
        stream = Groups(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/groups?limit=200", json=[groups_instance])
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == [groups_instance]

    def test_groups_parse_response(self, requests_mock, patch_base_class, groups_instance, url_base, api_url, start_date):
        stream = Groups(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[groups_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [groups_instance]


class TestStreamGroupMembers:
    def test_group_members(self, requests_mock, patch_base_class, group_members_instance, url_base, api_url, start_date):
        stream = GroupMembers(url_base=url_base, start_date=start_date)
        group_id = "test_group_id"
        requests_mock.get(f"{api_url}/groups/{group_id}/users?limit=200", json=[group_members_instance])
        inputs = {"sync_mode": SyncMode.incremental, "stream_state": {}, "stream_slice": {"group_id": group_id}}
        assert list(stream.read_records(**inputs)) == [group_members_instance]

    def test_group_members_parse_response(self, requests_mock, patch_base_class, group_members_instance, url_base, api_url, start_date):
        stream = GroupMembers(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[group_members_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [group_members_instance]

    def test_group_members_request_params_with_latest_entry(self, patch_base_class, group_members_instance, url_base, start_date):
        stream = GroupMembers(url_base=url_base, start_date=start_date)
        inputs = {
            "stream_slice": {"group_id": "some_group"},
            "stream_state": {"id": "some_test_id"},
            "next_page_token": {"next_cursor": "123"},
        }
        assert stream.request_params(**inputs) == {
            "limit": 200,
            "next_cursor": "123",
            "after": "some_test_id",
        }

    def test_group_members_slice_stream(
        self, requests_mock, patch_base_class, group_members_instance, groups_instance, url_base, api_url, start_date
    ):
        stream = GroupMembers(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/groups?limit=200", json=[groups_instance])
        assert list(stream.stream_slices()) == [{"group_id": "test_group_id"}]

    def test_group_member_request_get_update_state(self, latest_record_instance, url_base, start_date):
        stream = GroupMembers(url_base=url_base, start_date=start_date)
        stream._cursor_field = "id"
        current_stream_state = {"id": "test_user_group_id"}
        update_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record_instance)
        assert update_state == {"id": "test_user_group_id"}


class TestStreamGroupRoleAssignment:
    def test_group_role_assignments(self, requests_mock, patch_base_class, group_role_assignments_instance, url_base, api_url, start_date):
        stream = GroupRoleAssignments(url_base=url_base, start_date=start_date)
        group_id = "test_group_id"
        mock_address = f"{api_url}/groups/{group_id}/roles?limit=200"
        requests_mock.get(mock_address, json=[group_role_assignments_instance])
        inputs = {"sync_mode": SyncMode.full_refresh, "stream_state": {}, "stream_slice": {"group_id": group_id}}
        assert list(stream.read_records(**inputs)) == [group_role_assignments_instance]

    def test_group_role_assignments_parse_response(
        self, requests_mock, patch_base_class, group_role_assignments_instance, url_base, api_url, start_date
    ):
        stream = GroupRoleAssignments(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[group_role_assignments_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [group_role_assignments_instance]

    def test_group_role_assignments_slice_stream(
        self, requests_mock, patch_base_class, group_members_instance, groups_instance, url_base, api_url, start_date
    ):
        stream = GroupRoleAssignments(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/groups?limit=200", json=[groups_instance])
        assert list(stream.stream_slices()) == [{"group_id": "test_group_id"}]


class TestStreamLogs:
    def test_logs(self, requests_mock, patch_base_class, logs_instance, url_base, api_url, start_date):
        stream = Logs(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/logs?limit=200", json=[logs_instance])
        inputs = {"sync_mode": SyncMode.incremental}
        assert list(stream.read_records(**inputs)) == [logs_instance]

    def test_logs_parse_response(self, requests_mock, patch_base_class, logs_instance, url_base, api_url, start_date):
        stream = Logs(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/logs?limit=200", json=[logs_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}/logs?limit=200"))) == [logs_instance]

    def test_logs_request_params_for_since(self, patch_base_class, logs_instance, url_base, start_date):
        stream = Logs(url_base=url_base, start_date=start_date)
        inputs = {"stream_state": {"published": "2022-07-19T15:54:11.545Z"}, "stream_slice": None}
        assert stream.request_params(**inputs) == {
            "limit": 200,
            "since": "2022-07-19T15:54:11.545Z",
        }

    def test_logs_request_params_for_until(self, patch_base_class, logs_instance, url_base, start_date):
        stream = Logs(url_base=url_base, start_date=start_date)
        testing_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        inputs = {"stream_state": {"published": testing_date.isoformat()}, "stream_slice": None}
        assert stream.request_params(**inputs) == {"limit": 200, "since": testing_date.isoformat()}


class TestStreamUserRoleAssignment:
    def test_user_role_assignments(self, requests_mock, patch_base_class, user_role_assignments_instance, url_base, api_url, start_date):
        stream = UserRoleAssignments(url_base=url_base, start_date=start_date)
        user_id = "test_user_id"
        mock_address = f"{api_url}/users/{user_id}/roles?limit=200"
        requests_mock.get(mock_address, json=[user_role_assignments_instance])
        inputs = {"sync_mode": SyncMode.full_refresh, "stream_state": {}, "stream_slice": {"user_id": user_id}}
        assert list(stream.read_records(**inputs)) == [user_role_assignments_instance]

    def test_user_role_assignments_parse_response(
        self, requests_mock, patch_base_class, user_role_assignments_instance, url_base, api_url, start_date
    ):
        stream = UserRoleAssignments(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}", json=[user_role_assignments_instance])
        assert list(stream.parse_response(response=requests.get(f"{api_url}"))) == [user_role_assignments_instance]

    def test_user_role_assignments_slice_stream(
        self, requests_mock, patch_base_class, group_members_instance, users_instance, url_base, api_url, start_date
    ):
        stream = UserRoleAssignments(url_base=url_base, start_date=start_date)
        requests_mock.get(f"{api_url}/users?limit=200", json=[users_instance])
        assert list(stream.stream_slices()) == [{"user_id": "test_user_id"}]
