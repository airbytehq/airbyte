#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from airbyte_cdk.models import SyncMode
import base64
import json
import datetime


class ParcelPerformAuthenticator(Oauth2Authenticator):
    def get_refresh_request_body(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {"grant_type": "client_credentials"}
        return payload

    def request_headers(self) -> Mapping[str, Any]:
        """
        This method encodes the credentials in base64 client_id:client_secret format as required by parcelperform.
        """
        credentials = (self.client_id + ":" + self.client_secret).encode()
        encoded_credentials = base64.b64encode(credentials)
        return {
            "Accept": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded_credentials.decode(),
        }

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        Modified original method to add headers with encoding
        """
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                headers=self.request_headers(),
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class Shipments(HttpStream, ABC):

    url_base = "https://api.parcelperform.com"
    primary_key = "shipment_uuid"
    cursor_field = "updated_date"
    sync_end_range = datetime.datetime.now()
    shipment_ids = []
    config = {}
    raise_on_http_errors = False
    state_checkpoint_interval = None

    def sync_date_range(self, stream_state) -> Mapping[str, Any]:
        config_start_date = datetime.datetime.strptime(
            self.config["start_date"], "%Y-%m-%dT%H:%M:%S"
        )
        if self.cursor_field in stream_state.keys():
            start_date = min(
                datetime.datetime.strptime(
                    stream_state["updated_date"][:19], "%Y-%m-%dT%H:%M:%S"
                ),
                self.sync_end_range,
            )
        else:
            start_date = config_start_date
        return {
            "start": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": self.sync_end_range.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/v5/shipment/list/"

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        if response.status_code == 200:
            return response.json()["next_page"]
        elif response.status_code == 404 and response.json()["api_response"] == "4041":
            return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        date_range = self.sync_date_range(stream_state)
        # The api allows only for 100 shipments per page
        params = {
            "updated_date_from": date_range["start"],
            "updated_date_to": date_range["end"],
            "limit": 100,
        }
        if next_page_token:
            params["next_page"] = next_page_token
        return params

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        if response.status_code == 200:
            records = response.json()["data"]
            for row in records:
                self.shipment_ids.append(row[self.primary_key])
            yield from records
        elif response.status_code == 404 and response.json()["api_response"] == "4041":
            self.logger.info(response.json()["message"])

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, any]:
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field),
                current_stream_state.get(self.cursor_field, self.config["start_date"]),
            )
        }


class ShipmentsDetails(Shipments, ABC):
    shipment_ids_index = 0
    state_checkpoint_interval = None
    config = {}

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        """
        We pass each shipment_uuid as a next page token in order to make individual requests per shipment
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        self.shipment_ids_index += 1
        if self.shipment_ids_index >= len(self.shipment_ids):
            return {}
        return self.shipment_ids_index

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        try:
            return {"shipment_uuid": self.shipment_ids[self.shipment_ids_index]}
        except IndexError:
            return {}

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/v5/shipment/details/"

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        try:
            yield response.json()["data"]
        except KeyError:
            return None


class SourceParcelPerform(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check whether configuration is correct.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        auth = ParcelPerformAuthenticator(
            "https://api.parcelperform.com/auth/oauth/token/",
            config["client_id"],
            config["client_secret"],
            "access_token",
        )
        if auth.get_access_token():
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = ParcelPerformAuthenticator(
            "https://api.parcelperform.com/auth/oauth/token/",
            config["client_id"],
            config["client_secret"],
            "access_token",
        )
        shipments = Shipments(authenticator=auth)
        shipments.config = config
        shipments_details = ShipmentsDetails(authenticator=auth)
        shipments_details.config = config
        # If there are shipments to fetch details for
        if len(shipments.shipment_ids):
            shipments_details.shipment_ids = shipments.shipment_ids
        return [shipments, shipments_details]
