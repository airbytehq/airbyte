#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import parse

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator, Oauth2Authenticator


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


class OktaOauth2Authenticator(Oauth2Authenticator):
    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body(),
                                        auth=(self.client_id, self.client_secret))
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourceOkta(AbstractSource):
    def initialize_authenticator(self, config: Mapping[str, Any]):
        if "token" in config:
            return TokenAuthenticator(config["token"], auth_method="SSWS")

        creds = config.get("credentials")
        if not creds:
            raise "Config validation error. `credentials` not specified."

        auth_type = creds.get("auth_type")
        if not auth_type:
            raise "Config validation error. `auth_type` not specified."

        if auth_type == "api_token":
            return TokenAuthenticator(creds["api_token"], auth_method="SSWS")

        if auth_type == "oauth2.0":
            return OktaOauth2Authenticator(
                token_refresh_endpoint=self.get_token_refresh_endpoint(config),
                client_secret=creds["client_secret"],
                client_id=creds["client_id"],
                refresh_token=creds["refresh_token"],
            )

    @staticmethod
    def get_url_base(config: Mapping[str, Any]) -> str:
        return config.get("base_url") or f"https://{config['domain']}.okta.com"

    def get_api_endpoint(self, config: Mapping[str, Any]) -> str:
        return parse.urljoin(self.get_url_base(config), "/api/v1/")

    def get_token_refresh_endpoint(self, config: Mapping[str, Any]) -> str:
        return parse.urljoin(self.get_url_base(config), "/oauth2/v1/token")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = self.initialize_authenticator(config)
            api_endpoint = self.get_api_endpoint(config)
            url = parse.urljoin(api_endpoint, "users")

            response = requests.get(
                url,
                params={"limit": 1},
                headers=auth.get_auth_header(),
            )

            if response.status_code == requests.codes.ok:
                return True, None

            return False, response.json()
        except Exception:
            import traceback
            return False, traceback.format_exc()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.initialize_authenticator(config)
        api_endpoint = self.get_api_endpoint(config)

        initialization_params = {
            "authenticator": auth,
            "url_base": api_endpoint,
        }

        return [
            Groups(**initialization_params),
            Logs(**initialization_params),
            Users(**initialization_params),
        ]
