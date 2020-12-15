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
        self._group_ids = None

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
        yield users

    def get_groups(self):
        groups = filter(lambda item: 'Team' in item['resourceProvisioningOptions'], self._make_request('groups'))
        yield groups

    def _get_group_ids(self):
        if not self._group_ids:
            params = {
                '$select': 'id,resourceProvisioningOptions'
            }
            self._group_ids = [item["id"] for item in self._make_request('groups', params=params) if
                               'Team' in item['resourceProvisioningOptions']]
        return self._group_ids

    def get_group_members(self):
        for group_id in self._get_group_ids():
            members = self._make_request(f'groups/{group_id}/members')
            yield members

    def get_group_owners(self):
        for group_id in self._get_group_ids():
            owners = self._make_request(f'groups/{group_id}/owners')
            yield owners

    def get_channels(self):
        for group_id in self._get_group_ids():
            channels = self._make_request(f'teams/{group_id}/channels')
            yield channels

    def get_channel_members(self):
        for group_id in self._get_group_ids():
            channels = self._make_request(f'teams/{group_id}/channels')
            for channel in channels:
                members = self._make_request(f'teams/{group_id}/channels/{channel["id"]}/members')
                yield members

    def get_channel_tabs(self):
        for group_id in self._get_group_ids():
            channels = self._make_request(f'teams/{group_id}/channels')
            for channel in channels:
                tabs = self._make_request(f'teams/{group_id}/channels/{channel["id"]}/tabs')
                yield tabs

    def get_conversations(self):
        for group_id in self._get_group_ids():
            conversations = self._make_request(f'groups/{group_id}/conversations')
            yield conversations

    def get_conversation_threads(self):
        for group_id in self._get_group_ids():
            conversations = self._make_request(f'groups/{group_id}/conversations')
            for conversation in conversations:
                threads = self._make_request(f'groups/{group_id}/conversations/{conversation["id"]}/threads')
                yield threads

    def get_conversation_posts(self):
        for group_id in self._get_group_ids():
            conversations = self._make_request(f'groups/{group_id}/conversations')
            for conversation in conversations:
                threads = self._make_request(f'groups/{group_id}/conversations/{conversation["id"]}/threads')
                for thread in threads:
                    posts = self._make_request(
                        f'groups/{group_id}/conversations/{conversation["id"]}/threads/{thread["id"]}/posts')
                    yield posts

    def get_team_drives(self):
        for group_id in self._get_group_ids():
            drives = self._make_request(f'groups/{group_id}/drives')
            yield drives

    def get_team_device_usage_report(self):
        # start_date = self.configs['start_date']
        report = self._make_request('reports/getTeamsDeviceUsageUserDetail(period="D7")')
        return report
