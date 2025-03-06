#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from dateutil import parser
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

from httpx import stream
import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

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
class DatadogRumStream(HttpStream, ABC):
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
    `class DatadogRumStream(HttpStream, ABC)` which is the current class
    `class Customers(DatadogRumStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(DatadogRumStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalDatadogRumStream((DatadogRumStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    page_size = 1000 # Datadog's max page size

    @property
    def url_base(self) -> str:
        return "https://api.datadoghq.com"

    def __init__(self, authenticator=None, start_date=None, application_key=None, api_key=None):
        super().__init__(authenticator=authenticator)
        self.start_date = start_date
        self.api_key = api_key
        self.application_key = application_key

    def request_headers(self, stream_state: Mapping[str, Any] | None, stream_slice: Mapping[str, Any] | None = None, next_page_token: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        return {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.application_key
        }
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        TODO: Override this method to define a pagination strategy. If you will not be using pagination, no action is required - just return None.

        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        json_response = response.json()
        next_cursor = json_response.get("meta", {}).get("page", {}).get("after")
        
        if not next_cursor:
            return None
        
        return {
            "page[cursor]": next_cursor,
            "page[limit]": self.page_size
        }

    def request_params(
        self, stream_state: Mapping[str, Any] | None, stream_slice: Mapping[str, Any] | None = None, next_page_token: Mapping[str, Any] | None = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        params = {
            "page[limit]": self.page_size,
            "filter": {
                "from": stream_slice['start_time'] if stream_slice else self.start_date,
                "to": stream_slice['end_time'] if stream_slice else datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        }
        
        if next_page_token:
            params.update(next_page_token)
            
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        json_response = response.json()
        for record in json_response.get("data", []):
            if "attributes" in record and "timestamp" in record["attributes"]:
                record["timestamp"] = parser.parse(record['attributes']['timestamp']).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                record["attributes"] = json.dumps(record["attributes"])
            yield record


# Basic incremental stream
class IncrementalDatadogRumStream(DatadogRumStream, ABC):

    # Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    @property
    def state_checkpoint_interval(self) -> int | None:
        return None

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compares the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        if not isinstance(self.cursor_field, str):
            raise TypeError('Cursor field should be configured as a single timestamp field for Datadog Rum Events')
        current_state = None
        latest_state = None
        try:
            latest_state = latest_record.get(self.cursor_field)
            current_state = current_stream_state.get(self.cursor_field) or latest_state

            if current_state:
                return {self.cursor_field: max(latest_state, current_state)}
            return {}
        except TypeError as e:
            raise TypeError(
                f"Expected {self.cursor_field} type '{type(current_state).__name__}' but returned type '{type(latest_state).__name__}'."
            ) from e


class DatadogRumEvents(IncrementalDatadogRumStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return 'timestamp'

    @property
    def primary_key(self) -> str:
        """
        Required. This is usually a unique field in the stream, like an ID or a timestamp.
        """
        return 'id'

    def path(self, **kwargs) -> str:
        """
        Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "/api/v2/rum/events"

    def stream_slices(self, stream_state: Mapping[str, Any] | None = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        start_date = parser.parse(self.start_date or '2000-01-01')
        end_date = datetime.now()
        
        # Break into 24-hour chunks
        slice_date = start_date
        while slice_date < end_date:
            next_slice = min(slice_date + timedelta(days=1), end_date)
            yield {
                "start_time": slice_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": next_slice.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            slice_date = next_slice


# Source
class SourceDatadogRum(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            auth = TokenAuthenticator(token=config.get('api_key', ''))
            stream = DatadogRumEvents(authenticator=auth, application_key=config.get('DD-APPLICATION-KEY'), api_key=config.get('api_key'), start_date=config.get("start_date"))
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = TokenAuthenticator(token=config.get('api_key', ''))  # Oauth2Authenticator is also available if you need oauth support
        return [DatadogRumEvents(authenticator=auth, application_key=config.get('DD-APPLICATION-KEY'), api_key=config.get('api_key'), start_date=config.get("start_date"))]
