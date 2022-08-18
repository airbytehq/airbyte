#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class ZenefitsStream(HttpStream, ABC):
    LIMIT = 100

    url_base = "https://api.zenefits.com/"

    def __init__(self, token: str, **kwargs):
        super().__init__(**kwargs)
        self.token = token

    def request_params(
        self, stream_state: Mapping[str, any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"limit": self.LIMIT}
        if next_page_token:
            params = next_page_token
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "Accept": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json().get("data")
        next_page_url = response_json.get("next_url")
        if next_page_url:
            next_url = urlparse(next_page_url)
            next_params = parse_qs(next_url.query)
            return next_params

        return None


# Employee
class people(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:

        return "core/people"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        people_response = response.json().get("data")
        presponse = people_response.get("data")
        return presponse


# Employee Employment details
class employments(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/employments"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        employments_response = response.json().get("data")
        eresponse = employments_response.get("data")
        return eresponse


# Departments
class departments(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/departments"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        departments_response = response.json().get("data")
        dresponse = departments_response.get("data")
        return dresponse


# locations
class locations(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/locations"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        locations_response = response.json().get("data")
        lresponse = locations_response.get("data")
        return lresponse


# labor_groups
class labor_groups(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/labor_groups"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        labor_response = response.json().get("data")
        labor_groups_response = labor_response.get("data")
        return labor_groups_response


# labor_groups_types
class labor_group_types(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/labor_group_types"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        labor_groups_types = response.json().get("data")
        lt_response = labor_groups_types.get("data")
        return lt_response


# custom_fields
class custom_fields(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/custom_fields"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        custom_fields = response.json().get("data")
        cfresponse = custom_fields.get("data")
        return cfresponse


# custom_field_values
class custom_field_values(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/custom_field_values"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        custom_field_values = response.json().get("data")
        cfv_response = custom_field_values.get("data")
        return cfv_response


# Vacation Requested
class vacation_requests(ZenefitsStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "time_off/vacation_requests"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        vac_requests = response.json().get("data")
        vac_requests_data = vac_requests.get("data")
        return vac_requests_data


# Vacation Types
class vacation_types(ZenefitsStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "time_off/vacation_types"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        vac_types = response.json().get("data")
        vac_types_data = vac_types.get("data")
        return vac_types_data


# Time Durations
class time_durations(ZenefitsStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "time_attendance/time_durations"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        time_duration = response.json().get("data")
        time_duration_data = time_duration.get("data")
        return time_duration_data


class SourceZenefits(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        token = config["token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
        url = "https://api.zenefits.com/core/people"

        try:
            session = requests.get(url, headers=headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {"token": config["token"]}
        return [
            people(**args),
            employments(**args),
            vacation_requests(**args),
            vacation_types(**args),
            time_durations(**args),
            departments(**args),
            locations(**args),
            labor_group_types(**args),
            custom_fields(**args),
            custom_field_values(**args),
            labor_groups(**args),
        ]
