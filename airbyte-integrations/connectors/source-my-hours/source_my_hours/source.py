#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_my_hours.auth import MyHoursAuthenticator
from source_my_hours.stream import MyHoursStream

from .constants import REQUEST_HEADERS, URL_BASE


class Clients(MyHoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Clients"


class Projects(MyHoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Projects/getAll"


class Tags(MyHoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Tags"


class TimeLogs(MyHoursStream):
    primary_key = "logId"

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        start_date: str,
        batch_size: int,
        **kwargs,
    ):
        super().__init__(authenticator=authenticator)

        self.start_date = pendulum.parse(start_date)
        self.batch_size = batch_size

        if self.start_date > pendulum.now():
            self.logger.warn(f'Stream {self.name}: start_date "{start_date.isoformat()}" should be before today.')

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Reports/activity"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        previous_query = parse_qs(urlparse(response.request.url).query)
        previous_end = pendulum.parse(previous_query["DateTo"][0])

        new_from = previous_end.add(days=1)
        new_to = new_from.add(days=self.batch_size - 1)

        if new_from > pendulum.now():
            return None

        return {
            "DateFrom": new_from.to_date_string(),
            "DateTo": new_to.to_date_string(),
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        if next_page_token is None:
            return {"DateFrom": self.start_date.to_date_string(), "DateTo": self.start_date.add(days=self.batch_size - 1).to_date_string()}
        return next_page_token


class Users(MyHoursStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "Users/getAll"


# Source
class SourceMyHours(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config) -> Tuple[bool, any]:
        url = f"{URL_BASE}/Clients"

        try:
            authenticator = self._make_authenticator(config)
            headers = authenticator.get_auth_header()
            headers.update(REQUEST_HEADERS)

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._make_authenticator(config)
        return [
            Clients(authenticator=auth),
            Projects(authenticator=auth),
            Tags(authenticator=auth),
            TimeLogs(authenticator=auth, start_date=config["start_date"], batch_size=config["logs_batch_size"]),
            Users(authenticator=auth),
        ]

    @staticmethod
    def _make_authenticator(config) -> MyHoursAuthenticator:
        return MyHoursAuthenticator(config["email"], config["password"])
