#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Dict

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

class GenesysStream(HttpStream, ABC):
    url_base = "https://api.mypurecloud.com.au/api/v2/"
    page_size = 500

    def backoff_time(self, response: requests.Response) -> Optional[int]:
        delay_time = response.headers.get("Retry-After")
        if delay_time:
            return int(delay_time)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        yield from json_response.get("entities", [])

class RoutingRoutingAssessments(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/routing/routing/
    '''
    page_size = 200
    primary_key = "id"
    cursor_field = "dateModified"
    # next: before/after for cursor

    def path(self, **kwargs) -> str:
        return "routing/assessments"
class RoutingRoutingQueues(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/routing/routing/
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: before/after for cursor

    def path(self, **kwargs) -> str:
        return "routing/queues"
class TelephonyLocations(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/locations-apis
    '''
    primary_key = "id"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "locations"

class TelephonyProvidersEdges(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges"

class TelephonyProvidersEdgesDids(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/dids"

class TelephonyProvidersEdgesDidpools(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/didpools"
class TelephonyProvidersEdgesExtensions(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/extensions"
class TelephonyProvidersEdgesLines(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/lines"
class TelephonyProvidersEdgesOutboundroutes(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/outboundroutes"
class TelephonyProvidersEdgesPhones(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/phones"
class TelephonyProvidersEdgesSites(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/sites"
class TelephonyProvidersEdgesTrunks(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/telephony-apis
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    def path(self, **kwargs) -> str:
        return "telephony/providers/edges/trunks"
class TelephonyStations(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/telephony/stations-apis
    '''
    primary_key = "id"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "stations"
class UserUsers(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/useragentman/users/
    '''
    primary_key = "id"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "users"
class UserGroups(GenesysStream):
    '''
    API Docs: https://developer.genesys.cloud/useragentman/groups/
    '''
    primary_key = "id"
    cursor_field = "dateModified"
    # next: pageNumber
    def path(self, **kwargs) -> str:
        return "groups"

# https://developer.genesys.cloud/routing/conversations/conversations-apis
# https://developer.genesys.cloud/routing/architect/
# https://developer.genesys.cloud/routing/outbound/
# https://developer.genesys.cloud/routing/scripts/
# https://developer.genesys.cloud/telephony/telephony-apis
# https://developer.genesys.cloud/commdigital/voicemail/

# analytics
# https://developer.genesys.cloud/routing/conversations/conversations-apis



# # Basic incremental stream
# class IncrementalGenesysStream(GenesysStream, ABC):
#     """
#     TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
#          if you do not need to implement incremental sync for any streams, remove this class.
#     """

#     # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
#     state_checkpoint_interval = None

#     @property
#     def cursor_field(self) -> str:
#         """
#         TODO
#         Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
#         usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

#         :return str: The name of the cursor field.
#         """
#         return []

#     def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
#         """
#         Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
#         the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
#         """
#         return {}
class SourceGenesys(AbstractSource): 

    @staticmethod
    def get_connection_response(self, config: Mapping[str, Any]):
        GENESYS_TENANT_ENDPOINT_MAP: Dict = {
            "Americas (US East)": "https://login.mypurecloud.com",
            "Americas (US East 2)": "https://login.use2.us-gov-pure.cloud",
            "Americas (US West)": "https://login.usw2.pure.cloud",
            "Americas (Canada)": "https://login.cac1.pure.cloud",
            "Americas (São Paulo)": "https://login.sae1.pure.cloud",
            "EMEA (Frankfurt)": "https://login.mypurecloud.de",
            "EMEA (Dublin)": "https://login.mypurecloud.ie",
            "EMEA (London)": "https://login.euw2.pure.cloud",
            "Asia Pacific (Mumbai)": "https://login.aps1.pure.cloud",
            "Asia Pacific (Seoul)": "https://login.apne2.pure.cloud",
            "Asia Pacific (Sydney)": "https://login.mypurecloud.com.au"
        }

        token_refresh_endpoint = GENESYS_TENANT_ENDPOINT_MAP.get(config["tenant_endpoint"])
        token_refresh_endpoint = token_refresh_endpoint + "/oauth/token"
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        refresh_token = None
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}

        try:
            response = requests.request(method="POST", url=token_refresh_endpoint, data=data, headers=headers)
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
        return response

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the credentials.
        """

        try:
            if not config["client_secret"] or not config["client_id"]:
                raise Exception("Empty config values! Check your configuration file!")

            self.get_connection_response(config).raise_for_status()
            return True, None

        except Exception as e:
            return (
                False,
                f"Got an exception while trying to set up the connection: {e}. "
                f"Most probably, there are no users in the given Genesys instance or your token is incorrect",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        response = self.get_connection_response(self, config)
        response.raise_for_status()

        args = {
            "authenticator": TokenAuthenticator(response.json()["access_token"])
        }
        return [
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
