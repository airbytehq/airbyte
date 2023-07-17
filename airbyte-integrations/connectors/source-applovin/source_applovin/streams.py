from typing import Iterable, Mapping, Optional, Any

import requests
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream


class CampaignsStream(HttpStream):
    url_base = "https://o.applovin.com/campaign_management/v1/"
    primary_key = "campaign_id"

    def path(self, **kwargs) -> str:
        return "campaigns"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json
