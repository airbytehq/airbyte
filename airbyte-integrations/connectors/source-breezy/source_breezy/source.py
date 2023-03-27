#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.error import HTTPError

import pendulum
import requests
from airbyte_cdk.entrypoint import logger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class BreezyStream(HttpStream, ABC):
    """
    TODO remove this comment

    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class BreezyStream(HttpStream, ABC)` which is the current class
    `class Customers(BreezyStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(BreezyStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalBreezyStream((BreezyStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    page_size: int
    cookie: str
    company_id: str

    # TODO: Fill in the url base. Required.
    app_base = "https://app.breezy.hr"
    _current_rows = 0
    _internal_cursor = None
    total_rows_read = 0
    limit: int
    start_time: str
    data_field = "data"

    def __init__(self, limit=None, page_size=5000, cookie=None, company=None, start_time="2017-01-25T00:00:00Z", **kwargs):
        super().__init__(**kwargs)
        self.limit = limit
        self.page_size = page_size
        self.cookie = cookie
        self.company_id = company
        self.start_time = start_time
        self._start_date = pendulum.parse(start_time)

    @property
    def url_base(self) -> str:
        return f"https://app.breezy.hr/api/company/{self.company_id}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response = response.json()
        max_elements = response["total"]
        rows_read = len(response[self.data_field])
        self.total_rows_read += rows_read
        self._current_rows += rows_read
        if max_elements == 10001:
            max_val = max(response[self.data_field], default=None, key=lambda obj: obj["updated_date"])
            min_val = min(response[self.data_field], default=None, key=lambda obj: obj["updated_date"])
            max_date = max_val["updated_date"]
            min_date = min_val["updated_date"]
            self.logger.info(f"Need further pagination : Max record: {max_date} / Min record : {min_date}")
            self._current_rows = 0
            self._internal_cursor = int(self._field_to_datetime(min_date).timestamp() * 1000)
            return {
                "limit": self.page_size,
                "skip": self._current_rows,
                "updated_date": {"end": self._internal_cursor},
            }
        elif self._current_rows < max_elements or (self.limit and self.total_rows_read < self.limit):
            result = {"limit": self.page_size, "skip": self._current_rows}
            if self._internal_cursor:
                result.update({"updated_date": {"end": self._internal_cursor}})
            return result
        return None

    @property
    def http_method(self):
        return "POST"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"cookie": self.cookie, "origin": self.app_base}

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            value = pendulum.from_timestamp(value / 1000.0)
        elif isinstance(value, str):
            value = pendulum.parse(value)
        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")
        return value

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        response = response.json()
        if isinstance(response, Mapping):
            if response.get("status", None) == "error":
                self.logger.warning(f"Stream `{self.name}` cannot be procced. {response.get('message')}")
                return

            if response.get(self.data_field) is None:
                """
                When the response doen't have the stream's data, raise an exception.
                """
                raise RuntimeError("Unexpected API response: {} not in {}".format(self.data_field, response.keys()))
            yield from response[self.data_field]
        else:
            response = list(response)
            yield from response


# Basic incremental stream


class IncrementalBreezyStream(BreezyStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = 1000
    state_pk = "timestamp"
    need_chunk = True
    _start_date: Union[pendulum.Date, pendulum.Time, pendulum.DateTime, pendulum.Duration]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "updated_date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        if self.state:
            return self.state
        return (
            {self.cursor_field: int(self._start_date.timestamp() * 1000)}
            if self.state_pk == "timestamp"
            else {self.cursor_field: str(self._start_date)}
        )

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        if self._state:
            return (
                {self.cursor_field: int(self._state.timestamp() * 1000)}
                if self.state_pk == "timestamp"
                else {self.cursor_field: str(self._state)}
            )
        return None

    @state.setter
    def state(self, value: Mapping[str, Any]):
        state_value = value.get(self.cursor_field, self._state)

        self._state = (
            pendulum.parse(str(pendulum.from_timestamp(state_value / 1000)))
            if isinstance(state_value, int)
            else pendulum.parse(state_value)
        )
        self._start_date = max(self._state, self._start_date)

    def _update_state(self, latest_cursor):
        self._current_rows = 0
        self._internal_cursor = None
        if latest_cursor:
            new_state = max(latest_cursor, self._state) if self._state else latest_cursor
            if new_state != self._state:
                logger.info(f"Advancing bookmark for {self.name} stream from {self._state} to {latest_cursor}")
                self._state = new_state
                self._start_date = self._state

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        records = super().read_records(*args, **kwargs)
        latest_cursor = None
        for record in records:
            cursor = self._field_to_datetime(record[self.cursor_field])
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            yield record
        self._update_state(latest_cursor=latest_cursor)

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        chunk_size = pendulum.duration(days=30)
        slices = []

        now_ts = int(pendulum.now().timestamp() * 1000)
        start_ts = int(self._start_date.timestamp() * 1000)
        max_delta = now_ts - start_ts
        chunk_size = int(chunk_size.total_seconds() * 1000) if self.need_chunk else max_delta
        for ts in range(start_ts, now_ts, chunk_size):
            end_ts = ts + chunk_size
            slices.append({"updated_date": {"start": ts, "end": end_ts}})
        return slices


class Candidates(IncrementalBreezyStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "_id"
    max_retries = 8

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "candidates"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        common = {"get_totals": True, "all_positions": True, "sort": {"column": "updated_date", "sort": "DESC"}}
        if stream_slice:
            common.update(stream_slice)
        if next_page_token:
            if next_page_token.get("updated_date"):
                next_page_token["updated_date"] = {**stream_slice["updated_date"], **next_page_token["updated_date"]}
            common.update(next_page_token)
        else:
            common.update({"limit": self.page_size, "skip": 0})
        return common


# Source


class SourceBreezy(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        alive = True
        error_msg = None
        try:
            candidates = Candidates(
                limit=1, page_size=1, cookie=config["credentials"]["cookie"], company=config["company_id"], start_time=config["start_time"]
            )
            _ = next(candidates.read_records(sync_mode=SyncMode.full_refresh))
        except HTTPError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        # Oauth2Authenticator is also available if you need oauth support
        auth = config["credentials"]["cookie"]
        return [Candidates(authenticator=None, cookie=auth, company=config["company_id"], start_time=config["start_time"])]
