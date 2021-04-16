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
import urllib.parse as urlparse
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from base_python import HttpStream


class IterableStream(HttpStream, ABC):
    url_base = "https://api.iterable.com/api/"

    # Hardcode the value because it is not returned from the API
    BACKOFF_TIME_CONSTANT = 10.0

    @property
    @abstractmethod
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return self.BACKOFF_TIME_CONSTANT

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Iterable API does not support pagination
        """
        return None

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:

        params = self.authenticator.get_auth_params()
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self.data_field, [])


class IterableExportStream(IterableStream, ABC):
    def __init__(self, start_date, **kwargs):
        super(IterableExportStream, self).__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)

    cursor_field = "createdAt"

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            value = pendulum.from_timestamp(value / 1000.0)
        elif isinstance(value, str):
            value = pendulum.parse(value)
        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")
        return value

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = self._field_to_datetime(latest_record[self.cursor_field])
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: str(max(latest_benchmark, self._field_to_datetime(current_stream_state[self.cursor_field])))}
        return {self.cursor_field: str(latest_benchmark)}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:

        params = super(IterableExportStream, self).request_params(stream_state=stream_state)
        start_datetime = self._start_date
        if stream_state.get(self.cursor_field):
            start_datetime = pendulum.parse(stream_state[self.cursor_field])

        params.update(
            {"startDateTime": start_datetime.strftime("%Y-%m-%d %H:%M:%S"), "endDateTime": pendulum.now().strftime("%Y-%m-%d %H:%M:%S")}
        )
        return params

    def path(self, **kwargs) -> str:
        return f"/export/data.json?dataTypeName={self.data_field}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for obj in response.iter_lines():
            yield json.loads(obj)


class Lists(IterableStream):
    data_field = "lists"

    def path(self, **kwargs) -> str:
        return "lists"


class ListUsers(IterableStream):
    data_field = "getUsers"
    name = "list_users"

    def path(self, parent_stream_record, **kwargs) -> str:
        return f"lists/{self.data_field}?listId={parent_stream_record['id']}"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        list_id = self._get_list_id(response.url)
        for user in response.iter_lines():
            yield {"email": user.decode(), "listId": list_id}

    @staticmethod
    def _get_list_id(url: str) -> int:
        parsed_url = urlparse.urlparse(url)
        for q in parsed_url.query.split("&"):
            key, value = q.split("=")
            if key == "listId":
                return int(value)


class Campaigns(IterableStream):
    data_field = "campaigns"

    def path(self, **kwargs) -> str:
        return "campaigns"


class Channels(IterableStream):
    data_field = "channels"

    def path(self, **kwargs) -> str:
        return "channels"


class EmailBounce(IterableExportStream):
    name = "email_bounce"
    data_field = "emailBounce"


class EmailClick(IterableExportStream):
    name = "email_click"
    data_field = "emailClick"


class EmailComplaint(IterableExportStream):
    name = "email_complaint"
    data_field = "emailComplaint"


class EmailOpen(IterableExportStream):
    name = "email_open"
    data_field = "emailOpen"


class EmailSend(IterableExportStream):
    name = "email_send"
    data_field = "emailSend"


class EmailSendSkip(IterableExportStream):
    name = "email_send_skip"
    data_field = "emailSendSkip"


class EmailSubscribe(IterableExportStream):
    name = "email_subscribe"
    data_field = "emailSubscribe"


class EmailUnsubscribe(IterableExportStream):
    name = "email_unsubscribe"
    data_field = "emailUnsubscribe"


class MessageTypes(IterableStream):
    data_field = "messageTypes"
    name = "message_types"

    def path(self, **kwargs) -> str:
        return "messageTypes"


class Metadata(IterableStream):
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "metadata"


class Templates(IterableExportStream):
    data_field = "templates"
    template_types = ["Base", "Blast", "Triggered", "Workflow"]
    message_types = ["Email", "Push", "InApp", "SMS"]

    def path(self, **kwargs) -> str:
        return "templates?templateType={}&messageMedium={}"

    def _list_records(self, stream_state: Mapping[str, Any], parent_stream_record: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        """
        :param parent_stream_record If this is a child stream, this is a record from the parent stream. Otherwise, this record is None.
        :return:
        """

        for templete in self.template_types:
            for message in self.message_types:
                args = {"stream_state": stream_state}

                request = self._create_prepared_request(
                    path=self.path().format(templete, message),
                    headers=dict(self.request_headers(**args), **self.authenticator.get_auth_header()),
                    params=self.request_params(**args),
                    json=self.request_body_json(**args),
                )

                response = self._send_request(request)
                yield from self.parse_response(response, stream_state=stream_state)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self.data_field, [])


class Users(IterableExportStream):
    data_field = "user"
    cursor_field = "profileUpdatedAt"
