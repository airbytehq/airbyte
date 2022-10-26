#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .auth import AccessTokenAuthenticator
from .utils import read_full_refresh


# Basic full refresh stream
class RailzStream(HttpStream, ABC):
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
    `class RailzStream(HttpStream, ABC)` which is the current class
    `class Customers(RailzStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(RailzStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalRailzStream((RailzStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://api.railz.ai/"

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
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        for record in response_json["data"]:
            yield record


class Businesses(RailzStream):
    """
    https://api.railz.ai/businesses
    """

    primary_key = "businessName"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "businesses"


# Basic incremental stream
class IncrementalRailzStream(RailzStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class AccountingTransactions(IncrementalRailzStream):
    """
    https://docs.railz.ai/reference/accounting-transactions
    """

    cursor_field = "postedDate"
    primary_key = "id"
    serviceNames = [
        "dynamicsBusinessCentral",
        "freshbooks",
        "oracleNetsuite",
        "quickbooks",
        "quickbooksDesktop",
        "sageBusinessCloud",
        "sageIntacct",
        "wave",
        "xero",
    ]

    def __init__(self, *, parent: HttpStream, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent

    def path(self, **kwargs) -> str:
        return "accountingTransactions"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for record in read_full_refresh(self.parent):
            for connection in record["connections"]:
                if connection["serviceName"] in self.serviceNames:
                    yield {"businessName": record["businessName"], "serviceName": connection["serviceName"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"businessName": stream_slice["businessName"], "serviceName": stream_slice["serviceName"], "orderBy": "postedDate"}

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any], **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            record["businessName"] = stream_slice["businessName"]
            record["serviceName"] = stream_slice["serviceName"]
            yield record


# Source
class SourceRailz(AbstractSource):
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
        auth = AccessTokenAuthenticator(client_id=config["client_id"], secret_key=config["secret_key"])
        businesses = Businesses(authenticator=auth)
        return [businesses, AccountingTransactions(parent=businesses, authenticator=auth)]
