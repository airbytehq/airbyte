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

import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

logging.basicConfig(level=logging.DEBUG)
"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream
class PaypalTransactionStream(HttpStream, ABC):
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
    `class PaypalTransactionStream(HttpStream, ABC)` which is the current class
    `class Customers(PaypalTransactionStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(PaypalTransactionStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalPaypalTransactionStream((PaypalTransactionStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """

    url_base = "https://api-m.sandbox.paypal.com/v1/reporting/"
    # url_base = "https://api-m.paypal.com/v1/reporting/"

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
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        page_number = 1
        if next_page_token:
            page_number = next_page_token.get("page")

        start_date = stream_slice["date"]
        end_date_dt = datetime.fromisoformat(start_date) + timedelta(days=self.stream_size_in_days)

        date_time_now = datetime.now().astimezone()
        if end_date_dt > date_time_now:
            end_date_dt = date_time_now

        end_date = end_date_dt.isoformat()
        return {"start_date": start_date, "end_date": end_date, "fields": "all", "page_size": "1", "page": page_number}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        json_response = response.json()
        records = json_response.get(self.data_field, []) if self.data_field is not None else json_response
        yield from records

    @staticmethod
    def get_field(record: Mapping[str, Any], field_path: List[str]):

        data = record
        for attr in field_path:
            if data:
                data = data.get(attr)
            else:
                break

        return data


class Transactions(PaypalTransactionStream):
    """
    Stream for Transactions /v1/reporting/transactions
    """

    data_field = "transaction_details"
    primary_key = "transaction_id"
    cursor_field = ["transaction_info", "transaction_initiation_date"]
    stream_size_in_days = 1

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "transactions"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        # This method is called once for each record returned from the API to compare the cursor field value in that record with the current state
        # we then return an updated state object. If this is the first time we run a sync or no state was passed, current_stream_state will be None.
        latest_record_date_str = self.get_field(latest_record, self.cursor_field)

        if current_stream_state and "date" in current_stream_state and latest_record_date_str:
            if len(latest_record_date_str) == 24:
                # Add ':' to timezone part to match iso format, example:
                # python iso format:  2021-06-04T00:00:00+03:00
                # format from record: 2021-06-04T00:00:00+0300
                latest_record_date_str = ":".join([latest_record_date_str[:22], latest_record_date_str[22:]])

            latest_record_date = datetime.fromisoformat(latest_record_date_str)
            current_parsed_date = datetime.fromisoformat(current_stream_state["date"])

            return {"date": max(current_parsed_date, latest_record_date).isoformat()}
        else:
            return {"date": self.start_date.isoformat()}

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.now().astimezone() - timedelta(days=2):
            dates.append({"date": start_date.isoformat()})
            start_date += timedelta(days=self.stream_size_in_days)
        return dates

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:

        start_date = self.start_date
        if stream_state and "date" in stream_state:
            start_date = datetime.fromisoformat(stream_state["date"])

        return self._chunk_date_range(start_date)


class Balances(PaypalTransactionStream):
    """
    Stream for Balances /v1/reporting/balances
    """

    data_field = "transaction_details"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "as_of_time"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "balances"


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
        token = PayPalOauth2Authenticator(
            token_refresh_endpoint="https://api-m.sandbox.paypal.com/v1/oauth2/token",
            client_id=config["client_id"],
            client_secret=config["secret"],
            refresh_token="",
        ).get_access_token()
        if not token:
            return False, "Unable to fetch Paypal API token due to incorrect client_id or secret"

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
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d").astimezone()
        # return [Transactions(authenticator=auth), Balances(authenticator=auth)]
        return [Transactions(authenticator=authenticator, start_date=start_date)]
