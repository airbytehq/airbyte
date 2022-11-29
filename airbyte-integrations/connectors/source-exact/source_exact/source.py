#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum
import re

from datetime import datetime, timezone
from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


# Basic full refresh stream
class ExactStream(HttpStream, ABC):
    url_base = "https://start.exactonline.nl/api/v1/3361923/"
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        If response contains the __next property, there are more pages. This property contains the full url to 
        call next including endpoint and all query parameters.
        """

        response_json = response.json()
        next_url = response_json.get("d", {}).get("__next")
        return {
            "next_url": next_url
        }


    def request_headers(self, **kwargs) -> MutableMapping[str, Any]:
        """
        Default response type is XML, this is overriden to return JSON.
        """

        return {
            "Accept": "application/json"
        }

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
        Exact returns timestamps in following format: /Date(1672531200000)/
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
    endpoint = "subscription/Subscriptions"


# # Basic incremental stream
# class IncrementalExactStream(ExactStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}


# class Employees(IncrementalExactStream):
#     """
#     TODO: Change class name to match the table/data source this stream corresponds to.
#     """

#     # TODO: Fill in the cursor_field. Required.
#     cursor_field = "start_date"

#     # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
#     primary_key = "employee_id"

#     def path(self, **kwargs) -> str:
#         """
#         TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
#         return "single". Required.
#         """
#         return "employees"

#     def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
#         """
#         TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

#         Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
#         This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
#         section of the docs for more information.

#         The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
#         necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
#         This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

#         An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
#         craft that specific request.

#         For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
#         this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
#         till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
#         the date query param.
#         """
#         raise NotImplementedError("Implement stream slices or delete this method!")


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
