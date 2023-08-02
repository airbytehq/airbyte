#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib import parse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_auth0.utils import get_api_endpoint, initialize_authenticator


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record


# Basic full refresh stream
class Auth0Stream(HttpStream, ABC):
    api_version = "v2"
    page_size = 50
    resource_name = "entities"

    def __init__(self, url_base: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_endpoint = get_api_endpoint(url_base, self.api_version)

    def path(self, **kwargs) -> str:
        return self.resource_name

    @property
    def url_base(self) -> str:
        return self.api_endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        body = response.json()
        if "total" in body and "start" in body and "limit" in body and "length" in body:
            try:
                start = int(body["start"])
                limit = int(body["limit"])
                length = int(body["length"])
                total = int(body["total"])
                current = start // limit
                if length < limit or (start + length) == total:
                    return None
                else:
                    token = {
                        "page": current + 1,
                        "per_page": limit,
                    }
                    return token
            except Exception:
                return None
        else:
            if not body or len(body) < self.page_size:
                return None
            else:
                return {
                    "page": 0,
                    "per_page": self.page_size,
                }

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        return {
            "page": 0,
            "per_page": self.page_size,
            "include_totals": "true",
            **(next_page_token or {}),
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get(self.resource_name)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # The rate limit resets on the timestamp indicated
        # https://auth0.com/docs/troubleshoot/customer-support/operational-policies/rate-limit-policy/management-api-endpoint-rate-limits
        if response.status_code == requests.codes.TOO_MANY_REQUESTS:
            next_reset_epoch = int(response.headers["x-ratelimit-reset"])
            next_reset = pendulum.from_timestamp(next_reset_epoch)
            next_reset_duration = pendulum.now("UTC").diff(next_reset)
            return next_reset_duration.seconds


class IncrementalAuth0Stream(Auth0Stream, IncrementalMixin):
    min_id = ""
    cursor_field = "updated_at"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cursor_value = None

    @property
    def state(self) -> MutableMapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self.min_id}

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        new_state_value = max(latest_record.get(self.cursor_field), current_stream_state.get(self.cursor_field, self.min_id))
        self._cursor_value = new_state_value
        return {self.cursor_field: new_state_value}

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=self.state, next_page_token=next_page_token, **kwargs)
        filter_param = {"include_totals": "false", "sort": f"{self.cursor_field}:1"}
        if self.state:
            filter_param["q"] = self.cursor_field + ":{" + self.state.get(self.cursor_field) + " TO *]"
        params.update(filter_param)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        entities = response.json()
        yield from entities


class Clients(Auth0Stream):
    primary_key = "client_id"
    resource_name = "clients"


class Users(IncrementalAuth0Stream):
    min_id = "1900-01-01T00:00:00.000Z"
    primary_key = "user_id"
    resource_name = "users"
    cursor_field = "updated_at"


class Organizations(Auth0Stream):
    primary_key = "id"
    resource_name = "organizations"


class OrganizationMembers(Auth0Stream):
    primary_key = "id"
    resource_name = "members"

    def __init__(self, url_base: str, *args, **kwargs):
        super().__init__(url_base=url_base, *args, **kwargs)
        self.organizations = Organizations(url_base=url_base, *args, **kwargs)

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for org in read_full_refresh(self.organizations):
            for member in super().read_records(stream_slice={"organization_id": org["id"]}, **kwargs):
                yield member

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"organizations/{stream_slice['organization_id']}/members"

    def parse_response(self, response: requests.Response, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping]:
        record = response.json().get(self.resource_name)
        for r in record:
            r["org_id"] = stream_slice["organization_id"]
            r["id"] = stream_slice["organization_id"] + "_" + r["user_id"]
            yield r


class OrganizationMemberRoles(Auth0Stream):
    primary_key = "id"
    resource_name = "roles"

    def __init__(self, url_base: str, *args, **kwargs):
        super().__init__(url_base=url_base, *args, **kwargs)
        self.organization_members = OrganizationMembers(url_base=url_base, *args, **kwargs)

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        return f"organizations/{stream_slice['organization_id']}/members/{stream_slice['user_id']}/roles"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        for org_member in read_full_refresh(self.organization_members):
            for role in super().read_records(
                stream_slice={"organization_id": org_member["org_id"], "user_id": org_member["user_id"]}, **kwargs
            ):
                yield role

    def parse_response(self, response: requests.Response, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping]:
        record = response.json().get(self.resource_name)
        for r in record:
            r["org_id"] = stream_slice["organization_id"]
            r["user_id"] = stream_slice["user_id"]
            yield r


# Source
class SourceAuth0(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            auth = initialize_authenticator(config)
            api_endpoint = get_api_endpoint(config.get("base_url"), "v2")
            url = parse.urljoin(api_endpoint, "users")
            response = requests.get(
                url,
                params={"per_page": 1},
                headers=auth.get_auth_header(),
            )

            if response.status_code == requests.codes.ok:
                return True, None

            return False, response.json()
        except Exception:
            return False, "Failed to authenticate with the provided credentials"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        initialization_params = {"authenticator": initialize_authenticator(config), "url_base": config.get("base_url")}
        return [
            Clients(**initialization_params),
            Organizations(**initialization_params),
            OrganizationMembers(**initialization_params),
            OrganizationMemberRoles(**initialization_params),
            Users(**initialization_params),
        ]
