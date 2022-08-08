#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import parse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator


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


class GroupMembers(IncrementalOktaStream):
    cursor_field = "id"
    primary_key = "id"
    min_user_id = "00u00000000000000000"
    use_cache = True

    def stream_slices(self, **kwargs):
        group_stream = Groups(authenticator=self.authenticator, url_base=self.url_base)
        for group in group_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"group_id": group["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        group_id = stream_slice["group_id"]
        return f"groups/{group_id}/users"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = OktaStream.request_params(self, stream_state, stream_slice, next_page_token)
        latest_entry = stream_state.get(self.cursor_field)
        if latest_entry:
            params["after"] = latest_entry
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field, self.min_user_id),
                current_stream_state.get(self.cursor_field, self.min_user_id),
            )
        }


class GroupRoleAssignments(OktaStream):
    primary_key = "id"
    use_cache = True

    def stream_slices(self, **kwargs):
        group_stream = Groups(authenticator=self.authenticator, url_base=self.url_base)
        for group in group_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"group_id": group["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        group_id = stream_slice["group_id"]
        return f"groups/{group_id}/roles"


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
        params = OktaStream.request_params(self, stream_state, stream_slice, next_page_token)
        latest_entry = stream_state.get(self.cursor_field)
        if latest_entry:
            params["since"] = latest_entry
            # [Test-driven Development] Set until When the cursor value from the stream state
            #   is abnormally large, otherwise the server side that sets now to until
            #   will throw an error: The "until" date must be later than the "since" date
            # https://developer.okta.com/docs/reference/api/system-log/#request-parameters
            parsed = pendulum.parse(latest_entry)
            utc_now = pendulum.utcnow()
            if parsed > utc_now:
                params["until"] = latest_entry

        return params


class Users(IncrementalOktaStream):
    cursor_field = "lastUpdated"
    primary_key = "id"
    # Should add all statuses to filter. Considering Okta documentation https://developer.okta.com/docs/reference/api/users/#list-all-users,
    # users with "DEPROVISIONED" status are not returned by default.
    statuses = ["ACTIVE", "DEPROVISIONED", "LOCKED_OUT", "PASSWORD_EXPIRED", "PROVISIONED", "RECOVERY", "STAGED", "SUSPENDED"]

    def path(self, **kwargs) -> str:
        return "users"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        status_filters = " or ".join([f'status eq "{status}"' for status in self.statuses])
        if "filter" in params:
            # add status_filters to existing filters
            params["filter"] = f'{params["filter"]} and ({status_filters})'
        else:
            params["filter"] = status_filters
        return params


class CustomRoles(OktaStream):
    # https://developer.okta.com/docs/reference/api/roles/#list-roles
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "iam/roles"

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping]:
        yield from response.json()["roles"]


class UserRoleAssignments(OktaStream):
    primary_key = "id"
    use_cache = True

    def stream_slices(self, **kwargs):
        user_stream = Users(authenticator=self.authenticator, url_base=self.url_base)
        for user in user_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"user_id": user["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        user_id = stream_slice["user_id"]
        return f"users/{user_id}/roles"


class Permissions(OktaStream):
    # https://developer.okta.com/docs/reference/api/roles/#list-permissions
    primary_key = "label"
    use_cache = True

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping]:
        yield from response.json()["permissions"]

    def stream_slices(self, **kwargs):
        custom_roles = CustomRoles(authenticator=self.authenticator, url_base=self.url_base)
        for role in custom_roles.read_records(sync_mode=SyncMode.full_refresh):
            yield {"role_id": role["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        role_id = stream_slice["role_id"]
        return f"iam/roles/{role_id}/permissions"


class OktaOauth2Authenticator(Oauth2Authenticator):
    def get_refresh_request_body(self) -> Mapping[str, Any]:
        return {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def refresh_access_token(self) -> Tuple[str, int]:
        try:
            response = requests.request(
                method="POST",
                url=self.token_refresh_endpoint,
                data=self.get_refresh_request_body(),
                auth=(self.client_id, self.client_secret),
            )
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
            raise Exception("Config validation error. `credentials` not specified.")

        auth_type = creds.get("auth_type")
        if not auth_type:
            raise Exception("Config validation error. `auth_type` not specified.")

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
            return False, "Failed to authenticate with the provided credentials"

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
            GroupMembers(**initialization_params),
            CustomRoles(**initialization_params),
            UserRoleAssignments(**initialization_params),
            GroupRoleAssignments(**initialization_params),
            Permissions(**initialization_params),
        ]
