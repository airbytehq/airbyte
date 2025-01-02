#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import time
import json
import logging
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


class TotangoStream(HttpStream, ABC):
    # Base URL for the Totango API
    url_base = "https://api-gw-us.totango.com"

class TotangoAuthenticator(Oauth2Authenticator):
    """
    Custom Authenticator that handles token validation, refresh, and rotation.
    """
    url_base = "https://api-gw-us.totango.com"
    token_url = f"{url_base}/oauth/token"

    def __init__(self, config: Mapping[str, Any]):
        if not config.get("client_id") or not config.get("client_secret"):
            raise ValueError("Client ID or secret is missing in the configuration.")

        super().__init__(
            token_refresh_endpoint=self.token_url,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )
        self.config = config
        self.logger = logging.getLogger("TotangoAuthenticator")

    def is_token_expired(self) -> bool:
        """
        Check if the access token is expired based on the current time and expiry time.

        TODO: can check if the access token is getting expired within 3 hours, refresh the token
        """
        current_time =  int(time.time() * 1000)
        access_token_expiry = self.config.get("access_token_expiry", 0)
        expired = current_time >= access_token_expiry
        self.logger.info(f"Checking if token is expired. Current time: {current_time}, Expiry: {access_token_expiry}, Expired: {expired}")
        return expired

    def refresh_access_token(self) -> str:
        """
        Refresh the access token and update the config with the new token and expiry times.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "refresh_token": self.config["refresh_token"],
            "grant_type": "refresh_token",
        }

        response = requests.post(self.token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_data = response.json()
            self.config["access_token"] = token_data["access_token"]
            self.config["access_token_expiry"] = token_data["access_token_expiration"]
            self.config["refresh_token"] = token_data["refresh_token"]
            self.config["refresh_token_expiry"] = token_data["refresh_token_expiration"]
            self.logger.info("Access token and refresh token updated successfully.")
            return self.config["access_token"]
        else:
            self.logger.error(f"Failed to refresh access token: {response.text}")
            response.raise_for_status()

    def get_access_token(self) -> str:
        """
        Get the current valid access token or refresh it if expired.
        """
        if self.is_token_expired():
            self.logger.info("Access token expired. Refreshing token...")
            return self.refresh_access_token()
        self.logger.info("Using existing access token.")
        return self.config["access_token"]
    
    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        """
        Returns the headers required for making requests to the Totango API.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_access_token()}"
        }

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
        """Constructs the form-encoded body for the POST request."""
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
        """Returns the headers required for making requests."""
        headers = super().request_headers(**kwargs)  # Inherit default headers from HttpStream
        headers["Content-Type"] = "application/json"  # Add custom header
        return headers

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Handles pagination based on the API response."""
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
        """Returns the endpoint path for this stream."""
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
        """Handles pagination based on the API response."""
        return None


# Basic incremental stream
class IncrementalTotangoStream(TotangoStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


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

