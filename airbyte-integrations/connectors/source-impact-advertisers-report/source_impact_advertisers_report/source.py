#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from base64 import b64encode

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

class HttpBasicAuthenticator(TokenAuthenticator):
    def __init__(self, email: str, token: str, auth_method: str = "Basic", **kwargs):
        auth_string = f"{email}:{token}".encode("utf8")
        b64_encoded = b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)

# Basic full refresh stream
class ImpactAdvertisersReportStream(HttpStream, ABC):

    # Base URL
    url_base = "https://api.impact.com/Advertisers/"

    def __init__(self, account_sid: str, auth_token: str, report_id: str, start_date: str, sub_ad_id: str, **kwargs):
        super().__init__(**kwargs)
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.report_id = report_id
        self.start_date = start_date
        self.sub_ad_id = sub_ad_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()

        if response_json.get("@nextpageuri"):
            next_query_string = urllib.parse.urlsplit(response_json.get("@nextpageuri")).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        auth_header = HttpBasicAuthenticator(self.account_sid, self.auth_token, auth_method="Basic").get_auth_header()
        return {
            "Accept": "application/json",
            **auth_header,
        }

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {
            "PageSize": 5000,
            "Page": 1,
            "START_DATE": self.start_date,
            "SUBAID": self.sub_ad_id
        }
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        result = response_json.get("Records", [])
        yield from result


class Report(ImpactAdvertisersReportStream):
    primary_key = "Media"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.account_sid}/Reports/{self.report_id}"


# Source
class SourceImpactAdvertisersReport(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = HttpBasicAuthenticator(config["account_sid"], config["auth_token"], auth_method="Basic").get_auth_header()
        url = f"https://{ImpactAdvertisersReportStream.url_base}/Advertisers/{config['account_sid']}/CompanyInformation"
        try:
            response = requests.get(url, headers=auth)
            response.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = HttpBasicAuthenticator(config["account_sid"], config["auth_token"], auth_method="Basic")
        return [
            Report(
                authenticator=auth,
                account_sid=config["account_sid"],
                auth_token=config["auth_token"],
                report_id=config["report_id"],
                start_date=config["start_date"],
                sub_ad_id=config["sub_ad_id"]
            )
        ]
