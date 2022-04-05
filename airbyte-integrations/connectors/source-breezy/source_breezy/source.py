#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from http import cookies
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import datetime
from urllib.error import HTTPError
import pendulum
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Status,
    SyncMode,
)
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


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
    # url_base = "https://api.breezy.hr/"
    app_base = "https://app.breezy.hr"
    current_page = 0
    limit: int
    start_time: str

    def __init__(self, limit=None, page_size=1000, cookie=None, company=None, start_time="2017-01-25T00:00:00Z", **kwargs):
        super().__init__(**kwargs)
        self.limit = limit
        self.page_size = page_size
        self.cookie = cookie
        self.company_id = company
        self.start_time = start_time
        self._start_date = pendulum.parse(start_time)

    @property
    def url_base(self) -> str:
        return f'https://app.breezy.hr/api/company/{self.company_id}/'

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if len(response.json()) or (self.current_page * self.page_size) < self.limit:
            self.current_page += 1
            result = {'limit': self.page_size,
                      'skip': self.current_page * self.page_size}
            return result
        return None

    @property
    def http_method(self):
        return 'POST'

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {'cookie': self.cookie, 'origin': self.app_base}

    # def request_params(
    #     self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    # ) -> MutableMapping[str, Any]:
    #     """
    #     TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
    #     Usually contains common params e.g. pagination size etc.
    #     """
    #     return { 'page': next_page_token.page, 'page_size': 5000, 'sort': 'updated' }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        result = response.json()
        print(result)
        yield result

# Basic incremental stream


class IncrementalBreezyStream(BreezyStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = 1000
    state_pk = "timestamp"

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
        return 'updated_at'

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        if self.state:
            return self.state
        return (
            {self.updated_at_field: int(self._start_date.timestamp() * 1000)}
            if self.state_pk == "timestamp"
            else {self.updated_at_field: str(self._start_date)}
        )

    @property
    def state(self) -> Optional[Mapping[str, Any]]:
        """Current state, if wasn't set return None"""
        if self._state:
            return (
                {self.updated_at_field: int(self._state.timestamp() * 1000)}
                if self.state_pk == "timestamp"
                else {self.updated_at_field: str(self._state)}
            )
        return None

    @state.setter
    def state(self, value):
        state_value = value.get(self.updated_at_field, self._state)
        self._state = (
            pendulum.parse(str(pendulum.from_timestamp(state_value / 1000)))
            if isinstance(state_value, int)
            else pendulum.parse(state_value)
        )
        self._start_date = max(self._state, self._start_date)


class Candidates(IncrementalBreezyStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "_id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/customers then this
        should return "customers". Required.
        """
        return "candidates"

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        common = {"get_totals": True, "sort": {
            "column": "updated_date", "sort": "DESC"}}
        if next_page_token:
            return next_page_token.update(common)
        print(common)
        return {'limit': self.page_size,
                'skip': self.current_page * self.page_size}
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
                limit=1, page_size=1, cookie=config['credentials']["cookie"], company=config['company_id'], start_time=config['start_time'])
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
        auth = config['credentials']["cookie"]
        return [Candidates(cookie=auth, company=config['company_id'], start_time=config['start_time'])]
