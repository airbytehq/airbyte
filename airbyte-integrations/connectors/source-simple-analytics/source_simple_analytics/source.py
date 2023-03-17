from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth


# Basic full refresh stream
class SimpleAnalyticsStream(HttpStream, ABC):
    url_base = "https://simpleanalytics.com/api/"

    def __init__(self, hostname, start, api_key, **kwargs):
        super().__init__(**kwargs)
        self.hostname = hostname
        self.start = start
        self.api_key = api_key

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()["datapoints"]

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        print("saapikey", self.api_key)
        return {
            "Api-Key": self.api_key
        }


class Export(SimpleAnalyticsStream):
    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "export/datapoints"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {
            'version': 5,
            'format': 'json',
            'hostname': self.hostname,
            'start': self.start,
            'end': 'yesterday',
            'type': 'events',
            'fields': 'added_date,added_iso,added_unix,browser_name,browser_version,country_code,datapoint,device_type,document_referrer,hostname,hostname_original,is_robot,lang_language,lang_region,os_name,os_version,path,path_and_query,query,referrer_hostname,referrer_path,screen_height,screen_width,session_id,user_agent,utm_campaign,utm_content,utm_medium,utm_source,utm_term,uuid,viewport_height,viewport_width'
        }


# Source
class SourceSimpleAnalytics(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        headers = {"Api-Key": config["api_key"],
                   "Content-Type": "application/json"}
        hostname = config["hostname"]
        url = "https://simpleanalytics.com/api/export/datapoints?version=5&hostname=" + \
            hostname + "&fields=hostname"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        args = {"authenticator": auth, "api_key": config["api_key"],
                "hostname": config["hostname"], "start": config['start']}
        return [Export(**args)]
