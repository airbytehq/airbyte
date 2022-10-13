#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream


class Stream(HttpStream, ABC):
    url_base = "https://www.zopim.com/api/v2/"
    primary_key = "id"

    data_field = None

    limit = 100

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:

        return {"timeout": 60}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

    def path(self, **kwargs) -> str:
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()

        if "next_url" in response_data:
            next_url = response_data["next_url"]
            cursor = parse_qs(urlparse(next_url).query)["cursor"]
            return {"cursor": cursor}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        stream_data = self.get_stream_data(response_data)

        yield from stream_data

    def get_stream_data(self, response_data: Any) -> List[dict]:
        if self.data_field:
            response_data = response_data.get(self.data_field, [])

        if isinstance(response_data, list):
            return list(map(self.parse_response_obj, response_data))
        elif isinstance(response_data, dict):
            return [self.parse_response_obj(response_data)]
        else:
            raise Exception(f"Unsupported type of response data for stream {self.name}")

    def parse_response_obj(self, response_obj: dict) -> dict:
        return response_obj


class BaseIncrementalStream(Stream, ABC):
    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    @abstractmethod
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            value = pendulum.from_timestamp(value / 1000.0)
        elif isinstance(value, str):
            value = pendulum.parse(value)
        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")
        return value


class TimeIncrementalStream(BaseIncrementalStream, ABC):

    state_checkpoint_interval = 1000

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if response_data["count"] == self.limit:
            return {"start_time": response_data["end_time"]}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = self._field_to_datetime(latest_record[self.cursor_field])
        if current_stream_state.get(self.cursor_field):
            state = max(latest_benchmark, self._field_to_datetime(current_stream_state[self.cursor_field]))
            return {self.cursor_field: state.strftime("%Y-%m-%dT%H:%M:%SZ")}
        return {self.cursor_field: latest_benchmark.strftime("%Y-%m-%dT%H:%M:%SZ")}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token)
        if next_page_token:
            params.update(next_page_token)
        else:
            start_datetime = self._start_date
            if stream_state.get(self.cursor_field):
                start_datetime = pendulum.parse(stream_state[self.cursor_field])

            params.update({"start_time": int(start_datetime.timestamp())})

        params.update({"fields": f"{self.name}(*)"})
        return params

    def path(self, **kwargs) -> str:
        return f"incremental/{self.name}"

    def parse_response_obj(self, response_obj: dict) -> dict:
        response_obj[self.cursor_field] = pendulum.parse(response_obj[self.cursor_field]).strftime("%Y-%m-%dT%H:%M:%SZ")
        return response_obj


class IdIncrementalStream(BaseIncrementalStream):
    cursor_field = "id"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = self.get_stream_data(response.json())
        if len(stream_data) == self.limit:
            last_object_id = stream_data[-1]["id"]
            return {"since_id": last_object_id}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token)

        if next_page_token:
            params.update(next_page_token)
        elif stream_state.get(self.cursor_field):
            params.update({"since_id": stream_state[self.cursor_field]})

        return params


class Agents(IdIncrementalStream):
    """
    Agents Stream: https://developer.zendesk.com/rest_api/docs/chat/agents#list-agents
    """


class AgentTimelines(TimeIncrementalStream):
    """
    Agent Timelines Stream: https://developer.zendesk.com/rest_api/docs/chat/incremental_export#incremental-agent-timeline-export
    """

    primary_key = None
    cursor_field = "start_time"
    data_field = "agent_timeline"
    name = "agent_timeline"
    limit = 1000

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        if not kwargs.get("next_page_token"):
            params["start_time"] = params["start_time"] * 1000000
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        stream_data = self.get_stream_data(response_data)

        def generate_key(record):
            record.update({"id": "|".join((str(record.get("agent_id", "")), str(record.get("start_time", ""))))})
            return record

        # associate the surrogate key
        yield from map(
            generate_key,
            stream_data,
        )


class Accounts(Stream):
    """
    Accounts Stream: https://developer.zendesk.com/rest_api/docs/chat/accounts#show-account
    """

    primary_key = "account_key"

    def path(self, **kwargs) -> str:
        return "account"


class Chats(TimeIncrementalStream):
    """
    Chats Stream: https://developer.zendesk.com/api-reference/live-chat/chat-api/incremental_export/#incremental-chat-export
    """

    cursor_field = "update_timestamp"
    data_field = "chats"
    limit = 1000


class Shortcuts(Stream):
    """
    Shortcuts Stream: https://developer.zendesk.com/rest_api/docs/chat/shortcuts#list-shortcuts
    """


class Triggers(Stream):
    """
    Triggers Stream: https://developer.zendesk.com/rest_api/docs/chat/triggers#list-triggers
    """


class Bans(IdIncrementalStream):
    """
    Bans Stream: https://developer.zendesk.com/rest_api/docs/chat/bans#list-bans
    """

    def get_stream_data(self, response_data) -> List[dict]:
        bans = response_data["ip_address"] + response_data["visitor"]
        bans = sorted(bans, key=lambda x: pendulum.parse(x["created_at"]) if x["created_at"] else pendulum.datetime(1970, 1, 1))
        return bans


class Departments(Stream):
    """
    Departments Stream: https://developer.zendesk.com/rest_api/docs/chat/departments#list-departments
    """


class Goals(Stream):
    """
    Goals Stream: https://developer.zendesk.com/rest_api/docs/chat/goals#list-goals
    """


class Skills(Stream):
    """
    Skills Stream: https://developer.zendesk.com/rest_api/docs/chat/skills#list-skills
    """


class Roles(Stream):
    """
    Roles Stream: https://developer.zendesk.com/rest_api/docs/chat/roles#list-roles
    """


class RoutingSettings(Stream):
    """
    Routing Settings Stream: https://developer.zendesk.com/rest_api/docs/chat/routing_settings#show-account-routing-settings
    """

    primary_key = ""

    name = "routing_settings"
    data_field = "data"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "routing_settings/account"
