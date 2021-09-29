#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import csv
import json
import urllib.parse as urlparse
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

EVENT_ROWS_LIMIT = 200
CAMPAIGNS_PER_REQUEST = 20


class IterableStream(HttpStream, ABC):

    # Hardcode the value because it is not returned from the API
    BACKOFF_TIME_CONSTANT = 10.0
    # define date-time fields with potential wrong format

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
            yield record


class IterableExportStream(IterableStream, ABC):

    cursor_field = "createdAt"
    primary_key = None

    def __init__(self, start_date, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)
        self.stream_params = {"dataTypeName": self.data_field}

    def path(self, **kwargs) -> str:
        return "/export/data.json"

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
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {
                self.cursor_field: max(
                    latest_benchmark, self._field_to_datetime(current_stream_state[self.cursor_field])
                ).to_datetime_string()
            }
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
            record = json.loads(obj)
            record[self.cursor_field] = self._field_to_datetime(record[self.cursor_field])
            yield record


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
        """
        https://api.iterable.com/api/docs#campaigns_metrics
        """
        super().__init__(api_key)
        self.start_date = start_date

    def path(self, **kwargs) -> str:
        return "campaigns/metrics"

    def request_params(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["campaignId"] = stream_slice.get("campaign_ids")
        params["startDateTime"] = self.start_date

        return params

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        lists = Campaigns(api_key=self._api_key)
        campaign_ids = []
        for list_record in lists.read_records(sync_mode=kwargs.get("sync_mode", SyncMode.full_refresh)):
            campaign_ids.append(list_record["id"])

            if len(campaign_ids) == CAMPAIGNS_PER_REQUEST:
                yield {"campaign_ids": campaign_ids}
                campaign_ids = []

        if campaign_ids:
            yield {"campaign_ids": campaign_ids}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        content = response.content.decode()
        records = self._parse_csv_string_to_dict(content)

        for record in records:
            yield {"data": record}

    @staticmethod
    def _parse_csv_string_to_dict(csv_string: str) -> List[Dict[str, Any]]:
        """
        Parse a response with a csv type to dict object
        Example:
            csv_string = "a,b,c,d
                          1,2,,3
                          6,,1,2"

            output = [{"a": 1, "b": 2, "d": 3},
                      {"a": 6, "c": 1, "d": 2}]


        :param csv_string: API endpoint response with csv format
        :return: parsed API response

        """

        reader = csv.DictReader(StringIO(csv_string), delimiter=",")
        result = []

        for row in reader:
            for key, value in row.items():
                if value == "":
                    continue
                try:
                    row[key] = int(value)
                except ValueError:
                    row[key] = float(value)
            row = {k: v for k, v in row.items() if v != ""}

            result.append(row)

        return result


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
    """
    https://api.iterable.com/api/docs#events_User_events
    """
    primary_key = None
    data_field = "events"
    page_size = EVENT_ROWS_LIMIT

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return f"events/{stream_slice['email']}"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["limit"] = self.page_size

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
            yield record


class Users(IterableExportStream):
    data_field = "user"
    cursor_field = "profileUpdatedAt"
