#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
import time
import json
import logging
import requests
import dpath
import pendulum
from airbyte_cdk.models import SyncMode, FailureType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator, TokenAuthenticator
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets

class TotangoStream(HttpStream, ABC):
    # Base URL for the Totango API
    url_base = "https://api-gw-us.totango.com"

class TotangoOAuth(SingleUseRefreshTokenOauth2Authenticator):
    def build_refresh_request_headers(self) -> Mapping[str, Any]:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        return {
            "grant_type": "refresh_token",
            "refresh_token": self.get_refresh_token(),
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret()
        }

    def _get_refresh_access_token_response(self) -> Mapping[str, Any]:
        response = requests.post(
            url=self.get_token_refresh_endpoint(),
            data=self.build_refresh_request_body(),
            headers=self.build_refresh_request_headers(),
        )
        content = response.json()
        content["access_token_expiration"] = str(content["access_token_expiration"])

        if response.status_code == 400 and content.get("error") == "invalid_grant":
            raise AirbyteTracedException(
                internal_message=content.get("error_description"),
                message="Refresh token is invalid or expired. Please re-authenticate to restore access to Totango.",
                failure_type=FailureType.config_error,
            )

        response.raise_for_status()
        return content

    @staticmethod
    def get_new_token_expiry_date(access_token_expires_in: str, token_expiry_date_format: str = None) -> pendulum.DateTime:
        # Convert millisecond timestamp to seconds and return the parsed date
        timestamp = int(access_token_expires_in) / 1000
        return pendulum.from_timestamp(timestamp)

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        """
        Returns the headers required for making requests to the Totango API.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_access_token()}"
        }
    
    def get_token_expiry_date(self) -> pendulum.DateTime:
        expiry_date = dpath.util.get(self._connector_config, self._token_expiry_date_config_path, default="")
        expiry_date_seconds = int(expiry_date) / 1000
        return pendulum.from_timestamp(expiry_date_seconds)


class TotangoAuthenticator:
    url_base = "https://api-gw-us.totango.com"
    token_url = f"{url_base}/oauth/token"

    def __new__(self, config: dict) -> Union[TokenAuthenticator, TotangoOAuth]:
        return TotangoOAuth(
            connector_config=config,
            token_refresh_endpoint=self.token_url,
            access_token_name="access_token",
            expires_in_name="access_token_expiration",
            refresh_token_name="refresh_token",
            token_expiry_date_config_path=("credentials", "access_token_expiration"),
            token_expiry_date_format=None,
            token_expiry_is_time_of_expiration=True)


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

    def __init__(self, authenticator: TotangoAuthenticator):
        super().__init__(authenticator=authenticator)  # Pass authenticator to the parent class

    @property
    def http_method(self) -> str:
        """
        Returns the HTTP method to use for requests.
        """
        return "POST"

    def path(self, stream_state=None, stream_slice=None, next_page_token=None) -> str:
        """Returns the endpoint path for this stream."""
        return "/api/v1/search/accounts"

    def get_fields(self):
        """
        Returns the fields for the API response.
        """
        schema = self.get_json_schema()
        fields = []

        for field_name, field_details in schema["properties"].items():
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
        return fields

    def request_body_json(self, stream_state=None, stream_slice=None, next_page_token=None) ->  MutableMapping[str, Any]:
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

    def stream_slices(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
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
    url_base = "https://api-gw-us.totango.com"

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check connection and handle token rotation.
        """
        self.logger.info("Checking connection...")
        authenticator = TotangoAuthenticator(config)

        try:
            access_token = authenticator.get_access_token()
            self.logger.info(f"Access token used for connection check: {access_token}")

            url = f"{self.url_base}/api/v1/users/whoami"
            response = requests.get(url, headers=authenticator.request_headers())

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
        authenticator = TotangoAuthenticator(config)

        return [Account(authenticator=authenticator), Tasks(parent=Account(authenticator=authenticator), authenticator=authenticator)]

