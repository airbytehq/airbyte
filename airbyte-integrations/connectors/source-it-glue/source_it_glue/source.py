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
class ItGlueStream(HttpStream, ABC):

    # FIRST_PAGE = 1
    LIMIT = 1000

    # TODO: Fill in the url base. Required.
    url_base = "https://api.itglue.com"

    def __init__(self, api_key: str, fatId: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.fatId = fatId

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {"page[size]": self.LIMIT}
        if next_page_token:
            params = next_page_token
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        results = response.json().get("meta")
        next_page = results.get("next-page")
        if next_page:
            response_json = response.json().get("links")
            next_page_url = response_json.get("next")
            next_url = urlparse(next_page_url)
            next_params = parse_qs(next_url.query)
            return next_params
        return None

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        api_key = self.api_key
        headers = {"x-api-key": f"{api_key}", "Content-Type": "application/vnd.api+json"}
        return headers


class contact_types(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/contact_types"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        contact_types = response.json().get("data")
        return contact_types


class contacts(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/contacts"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        contacts = response.json().get("data")
        return contacts


class countries(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/countries"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        countries = response.json().get("data")
        return countries


class expirations(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/expirations"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        expirations = response.json().get("data")
        return expirations


class groups(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/groups"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        groups = response.json().get("data")
        return groups


class locations(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/locations"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        locations = response.json().get("data")
        return locations


class models(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/models"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        models = response.json().get("data")
        return models


class manufacturers(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/manufacturers"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        manufacturers = response.json().get("data")
        return manufacturers


class operating_systems(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/operating_systems"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        operating_systems = response.json().get("data")
        return operating_systems


class organization_statuses(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/organization_statuses"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        organization_statuses = response.json().get("data")
        return organization_statuses


class organization_types(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/organization_types"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        organization_types = response.json().get("data")
        return organization_types


class platforms(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/platforms"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        platforms = response.json().get("data")
        return platforms


class organizations(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/organizations"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        organizations = response.json().get("data")
        return organizations


class regions(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/regions"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        regions = response.json().get("data")
        return regions


class user_metrics(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/user_metrics"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        user_metrics = response.json().get("data")
        return user_metrics


class users(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/users"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        users = response.json().get("data")
        return users


class configuration_statuses(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/configuration_statuses"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        configuration_statuses = response.json().get("data")
        return configuration_statuses


class configuration_types(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/configuration_types"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        configuration_types = response.json().get("data")
        return configuration_types


# flexible_assets
class flexible_assets(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        fatId = self.fatId
        return f"/flexible_assets?filter[flexible-asset-type-id]={fatId}"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        flexible_assets = response.json().get("data")
        return flexible_assets


class configurations(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/configurations"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        configurations = response.json().get("data")
        return configurations

class domains(ItGlueStream):
    primary_key = None

    def path(self, **kwargs) -> str:
        return "/domains"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:

        domains = response.json().get("data")
        return domains

class SourceItGlue(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        headers = {"x-api-key": config["api_key"], "Content-Type": "application/vnd.api+json"}
        url = "https://api.itglue.com/contact_types"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = {"api_key": config["api_key"], "fatId": config["fatId"]}
        return [
            domains(**args),
            flexible_assets(**args),
            configurations(**args),
            configuration_types(**args),
            configuration_statuses(**args),
            users(**args),
            user_metrics(**args),
            regions(**args),
            platforms(**args),
            organizations(**args),
            organization_types(**args),
            organization_statuses(**args),
            operating_systems(**args),
            models(**args),
            manufacturers(**args),
            locations(**args),
            groups(**args),
            expirations(**args),
            countries(**args),
            contacts(**args),
            contact_types(**args),
        ]
