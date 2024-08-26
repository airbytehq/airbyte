#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union, Callable
import dpath.util
import json

import backoff
import requests
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.extractors.dpath_extractor import DpathExtractor
from airbyte_cdk.sources.declarative.types import Config, Record
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString


logger = logging.getLogger("airbyte")


@dataclass
class PayPalOauth2Authenticator(DeclarativeOauth2Authenticator):
    """Request example for API token extraction:
    For `old_config` scenario:
        curl -v POST https://api-m.sandbox.paypal.com/v1/oauth2/token \
        -H "Accept: application/json" \
        -H "Accept-Language: en_US" \
        -u "CLIENT_ID:SECRET" \
        -d "grant_type=client_credentials"
    """

    # config: Mapping[str, Any]
    # client_id: Union[InterpolatedString, str]
    # client_secret: Union[InterpolatedString, str]
    # refresh_request_body: Optional[Mapping[str, Any]] = None
    # token_refresh_endpoint: Union[InterpolatedString, str]
    # grant_type: Union[InterpolatedString, str] = "refresh_token"
    # expires_in_name: Union[InterpolatedString, str] = "expires_in"
    # access_token_name: Union[InterpolatedString, str] = "access_token"
    # parameters: InitVar[Mapping[str, Any]]

    def get_headers(self):
        basic_auth = base64.b64encode(bytes(f"{self.get_client_id()}:{self.get_client_secret()}", "utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {basic_auth}"}

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        max_tries=2,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _get_refresh_access_token_response(self):
        try:
            request_url = self.get_token_refresh_endpoint()
            request_headers = self.get_headers()
            request_body = self.build_refresh_request_body()

            logger.info(f"Sending request to URL: {request_url}")

            response = requests.request(method="POST", url=request_url, data=request_body, headers=request_headers)

            self._log_response(response)
            response.raise_for_status()

            response_json = response.json()

            self.access_token = response_json.get("access_token")

            return response.json()

        except requests.exceptions.RequestException as e:
            if e.response and (e.response.status_code == 429 or e.response.status_code >= 500):
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

class InterviewRecordExtractor(RecordExtractor):
    """
    Create records from complex response structure
    Issue: https://github.com/airbytehq/airbyte/issues/23145
    """
    config: Config
    field_path: List[Union[InterpolatedString, str]]
    parameters: Mapping[str, Any]
    records = [
        ] 
    done = False

    def __init__(self, config: Config, field_path, parameters: MutableMapping[str, Any]): 
        self.config = config
        self.field_path = field_path
        self.parameters = parameters
        if "field_path" in parameters:
            self.field_path = [parameters["field_path"]]

    def extract_records(self, response: requests.Response) -> Iterable[Record]:
        if self.done:
            return []
        else:
            self.done = True
            return self.records

class PaypalRequester(HttpRequester):
    def send_request(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        response = requests.Response()
        response.status_code = 200 
        response._content = json.dumps({
            "transaction_details": [
{"transaction_info": {"paypal_account_id": "LNTXN", "transaction_id": "5AV84042KY532240C", "paypal_reference_id": "7G123FED297826", "paypal_reference_id_type": "TXN", "transaction_event_code": "T0006", "transaction_initiation_date": "2021-07-09T07:27:58+0000", "transaction_updated_date": "2021-08-09T07:27:58+0000", "transaction_amount": {"currency_code": "USD", "value": "13.00"}, "fee_amount": {"currency_code": "USD", "value": "-1.14"}, "transaction_status": "S", "ending_balance": {"currency_code": "USD", "value": "2067.82"}, "available_balance": {"currency_code": "USD", "value": "2067.82"}, "custom_field": "3f2d29d7-5eaf-4fb2-834f", "protection_eligibility": "01"}, "payer_info": {"account_id": "********", "email_address": "contact@airbyte.com", "address_status": "N", "payer_status": "Y", "payer_name": {"alternate_full_name": "eupshot"}, "country_code": "IN"}, "shipping_info": {"name": "sasi, kumar"}, "cart_info": {"item_details": [{"item_name": "StartUp 1 Month Plan", "item_quantity": "1", "item_unit_price": {"currency_code": "USD", "value": "13.00"}, "item_amount": {"currency_code": "USD", "value": "13.00"}, "total_item_amount": {"currency_code": "USD", "value": "13.00"}}]}, "store_info": {}, "auction_info": {}, "incentive_info": {}, "transaction_updated_date": "2021-07-09T07:27:58Z", "transaction_id": "5AV84042KY532240C"},
{"transaction_info": {"paypal_account_id": "LNTXN", "transaction_id": "17E39458423484J", "paypal_reference_id": "7G123FED297827", "paypal_reference_id_type": "TXN", "transaction_event_code": "T0006", "transaction_initiation_date": "2021-07-09T07:36:34+0000", "transaction_updated_date": "2021-07-09T07:36:34+0000", "transaction_amount": {"currency_code": "USD", "value": "6.88"}, "fee_amount": {"currency_code": "USD", "value": "-0.83"}, "transaction_status": "S", "ending_balance": {"currency_code": "USD", "value": "2073.87"}, "available_balance": {"currency_code": "USD", "value": "2073.87"}, "custom_field": "a8cbf197-86a0-47b0-9220", "protection_eligibility": "01"}, "payer_info": {"account_id": "********", "email_address": "contact@airbyte.com", "address_status": "N", "payer_status": "Y", "payer_name": {"given_name": "Airbyte", "surname": "Paypal", "alternate_full_name": "Airbyte Paypal"}, "country_code": "ES"}, "shipping_info": {"name": "Sacer, Paypal"}, "cart_info": {"item_details": [{"item_name": "50 Credits", "item_quantity": "1", "item_unit_price": {"currency_code": "USD", "value": "5.69"}, "item_amount": {"currency_code": "USD", "value": "5.69"}, "tax_amounts": [{"tax_amount": {"currency_code": "USD", "value": "1.19"}}], "total_item_amount": {"currency_code": "USD", "value": "6.88"}}]}, "store_info": {}, "auction_info": {}, "incentive_info": {}, "transaction_updated_date": "2022-08-09T07:36:34Z", "transaction_id": "17E39458423484J"},
{"transaction_info": {"paypal_account_id": "LNTXN", "transaction_id": "7NB01743HH290794E", "paypal_reference_id": "7G123FED297828", "paypal_reference_id_type": "TXN", "transaction_event_code": "T0006", "transaction_initiation_date": "2021-07-09T07:36:34+0000", "transaction_updated_date": "2021-07-09T07:36:34+0000", "transaction_amount": {"currency_code": "USD", "value": "6.88"}, "fee_amount": {"currency_code": "USD", "value": "-0.83"}, "transaction_status": "S", "ending_balance": {"currency_code": "USD", "value": "2073.87"}, "available_balance": {"currency_code": "USD", "value": "2073.87"}, "custom_field": "a8cbf197-86a0-47b0-9220", "protection_eligibility": "01"}, "payer_info": {"account_id": "********", "email_address": "contact@airbyte.com", "address_status": "N", "payer_status": "Y", "payer_name": {"given_name": "Airbyte", "surname": "Paypal", "alternate_full_name": "Airbyte Paypal"}, "country_code": "ES"}, "shipping_info": {"name": "Sacer, Paypal"}, "cart_info": {"item_details": [{"item_name": "50 Credits", "item_quantity": "1", "item_unit_price": {"currency_code": "USD", "value": "5.69"}, "item_amount": {"currency_code": "USD", "value": "5.69"}, "tax_amounts": [{"tax_amount": {"currency_code": "USD", "value": "1.19"}}], "total_item_amount": {"currency_code": "USD", "value": "6.88"}}]}, "store_info": {}, "auction_info": {}, "incentive_info": {}, "transaction_updated_date": "2022-08-09T07:36:34Z", "transaction_id": "7NB01743HH290794E"},
            ]
        }).encode("utf-8")
        return response