#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from datetime import datetime, timedelta
from airbyte_cdk.logger import init_logger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from source_genesys.authenticator import GenesysOAuthAuthenticator
from source_genesys.analytics_utils import generate_query, parse_analytics_records, str_timestamp_to_datetime


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
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"pageSize": self.page_size}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        yield from json_response.get("entities", [])


class GenesysAnalyticsStream(GenesysStream, IncrementalMixin, ABC):
    url_base = "https://api.usw2.pure.cloud/api/v2/"
    page_size = 1000
    cursor_field = "interval_end"
    client_id = None
    start_date = None
    _cursor_value = None
    analytics_metrics_list = None

    # Init constructor with Parent class args + incremental params
    def __init__(self, client_id: str, analytics_metrics_list_str: str, start_date: datetime, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Metrics selection
        self.analytics_metrics_list = analytics_metrics_list_str.replace(" ", "").split(",")
        self.client_id = client_id
        # Incremental parameters:
        self.start_date = start_date

    # Getter/setter to maintain incremental state
    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime('%Y-%m-%d')}
        else:
            return {self.cursor_field: self.start_date.strftime('%Y-%m-%d')}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = str_timestamp_to_datetime(value[self.cursor_field])

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                latest_record_date = str_timestamp_to_datetime(record[self.cursor_field])
                cursor_date = str_timestamp_to_datetime(self._cursor_value)
                self._cursor_value = max(cursor_date, latest_record_date)
            yield record

    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now.
        :param start_date: The datetime value to start from.
        :return: list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.now():
            dates.append({self.cursor_field: start_date.strftime('%Y-%m-%d')})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> \
    Iterable[Optional[Mapping[str, Any]]]:
        """
        return a list of the dates for which we should pull data based on the stream state if it exists.
        Each slice will cause a HTTP request to be made to the API.
        :param sync_mode: The stream sync mode (Not implemented)
        :param cursor_field: The cursor field to derive state from.
        :param stream_state: The existing stream state map to update.
        :return: list of dicts {'date': date_string}.
        """
        start_date = str_timestamp_to_datetime(stream_state[self.cursor_field]) if stream_state and self.cursor_field in stream_state else self.start_date
        return self._chunk_date_range(start_date)

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
        logger = init_logger()
        # Set query as stream state
        latest_cursor = stream_slice.get('interval_end', None)
        logger.info(f"latest_cursor: {latest_cursor}")
        logger.info(f"Initialized metrics: {self.analytics_metrics_list}")
        stream_state = generate_query(latest_cursor, self.analytics_metrics_list)

        return stream_state

    # Override parent parse_response() to traverse response body and retrieve data
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Parse json response and format records for output.
        :param response: The HTTP response received from the api.
        :param kwargs: Extra args.
        :yield:
        """
        json_response = response.json()
        results_json = json_response.get("results", [])
        
        # If response json not empty
        if results_json is not None:
            # Return records via metric_record generator
            yield from parse_analytics_records(client_id=self.client_id, results_json=results_json)


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

    primary_key = "uid"
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
        # Fetch valid start date from config
        start_date = str_timestamp_to_datetime(config['start_date'])

        # Fetch client_id + list of metrics for analytics api streams
        analytics_metrics_list_str = config['analytics_metrics']
        client_id = config['client_id']

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
            # New Streams here:
            AnalyticsConversations(client_id, analytics_metrics_list_str, start_date, **args),
            #
            UserGroups(**args),
            UserUsers(**args),
        ]
