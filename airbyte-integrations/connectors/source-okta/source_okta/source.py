#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import parse

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class OktaStream(HttpStream, ABC):
    page_size = 200

    def __init__(self, url_base: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject custom url base to the stream
        self._url_base = url_base.rstrip("/") + "/"

    @property
    def url_base(self) -> str:
        return self._url_base

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Follow the next page cursor
        # https://developer.okta.com/docs/reference/api-overview/#pagination
        links = response.links
        if "next" in links:
            next_url = links["next"]["url"]
            parsed_link = parse.urlparse(next_url)
            query_params = dict(parse.parse_qsl(parsed_link.query))

            # Typically, the absence of the "next" link header indicates there are more pages to read
            # However, some streams contain the "next" link header even when there are no more pages to read
            # See https://developer.okta.com/docs/reference/api-overview/#link-header
            if "self" in links:
                if links["self"]["url"] == next_url:
                    return None

            return query_params

        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "limit": self.page_size,
            **(next_page_token or {}),
        }

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping]:
        yield from response.json()

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # The rate limit resets on the timestamp indicated
        # https://developer.okta.com/docs/reference/rate-limits
        if response.status_code == requests.codes.TOO_MANY_REQUESTS:
            next_reset_epoch = int(response.headers["x-rate-limit-reset"])
            next_reset = pendulum.from_timestamp(next_reset_epoch)
            next_reset_duration = pendulum.utcnow().diff(next_reset)
            return next_reset_duration.seconds


class IncrementalOktaStream(OktaStream, ABC):
    @property
    @abstractmethod
    def cursor_field(self) -> str:
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        lowest_date = str(pendulum.datetime.min)
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field, lowest_date),
                current_stream_state.get(self.cursor_field, lowest_date),
            )
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        params = super().request_params(stream_state, stream_slice, next_page_token)
        latest_entry = stream_state.get(self.cursor_field)
        if latest_entry:
            params["filter"] = f'{self.cursor_field} gt "{latest_entry}"'
        return params


class Groups(IncrementalOktaStream):
    cursor_field = "lastUpdated"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "groups"


class Logs(IncrementalOktaStream):

    cursor_field = "published"
    primary_key = "uuid"

    def path(self, **kwargs) -> str:
        return "logs"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The log stream use a different params to get data
        # https://developer.okta.com/docs/reference/api/system-log/#datetime-filter
        stream_state = stream_state or {}
        params = {
            "limit": self.page_size,
            **(next_page_token or {}),
        }
        latest_entry = stream_state.get(self.cursor_field)
        if latest_entry:
            params["since"] = latest_entry
        return params


class Users(IncrementalOktaStream):
    cursor_field = "lastUpdated"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"


class SourceOkta(AbstractSource):
    def initialize_authenticator(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        return TokenAuthenticator(config["token"], auth_method="SSWS")

    def get_url_base(self, config: Mapping[str, Any]) -> str:
        return parse.urljoin(config["base_url"], "/api/v1/")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = self.initialize_authenticator(config)
            base_url = self.get_url_base(config)
            url = parse.urljoin(base_url, "users")

            response = requests.get(
                url,
                params={"limit": 1},
                headers=auth.get_auth_header(),
            )

            if response.status_code == requests.codes.ok:
                return True, None

            return False, response.json()
        except Exception:
            return False, "Failed to authenticate with the provided credentials"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.initialize_authenticator(config)
        url_base = self.get_url_base(config)

        initialization_params = {
            "authenticator": auth,
            "url_base": url_base,
        }

        return [
            Groups(**initialization_params),
            Logs(**initialization_params),
            Users(**initialization_params),
        ]
