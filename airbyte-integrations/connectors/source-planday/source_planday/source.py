#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

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
class PlandayStream(HttpStream, ABC):
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
    `class PlandayStream(HttpStream, ABC)` which is the current class
    `class Customers(PlandayStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(PlandayStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalPlandayStream((PlandayStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # TODO: Fill in the url base. Required.
    url_base = "https://openapi.planday.com/"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=Oauth2Authenticator(token_refresh_endpoint="https://id.planday.com/connect/token",
                                                           client_id=config["client_id"], client_secret="", refresh_token=config["refresh_token"]))
        self.client_id = config["client_id"]
        self.sync_from = config["sync_from"]
        self.loockback_window = config.get("loockback_window")

        self.uri_params = {
            "offset": 0,
            "limit": 50,
            "from": self.sync_from if self.loockback_window is None else self.get_today_string(delta=self.loockback_window),
        }

    @staticmethod
    def get_today_string(delta: int = 0):
        return (datetime.datetime.now()-datetime.timedelta(days=delta)).strftime("%Y-%m-%d")

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
        paging = response.json().get("paging", {})
        offset = paging.get("offset", 0)
        limit = paging.get("limit", 0)
        total = paging.get("total", 0)
        next_offset = offset + limit
        if next_offset < total:
            return {"offset": next_offset}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = self.uri_params
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data", [])
        print(data)
        print(response.json())
        yield from data if isinstance(data, list) else [data]

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {"X-ClientId": self.client_id}


class Departments(PlandayStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "hr/v1/departments"


class Employees(PlandayStream):

    primary_key = "id"

    @property
    def use_cache(self) -> bool:
        return True

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "hr/v1/employees"


class EmployeeGroups(PlandayStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "hr/v1/employeegroups"


class TimeAndCosts(HttpSubStream, PlandayStream):
    # TODO: How to get this to work with department ID
    primary_key = "id"

    def __init__(self, parent: Departments, config: Mapping[str, Any]):
        super().__init__(parent=parent, config=config)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"scheduling/v1/timeandcost/{stream_slice['parent']['id']}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "from": self.sync_from,
            "to": self.get_today_string(),
        }


class EmployeeDetails(HttpSubStream, PlandayStream):
    # TODO: How to get this to work with department ID
    primary_key = "id"

    def __init__(self, parent: Employees, config: Mapping[str, Any]):
        super().__init__(parent=parent, config=config)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"hr/v1/employees/{stream_slice['parent']['id']}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            "special": "BankAccount,BirthDate,Ssn"
        }


class Shifts(PlandayStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "scheduling/v1/shifts"


class ShiftTypes(PlandayStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "scheduling/v1/shifttypes"


class SourcePlanday(AbstractSource):
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
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        employees = Employees(config)
        return [Departments(config), employees, EmployeeGroups(config), TimeAndCosts(parent=Departments(config), config=config), Shifts(config), ShiftTypes(config), EmployeeDetails(parent=Employees(config), config=config)]
