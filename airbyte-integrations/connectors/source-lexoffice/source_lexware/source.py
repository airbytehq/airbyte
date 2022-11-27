#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


# Basic full refresh stream
class LexwareStream(HttpStream, ABC):
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
    `class LexwareStream(HttpStream, ABC)` which is the current class
    `class Customers(LexwareStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(LexwareStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalLexwareStream((LexwareStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    # url base. Required.
    url_base = "https://api.lexoffice.io/v1/"

    def __init__(self, authenticator: TokenAuthenticator = None, **kwargs):
        super().__init__(authenticator=authenticator or None)

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
        decoded_response = response.json()
        if not bool(decoded_response.get("last", True)):
            last_page = decoded_response.get("number", 0) + 1
            return {"page": last_page}
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """

        # we only get one voucher after another (for incremental sync) and sort by updatedDate
        params = {"size": 1, "sort": "updatedDate,ASC"}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Override this method to define how a response is parsed specifically. Otherwise just return a json.
        :return an iterable containing each record in the response
        """
        yield response.json()


class VoucherList(LexwareStream, IncrementalMixin):

    # The primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "id"

    cursor_field = "updatedDate"

    date_format = "%Y-%m-%d"

    def __init__(
        self,
        authenticator=None,
        voucherType: str = "any",
        voucherStatus: str = "any",
        start_date: datetime = None,
        **kwargs,
    ):
        super().__init__(authenticator=authenticator)
        self.voucherType = voucherType
        self.voucherStatus = voucherStatus
        self.start_date = start_date
        self._cursor_value = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "voucherlist"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        # get start_date from cursor_field/state or from settings
        updated_date_from = self.start_date if self.start_date is not None else None
        if stream_state.get(self.cursor_field):
            updated_date_from = pendulum.parse(stream_state[self.cursor_field])

        if updated_date_from is not None:
            # Add one second to avoid duplicate records and ensure greater than
            params.update({"updatedDateFrom": (updated_date_from + timedelta(seconds=1)).strftime("%Y-%m-%d")})

        # Add voucher type and status filters (they always have a value)
        params.update({"voucherType": self.voucherType, "voucherStatus": self.voucherStatus})
        return params

    #
    # We'll structure our state object very simply: it will be a dict whose single key is 'date' and value is the date of the last day we synced data from. For example, {'date': '2021-04-26'} indicates the connector previously read data up until April 26th and therefore shouldn't re-read anything before April 26th.
    # Let's do this by implementing the getter and setter for the state.
    #

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime(self.date_format)}
        else:
            return {}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = datetime.strptime(value[self.cursor_field], self.date_format)

    #
    # This implementation compares the date from the latest record with the date in the current state and takes the maximum as the "new" state object:
    #

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):

            # If record is empty, do not return
            if not record:
                continue

            date_format = "%Y-%m-%dT%H:%M:%S.%f%z"  # 2022-09-11T04:21:36.000+02:00
            updatedDate = datetime.strptime(record[self.cursor_field], date_format).replace(tzinfo=None)
            if self._cursor_value and self._cursor_value < updatedDate:
                self._cursor_value = updatedDate

            yield record

    #
    # We'll implement the stream_slices method to return a list of the dates for which we should pull data based on the stream state if it exists:
    #

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.

        As we read all vouchers that are AFTER start_date, we only need a single slice.
        The read_records method will write the new state containing the newest voucher record
        """
        return [{self.cursor_field: start_date.strftime(self.date_format)}]


    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = (
            datetime.strptime(stream_state[self.cursor_field], self.date_format)
            if stream_state and self.cursor_field in stream_state
            else self.start_date
        )
        return self._chunk_date_range(start_date)

    #
    # We only return a voucher without any meta data
    #

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        We return the first (and only since page size is 1) voucher here or an empty object if none
        """
        resultList = response.json().get("content", [])
        result = resultList[0] if len(resultList) > 0 else {}
        yield result


# Source
class SourceLexware(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        A connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        apikey = config["apikey"]
        r = requests.get("https://api.lexoffice.io/v1/ping", headers={"Authorization": "Bearer " + apikey})

        # check for status_code
        if r.status_code == 200:
            return True, None
        else:
            return False, "Could not verify connection to lexoffice API. Did you provide the correct API key?"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = TokenAuthenticator(config["apikey"])  # Oauth2Authenticator is also available if you need oauth support

        # Parse the date from a string into a datetime object
        date_format = "%Y-%m-%d"  # %Y-%m-%dT%H%M%S.%f%z = 2022-09-11T04: 21: 36.000+02: 00
        date = config.get("start_date", None)
        start_date = datetime.strptime(date, date_format) if date is not None and date != "" else None

        voucherType = config.get("voucher_type", "any").replace(" ", "")
        voucherStatus = config.get("voucher_status", "any").replace(" ", "")

        return [VoucherList(authenticator=auth, voucherType=voucherType, voucherStatus=voucherStatus, start_date=start_date)]
