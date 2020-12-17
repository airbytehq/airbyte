"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import csv
import io
import json
import pkgutil
import time
from typing import Dict, List, Optional, Tuple, Union

import msal
import requests
from airbyte_protocol import AirbyteStream
from msal.exceptions import MsalServiceError


class Client:
    """
        Microsoft Teams API Reference: https://docs.microsoft.com/en-us/graph/api/resources/teams-api-overview?view=graph-rest-1.0
    """
    MICROSOFT_GRAPH_BASE_API_URL: str = "https://graph.microsoft.com/"
    MICROSOFT_GRAPH_API_VERSION: str = "v1.0"
    PAGINATION_COUNT: Optional[int] = 20

    def __init__(self, config: json):
        self.ENTITY_MAP = {
            "users": self.get_users,
            "groups": self.get_groups,
            "group_members": self.get_group_members,
            "group_owners": self.get_group_owners,
            "channels": self.get_channels,
            "channel_members": self.get_channel_members,
            "channel_tabs": self.get_channel_tabs,
            "conversations": self.get_conversations,
            "conversation_threads": self.get_conversation_threads,
            "conversation_posts": self.get_conversation_posts,
            "team_drives": self.get_team_drives,
            "team_device_usage_report": self.get_team_device_usage_report,
        }
        self.configs = config
        self._group_ids = None
        self.msal_app = msal.ConfidentialClientApplication(
            self.configs["client_id"],
            authority=f"https://login.microsoftonline.com/" f"{self.configs['tenant_id']}",
            client_credential=self.configs["client_secret"],
        )

    def _get_api_url(self, endpoint: str) -> str:
        api_url = f"{self.MICROSOFT_GRAPH_BASE_API_URL}{self.MICROSOFT_GRAPH_API_VERSION}/{endpoint}/"
        return api_url

    def _get_access_token(self) -> str:
        scope = ["https://graph.microsoft.com/.default"]
        # First, the code looks up a token from the cache.
        result = self.msal_app.acquire_token_silent(scope, account=None)
        # If no suitable token exists in cache. Let's get a new one from AAD.
        if not result:
            result = self.msal_app.acquire_token_for_client(scopes=scope)
        if "access_token" in result:
            return result["access_token"]
        else:
            raise MsalServiceError(error=result.get("error"), error_description=result.get("error_description"))

    def _make_request(self, api_url: str, params: Optional[Dict] = None) -> Union[Dict, object]:
        access_token = self._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 429:
            if 'Retry-After' in response.headers:
                pause_time = float(response.headers['Retry-After'])
                time.sleep(pause_time)
                response = requests.get(api_url, headers=headers, params=params)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(response.text)
        if response.headers["Content-Type"] == "application/octet-stream":
            raw_response = response.content
        else:
            raw_response = response.json()
        return raw_response

    @staticmethod
    def _get_response_value_unsafe(raw_response: Dict) -> List:
        if "value" not in raw_response:
            raise requests.exceptions.RequestException()
        value = raw_response["value"]
        return value

    def _get_request_params(self, params: Optional[Dict] = None, pagination: bool = True) -> Dict:
        if self.PAGINATION_COUNT and pagination:
            params = params if params else {}
            if "$top" not in params:
                params["$top"] = self.PAGINATION_COUNT
        return params

    def _fetch_data(self, endpoint: str, params: Optional[Dict] = None, pagination: bool = True):
        api_url = self._get_api_url(endpoint)
        params = self._get_request_params(params, pagination)
        while True:
            raw_response = self._make_request(api_url, params)
            value = self._get_response_value_unsafe(raw_response)
            yield value
            if "@odata.nextLink" not in raw_response:
                break
            params = None
            api_url = raw_response["@odata.nextLink"]

    def health_check(self) -> Tuple[bool, object]:
        try:
            self._get_access_token()
            return True, None
        except MsalServiceError as err:
            return False, err.args[0]

    def get_streams(self):
        streams = []
        for schema, method in self.ENTITY_MAP.items():
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], f"schemas/{schema}.json"))
            streams.append(AirbyteStream(name=schema, json_schema=raw_schema))
        return streams

    def get_users(self):
        for users in self._fetch_data("users"):
            yield users

    def get_groups(self):
        for groups in self._fetch_data("groups"):
            yield filter(lambda item: "Team" in item["resourceProvisioningOptions"], groups)

    def _get_group_ids(self):
        if not self._group_ids:
            api_url = self._get_api_url("groups")
            params = {"$select": "id,resourceProvisioningOptions"}
            groups = self._get_response_value_unsafe(self._make_request(api_url, params=params))
            self._group_ids = [item["id"] for item in groups if "Team" in item["resourceProvisioningOptions"]]
        return self._group_ids

    def get_group_members(self):
        for group_id in self._get_group_ids():
            for members in self._fetch_data(f"groups/{group_id}/members"):
                yield members

    def get_group_owners(self):
        for group_id in self._get_group_ids():
            for owners in self._fetch_data(f"groups/{group_id}/owners"):
                yield owners

    def get_channels(self):
        for group_id in self._get_group_ids():
            for channels in self._fetch_data(f"teams/{group_id}/channels", pagination=False):
                yield channels

    def _get_channel_ids(self, group_id: str):
        api_url = self._get_api_url(f"teams/{group_id}/channels")
        params = {"$select": "id"}
        channels_ids = self._get_response_value_unsafe(self._make_request(api_url, params=params))
        return channels_ids

    def get_channel_members(self):
        for group_id in self._get_group_ids():
            channels = self._get_channel_ids(group_id=group_id)
            for channel in channels:
                for members in self._fetch_data(f'teams/{group_id}/channels/{channel["id"]}/members'):
                    yield members

    def get_channel_tabs(self):
        for group_id in self._get_group_ids():
            channels = self._get_channel_ids(group_id=group_id)
            for channel in channels:
                for tabs in self._fetch_data(f'teams/{group_id}/channels/{channel["id"]}/tabs', pagination=False):
                    yield tabs

    def get_conversations(self):
        for group_id in self._get_group_ids():
            for conversations in self._fetch_data(f"groups/{group_id}/conversations"):
                yield conversations

    def _get_conversation_ids(self, group_id: str):
        api_url = self._get_api_url(f"groups/{group_id}/conversations")
        params = {"$select": "id"}
        conversation_ids = self._get_response_value_unsafe(self._make_request(api_url, params=params))
        return conversation_ids

    def get_conversation_threads(self):
        for group_id in self._get_group_ids():
            conversations = self._get_conversation_ids(group_id=group_id)
            for conversation in conversations:
                for threads in self._fetch_data(f'groups/{group_id}/conversations/{conversation["id"]}/threads'):
                    yield threads

    def _get_thread_ids(self, group_id: str, conversation_id: str):
        api_url = self._get_api_url(f"groups/{group_id}/conversations/{conversation_id}/threads")
        params = {"$select": "id"}
        thread_ids = self._get_response_value_unsafe(self._make_request(api_url, params=params))
        return thread_ids

    def get_conversation_posts(self):
        for group_id in self._get_group_ids():
            conversations = self._get_conversation_ids(group_id=group_id)
            for conversation in conversations:
                threads = self._get_thread_ids(group_id, conversation["id"])
                for thread in threads:
                    for posts in self._fetch_data(f'groups/{group_id}/conversations/{conversation["id"]}/threads/{thread["id"]}/posts'):
                        yield posts

    def get_team_drives(self):
        for group_id in self._get_group_ids():
            for drives in self._fetch_data(f"groups/{group_id}/drives"):
                yield drives

    def get_team_device_usage_report(self):
        period = self.configs["period"]
        api_url = self._get_api_url(f"reports/getTeamsDeviceUsageUserDetail(period='{period}')")
        csv_response = io.BytesIO(self._make_request(api_url))
        csv_response.readline()
        with io.TextIOWrapper(csv_response, encoding="utf-8-sig") as text_file:
            field_names = [
                "report_refresh_date",
                "user_principal_name",
                "last_activity_date",
                "is_deleted",
                "deleted_date",
                "used_web",
                "used_windows_phone",
                "used_i_os",
                "used_mac",
                "used_android_phone",
                "used_windows",
                "report_period",
            ]
            reader = csv.DictReader(text_file, fieldnames=field_names)
            for row in reader:
                yield [
                    row,
                ]
