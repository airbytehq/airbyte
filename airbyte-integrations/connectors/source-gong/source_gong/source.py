#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from asyncio.log import logger
from glob import glob
from sqlite3 import Timestamp
from pendulum import DateTime, Period
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from abc import ABC, abstractmethod
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import pendulum
from airbyte_cdk.models import SyncMode
import time
import datetime
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
class GongStream(HttpStream, ABC):
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
    `class GongStream(HttpStream, ABC)` which is the current class
    `class Customers(GongStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(GongStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalGongStream((GongStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://api.gong.io/v2/"
    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Slack uses a cursor-based pagination strategy.
        Extract the cursor from the response if it exists and return it in a format
        that can be used to update request parameters"""

        json_response = response.json()
        next_cursor = json_response.get("response_metadata", {}).get("next_cursor")
        if next_cursor:
            return {"cursor": next_cursor}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[MutableMapping]:
        json_response = response.json()
        print(json_response)
        if "errors" in json_response:
            if json_response["errors"][0] == "No calls found corresponding to the provided filters":
                json_response={}
            else : raise Exception(json_response["error"])
        yield from json_response.get(self.data_field, [])
    @property
    @abstractmethod
    def data_field(self) -> str:
        """The name of the field in the response which contains the data"""
# Incremental Streams
def chunk_date_range(start_date: DateTime, interval=pendulum.duration(days=1)) -> Iterable[Period]:
    """
    Yields a list of the beginning and ending timestamps of each day between the start date and now.
    The return value is a pendulum.period
    """

    now = pendulum.now()
    # Each stream_slice contains the beginning and ending timestamp for a 24 hour period
    while start_date <= now:
        end_date = start_date + interval
        yield pendulum.period(start_date, end_date)
        start_date = end_date

    
# Basic incremental stream
class IncrementalGongStream(GongStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """
    def __init__(self, default_start_date: DateTime, **kwargs):
        self._start_ts = default_start_date.timestamp()
        super().__init__(**kwargs)
    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return "_airbyte_emitted_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any] =None) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        logger = AirbyteLogger()
        if latest_record is not None and self.cursor_field in latest_record: 
            current_stream_state[self.cursor_field] = latest_record[self.cursor_field]

        else :
            current_stream_state[self.cursor_field] = int(time.time())

        return current_stream_state


    # def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
    #     """
    #     TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

    #     Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
    #     This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
    #     section of the docs for more information.

    #     The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
    #     necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
    #     This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

    #     An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
    #     craft that specific request.

    #     For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
    #     this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
    #     till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
    #     the date query param.
    #     """
    #     raise NotImplementedError("Implement stream slices or delete this method!")


class Calls(IncrementalGongStream):
    http_method = "POST"
    data_field = "calls"
    primary_key = "id"
    cursor_field ="_airbyte_emitted_at"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if self.cursor_field not in  stream_state:

            date = self._start_ts
            print("******First sync detected *******")
            print("Start date is: ")
            print(date)
            date = datetime.datetime.fromtimestamp(date)
            return "calls/?fromDateTime={}".format((date).strftime("%Y-%m-%dT%H:%M:%SZ"))
        else:
            print("Start date is: ")
            print(stream_state)
            date = datetime.datetime.fromtimestamp(stream_state[self.cursor_field])
            return "calls/?fromDateTime={}".format((date).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "calls/extensive"

    def request_body_json(self, stream_slice: Mapping = None, **kwargs) -> Optional[Mapping]:
        stream_state =kwargs["stream_state"]
        if self.cursor_field not in  stream_state:
            date = self._start_ts
            print("Start date is: ")
            print(date)
            return {
             "contentSelector": {
            "context": "Extended",
            "exposedFields": {
            "collaboration": {
                "publicComments": False
            },
            "content": {
                "pointsOfInterest": False,
                "structure": False,
                "topics": False,
                "trackers": False
            },
            "interaction": {
                "personInteractionStats": True,
                "questions": True,
                "speakers": True,
                "video": False
                },
                "media": False,
                "parties":True,
                }
            },
            "filter": {
                "fromDateTime": date
                   
            }
}
        else:
            print("Start date is: ")
            print(stream_state)
            date = datetime.datetime.fromtimestamp(stream_state[self.cursor_field])
            return {
                     "contentSelector": {
                    "context": "Extended",
                    "exposedFields": {
                    "collaboration": {
                        "publicComments": False
                    },
                    "content": {
                        "pointsOfInterest": False,
                        "structure": False,
                        "topics": False,
                        "trackers": False
                    },
                    "interaction": {
                        "personInteractionStats": True,
                        "questions": True,
                        "speakers": True,
                        "video": False
                    },
                    "media": False,
                    "parties":True,
                    }
                },
                "filter": {
       "fromDateTime": (date).strftime("%Y-%m-%dT%H:%M:%SZ")

                }
                }

        
class Users(GongStream):
    http_method = "GET"
    data_field = "users"
    primary_key = "id"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "users"

class CallTranscripts(IncrementalGongStream):
    http_method = "POST"
    data_field = "callTranscripts"
    primary_key = "callId"
    cursor_field ="_airbyte_emitted_at"
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "calls/transcript"
    def request_body_json(self, stream_slice: Mapping = None, **kwargs) -> Optional[Mapping]:
        stream_state =kwargs["stream_state"]
        if self.cursor_field not in  stream_state:
            date = self._start_ts
            print("Start date is: ")
            print(date)
            return {"filter": {
            

                }}
        else:
            print("Start date is: ")
            print(stream_state)
            date = datetime.datetime.fromtimestamp(stream_state[self.cursor_field])
            return {"filter": {
               
                }}


   


# Source
class SourceGong(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None
    def _get_authenticator(self, config: Mapping[str, Any]):
        # Added to maintain backward compatibility with previous versions
        credentials = config.get("credentials")
        return TokenAuthenticator(token= credentials["access_token"])
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        authenticator = self._get_authenticator(config)
          # Oauth2Authenticator is also available if you need oauth support
        global default_start_date
        default_start_date = pendulum.parse(config["start_date"])
        return [Calls(authenticator=authenticator,default_start_date=default_start_date),CallTranscripts(authenticator=authenticator,default_start_date=default_start_date),Users(authenticator=authenticator)]
