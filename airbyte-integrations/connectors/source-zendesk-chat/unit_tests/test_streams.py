#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_zendesk_chat.source import ZendeskAuthentication
from source_zendesk_chat.streams import (
    Accounts,
    Agents,
    AgentTimelines,
    Bans,
    Chats,
    Departments,
    Goals,
    Roles,
    RoutingSettings,
    Shortcuts,
    Skills,
    Triggers,
)

TEST_CONFIG: dict = {
    "start_date": "2020-10-01T00:00:00Z",
    "access_token": "access_token",
}
TEST_CONFIG.update(**{"authenticator": ZendeskAuthentication(TEST_CONFIG).get_auth()})


class TestFullRefreshStreams:
    """
    STREAMS: 
        Accounts, Shortcuts, Triggers, Departments, Goals, Skills, Roles, RoutingSettings
    """

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Accounts),
            (Departments),
            (Goals),
            (Roles),
            (RoutingSettings),
            (Shortcuts),
            (Skills),
            (Triggers),
        ],
    )
    def test_request_kwargs(self, stream_cls):
        stream = stream_cls(TEST_CONFIG)
        expected = {"timeout": 60}
        assert expected == stream.request_kwargs(stream_state=None)
    
    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, "5"),
            (Departments, "5"),
            (Goals, "5"),
            (Roles, "3"),
            (RoutingSettings, "3"),
            (Shortcuts, "3"),
            (Skills, "1"),
            (Triggers, "1"),
        ],
    )
    def test_backoff_time(self, requests_mock, stream_cls, expected):
        stream = stream_cls(TEST_CONFIG)
        url =f"{stream.url_base}{stream.path()}"
        test_headers = {"Retry-After": expected}
        requests_mock.get(url, headers=test_headers)
        response = requests.get(url)
        result = stream.backoff_time(response)
        assert result == int(expected)

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, "account"),
            (Departments, "departments"),
            (Goals, "goals"),
            (Roles, "roles"),
            (RoutingSettings, "routing_settings/account"),
            (Shortcuts, "shortcuts"),
            (Skills, "skills"),
            (Triggers, "triggers"),
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.path()
        assert result == expected
    
    @pytest.mark.parametrize(
        "stream_cls, expected_cursor",
        [
            (Accounts, "MTU4MD"),
            (Departments, "c1Mzc"),
            (Goals, "wfHw0MzJ8"),
            (Roles, "0MzJ8"),
            (RoutingSettings, "MTUC4wJ8"),
            (Shortcuts, "MTU4MD"),
            (Skills, "c1Mzc"),
            (Triggers, "0MzJ8"),
        ],
    )
    def test_next_page_token(self, requests_mock, stream_cls, expected_cursor):
        stream = stream_cls(TEST_CONFIG)
        url = f"{stream.url_base}{stream.path()}"
        next_url = f"{url}/cursor.json?cursor={expected_cursor}"
        test_response = {"next_url": next_url}
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.next_page_token(response)
        assert result == {"cursor": [expected_cursor]}
        
    @pytest.mark.parametrize(
        "stream_cls, next_page_token, expected",
        [
            (Accounts, {"cursor": "MTU4MD"}, {'limit': 100, 'cursor': 'MTU4MD'}),
            (Departments, {"cursor": "c1Mzc"}, {'limit': 100, 'cursor': 'c1Mzc'}),
            (Goals, {"cursor": "wfHw0MzJ8"}, {'limit': 100, 'cursor': 'wfHw0MzJ8'}),
            (Roles, {"cursor": "0MzJ8"}, {'limit': 100, 'cursor': '0MzJ8'}),
            (RoutingSettings, {"cursor": "MTUC4wJ8"}, {'limit': 100, 'cursor': 'MTUC4wJ8'}),
            (Shortcuts, {"cursor": "MTU4MD"}, {'limit': 100, 'cursor': 'MTU4MD'}),
            (Skills, {"cursor": "c1Mzc"}, {'limit': 100, 'cursor': 'c1Mzc'}),
            (Triggers, {"cursor": "0MzJ8"}, {'limit': 100, 'cursor': '0MzJ8'}),
        ],
    )
    def test_request_params(self, stream_cls, next_page_token, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.request_params(stream_state=None, next_page_token=next_page_token)
        assert result == expected
    
    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (Accounts, [{"id": "123"}], [{"id": "123"}]),
            (Departments, {"id": "123"}, [{"id": "123"}]),
            (Goals, {}, [{}]),
            (Roles, [{"id": "123"}], [{"id": "123"}]),
            (RoutingSettings, {"data": {"id": "123"}}, [{"id": "123"}]),
            (Shortcuts, [{"id": "123"}], [{"id": "123"}]),
            (Skills, [{"id": "123"}], [{"id": "123"}]),
            (Triggers, [{"id": "123"}], [{"id": "123"}]),
        ],
    )
    def test_parse_response(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(TEST_CONFIG)
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.parse_response(response)
        assert list(result) == expected
    

class TestTimeIncrementalStreams:
    """
    STREAMS: 
        AgentTimelines, Chats
    """

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (AgentTimelines, 1000),
            (Chats, 1000),
        ],
    )
    def test_state_checkpoint_interval(self, stream_cls, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        result = stream.state_checkpoint_interval
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (AgentTimelines, "start_time"),
            (Chats, "update_timestamp"),
        ],
    )
    def test_cursor_field(self, stream_cls, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        result = stream.cursor_field
        assert result == expected
    
    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (AgentTimelines, {"end_time": "123"}, {'start_time': '123'}),
            (Chats, {"end_time": "123"}, {'start_time': '123'}),
        ],
    )    
    def test_next_page_token(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        test_response.update(**{"count": stream.limit})
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.next_page_token(response)
        assert result == expected
    
    @pytest.mark.parametrize(
        "stream_cls, current_state, last_record, expected",
        [
            (AgentTimelines, {}, {'start_time': '2021-01-01'}, {'start_time': '2021-01-01T00:00:00Z'}),
            (Chats, {"update_timestamp": "2022-02-02"}, {'update_timestamp': '2022-03-03'}, {'update_timestamp': '2022-03-03T00:00:00Z'}),
        ],
    )      
    def test_get_updated_state(self, stream_cls, current_state, last_record, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        result = stream.get_updated_state(current_state, last_record)
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, stream_state, next_page_token, expected",
        [
            (AgentTimelines, {}, {'start_time': '123'}, {'limit': 1000, 'start_time': '123', 'fields': 'agent_timeline(*)'}),
            (Chats, {"update_timestamp": "2022-02-02"}, {'start_time': '234'}, {'limit': 1000, 'start_time': '234', 'fields': 'chats(*)'}),
        ],
    )
    def test_request_params(self, stream_cls, stream_state, next_page_token, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        result = stream.request_params(stream_state=stream_state, next_page_token=next_page_token)
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (
                AgentTimelines,
                {"agent_timeline" : {"id": "123", "agent_id": "test_id", "start_time": "2021-01-01"}},
                [{'id': 'test_id|2021-01-01T00:00:00Z', 'agent_id': 'test_id', 'start_time': '2021-01-01T00:00:00Z'}],
            ),
            (
                Chats,
                {"chats" : {"id": "234", "agent_id": "test_id", "update_timestamp": "2022-01-01"}},
                [{'id': '234', 'agent_id': 'test_id', 'update_timestamp': '2022-01-01T00:00:00Z'}],
            ),
        ],
    )    
    def test_parse_response(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.parse_response(response)
        assert list(result) == expected
        

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (AgentTimelines, "incremental/agent_timeline"),
            (Chats, "incremental/chats"),
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(start_date=TEST_CONFIG["start_date"])
        result = stream.path()
        assert result == expected
        

class TestIdIncrementalStreams:
    """
    STREAMS: 
        Agents, Bans
    """

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Agents, "agents"),
            (Bans, "bans"),
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.path()
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Agents, "id"),
            (Bans, "id"),
        ],
    )
    def test_cursor_field(self, stream_cls, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.cursor_field
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, current_state, last_record, expected",
        [
            (Agents, {}, {'id': '1'}, {'id': '1'}),
            (Bans, {"id": "1"}, {'id': '2'}, {'id': '2'}),
        ],
    )    
    def test_get_updated_state(self, stream_cls, current_state, last_record, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.get_updated_state(current_state, last_record)
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (Agents, [{"id": "2"}], {'since_id': '2'}),
        ],
    )    
    def test_next_page_token(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(TEST_CONFIG)
        stream.limit = 1
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.next_page_token(response)
        assert result == expected
        
    @pytest.mark.parametrize(
        "stream_cls, test_response, expected",
        [
            (Agents, {"id": "2"}, [{"id": "2"}]),
        ],
    )    
    def test_parse_response(self, requests_mock, stream_cls, test_response, expected):
        stream = stream_cls(TEST_CONFIG)
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json=test_response)
        response = requests.get(url)
        result = stream.parse_response(response)
        assert list(result) == expected
        
    @pytest.mark.parametrize(
        "stream_cls, stream_state, next_page_token, expected",
        [
            (Agents, {}, {'since_id': '1'}, {'limit': 100, 'since_id': '1'}),
            (Bans, {"id": "1"}, {'since_id': '2'}, {'limit': 100, 'since_id': '2'}),
        ],
    )
    def test_request_params(self, stream_cls, stream_state, next_page_token, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.request_params(stream_state=stream_state, next_page_token=next_page_token)
        assert result == expected

