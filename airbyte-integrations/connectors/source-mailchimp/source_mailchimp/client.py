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
    _EMAIL_ACTIVITY = "Email_activity"
    _ENTITIES = [_CAMPAIGNS, _LISTS, _EMAIL_ACTIVITY]

    def __init__(self, username: str, apikey: str):
        self._client = MailChimp(mc_api=apikey, mc_user=username)
        self.reset_campaign_ids()

    def reset_campaign_ids(self):
        self.campaign_ids = []

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

        generator = self.query_paginated(
            state=state,
            stream_name=stream_name,
            params=dict(default_params, count=self.PAGINATION, offset=0),
            query_subject=self._client.lists,
            response_data_field="lists",
            cursor_field=cursor_field,
            max_cursor_field_value=max_date_created,
        )
        return generator

    def campaigns(self, state: DefaultDict[str, any]) -> Generator[AirbyteMessage, None, None]:

        self.reset_campaign_ids()
        cursor_field = "create_time"
        stream_name = self._CAMPAIGNS
        create_time = self._get_cursor_or_none(state, stream_name, cursor_field)
        default_params, max_create_time = self._get_default_params_and_cursor(cursor_field, create_time)

        generator = self.query_paginated(
            state=state,
            stream_name=stream_name,
            params=dict(default_params, count=self.PAGINATION, offset=0),
            query_subject=self._client.campaigns,
            response_data_field="campaigns",
            cursor_field=cursor_field,
            max_cursor_field_value=max_create_time,
            store_responce_field={"where": self.campaign_ids, "field": "id"},
        )
        return generator

    def email_activity(self, state: DefaultDict[str, any]) -> Generator[AirbyteMessage, None, None]:
        if not self.campaign_ids:
            _ = self.campaigns(state=state)
        stream_name = self._EMAIL_ACTIVITY
        for campaign_id in self.campaign_ids:
            # possible TODO - use batch
            params = {"campaign_id": campaign_id, "count": self.PAGINATION, "offset": 0}
            generator = self.query_paginated(
                state=state,
                stream_name=stream_name,
                params=params,
                query_subject=self._client.reports.email_activity,
                response_data_field="emails",
                cursor_field=None,
                max_cursor_field_value=None,
            )

            yield from generator

    def query_paginated(
        self,
        state: DefaultDict[str, any],
        stream_name: str,
        params: dict,
        query_subject,
        response_data_field: str,
        cursor_field: str = None,
        max_cursor_field_value: str = None,
        store_responce_field: Dict[str, str] = None,
    ) -> Generator[AirbyteMessage, None, None]:

        done = False
        while not done:
            api_response = query_subject.all(**params)
            api_data = api_response[response_data_field]
            for entry in api_data:
                if store_responce_field:
                    value = entry[store_responce_field["field"]]
                    store_responce_field["where"].append(value)
                if cursor_field:
                    created_at = parser.isoparse(entry[cursor_field])
                    max_cursor_field_value = max(max_cursor_field_value, created_at) if max_cursor_field_value else created_at
                yield self._record(stream=stream_name, data=entry)

            if max_cursor_field_value:
                state[stream_name][cursor_field] = self._format_date_as_string(max_cursor_field_value)
                yield self._state(state)

            done = len(api_data) < self.PAGINATION
            params["offset"] += self.PAGINATION

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
