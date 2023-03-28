#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import math
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from urllib.parse import urlparse, parse_qs
from datetime import datetime


# Basic full refresh stream
class ProvetStream(HttpStream, ABC):
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
    `class ProvetStream(HttpStream, ABC)` which is the current class
    `class Customers(ProvetStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(ProvetStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalProvetStream((ProvetStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://provetcloud.com"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=TokenAuthenticator(
            token=config["token"], auth_method="Token"))
        self.provet_id = config["provet_id"]

        self.url_base = f"{ProvetStream.url_base}/{self.provet_id}/api/0.1/"

        self.uri_params = {
            "page": 1,
            "page_size": 500
        }

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
        next_url = response.json().get("next", None)
        if next_url is None:
            return next_url
        parsed_url = urlparse(next_url)
        next_page = parse_qs(parsed_url.query)['page']
        if len(next_page) == 0:
            return None
        return {"page": next_page[0]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = self.uri_params.copy()
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        How a response is parsed.
        :return an iterable containing each record in the response
        """
        print(f"Request url: {response.url}")
        yield from response.json().get("results", [])

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return float(response.headers.get("Retry-After", 60))

# Basic incremental stream


class IncrementalProvetStream(ProvetStream, ABC):

    # Don't checkpoint state, wait until entire sync is finished
    state_checkpoint_interval = math.inf

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(config)

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return "modified"

    @property
    def cursor_field_filter(self) -> str:
        """
        :return str: filter method for the cursor field.
        """
        return f"{self.cursor_field}__gte"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        old_state_date = current_stream_state.get(self.cursor_field, None)
        latest_record_date = latest_record.get(self.cursor_field)
        if old_state_date is not None:
            return {self.cursor_field: max(datetime.fromisoformat(latest_record_date) if not isinstance(latest_record_date, datetime) else latest_record_date, datetime.fromisoformat(old_state_date) if not isinstance(old_state_date, datetime) else old_state_date)}
        return {self.cursor_field: latest_record_date}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        if stream_state and self.cursor_field in stream_state:
            params.update(
                {self.cursor_field_filter: stream_state.get(self.cursor_field)})
        return params


class Patients(IncrementalProvetStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "patient"


class Clients(IncrementalProvetStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "client"


class Consultations(IncrementalProvetStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "consultation"


class Invoices(IncrementalProvetStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "invoice"


class InvoiceRows(IncrementalProvetStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "invoicerow"


class InvoicePayments(IncrementalProvetStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "invoicepayment"

# Source


class SourceProvet(AbstractSource):
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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [Patients(config), Clients(config), Consultations(config), Invoices(config), InvoiceRows(config), InvoicePayments(config)]
