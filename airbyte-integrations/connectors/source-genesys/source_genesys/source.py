#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_genesys.authenicator import GenesysOAuthAuthenticator


class GenesysStream(HttpStream, ABC):
    page_size = 500

    @property
    def url_base(self):
        if self._api_base_url is not None:
            return self._api_base_url + "/api/v2/"
        return None

    def __init__(self, api_base_url, *args, **kwargs):
        self._api_base_url = api_base_url
        super().__init__(*args, **kwargs)

    def backoff_time(self, response: requests.Response) -> Optional[int]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()

        if response_json.get("nextUri"):
            next_query_string = urllib.parse.urlsplit(response_json.get("nextUri")).query
            return dict(urllib.parse.parse_qsl(next_query_string))

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"pageSize": self.page_size}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        yield from json_response.get("entities", [])


class RoutingOutboundEvents(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/routing/routing/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "routing/assessments"


class RoutingRoutingAssessments(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/routing/routing/
    """

    page_size = 200
    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "routing/assessments"


class RoutingRoutingQueues(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/routing/routing/
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "routing/queues"


class TelephonyLocations(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/locations-apis
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "locations"


class TelephonyProvidersEdges(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges"


class TelephonyProvidersEdgesDids(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/dids"


class TelephonyProvidersEdgesDidpools(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/didpools"


class TelephonyProvidersEdgesExtensions(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/extensions"


class TelephonyProvidersEdgesLines(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/lines"


class TelephonyProvidersEdgesOutboundroutes(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/outboundroutes"


class TelephonyProvidersEdgesPhones(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/phones"


class TelephonyProvidersEdgesSites(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/sites"


class TelephonyProvidersEdgesTrunks(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/trunks"


class TelephonyStations(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/telephony/stations-apis
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "stations"


class UserUsers(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/useragentman/users/
    """

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "users"


class UserGroups(GenesysStream):
    """
    API Docs: https://developer.genesys.cloud/useragentman/groups/
    """

    primary_key = "id"
    cursor_field = "dateModified"

    def path(self, **kwargs) -> str:
        return "groups"


class SourceGenesys(AbstractSource):
    def build_refresh_request_body(self) -> Mapping[str, Any]:
        return {
            "grant_type": "client_credentials",
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
        }

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement true connection checks using an endpoint that is always live
        Testing connection availability for the connector by granting the credentials.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        GENESYS_REGION_DOMAIN_MAP: Dict[str, str] = {
            "Americas (US East)": "mypurecloud.com",
            "Americas (US East 2)": "use2.us-gov-pure.cloud",
            "Americas (US West)": "usw2.pure.cloud",
            "Americas (Canada)": "cac1.pure.cloud",
            "Americas (São Paulo)": "sae1.pure.cloud",
            "EMEA (Frankfurt)": "mypurecloud.de",
            "EMEA (Dublin)": "mypurecloud.ie",
            "EMEA (London)": "euw2.pure.cloud",
            "Asia Pacific (Mumbai)": "aps1.pure.cloud",
            "Asia Pacific (Seoul)": "apne2.pure.cloud",
            "Asia Pacific (Sydney)": "mypurecloud.com.au",
        }
        domain = GENESYS_REGION_DOMAIN_MAP.get(config["tenant_endpoint"])
        base_url = f"https://login.{domain}"
        api_base_url = f"https://api.{domain}"
        args = {
            "api_base_url": api_base_url,
            "authenticator": GenesysOAuthAuthenticator(base_url, config["client_id"], config["client_secret"]),
        }

        # response = self.get_connection_response(config)
        # response.raise_for_status()

        # args = {"authenticator": TokenAuthenticator(response.json()["access_token"])}
        return [
            RoutingOutboundEvents(**args),
            RoutingRoutingAssessments(**args),
            RoutingRoutingQueues(**args),
            TelephonyLocations(**args),
            TelephonyProvidersEdges(**args),
            TelephonyProvidersEdgesDids(**args),
            TelephonyProvidersEdgesDidpools(**args),
            TelephonyProvidersEdgesExtensions(**args),
            TelephonyProvidersEdgesLines(**args),
            TelephonyProvidersEdgesOutboundroutes(**args),
            TelephonyProvidersEdgesPhones(**args),
            TelephonyProvidersEdgesSites(**args),
            TelephonyProvidersEdgesTrunks(**args),
            TelephonyStations(**args),
            UserGroups(**args),
            UserUsers(**args),
        ]
