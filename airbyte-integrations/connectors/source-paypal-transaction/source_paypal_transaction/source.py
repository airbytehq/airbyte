#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import time
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from dateutil.parser import isoparse


def get_endpoint(is_sandbox: bool = False) -> str:
    if is_sandbox:
        endpoint = "https://api-m.sandbox.paypal.com"
    else:
        endpoint = "https://api-m.paypal.com"
    return endpoint


class PaypalTransactionStream(HttpStream, ABC):

    page_size = "500"  # API limit

    # Date limits are needed to prevent API error: Data for the given start date is not available
    # API limit: (now() - start_date_min) < start_date < (now() - start_date_max)
    start_date_min: Mapping[str, int] = {"days": 3 * 364}  # API limit - 3 years
    start_date_max: Mapping[str, int] = {"hours": 0}

    stream_slice_period: Mapping[str, int] = {"days": 1}  # max period is 31 days (API limit)

    requests_per_minute: int = 30  # API limit is 50 reqs/min from 1 IP to all endpoints

    def __init__(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_sandbox: bool = False,
        config: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ):

        # Initiate data from config
        if config:
            start_date = isoparse(config["start_date"])
            end_date_str = config.get("end_date")
            end_date = isoparse(end_date_str) if end_date_str else None
            is_sandbox = config["is_sandbox"]

        self.start_date = start_date
        self._end_date = end_date
        self.is_sandbox = is_sandbox

        self._validate_input_dates()

        super().__init__(**kwargs)

    @property
    def end_date(self):
        """Return initiated end_date or now()"""
        now = datetime.now().replace(microsecond=0).astimezone()
        if not self._end_date or self._end_date > now:
            # If no end_date or end_date is in future then return now:
            return now
        else:
            return self._end_date

    def _validate_input_dates(self):

        # Validate input dates
        if self.start_date > self.end_date:
            raise Exception(f"start_date {self.start_date.isoformat()} is greater than end_date {self.end_date.isoformat()}")

        current_date = datetime.now().replace(microsecond=0).astimezone()
        current_date_delta = current_date - self.start_date

        # Check for minimal possible start_date
        if current_date_delta > timedelta(**self.start_date_min):
            raise Exception(
                f"Start_date {self.start_date.isoformat()} is too old. "
                f"Min date limit is {self.start_date_min} before now:{current_date.isoformat()}."
            )

        # Check for maximum possible start_date
        if current_date_delta < timedelta(**self.start_date_max):
            raise Exception(
                f"Start_date {self.start_date.isoformat()} is too close to now. "
                f"Max date limit is {self.start_date_max} before now:{current_date.isoformat()}."
            )

    @property
    def url_base(self) -> str:

        return f"{get_endpoint(self.is_sandbox)}/v1/reporting/"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:

        return {"Content-Type": "application/json"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        json_response = response.json()
        if self.data_field is not None:
            data = json_response.get(self.data_field, [])
        else:
            data = [json_response]

        for record in data:
            # In order to support direct datetime string comparison (which is performed in incremental acceptance tests)
            # convert any date format to python iso format string for date based cursors
            self.update_field(record, self.cursor_field, lambda date: isoparse(date).isoformat())
            yield record

        # sleep for 1-2 secs to not reach rate limit: 50 requests per minute
        time.sleep(60 / self.requests_per_minute)

    @staticmethod
    def update_field(record: Mapping[str, Any], field_path: List[str], update: Callable[[Any], None]):

        data = record
        if not isinstance(field_path, List):
            field_path = [field_path]

        for attr in field_path[:-1]:
            if data and isinstance(data, dict):
                data = data.get(attr)
            else:
                break

        last_field = field_path[-1]
        data[last_field] = update(data[last_field])

        return data

    @staticmethod
    def get_field(record: Mapping[str, Any], field_path: List[str]):

        data = record
        if not isinstance(field_path, List):
            field_path = [field_path]

        for attr in field_path:
            if data and isinstance(data, dict):
                data = data.get(attr)
            else:
                break

        return data

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:

        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        latest_record_date_str: str = self.get_field(latest_record, self.cursor_field)

        if current_stream_state and "date" in current_stream_state and latest_record_date_str:
            # isoparse supports different formats, like:
            # python iso format:               2021-06-04T00:00:00+03:00
            # format from transactions record: 2021-06-04T00:00:00+0300
            # format from balances record:     2021-06-02T00:00:00Z
            latest_record_date = isoparse(latest_record_date_str)
            current_parsed_date = isoparse(current_stream_state["date"])

            return {"date": max(current_parsed_date, latest_record_date).isoformat()}
        else:
            return {"date": self.start_date.isoformat()}


class Transactions(PaypalTransactionStream):
    """
    Stream for Transactions /v1/reporting/transactions
    """

    data_field = "transaction_details"
    primary_key = ["transaction_info", "transaction_id"]
    cursor_field = ["transaction_info", "transaction_initiation_date"]

    start_date_max = {"hours": 36}  # this limit is found experimentally
    records_per_request = 10000  # API limit

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "transactions"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        decoded_response = response.json()
        total_pages = decoded_response.get("total_pages")
        page_number = decoded_response.get("page")
        if page_number < total_pages:
            return {"page": page_number + 1}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        page_number = 1
        if next_page_token:
            page_number = next_page_token.get("page")

        return {
            "start_date": stream_slice["start_date"],
            "end_date": stream_slice["end_date"],
            "fields": "all",
            "page_size": self.page_size,
            "page": page_number,
        }

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Returns a list of slices for each day (by default) between the start date and end date.
        The return value is a list of dicts {'start_date': date_string, 'end_date': date_string}.
        """
        if stream_state and stream_state.get("date"):
            start_date = isoparse(stream_state.get("date"))
        else:
            start_date = self.start_date

        # choose first slice period (for the most recent time)
        first_slice_period = max(timedelta(**self.start_date_max), timedelta(**self.stream_slice_period))
        end_date = self.end_date

        start_date_slice = end_date - first_slice_period
        end_date_slice = end_date

        # Do not run any requests if start_date is less than 36 hrs before current time, otherwise API throws an error:
        #   'message': 'Data for the given start date is not available.'
        if start_date > start_date_slice:
            # Options 1 - sync just should be stopped since start_date is invalid and will cause API error,
            #             but incremental test fails with message: "The sync should produce at least one STATE message"
            return []
            # Option 2 - just re-sync the latest possible period, it fixes test failure mentioned above but
            #            it leaves new state message with unexpected date
            #            it duplicates the most recent records
            #            later it could cause a lack of data between the last scan and previous unexpected date
            # start_date = start_date_slice

        dates = []
        while start_date < start_date_slice:
            dates.append({"start_date": start_date_slice.isoformat(), "end_date": end_date_slice.isoformat()})
            end_date_slice = start_date_slice
            start_date_slice = start_date_slice - timedelta(**self.stream_slice_period)

        # add last (the oldest) slice period
        dates.append({"start_date": start_date.isoformat(), "end_date": end_date_slice.isoformat()})

        return dates[::-1]  # inverse stream slices to start read requests from the oldest slices


class Balances(PaypalTransactionStream):
    """
    Stream for Balances /v1/reporting/balances
    """

    primary_key = "as_of_time"
    cursor_field = "as_of_time"
    data_field = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "balances"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        return {
            "as_of_time": stream_slice["start_date"],
        }

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        return None

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Returns a list of slices for each day (by default) between the start_date and end_date (containing the last)
        The return value is a list of dicts {'start_date': date_string}.
        """
        if stream_state and stream_state.get("date"):
            if isoparse(stream_state.get("date")) == self._end_date:
                # Do not run any incremental requests if _end_date has been reached already
                return []
            # For incremental sync don't extract balance at stream_state, because
            # it has been already extracted in previous scan. Start from next slice period instead:
            start_date_slice = isoparse(stream_state.get("date")) + timedelta(**self.stream_slice_period)
        else:
            start_date_slice = self.start_date

        dates = []
        while start_date_slice < self.end_date:
            dates.append({"start_date": start_date_slice.isoformat()})
            start_date_slice = start_date_slice + timedelta(**self.stream_slice_period)

        # Add last (the newest) slice with the current time of the sync
        dates.append({"start_date": self.end_date.isoformat()})

        return dates


class PayPalOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl -v POST https://api-m.sandbox.paypal.com/v1/oauth2/token \
      -H "Accept: application/json" \
      -H "Accept-Language: en_US" \
      -u "CLIENT_ID:SECRET" \
      -d "grant_type=client_credentials"
    """

    def __init__(self, config):

        super().__init__(
            token_refresh_endpoint=f"{get_endpoint(config['is_sandbox'])}/v1/oauth2/token",
            client_id=config["client_id"],
            client_secret=config["secret"],
            refresh_token="",
        )

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return {"grant_type": "client_credentials"}

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            data = "grant_type=client_credentials"
            headers = {"Accept": "application/json", "Accept-Language": "en_US"}
            auth = (self.client_id, self.client_secret)
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=data, headers=headers, auth=auth)
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourcePaypalTransaction(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        authenticator = PayPalOauth2Authenticator(config)

        # Try to get API TOKEN
        token = authenticator.get_access_token()
        if not token:
            return False, "Unable to fetch Paypal API token due to incorrect client_id or secret"

        # Try to initiate a stream and validate input date params
        try:
            Transactions(authenticator=authenticator, config=config)
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = PayPalOauth2Authenticator(config)

        return [
            Transactions(authenticator=authenticator, config=config),
            Balances(authenticator=authenticator, config=config),
        ]
