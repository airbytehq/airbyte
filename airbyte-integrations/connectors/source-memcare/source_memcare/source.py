#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import math
import datetime
import dateutil.parser
import pytz
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import SyncMode

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.yaml file.
"""


# Basic full refresh stream
class MemcareStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class MemcareStream(HttpStream, ABC)` which is the current class
    `class Customers(MemcareStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(MemcareStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalMemcareStream((MemcareStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://core.prod.memcare.com/api/v2/"

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.funeral_homes = [funeral_home.strip(
        ) for funeral_home in config.get('funeral_homes').split(',')]
        sync_from = datetime.datetime.strptime(
            config.get('sync_from'), "%Y-%m-%d")
        self.sync_from = sync_from.replace(tzinfo=pytz.UTC)
        self.per = 100
        self.page = 1
        self.params = {
            "per": self.per,
            "page": self.page,
            "order": "created_asc"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        total_responses = response.json().get('total_items')
        if total_responses > self.page * self.per:
            self.page += 1
            return {'page': self.page}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = self.params.copy()
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self,
                       response: requests.Response,
                       *,
                       sync_mode: SyncMode,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None,) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        print(response.url)
        yield from [{**data, "funeral_home": stream_slice["funeral_home"]} for data in response.json().get('data', [])]

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for funeral_home in self.funeral_homes:
            self.page = 1
            yield {"funeral_home": funeral_home, "is_incremental": sync_mode == SyncMode.incremental}


class IncrementalMemcareStream(MemcareStream, ABC):
    state_checkpoint_interval = math.inf

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(config)

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        print("current stream state")
        print(current_stream_state)
        new_state = current_stream_state.copy()
        new_state.update({self.cursor_field+latest_record.get("funeral_home")
                         : datetime.datetime.now().replace(tzinfo=pytz.UTC)})
        return new_state

    def parse_response(self,
                       response: requests.Response,
                       *,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None,) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        print(response.url)
        all_data = response.json().get('data', [])
        print("before", len(all_data))
        funeral_home = stream_slice.get("funeral_home")
        if stream_slice.get('is_incremental'):
            print("INCREMENTAL")
            sync_start = stream_state.get(
                self.cursor_field+funeral_home, self.sync_from)
            if isinstance(sync_start, str):
                sync_start = dateutil.parser.isoparse(sync_start)
            print(sync_start)
            print(all_data)
            all_data = [data for data in all_data if dateutil.parser.isoparse(data.get(
                self.cursor_field)) >= sync_start]
            print("after", len(all_data))
        yield from [{**data, "funeral_home": funeral_home} for data in all_data]


class Memory(IncrementalMemcareStream):

    primary_key = "id"
    cursor_field = "created_at"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"public/funeral_homes/{stream_slice['funeral_home']}/memorial_pages.json"


class SourceMemcare(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Memory(config=config)]
