# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from base_python import HttpStream


class ZendeskChatStream(HttpStream, ABC):
    url_base = "https://www.zopim.com/api/v2/"

    data_field = None
    pagination_support = False
    limit = 100

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

    def path(self, **kwargs) -> str:
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.pagination_support:
            stream_data = self.get_stream_data(response.json())
            if len(stream_data) == self.limit:
                last_object_id = stream_data[-1]["id"]
                return {"since_id": last_object_id}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.limit}
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        stream_data = self.get_stream_data(response_data)

        # Getting rid of duplicates
        if self.pagination_support and response.url.find("since_id") > -1:
            stream_data = stream_data[1:]

        yield from stream_data

    def get_stream_data(self, response_data: Any) -> List[dict]:
        if self.data_field:
            response_data = response_data.get(self.data_field, [])

        if isinstance(response_data, list):
            return response_data
        elif isinstance(response_data, dict):
            return [response_data]
        else:
            raise Exception(f"Unsupported type of response data for stream {self.name}")


class Agents(ZendeskChatStream):
    """
    Agents Stream: https://developer.zendesk.com/rest_api/docs/chat/agents#list-agents
    """

    pagination_support = True


class Accounts(ZendeskChatStream):
    """
    Accounts Stream: https://developer.zendesk.com/rest_api/docs/chat/accounts#show-account
    """

    def path(self, **kwargs) -> str:
        return "account"


class Chats(ZendeskChatStream):
    """
    Chats Stream: https://developer.zendesk.com/rest_api/docs/chat/chats#list-chats
    """

    data_field = "chats"


class Shortcuts(ZendeskChatStream):
    """
    Shortcuts Stream: https://developer.zendesk.com/rest_api/docs/chat/shortcuts#list-shortcuts
    """


class Triggers(ZendeskChatStream):
    """
    Triggers Stream: https://developer.zendesk.com/rest_api/docs/chat/triggers#list-triggers
    """


class Bans(ZendeskChatStream):
    """
    Bans Stream: https://developer.zendesk.com/rest_api/docs/chat/bans#list-bans
    """

    pagination_support = True

    def get_stream_data(self, response_data) -> List[dict]:
        bans = response_data["ip_address"] + response_data["visitor"]
        bans = sorted(bans, key=lambda x: pendulum.parse(x["created_at"]))
        return bans


class Departments(ZendeskChatStream):
    """
    Departments Stream: https://developer.zendesk.com/rest_api/docs/chat/departments#list-departments
    """


class Goals(ZendeskChatStream):
    """
    Goals Stream: https://developer.zendesk.com/rest_api/docs/chat/goals#list-goals
    """


class Skills(ZendeskChatStream):
    """
    Skills Stream: https://developer.zendesk.com/rest_api/docs/chat/skills#list-skills
    """


class Roles(ZendeskChatStream):
    """
    Roles Stream: https://developer.zendesk.com/rest_api/docs/chat/roles#list-roles
    """


class RoutingSettings(ZendeskChatStream):
    """
    Routing Settings Stream: https://developer.zendesk.com/rest_api/docs/chat/routing_settings#show-account-routing-settings
    """

    name = "routing_settings"
    data_field = "data"

    def path(self, **kwargs) -> str:
        return "routing_settings/account"
