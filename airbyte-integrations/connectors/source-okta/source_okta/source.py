#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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

from .utils import datetime_to_string, delete_milliseconds, get_api_endpoint, get_start_date, initialize_authenticator


class OktaStream(HttpStream, ABC):
    page_size = 200

    def __init__(self, url_base: str, start_date: pendulum.datetime, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject custom url base to the stream
        self._url_base = url_base.rstrip("/") + "/"
        self.start_date = start_date

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

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if isinstance(response_json, list):
            for record in response_json:
                yield self.transform(record=record, **kwargs)
        else:
            yield self.transform(record=response_json, **kwargs)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return record

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # The rate limit resets on the timestamp indicated
        # https://developer.okta.com/docs/reference/rate-limits
        if response.status_code == requests.codes.TOO_MANY_REQUESTS:
            next_reset_epoch = int(response.headers["x-rate-limit-reset"])
            next_reset = pendulum.from_timestamp(next_reset_epoch)
            next_reset_duration = pendulum.utcnow().diff(next_reset)
            return next_reset_duration.seconds


class IncrementalOktaStream(OktaStream, ABC):
    min_id = ""

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        pass

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        min_cursor_value = self.min_id if self.min_id else str(pendulum.datetime.min)
        return {
            self.cursor_field: max(
                latest_record.get(self.cursor_field, min_cursor_value),
                current_stream_state.get(self.cursor_field, min_cursor_value),
            )
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        latest_entry = stream_state.get(self.cursor_field) if stream_state else datetime_to_string(self.start_date)
        filter_param = {"filter": f'{self.cursor_field} gt "{latest_entry}"'}
        params.update(filter_param)
        return params


class Groups(IncrementalOktaStream):
    cursor_field = "lastUpdated"
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "groups"


class GroupMembers(OktaStream):
    cursor_field = "id"
    primary_key = ["groupId", "id"]
    use_cache = True
    min_id = "00u00000000000000000"

    def stream_slices(self, **kwargs):
        group_stream = Groups(authenticator=self.authenticator, url_base=self.url_base, start_date=self.start_date)
        for group in group_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"group_id": group["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        group_id = stream_slice["group_id"]
        return f"groups/{group_id}/users"

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["groupId"] = stream_slice["group_id"]
        return record


class GroupRoleAssignments(OktaStream):
    primary_key = ["groupId", "id"]
    use_cache = True

    def stream_slices(self, **kwargs):
        group_stream = Groups(authenticator=self.authenticator, url_base=self.url_base, start_date=self.start_date)
        for group in group_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"group_id": group["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        group_id = stream_slice["group_id"]
        return f"groups/{group_id}/roles"

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["groupId"] = stream_slice["group_id"]
        return record


class Logs(IncrementalOktaStream):

    cursor_field = "published"
    primary_key = "uuid"

    def __init__(self, url_base, **kwargs):
        super().__init__(url_base=url_base, **kwargs)
        self._raise_on_http_errors: bool = True

    @property
    def raise_on_http_errors(self) -> bool:
        return self._raise_on_http_errors

    def should_retry(self, response: requests.Response) -> bool:
        """
        When the connector gets abnormal state API retrun errror with 400 status code
        and internal error code E0000001. The connector ignores an error with 400 code
        to finish successfully sync and inform the user about an error in logs with an
        error message.
        """

        if response.status_code == 400 and response.json().get("errorCode") == "E0000001":
            self.logger.info(f"{response.json()['errorSummary']}")
            self._raise_on_http_errors = False
            return False
        return HttpStream.should_retry(self, response)

    def path(self, **kwargs) -> str:
        return "logs"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The log stream use a different params to get data.
        # Docs: https://developer.okta.com/docs/reference/api/system-log/#datetime-filter
        # Filter param should be ignored SCIM filter expressions can't use the published
        # attribute since it may conflict with the logic of the since, after, and until query params.
        # Docs: https://developer.okta.com/docs/reference/api/system-log/#expression-filter
        params = super(IncrementalOktaStream, self).request_params(stream_state, stream_slice, next_page_token)
        latest_entry = stream_state.get(self.cursor_field) if stream_state else self.start_date
        params["since"] = latest_entry
        return params

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping]:
        data = response.json() if isinstance(response.json(), list) else []

        for record in data:
            record[self.cursor_field] = delete_milliseconds(record[self.cursor_field])
            yield record


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


class ResourceSets(OktaStream):
    primary_key = "id"
    min_id = "iam00000000000000000"

    def path(self, **kwargs) -> str:
        return "iam/resource-sets"

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping]:
        yield from response.json()["resource-sets"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # We can't follow the default pagination that takes query from header.links
        # Instead, the payload contains _links that offers the next link
        body = response.json()
        if "_links" in body and "next" in body["_links"] and "href" in body["_links"]["next"]:
            next_url = body["_links"]["next"]["href"]
            parsed_link = parse.urlparse(next_url)
            return dict(parse.parse_qsl(parsed_link.query))

        return None


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
    primary_key = ["userId", "id"]
    use_cache = True

    def stream_slices(self, **kwargs):
        user_stream = Users(authenticator=self.authenticator, url_base=self.url_base, start_date=self.start_date)
        for user in user_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"user_id": user["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        user_id = stream_slice["user_id"]
        return f"users/{user_id}/roles"

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["userId"] = stream_slice["user_id"]
        return record


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
        custom_roles = CustomRoles(authenticator=self.authenticator, url_base=self.url_base, start_date=self.start_date)
        for role in custom_roles.read_records(sync_mode=SyncMode.full_refresh):
            yield {"role_id": role["id"]}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        role_id = stream_slice["role_id"]
        return f"iam/roles/{role_id}/permissions"


class SourceOkta(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = initialize_authenticator(config)
            api_endpoint = get_api_endpoint(config)
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
        auth = initialize_authenticator(config)
        api_endpoint = get_api_endpoint(config)
        start_date = get_start_date(config)

        initialization_params = {"authenticator": auth, "url_base": api_endpoint, "start_date": start_date}

        return [
            Groups(**initialization_params),
            Logs(**initialization_params),
            Users(**initialization_params),
            GroupMembers(**initialization_params),
            CustomRoles(**initialization_params),
            UserRoleAssignments(**initialization_params),
            GroupRoleAssignments(**initialization_params),
            Permissions(**initialization_params),
            ResourceSets(**initialization_params),
        ]
