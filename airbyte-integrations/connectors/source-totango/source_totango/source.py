#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import json
import logging
import requests
import dpath
import datetime
import time
from airbyte_cdk.models import SyncMode, FailureType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets

_TOTANGO_URL_BASE = "https://api-gw-us.totango.com"


class TotangoStream(HttpStream, ABC):
    # Base URL for the Totango API
    url_base = _TOTANGO_URL_BASE

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        https://support.totango.com/hc/en-us/articles/15312978301588-API-rate-limit
        """
        try:
            self.logger.info("Backing off...")
            self.logger.info(f"X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit')}")
            self.logger.info(f"X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining')}")
            self.logger.info(f"X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset')}")

            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining'))
            next_attempt_ts = int(response.headers.get('X-RateLimit-Reset', time.time() + (60 * 3)))

            if rate_limit_remaining <= 5:
                delay = next_attempt_ts - time.time() + 15.0
                self.logger.info(f"Backing off, will retry in {delay} seconds")
                return delay
            else:
                self.logger("Plenty remaining, not backing off")
                return 0

        except:
            self.logger.warn("Exception getting backoff time, defaulting to 4m")
            return 4.0 * 60.0


class TotangoAuthenticator(requests.auth.AuthBase):
    _token_request_path = '/oauth/token'
    _grant_type = 'client_credentials'
    _headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def __init__(self, credentials: dict):
        self._client_secret = credentials["client_secret"]
        self._client_id = credentials["client_id"]

        self._token: dict = {}

    def _payload(self) -> dict:
        return {
            "grant_type": self._grant_type,
            "client_id": self._client_id,
            "client_secret": self._client_secret
        }

    def _token_expired(self):
        if not self._token:
            return True
        return self._token["access_token_expiration"] < (
            datetime.datetime.now().timestamp() * 1000
        )

    def _rotate(self):
        if self._token_expired():
            try:
                response = requests.request(
                    method="POST",
                    headers=self._headers,
                    url=f"{_TOTANGO_URL_BASE}{self._token_request_path}",
                    data=self._payload()
                ).json()
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching access token: {e}") from e
            self._token = response

    def __call__(self, r: requests.Request) -> requests.Request:
        self._rotate()

        r.headers["Authorization"] = f"Bearer {self._token['access_token']}"
        return r


class Account(TotangoStream):
    # Primary key of the stream
    primary_key = "account_id"
    record_count = 1000

    @property
    def use_cache(self):
        return True

    @property
    def cache_filename(self):
        return "accounts.yml"

    def __init__(self, authenticator: TotangoAuthenticator, config: dict):
        super().__init__(authenticator=authenticator)
        self._connector_config = config

    @property
    def http_method(self) -> str:
        """
        Returns the HTTP method to use for requests.
        """
        return "POST"

    def path(self, stream_state=None, stream_slice=None, next_page_token=None) -> str:
        """Returns the endpoint path for this stream."""
        return "/api/v1/search/accounts"

    def get_json_schema(self):
        schema = super().get_json_schema()

        if 'AccountConfig' in self._connector_config:
            custom_fields = dpath.util.get(
                self._connector_config["AccountConfig"],
                "customFields",
                default=[]
            )

            if custom_fields:
                for field in custom_fields:
                    schema["properties"][field["attribute"]] = field

        return schema

    def get_fields(self):
        """
        Returns the fields for the API response.
        """
        schema = self.get_json_schema()

        custom_fields = None
        if 'AccountConfig' in self._connector_config:
            custom_fields = dpath.util.get(
                self._connector_config["AccountConfig"],
                "customFields",
                default=[]
            )

        fields = []

        for _, field_details in schema["properties"].items():
            field = {
                "type": field_details["source_attribute"],
            }
            if "additionalProps" in field_details:
                field.update(field_details["additionalProps"])
                field["field_display_name"] = field_details["attribute"]
                fields.append(field)
                continue

            field["attribute"] = field_details["attribute"]
            fields.append(field)

        if custom_fields:
            print("adding custom fields")
            for field in custom_fields:
                print("custom field: ", field)
                custom_field = {
                    "type": field["source_attribute"],
                }
                if field.get("additionalProps"):
                    custom_field.update(field["additionalProps"])
                    custom_field["field_display_name"] = field["attribute"]
                    fields.append(custom_field)
                    continue

                custom_field["attribute"] = field["attribute"]
                fields.append(custom_field)

        return fields

    def request_body_json(
        self,
        stream_state=None,
        stream_slice=None,
        next_page_token=None
    ) -> MutableMapping[str, Any]:
        """
        Constructs the form-encoded body for the POST request.
        """
        query = {
            "terms": [],
            "count": self.record_count,
            "offset": next_page_token.get("offset", 0) if next_page_token else 0,
            "fields": self.get_fields(),
            "sort_by": "display_name",
            "sort_order": "ASC",
            "scope": "all",
        }
        data = {
            "query": json.dumps(query)
        }

        return data

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        """
        Returns the headers required for making requests.
        """
        headers = super().request_headers(**kwargs)  # Inherit default headers from HttpStream
        headers["Content-Type"] = "application/json"  # Add custom header
        return headers

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Handles pagination based on the API response.
        """
        total_hits = response.json().get("response", {}).get("stats", {}).get("total_hits", 0)
        current_offset = response.json().get("response", {}).get("accounts", {}).get("offset", 0)
        count = self.record_count

        if current_offset + count < total_hits:
            return {"offset": current_offset + count}
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parses the API response to yield individual records.
        """
        accounts = response.json().get("response", {}).get("accounts", {}).get("hits", [])
        fields = self.get_fields()
        for account in accounts:
            selected_fields = account.get("selected_fields", [])
            yield_dict = {}
            account_id = account.get('name')
            yield_dict["account_id"] = account_id

            yield_dict["account_name"] = account.get("display_name")
            for field, value in zip(fields, selected_fields):
                # had to skip account_name and account_id as they are already added to the yield_dict
                if field.get("attribute") == "account_name" or field.get("attribute") == "account_id":
                    continue
                if "attribute" in field:
                    yield_dict[field.get("attribute")] = value
                else:
                    yield_dict[field.get("field_display_name")] = value

            yield yield_dict


class Tasks(HttpSubStream, TotangoStream):
    primary_key = "id"
    record_count = 1000

    def __init__(self, parent: Account, **kwargs):
        super().__init__(parent=parent, **kwargs)

    @property
    def http_method(self) -> str:
        """Returns the HTTP method to use for requests."""
        return "GET"

    @property
    def cache_filename(self):
        return "tasks.yml"
    
    @property
    def use_cache(self):
        return True

    @property
    def name(self):
        return "tasks"

    def path(self, stream_state=None, stream_slice=None, next_page_token=None) -> str:
        """
        Returns the endpoint path for this stream.
        """
        account_id = stream_slice["account_id"]
        return f"/api/v2/events?account_id={account_id}"

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Returns the stream slices for this stream.
        """
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh,
            cursor_field=cursor_field,
            stream_state=stream_state
        )
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
                stream_slice=stream_slice,
                stream_state=stream_state
            )
            for record in parent_records:
                yield {"account_id": record.get("account_id")}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parses the API response to yield individual records.
        """
        response_json = response.json()

        for task in response_json:
            yield task

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Handles pagination based on the API response.
        """
        return None


class SourceTotango(AbstractSource):
    logger = logging.getLogger("SourceTotango")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check connection and handle token rotation.
        """
        self.logger.info("Checking connection...")
        authenticator = TotangoAuthenticator(config['credentials'])

        try:
            url = f"{_TOTANGO_URL_BASE}/api/v1/users/whoami"
            response = requests.get(url, auth=authenticator)

            self.logger.info(f"Connection check response: {response.text}")

            if response.status_code == 200:
                return True, None
            else:
                return False, f"Failed to connect to API: {response.text}"
        except Exception as e:
            self.logger.error(f"Error during connection check: {str(e)}")
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Define streams for this source.
        """
        authenticator = TotangoAuthenticator(config["credentials"])

        return [
            Account(authenticator=authenticator, config=config),
            Tasks(parent=Account(
                authenticator=authenticator, config=config),
                authenticator=authenticator
            )
        ]
