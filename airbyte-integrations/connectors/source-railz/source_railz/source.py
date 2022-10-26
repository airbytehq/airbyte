#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
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

    page_size = 100
    url_base = "https://api.railz.ai/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.status_code == 204:
            return
        response_json = response.json()
        pagination = response_json.get("pagination", response_json.get("meta"))
        if pagination:
            if pagination["offset"] + self.page_size < pagination["count"]:
                return {"offset": str(pagination["offset"] + self.page_size)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": str(self.page_size)}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.status_code == 204:
            return
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
        businessName = latest_record["businessName"]
        serviceName = latest_record["serviceName"]
        updated_state = pendulum.parse(latest_record[self.cursor_field]).date()
        stream_state_value = current_stream_state.setdefault(businessName, {}).setdefault(serviceName, {}).get(self.cursor_field)
        if stream_state_value:
            stream_state_value = pendulum.parse(stream_state_value).date()
            updated_state = max(updated_state, stream_state_value)
        current_stream_state[businessName][serviceName][self.cursor_field] = updated_state.format("YYYY-MM-DD")
        return current_stream_state


class ServiceIncrementalRailzStream(IncrementalRailzStream):
    cursor_field = "postedDate"
    primary_key = "id"

    def __init__(self, *, parent: HttpStream, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.start_date_cache = {}

    @abstractmethod
    def path(self, **kwargs) -> str:
        pass

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for record in read_full_refresh(self.parent):
            for connection in record["connections"]:
                if connection["serviceName"] in self.serviceNames:
                    yield {"businessName": record["businessName"], "serviceName": connection["serviceName"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        businessName = stream_slice["businessName"]
        serviceName = stream_slice["serviceName"]
        params.update({"businessName": businessName, "serviceName": serviceName, "orderBy": self.cursor_field})
        startDate = self.get_start_date(stream_state, stream_slice)
        if startDate:
            params["startDate"] = startDate
        return params

    def get_start_date(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any]) -> str:
        businessName = stream_slice["businessName"]
        serviceName = stream_slice["serviceName"]
        start_date = stream_state.get(businessName, {}).get(serviceName, {}).get(self.cursor_field)
        return self.start_date_cache.setdefault(businessName, {}).setdefault(serviceName, start_date)

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any], **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            record["businessName"] = stream_slice["businessName"]
            record["serviceName"] = stream_slice["serviceName"]
            yield record


class AccountingTransactions(ServiceIncrementalRailzStream):
    """
    https://docs.railz.ai/reference/accounting-transactions
    """

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

    def path(self, **kwargs) -> str:
        return "accountingTransactions"


class Bills(ServiceIncrementalRailzStream):
    """
    https://api.railz.ai/bills
    """

    serviceNames = [
        "dynamicsBusinessCentral",
        "freshbooks",
        "oracleNetsuite",
        "plaid",
        "quickbooks",
        "quickbooksDesktop",
        "sageBusinessCloud",
        "sageIntacct",
        "shopify",
        "square",
        "wave",
        "xero",
    ]

    def path(self, **kwargs) -> str:
        return "bills"


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
        return [businesses, AccountingTransactions(parent=businesses, authenticator=auth), Bills(parent=businesses, authenticator=auth)]
