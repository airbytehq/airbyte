import logging
from time import sleep
from typing import Iterable, Mapping, Optional, Any, List

import requests
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode


class ApplovinStream(HttpStream):
    url_base = "https://o.applovin.com/campaign_management/v1/"
    use_cache = True  # it is used in all streams

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json

class Campaigns(ApplovinStream):
    primary_key = "campaign_id"

    def path(self, **kwargs) -> str:
        return "campaigns"


class Creatives(HttpSubStream, ApplovinStream):
    primary_key = "id"
    backoff = 120
    count = 0

    def __init__(self, authenticator: TokenAuthenticator, **kwargs):
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator),
        )

    def use_cache(self):
        return True

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429 or 501 <= response.status_code < 600:
            logging.warning("Received error: " + str(response.status_code) + " " + response.text)
            return True
        else:
            return False

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        sleep(self.backoff)
        self.backoff *= 2
        return super().backoff_time(response)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        logging.info("COUNT: " + str(self.count))
        self.count += 1
        return f"creative_sets/{campaign_id}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        campaigns = Campaigns(authenticator=self._session.auth)
        for campaign in campaigns.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["campaign_id"]}
            continue
