#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
# Assignments
class Assignments(HttpStream):

    url_base = "https://api.primetric.com/beta/"
    primary_key = "uuid"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_url = response.json()["next"]
        return parse_qs(urlparse(next_page_url).query)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["results"]

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "assignments"


# Basic full refresh stream
# Employees
class Employees(HttpStream):

    url_base = "https://api.primetric.com/beta/"
    primary_key = "uuid"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_url = response.json()["next"]
        return parse_qs(urlparse(next_page_url).query)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["results"]

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "employees"


# Basic full refresh stream
# Projects
class Projects(HttpStream):

    url_base = "https://api.primetric.com/beta/"
    primary_key = "uuid"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page_url = response.json()["next"]
        return parse_qs(urlparse(next_page_url).query)

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["results"]

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "projects"


# Source
class SourcePrimetric(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:

            if not config["client_secret"] or not config["client_id"]:
                raise Exception("Empty config values! Check your configuration file!")

            token_refresh_endpoint = f"https://api.primetric.com/auth/token/"
            client_id = config["client_id"]
            client_secret = config["client_secret"]
            refresh_token=None
            headers = {"content-type": "application/x-www-form-urlencoded"}
            data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}

            try:
                response = requests.request(
                    method="POST",
                    url=token_refresh_endpoint,
                    data=data,
                    headers=headers
                )
                response.json()
                print (response.json()["access_token"], response.json()["expires_in"])

            except Exception as e:
                raise Exception(f"Error while refreshing access token: {e}") from e

            return True, None

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        token_refresh_endpoint = f"https://api.primetric.com/auth/token/"
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        refresh_token=None
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}

        try:
            response = requests.request(
                method="POST",
                url=token_refresh_endpoint,
                data=data,
                headers=headers
            )
            response.json()

            authenticator = TokenAuthenticator(response.json()["access_token"])

            return [Assignments(authenticator=authenticator),
                    Employees(authenticator=authenticator),
                    Projects(authenticator=authenticator)]

        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
