#
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
#

import json
import urllib.parse as urlparse
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

EVENT_ROWS_LIMIT = 200


class IterableStream(HttpStream, ABC):

    # Hardcode the value because it is not returned from the API
    BACKOFF_TIME_CONSTANT = 10.0
    # define date-time fields with potential wrong format
    DATE_TIME_FIELDS = {
        "createdAt",
        "updatedAt",
        "startAt",
        "endedAt",
        "profileUpdatedAt",
    }

    url_base = "https://api.iterable.com/api/"
    primary_key = "id"

    def __init__(self, api_key, **kwargs):
        super().__init__(**kwargs)
        self._api_key = api_key

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

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"api_key": self._api_key}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.data_field, [])

        for record in records:
            yield self._convert_timestamp_fields_to_datetime(record)

    @staticmethod
    def _parse_plain_text_to_dict(text: str) -> Dict[str, Any]:
        """
        :param text: API endpoint response with plain/text format
        :return: parsed API response
        """

        result = dict()
        data = text.split("\n")

        names = data[0].split(",")
        raw_values = data[1].split(",")

        for key, value in zip(names, raw_values):
            try:
                result[key] = int(value)
            except ValueError:
                result[key] = float(value)

        return result

    def _convert_timestamp_fields_to_datetime(self, record: Dict[str, Any]):
        for field in self.DATE_TIME_FIELDS:
            # check for optional timestamp fields and convert to date-time
            if record.get(field):
                record[field] = self._field_to_datetime(record[field])

        return record

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            # divide by 1000.0, because timestamp present in milliseconds
            value = pendulum.from_timestamp(value / 1000.0)

        elif isinstance(value, str):
            value = pendulum.parse(value)

        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")

        return value


class IterableExportStream(IterableStream, ABC):

    cursor_field = "createdAt"
    primary_key = None

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)
        self.stream_params = {"dataTypeName": self.data_field}

    def path(self, **kwargs) -> str:
        return "/export/data.json"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, pendulum.parse(current_stream_state[self.cursor_field])).to_datetime_string()}
        return {self.cursor_field: latest_benchmark.to_datetime_string()}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state=stream_state)
        start_datetime = self._start_date
        if stream_state.get(self.cursor_field):
            start_datetime = pendulum.parse(stream_state[self.cursor_field])

        params.update(
            {"startDateTime": start_datetime.strftime("%Y-%m-%d %H:%M:%S"), "endDateTime": pendulum.now().strftime("%Y-%m-%d %H:%M:%S")},
            **self.stream_params,
        )
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for obj in response.iter_lines():
            yield self._convert_timestamp_fields_to_datetime(json.loads(obj))


class Lists(IterableStream):
    data_field = "lists"

    def path(self, **kwargs) -> str:
        return "lists"


class ListUsers(IterableStream):
    primary_key = "listId"
    data_field = "getUsers"
    name = "list_users"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"lists/{self.data_field}?listId={stream_slice['list_id']}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = Lists(api_key=self._api_key)
        for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh)):
            yield {"list_id": list_record["id"]}

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


class CampaignsMetrics(IterableStream):
    primary_key = None
    data_field = None

    def __init__(self, api_key: str, start_date: str):
        super().__init__(api_key)
        self.start_date = start_date

    def path(self, **kwargs) -> str:
        return "campaigns/metrics"

    def request_params(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["campaignId"] = stream_slice.get("campaign_id")
        params["startDateTime"] = self.start_date

        return params

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = Campaigns(api_key=self._api_key)
        for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh)):
            yield {"campaign_id": list_record["id"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        plain_text = response.content.decode()
        yield {"data": self._parse_plain_text_to_dict(plain_text)}


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


class Events(IterableStream):
    primary_key = None
    data_field = "events"

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"events/{stream_slice['email']}"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["limit"] = EVENT_ROWS_LIMIT

        return params

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = ListUsers(api_key=self._api_key)
        stream_slices = lists.stream_slices()

        for stream_slice in stream_slices:
            for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh), stream_slice=stream_slice):
                yield {"email": list_record["email"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            yield {"data": record}


class MessageTypes(IterableStream):
    data_field = "messageTypes"
    name = "message_types"

    def path(self, **kwargs) -> str:
        return "messageTypes"


class Metadata(IterableStream):
    primary_key = None
    data_field = "results"

    def path(self, **kwargs) -> str:
        return "metadata"


class Templates(IterableExportStream):
    data_field = "templates"
    template_types = ["Base", "Blast", "Triggered", "Workflow"]
    message_types = ["Email", "Push", "InApp", "SMS"]

    def path(self, **kwargs) -> str:
        return "templates"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for template in self.template_types:
            for message in self.message_types:
                self.stream_params = {"templateType": template, "messageMedium": message}
                yield from super().read_records(stream_slice=stream_slice, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.data_field, [])

        for record in records:
            yield self._convert_timestamp_fields_to_datetime(record)


class Users(IterableExportStream):
    data_field = "user"
    cursor_field = "profileUpdatedAt"
