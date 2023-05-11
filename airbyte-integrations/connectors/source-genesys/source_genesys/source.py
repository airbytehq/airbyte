#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from datetime import datetime
from airbyte_cdk.logger import init_logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_genesys.authenicator import GenesysOAuthAuthenticator

logger = init_logger()

metrics = ['nBlindTransferred', 'nCobrowseSessions', 'nConnected', 'nConsult', 'nConsultTransferred', 'nError',
           'nOffered', 'nOutbound', 'nOutboundAbandoned', 'nOutboundAttempted', 'nOutboundConnected', 'nOverSla',
           'nStateTransitionError', 'nTransferred', 'oExternalMediaCount', 'oMediaCount', 'oMessageTurn',
           'oServiceLevel', 'oServiceTarget', 'tAbandon', 'tAcd', 'tAcw', 'tAgentResponseTime', 'tAlert', 'tAnswered',
           'tBarging', 'tCoaching', 'tCoachingComplete', 'tConnected', 'tContacting', 'tDialing', 'tFirstConnect',
           'tFirstDial', 'tFlowOut', 'tHandle', 'tHeld', 'tHeldComplete', 'tIvr', 'tMonitoring', 'tMonitoringComplete',
           'tNotResponding', 'tShortAbandon', 'tTalk', 'tTalkComplete', 'tUserResponseTime', 'tVoicemail', 'tWait']

# TODO: Get delta
query = {
    "interval": "2023-02-27T00:00:00.000Z/2023-02-27T23:59:59.000Z",
    # "granularity": "P1D",
    "metrics": metrics
}


def split_utc_timestamp_interval(timestamp_range):
    """
    :param timestamp_range: An interval string timestamp value split by '/' in the following format:
        YYYY-MM-DDThh:mm:ss/YYYY-MM-DDThh:mm:ss
    :return: tuple containing the values: start_datetime, end_datetime
    """
    start, end = timestamp_range.split('/')
    start_datetime = datetime.fromisoformat(start.rstrip('Z'))
    end_datetime = datetime.fromisoformat(end.rstrip('Z'))
    return start_datetime, end_datetime


class GenesysStream(HttpStream, ABC):
    url_base = "https://api.mypurecloud.com.au/api/v2/"
    page_size = 500

    def __init__(self, *args, **kwargs):
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


class GenesysAnalyticsStream(GenesysStream, ABC):
    url_base = "https://api.usw2.pure.cloud/api/v2/"
    page_size = 1000

    # Init constructor with Parent class args
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Override parent http_method() to POST
    @property
    def http_method(self) -> str:
        """
        Override if needed. See get_request_data/get_request_json if using POST/PUT/PATCH.
        """
        return "POST"

    # Override parent request_body_json() to populate POST request body
    def request_body_json(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        """
        Override when creating POST/PUT/PATCH requests to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        # Todo: map query to relevant analytics stream
        # Set query as stream state
        logger.info(f"stream_state: {stream_state}")
        logger.info(f"stream_slice: {stream_slice}")
        logger.info(f"next_page_token: {next_page_token}")
        stream_state = query

        return stream_state

    # Override parent parse_response() to traverse response body and retrieve data
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:

        json_response = response.json()
        results_json = json_response.get("results", [])

        # If response json not empty
        if results_json is not None:
            # TODO: Reformat and flatten response into expected output record
            # Traverse through the different metric groups within the response
            for metric_group in results_json:

                # Retrieve the start/end timestamps from the interval value
                start_timestamp, end_timestamp = split_utc_timestamp_interval(metric_group["data"][0]["interval"])

                # Retrieve the start/end timestamps from the interval value
                for metric in metric_group["data"][0]["metrics"]:

                    # Flatten metric results into individual records
                    metric_record = {
                        "media_type": metric_group["group"]["mediaType"],
                        "interval_start": start_timestamp,
                        "interval_end": end_timestamp,
                        "metric": metric["metric"],
                        "max": metric.get("stats").get("max", None),
                        "min": metric.get("stats").get("min", None),
                        "count": metric.get("stats").get("count", None),
                        "sum": metric.get("stats").get("sum", None),
                    }
                    logger.info(f"metric record: {metric_record}")
                    yield metric_record

        # Else: no response results returned
        else:
            logger.warning(f"{self.name} returned 0 records!")
            yield from results_json


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


# NEW - Add new streams here
class AnalyticsConversations(GenesysAnalyticsStream):
    """
    API Docs: https://developer.genesys.cloud/analyticsdatamanagement/analytics/analytics-apis
    """

    primary_key = "id"
    cursor_field = "interval_end"

    def path(self, **kwargs) -> str:
        return "analytics/conversations/aggregates/query"
# /api/v2
# analytics/conversations/aggregates/query


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
            "Asia Pacific (Sydney)": "https://login.mypurecloud.com.au",
        }
        base_url = GENESYS_TENANT_ENDPOINT_MAP.get(config["tenant_endpoint"])
        args = {"authenticator": GenesysOAuthAuthenticator(base_url, config["client_id"], config["client_secret"])}

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
            # New Streams here:
            AnalyticsConversations(**args),
            #
            UserGroups(**args),
            UserUsers(**args),
        ]
