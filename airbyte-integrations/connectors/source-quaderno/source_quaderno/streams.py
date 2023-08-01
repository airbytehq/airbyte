#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from pendulum.date import Date

DEFAULT_PRIMARY_KEY = "id"
DEFAULT_CURSOR = "issue_date"
DEFAULT_LIMIT = 100


class QuadernoStream(HttpStream):
    """
    This class represents a stream output by the connector.

    Each stream should extend this class to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/invoices
        - GET v1/credits

    then you should have three classes:
    `class QuadernoStream(HttpStream)` which is the current class
    `class Invoices(QuadernoStream)` contains behavior to pull data for invoices using invoices
    `class Credits(QuadernoStream)` contains behavior to pull data for employees using credits

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalQuadernoStream(QuadernoStream)`. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    path = None

    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        self._url_base = f"https://{config['account_name']}.quadernoapp.com/api/"
        self._start_date = pendulum.parse(config.get("start_date")).date()

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        The Quaderno resource primary key. Most of the Quaderno resources have `id` as a primary ID.

        :return: The Quaderno resource primary key(s)
        :rtype: Either `str`, list(str) or list(list(str))
        """
        return DEFAULT_PRIMARY_KEY

    @property
    def limit(self) -> int:
        """
        Returns the number of records limit
        """
        return DEFAULT_LIMIT

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """ Return a mapping (e.g: dict) containing information needed to query the next page in the response.
        :param response: the most recent response from the API
        :return If there is another page in the result, a dict containing information needed to query the next page.
                If there are no more pages in the result, return None.
        """
        if response.headers["x-pages-hasmore"] == "true":
            parsed_url = urlparse(response.headers["x-pages-nextpage"])
            return dict(parse_qsl(parsed_url.query))

        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """Define any query parameters to be set."""
        params = {"limit": self.limit}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        yield from response_json


class BasePaginationQuadernoStream(QuadernoStream):
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if 'date' in stream_slice:
            params['date'] = stream_slice['date']
        return params

    def chunk_dates(self, start_date: Date) -> Iterable[Tuple[Date, Date]]:
        today = pendulum.today().date()
        step = pendulum.duration(days=1)
        after_date = start_date
        while after_date < today:
            before_date = min(today, after_date + step)
            yield after_date, before_date
            after_date = before_date + step

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for start, end in self.chunk_dates(self._start_date):
            yield {"date": f"{start.isoformat(), end.isoformat()}"}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            return []

        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)


class IncrementalQuadernoStream(BasePaginationQuadernoStream):

    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Returns the cursor field to be used in the `incremental` sync mode.

        By default enable the `incremental` sync mode for all resources.

        :return: The cursor field(s) to be used in the `incremental` sync mode.
        :rtype: Union[str, List[str]]
        """
        return DEFAULT_CURSOR

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """
        Determine the latest state after reading the latest record by comparing the cursor_field from the latest record
        and the current state and picks the 'most' recent cursor. This is how a stream's state is determined.
        Required for incremental.
        """
        current_issue_date = pendulum.parse(
            (current_stream_state or {}).get(self.cursor_field, pendulum.from_timestamp(0).isoformat())
        )
        latest_record_issue_date = pendulum.parse(latest_record[self.cursor_field])

        return {self.cursor_field: max(current_issue_date, latest_record_issue_date).to_date_string()}

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = self.get_start_date(stream_state)
        if start_date >= pendulum.today().date():
            # if the state is in the future - this will produce a state message but not make an API request
            yield None
        else:
            for start, end in self.chunk_dates(start_date):
                yield {"date": f"{start.isoformat(), end.isoformat()}"}

    def get_start_date(self, stream_state) -> Date:
        start_point = self._start_date
        if stream_state and self.cursor_field in stream_state:
            start_point = max(start_point, pendulum.parse(stream_state[self.cursor_field]).date())
        return start_point


class Credits(IncrementalQuadernoStream):

    def path(self, **kwargs) -> str:
        return "credits"


class Contacts(IncrementalQuadernoStream):

    def path(self, **kwargs) -> str:
        return "contacts"


class Invoices(IncrementalQuadernoStream):

    def path(self, **kwargs) -> str:
        return "invoices"
