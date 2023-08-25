#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.models import SyncMode


class TripletexApiStream(HttpStream, ABC):
    url_base = "https://tripletex.no/v2/"

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.today = pendulum.today()
        self.start_date = config.get('start_date')
        self.consumer_token = config.get('consumer_token')
        self.employee_token = config.get('employee_token')
        self.session_token = None
        self.get_session_token()

        self.date_to = None

    def get_session_token(self):
        querystring = {
            "consumerToken": self.consumer_token,
            "employeeToken": self.employee_token,
            "expirationDate": pendulum.today().add(days=2).format("YYYY-MM-DD"),
        }
        url = "https://tripletex.no/v2/token/session/:create"
        response = requests.request("PUT", url, params=querystring)

        session_token = json.loads(response.text)["value"]["token"]
        username_and_pass = str.encode("0:{}".format(session_token))
        self.session_token = base64.b64encode(
            username_and_pass).decode("utf-8")

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Authorization": f"Basic {self.session_token}"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        print(response.url)
        yield from response.json().get("values", [])


class DateRequiredStream(TripletexApiStream, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date_from_key_name = "dateFrom"
        self.date_to_key_name = "dateTo"

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
        last_date = pendulum.parse(self.date_to or self.start_date)

        if last_date < self.today:
            self.date_to = last_date.add(days=3).format("YYYY-MM-DD")
            return {
                self.date_from_key_name: last_date.format("YYYY-MM-DD"),
                self.date_to_key_name: self.date_to
            }

        return None

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            self.date_from_key_name: self.start_date,
            self.date_to_key_name: pendulum.parse(self.start_date).add(days=3).format("YYYY-MM-DD"),
            "count": 10000
        }

        if next_page_token:
            params.update(next_page_token)

        return params


class Postings(DateRequiredStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "ledger/posting"


class Invoice(DateRequiredStream):
    primary_key = "id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date_from_key_name = "invoiceDateFrom"
        self.date_to_key_name = "invoiceDateTo"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "invoice"


class Departments(TripletexApiStream):
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "department"


class Accounts(TripletexApiStream):
    primary_key = "id"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "ledger/account"


class TripletexPaginationStream(TripletexApiStream, ABC):

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        full_result_size = response.json().get("fullResultSize")
        data = response.json()
        index = data.get("from")
        count = data.get("count")
        return None if index + count >= full_result_size else {"from": index + count}

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(next_page_token)

        return params


class Payslip(TripletexPaginationStream):
    primary_key = "id"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "fields": "id,version,url,employee,date,year,month,specifications,vacationAllowanceAmount,grossAmount,amount,number"}
        params.update(super().request_params(
            stream_state, stream_slice, next_page_token))
        return params

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "salary/payslip"


class SalaryType(TripletexPaginationStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "salary/type"


class Employee(TripletexApiStream):
    primary_key = "id"

    @property
    def use_cache(self) -> bool:
        return True

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "employee"


class BalanceSheet(DateRequiredStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "balanceSheet"


class MonthlyStatus(TripletexPaginationStream):
    primary_key = "id"

    def __init__(self, parent: Employee, config: Mapping[str, Any]):
        super().__init__(config=config)
        self.parent = parent
        self.lookback = config.get("lookback_monthly_status", 0)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "timesheet/month/byMonthNumber"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update({"monthYear": stream_slice.get("monthYear"),
                       "employeeIds": stream_slice.get("parent", {}).get("id")})
        return params

    def _month_slices(self):
        current_month = pendulum.today().start_of("month")
        return [current_month.subtract(months=i).format("YYYY-MM") for i in range(self.lookback+1)]

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
            months = self._month_slices()
            for record in parent_records:
                for month in months:
                    yield {"parent": record, "monthYear": month}


class SourceTripletexApi(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """

        employee_stream = Employee(config=config)
        return [Postings(config=config), Departments(config=config), Accounts(config=config), BalanceSheet(config=config),
                employee_stream, Invoice(config=config), Payslip(
                    config=config), SalaryType(config=config),
                MonthlyStatus(parent=employee_stream, config=config)]
