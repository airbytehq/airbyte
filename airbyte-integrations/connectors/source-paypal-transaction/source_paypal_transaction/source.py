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

from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from dateutil.parser import isoparse


class PaypalTransactionStream(HttpStream, ABC):

    sandbox = True

    page_size = "500"  # API limit

    # Date limits are needed to prevent API error: Data for the given start date is not available
    start_date_limits: Mapping[str, Mapping] = {"min_date": {"days": 3 * 364}, "max_date": {"hours": 12}}  # API limit - 3 years

    stream_slice_period: Mapping[str, int] = {"days": 1}

    def __init__(self, start_date: datetime, end_date: datetime, env: str = "Production", **kwargs):
        super().__init__(**kwargs)

        self._validate_input_dates(start_date=start_date, end_date=end_date)

        self.start_date = start_date
        self.end_date = end_date
        self.env = env

    def _validate_input_dates(self, start_date, end_date):

        # Validate input dates
        if start_date > end_date:
            raise Exception(f"start_date {start_date} is greater than end_date {end_date}")

        current_date = datetime.now().replace(microsecond=0).astimezone()
        current_date_delta = current_date - start_date

        # Check for minimal possible start_date
        if current_date_delta > timedelta(**self.start_date_limits.get("min_date")):
            raise Exception(
                f"Start_date {start_date.isoformat()} is too old. "
                f"Min date limit is {self.start_date_limits.get('min_date')} before now:{current_date.isoformat()}."
            )

        # Check for maximum possible start_date
        if current_date_delta < timedelta(**self.start_date_limits.get("max_date")):
            raise Exception(
                f"Start_date {start_date.isoformat()} is too close to now. "
                f"Max date limit is {self.start_date_limits.get('max_date')} before now:{current_date.isoformat()}."
            )

    @property
    def url_base(self) -> str:

        if self.env == "Production":
            url_base = "https://api-m.paypal.com/v1/reporting/"
        else:
            url_base = "https://api-m.sandbox.paypal.com/v1/reporting/"

        return url_base

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
            self.update_field(record, self.cursor_field, lambda x: isoparse(x).isoformat())
            yield record

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

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        """
        Returns a list of each day (by default) between the start date and end date.
        The return value is a list of dicts {'start_date': date_string, 'end_date': date_string}.
        """
        dates = []

        # start date should not be less than 12 hrs before current time, otherwise API throws an error:
        #   'message': 'Data for the given start date is not available.'
        start_date_limit_max = self.end_date - timedelta(**self.start_date_limits.get("max_date")) - timedelta(**self.stream_slice_period)
        while start_date < start_date_limit_max:
            end_date = start_date + timedelta(**self.stream_slice_period)
            dates.append({"start_date": start_date.isoformat(), "end_date": end_date.isoformat()})
            start_date = end_date

        dates.append({"start_date": start_date.isoformat(), "end_date": self.end_date.isoformat()})

        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        start_date = self.start_date
        if stream_state and "date" in stream_state:
            start_date = isoparse(stream_state["date"])

        return self._chunk_date_range(start_date)

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

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "transactions"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:

        decoded_response = response.json()
        total_pages = decoded_response.get("total_pages")
        page_number = decoded_response.get("page")
        if page_number >= total_pages:
            return None
        else:
            return {"page": page_number + 1}

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


class PayPalOauth2Authenticator(Oauth2Authenticator):
    """
    curl -v POST https://api-m.sandbox.paypal.com/v1/oauth2/token \
      -H "Accept: application/json" \
      -H "Accept-Language: en_US" \
      -u "CLIENT_ID:SECRET" \
      -d "grant_type=client_credentials"
    """

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        """ Override to define additional parameters """
        payload: MutableMapping[str, Any] = {"grant_type": "client_credentials"}
        return payload

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
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        start_date = isoparse(config["start_date"])
        end_date_str = config["end_date"]
        if end_date_str:
            end_date = isoparse(end_date_str)
        else:
            end_date = datetime.now().replace(microsecond=0).astimezone()

        if config["environment"] == "Production":
            url_auth = "https://api-m.paypal.com/v1/oauth2/token"
        else:
            url_auth = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

        authenticator = PayPalOauth2Authenticator(
            token_refresh_endpoint=url_auth,
            client_id=config["client_id"],
            client_secret=config["secret"],
            refresh_token="",
        )
        # Try to get API TOKEN
        token = authenticator.get_access_token()
        if not token:
            return False, "Unable to fetch Paypal API token due to incorrect client_id or secret"

        # Try to initiate a stream and validate input date params
        try:
            Transactions(authenticator=authenticator, start_date=start_date, end_date=end_date, env=config["environment"])
        except Exception as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """58
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = PayPalOauth2Authenticator(
            token_refresh_endpoint="https://api-m.sandbox.paypal.com/v1/oauth2/token",
            client_id=config["client_id"],
            client_secret=config["secret"],
            refresh_token="",
        )

        start_date = isoparse(config["start_date"])
        end_date_str = config["end_date"]
        if end_date_str:
            end_date = isoparse(end_date_str)
        else:
            end_date = datetime.now().replace(microsecond=0).astimezone()

        return [
            Transactions(authenticator=authenticator, start_date=start_date, end_date=end_date, env=config["environment"]),
            Balances(authenticator=authenticator, start_date=start_date, end_date=end_date, env=config["environment"]),
        ]
