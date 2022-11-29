#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum
import re

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


class SingleRefreshOauth2Authenticator(Oauth2Authenticator):
    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns the refresh token and its lifespan in seconds

        :return: a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.post(
                url=self.get_token_refresh_endpoint(),
                data=self.build_refresh_request_body(),

            )
            response_json = response.json()
            print(response_json)
            response.raise_for_status()

            self._refresh_token = response_json["refresh_token"]

            return response_json[self.get_access_token_name()], response_json[self.get_expires_in_name()]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class ExactStream(HttpStream, IncrementalMixin):
    url_base = "https://start.exactonline.nl/api/v1/3361923/"
    cursor_field = "Timestamp"
    state_checkpoint_interval = 1000

    _cursor_value = None

    @property
    def state(self) -> MutableMapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        if value:
            self._cursor_value = value[self.cursor_field]

    def read_records(self, *args, **kwargs) -> Iterable[StreamData]:
        for record in super().read_records(*args, **kwargs):
            # Track the largest timestamp value
            timestamp = record[self.cursor_field]
            self._cursor_value = max(timestamp, self._cursor_value) if self._cursor_value else timestamp

            yield record


    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If response contains the __next property, there are more pages. This property contains the full url to 
        call next including endpoint and all query parameters.
        """

        response_json = response.json()
        next_url = response_json.get("d", {}).get("__next")

        return { "next_url": next_url } if next_url else None
        

    def request_headers(self, **kwargs) -> MutableMapping[str, Any]:
        """
        Default response type is XML, this is overriden to return JSON.
        """

        return {
            "Accept": "application/json"
        }

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        The sync endpoints requires selection of fields to return. We use the configured catalog to make selection
        of fields we want to have.
        """

        # Contains the full next page, so don't append new query params
        if next_page_token:
            return {}

        configured_properties = list(self.get_json_schema()["properties"].keys())
        params = {
            "$select": ",".join(configured_properties),
        }

        if self._cursor_value:
            params["$filter"] = f"Timestamp gt {self._cursor_value}L"

        return params


    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Parse the results array from returned object
        response_json = response.json()
        results = response_json.get("d", {}).get("results")

        return [self._parse_timestamps(x) for x in results]
    
    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> str:
        """
        Returns the URL to call. On first call uses the property `endpoint` of subclass. For subsequent
        pages, `next_page_token` is used.
        """

        if not self.endpoint:
            raise RuntimeError("Subclass is missing endpoint")

        if next_page_token:
            return next_page_token["next_url"]

        return self.endpoint

    def _parse_timestamps(self, obj: dict):
        """
        Exact returns timestamps in following format: /Date(1672531200000)/ (OData date format).
        The value is in seconds since Epoch (UNIX time). Note, the time is in CET and not in GMT/UTC.
        https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-faq-rest-api
        """

        regex_timestamp = re.compile(r"^\/Date\((\d+)\)\/$")

        def parse_value(value):
            if isinstance(value, dict):
                return {k: parse_value(v) for k, v in value.items()}

            if isinstance(value, list):
                return [parse_value(v) for v in value]

            if isinstance(value, str):
                match = regex_timestamp.match(value)
                if match:
                    unix_seconds = int(match.group(1)) / 1000
                    timestamp = pendulum.from_timestamp(unix_seconds, "CET").set(tz="UTC")

                    return timestamp.isoformat()

            return value

        return {k: parse_value(v) for k, v in obj.items()}



class Subscriptions(ExactStream):
    primary_key = "EntryID"
    endpoint = "sync/subscription/Subscriptions"



# Source
class SourceExact(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        token_endpoint = "https://start.exactonline.nl/api/oauth2/token"

        print(config)

        access_token = config.get('access_token')
        refresh_token = config.get('refresh_token')
        if not access_token or not refresh_token:
            resp = requests.post(
                token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "redirect_uri": "https://auth.intern.gynzy.net/_oauth/",
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code": config["code"],
                },
                headers={
                    "Accept": "application/json",
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )

            response_json = resp.json()
            if resp.status_code != 200:
                # Yield more user friendly error message
                error_description = response_json.get("error_description")
                if error_description:
                    if 'The message expired at' in response_json.get("error_description"):
                        raise RuntimeError("Discovery failed: the code is expired. Create a new code by initiating the OAuth flow manually.")
                    if 'This message has already been processed' in response_json.get("error_description"):
                        raise RuntimeError("Discovery failed: the code is already used. Create a new code by initiating the OAuth flow manually.")
                    
                    raise RuntimeError(f"Discovery failed: {response_json.get('error_description')}")

                raise RuntimeError(f"Discovery failed: failed to retrieve token\n{response_json}")

            access_token = response_json["access_token"]
            refresh_token = response_json["refresh_token"]

        auth = SingleRefreshOauth2Authenticator(
            token_refresh_endpoint=token_endpoint,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=refresh_token,
            # Hardcoded: access tokens are valid for 10 minutes (from the documentation). Even the first one
            # is subject to rate limit.
            token_expiry_date=pendulum.now().add(minutes=10)
        )
        auth.access_token = access_token

        return [
            Subscriptions(authenticator=auth),
        ]
