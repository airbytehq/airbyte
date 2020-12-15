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
import json
import pkgutil

import msal
import requests

from typing import Dict, List, Optional, Tuple
from msal.exceptions import MsalServiceError

from airbyte_protocol import AirbyteStream


class Client:
    MICROSOFT_GRAPH_BASE_API_URL = 'https://graph.microsoft.com/'
    MICROSOFT_GRAPH_API_VERSION = 'v1.0'

    def __init__(self, config: Dict):
        self.ENTITY_MAP = {
            'users': self.get_users,
            'groups': self.get_groups,
            'group_members': self.get_group_members,
            'group_owners': self.get_group_owners,
            'channels': self.get_channels,
            'channel_members': self.get_channel_members,
            'channel_tabs': self.get_channel_tabs,
            'conversations': self.get_conversations,
            'conversation_threads': self.get_conversation_threads,
            'conversation_posts': self.get_conversation_posts,
            'team_drives': self.get_team_drives,
            # 'team_device_usage_report': self.get_team_device_usage_report,
        }
        self.configs = config

    def _get_api_url(self, endpoint: str) -> str:
        api_url = f'{self.MICROSOFT_GRAPH_BASE_API_URL}{self.MICROSOFT_GRAPH_API_VERSION}/{endpoint}/'
        return api_url

    def _get_access_token(self) -> Dict[str, str]:
        scope = ['https://graph.microsoft.com/.default']
        app = msal.ConfidentialClientApplication(self.configs['client_id'],
                                                 authority=f"https://login.microsoftonline.com/"
                                                           f"{self.configs['tenant_id']}",
                                                 client_credential=self.configs['client_secret'])
        result = app.acquire_token_silent(scope, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scope)
        if 'access_token' in result:
            return result['access_token']
        else:
            raise MsalServiceError(error=result.get('error'), error_description=result.get("error_description"))

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> List:
        api_url = self._get_api_url(endpoint)
        access_token = self._get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(api_url, headers=headers, params=params)
        raw_response = response.json()
        value = raw_response['value']
        return value

    def health_check(self) -> Tuple[bool, object]:
        try:
            self._get_access_token()
            return True, None
        except MsalServiceError as err:
            return False, err.args[0]

    def get_streams(self):
        streams = []
        for schema, method in self.ENTITY_MAP.items():
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split('.')[0], f'schemas/{schema}.json'))
            streams.append(AirbyteStream(name=schema, json_schema=raw_schema))
        return streams

    def get_users(self):
        users = self._make_request('users')
        return users

    def get_groups(self):
        groups = filter(lambda item: 'Team' in item['resourceProvisioningOptions'], self._make_request('groups'))
        return groups

    def get_group_members(self):
        members = []
        groups = self.get_groups()
        for group in groups:
            members.extend(self._make_request(f'groups/{group["id"]}/members'))
        return members

    def get_group_owners(self):
        owners = []
        groups = self.get_groups()
        for group in groups:
            owners.extend(self._make_request(f'groups/{group["id"]}/owners'))
        return owners

    def get_channels(self):
        channels = []
        groups = self.get_groups()
        for group in groups:
            channels.extend(self._make_request(f'teams/{group["id"]}/channels'))
        return channels

    def get_channel_members(self):
        members = []
        groups = self.get_groups()
        for group in groups:
            channels = self._make_request(f'teams/{group["id"]}/channels')
            for channel in channels:
                members.extend(self._make_request(f'teams/{group["id"]}/channels/{channel["id"]}/members'))
        return members

    def get_channel_tabs(self):
        tabs = []
        groups = self.get_groups()
        for group in groups:
            channels = self._make_request(f'teams/{group["id"]}/channels')
            for channel in channels:
                tabs.extend(self._make_request(f'teams/{group["id"]}/channels/{channel["id"]}/tabs'))
        return tabs

    def get_conversations(self):
        conversations = []
        groups = self.get_groups()
        for group in groups:
            conversations.extend(self._make_request(f'groups/{group["id"]}/conversations'))
        return conversations

    def get_conversation_threads(self):
        threads = []
        groups = self.get_groups()
        for group in groups:
            conversations = self._make_request(f'groups/{group["id"]}/conversations')
            for conversation in conversations:
                threads.extend(self._make_request(f'groups/{group["id"]}/conversations/{conversation["id"]}/threads'))
        return threads

    def get_conversation_posts(self):
        posts = []
        groups = self.get_groups()
        for group in groups:
            conversations = self._make_request(f'groups/{group["id"]}/conversations')
            for conversation in conversations:
                threads = self._make_request(f'groups/{group["id"]}/conversations/{conversation["id"]}/threads')
                for thread in threads:
                    posts.extend(self._make_request(
                        f'groups/{group["id"]}/conversations/{conversation["id"]}/threads/{thread["id"]}/posts'))
        return posts

    def get_team_drives(self):
        drives = []
        groups = self.get_groups()
        for group in groups:
            drives.extend(self._make_request(f'groups/{group["id"]}/drives'))
        return drives

    def get_team_device_usage_report(self):
        start_date = self.configs['start_date']
        report = self._make_request('reports/getTeamsDeviceUsageUserDetail(period="D7")')
        return report
