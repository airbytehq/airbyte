#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import dateutil.parser
import math
import requests
import datetime
from airbyte_cdk.models import SyncMode
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

    url_base = "https://openapi.planday.com/"
    primary_key = "id"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=Oauth2Authenticator(token_refresh_endpoint="https://id.planday.com/connect/token",
                                                           client_id=config["client_id"], client_secret="", refresh_token=config["refresh_token"]))
        self.client_id = config["client_id"]
        self.sync_from = config["sync_from"]
        self.loockback_window = config.get("loockback_window")
        self.use_lookback = self.loockback_window is not None

        self.uri_params = {
            "offset": 0,
            "limit": 50,
            "from": self.sync_from if not self.use_lookback else self.get_today_string(delta=self.loockback_window),
        }

    @staticmethod
    def get_today_string(delta: int = 0):
        return (datetime.datetime.now()-datetime.timedelta(days=delta)).strftime("%Y-%m-%d")

    @staticmethod
    def get_today_date():
        return datetime.datetime.now().date()

    def get_date(self):
        sync_from = self.sync_from
        if self.use_lookback:
            sync_from = self.get_today_string(delta=self.loockback_window)
        return dateutil.parser.isoparse(sync_from).date()

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
        params = self.uri_params.copy()
        if next_page_token:
            params.update(next_page_token)
        else:
            params.update(self.uri_params)
        if stream_slice is not None:
            for key in ("from", "to"):
                if key in stream_slice:
                    params.update({key: stream_slice[key]})
        return params

    def parse_response(self,
                       response: requests.Response,
                       *,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None,) -> Iterable[Mapping]:
        data = response.json().get("data", [])
        yield from data if isinstance(data, list) else [data]

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {"X-ClientId": self.client_id}


class IncrementalPlandayStream(PlandayStream, ABC):
    state_checkpoint_interval = math.inf
    slice_range = 35
    stop_at_today = True

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
        old_state_date = current_stream_state.get(
            self.cursor_field, self.get_date())
        if isinstance(old_state_date, str):
            old_state_date = dateutil.parser.isoparse(old_state_date).date()
        latest_record_date = latest_record.get(self.cursor_field)
        return {self.cursor_field: max(dateutil.parser.isoparse(latest_record_date).date(), old_state_date)}

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_ts = self.get_start_timestamp(stream_state)
        for start, end in self.chunk_dates(start_ts):
            yield {"from": start, "to": end}

    def get_start_timestamp(self, stream_state) -> datetime.date:
        start_point = self.get_date()
        if stream_state and self.cursor_field in stream_state:
            state_start = stream_state[self.cursor_field]
            if isinstance(stream_state[self.cursor_field], str):
                state_start = dateutil.parser.isoparse(state_start).date()
            start_point = max(start_point, state_start)

        return start_point

    def chunk_dates(self, start_date_ts: datetime.date) -> Iterable[Tuple[datetime.date, Union[datetime.date, None]]]:
        today = self.get_today_date()
        step = datetime.timedelta(days=self.slice_range)
        after_ts = start_date_ts
        while after_ts < today:
            before_ts = min(today, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + datetime.timedelta(days=1)
        if not self.stop_at_today:
            yield after_ts, None


class IncrementalSubPlandayStream(IncrementalPlandayStream, ABC):

    def __init__(self, parent: HttpSubStream, config: Mapping[str, Any]):
        super().__init__(config)
        self.parent = parent

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            # iterate over all parent records with current stream_slice
            start_ts = self.get_start_timestamp(stream_state)
            for record in parent_records:
                for start, end in self.chunk_dates(start_ts):
                    yield {"parent": record, "from": start, "to": end}


class Departments(PlandayStream):
    primary_key = "id"

    @property
    def use_cache(self) -> bool:
        return True

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


class TimeAndCosts(IncrementalSubPlandayStream):

    primary_key = "shiftId"
    cursor_field = "from"

    def __init__(self, parent: Departments, config: Mapping[str, Any]):
        super().__init__(parent=parent, config=config)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"scheduling/v1/timeandcost/{stream_slice['parent']['id']}"

    def parse_response(self,
                       response: requests.Response,
                       *,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None,) -> Iterable[Mapping]:
        data = response.json().get("data", {})
        costs = data.get("costs", [])
        yield from [{**cost, "departmentId": stream_slice['parent']['id']} for cost in costs]


class EmployeeDetails(HttpSubStream, PlandayStream):

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


class Shifts(IncrementalPlandayStream):

    primary_key = "id"
    cursor_field = "date"
    stop_at_today = False

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
        Check if connection works.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            employees = Employees(config)
            records = employees.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        employees = Employees(config)
        departments = Departments(config)
        return [departments, employees, EmployeeGroups(config), TimeAndCosts(parent=departments, config=config), Shifts(config), ShiftTypes(config), EmployeeDetails(parent=employees, config=config)]
