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

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        return response.json().get("data", {}).get("data")


# Employee
class People(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:

        return "core/people"


# Employee Employment details
class Employments(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/employments"


# Departments
class Departments(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/departments"


# locations
class Locations(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/locations"


# labor_groups
class Labor_groups(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/labor_groups"


# labor_groups_types
class Labor_group_types(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/labor_group_types"


# custom_fields
class Custom_fields(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/custom_fields"


# custom_field_values
class Custom_field_values(ZenefitsStream):

    primary_key = None

    def path(self, **kwargs) -> str:
        return "core/custom_field_values"


# Vacation Requested
class Vacation_requests(ZenefitsStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "time_off/vacation_requests"


# Vacation Types
class Vacation_types(ZenefitsStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "time_off/vacation_types"


# Time Durations
class Time_durations(ZenefitsStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "time_attendance/time_durations"


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
            People(**args),
            Employments(**args),
            Vacation_requests(**args),
            Vacation_types(**args),
            Time_durations(**args),
            Departments(**args),
            Locations(**args),
            Labor_group_types(**args),
            Custom_fields(**args),
            Custom_field_values(**args),
            Labor_groups(**args),
        ]
