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
from datetime import datetime
from typing import DefaultDict, Dict, Generator, Tuple

from airbyte_protocol import AirbyteMessage, AirbyteRecordMessage, AirbyteStateMessage, AirbyteStream, Type
from dateutil import parser
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from .models import HealthCheckError


class Client:
    PAGINATION = 100
    _CAMPAIGNS = "Campaigns"
    _LISTS = "Lists"
    _ENTITIES = [_CAMPAIGNS, _LISTS]

    def __init__(self, username: str, apikey: str):
        self._client = MailChimp(mc_api=apikey, mc_user=username)

    def health_check(self):
        try:
            self._client.ping.get()
            return True, None
        except MailChimpError as err:
            return False, HealthCheckError.parse_obj(err.args[0])

    def get_streams(self):
        streams = []
        for entity in self._ENTITIES:
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], f"schemas/{entity}.json"))
            streams.append(AirbyteStream.parse_obj(raw_schema))
        return streams

    def lists(self, state: DefaultDict[str, any]) -> Generator[AirbyteMessage, None, None]:
        cursor_field = "date_created"
        stream_name = self._LISTS
        date_created = self._get_cursor_or_none(state, stream_name, cursor_field)
        default_params, max_date_created = self._get_default_params_and_cursor(cursor_field, date_created)

        offset = 0
        done = False
        while not done:
            params = dict(default_params, count=self.PAGINATION, offset=offset)
            lists_response = self._client.lists.all(**params)["lists"]
            for mc_list in lists_response:
                list_created_at = parser.isoparse(mc_list[cursor_field])
                max_date_created = max(max_date_created, list_created_at) if max_date_created else list_created_at
                yield self._record(stream=self._LISTS, data=mc_list)

            if max_date_created:
                state[self._LISTS][cursor_field] = self._format_date_as_string(max_date_created)
                yield self._state(state)

            done = len(lists_response) < self.PAGINATION
            offset += self.PAGINATION

    def campaigns(self, state: DefaultDict[str, any]) -> Generator[AirbyteMessage, None, None]:
        cursor_field = "create_time"
        stream_name = self._CAMPAIGNS
        create_time = self._get_cursor_or_none(state, stream_name, cursor_field)
        default_params, max_create_time = self._get_default_params_and_cursor(cursor_field, create_time)

        offset = 0
        done = False
        while not done:
            params = dict(default_params, count=self.PAGINATION, offset=offset)
            campaigns_response = self._client.campaigns.all(**params)
            for campaign in campaigns_response["campaigns"]:
                campaign_created_at = parser.isoparse(campaign[cursor_field])
                max_create_time = max(max_create_time, campaign_created_at) if max_create_time else campaign_created_at
                yield self._record(stream=stream_name, data=campaign)

            if max_create_time:
                state[stream_name][cursor_field] = self._format_date_as_string(max_create_time)
                yield self._state(state)

            done = len(campaigns_response) < self.PAGINATION
            offset += self.PAGINATION

    @staticmethod
    def _get_default_params_and_cursor(cursor_field_name: str, cursor_value: str) -> Tuple[Dict[str, str], datetime]:
        """
        :param cursor_field_name:
        :param cursor_value: assumed to be a date represented as an ISO8601 string
        :return:
        """
        default_params = {"sort_field": cursor_field_name, "sort_dir": "ASC"}
        if cursor_value:
            default_params[f"since_{cursor_field_name}"] = cursor_value
            parsed_date_cursor = parser.isoparse(cursor_value)
        else:
            parsed_date_cursor = None

        return default_params, parsed_date_cursor

    @staticmethod
    def _format_date_as_string(d: datetime) -> str:
        return d.astimezone().replace(microsecond=0).isoformat()

    @staticmethod
    def _get_cursor_or_none(state: DefaultDict[str, any], stream_name: str, cursor_name: str) -> any:
        if state and stream_name in state and cursor_name in state[stream_name]:
            return state[stream_name][cursor_name]
        else:
            return None

    @staticmethod
    def _record(stream: str, data: Dict[str, any]) -> AirbyteMessage:
        now = int(datetime.now().timestamp()) * 1000
        return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=now))

    @staticmethod
    def _state(data: Dict[str, any]):
        return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))
