import logging
from time import sleep
from typing import Iterable, Mapping, Optional, Any, List, Union

import requests
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode


class ApplovinStream(HttpStream):
    url_base = "https://o.applovin.com/campaign_management/v1/"
    use_cache = True  # it is used in all streams

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        yield from response.json()

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 500:
            logging.warning("Received error: " + str(response.status_code) + " " + response.text)
            return False
        if response.status_code == 429 or 501 <= response.status_code < 600:
            return True
        else:
            return False


class Campaigns(ApplovinStream):
    primary_key = "campaign_id"

    def path(self, **kwargs) -> str:
        return "campaigns"


class Creatives(HttpSubStream, ApplovinStream):
    primary_key = "id"
    backoff = 120
    raise_on_http_errors = False
    use_cache = True

    def __init__(self, authenticator: TokenAuthenticator, **kwargs):
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator),
        )

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"creative_sets/{campaign_id}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        campaigns = Campaigns(authenticator=self._session.auth)
        for campaign in campaigns.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["campaign_id"]}
            continue


class Targets(HttpSubStream, ApplovinStream):
    primary_key = "campaign_id"
    backoff = 120
    count = 0
    raise_on_http_errors = False
    use_cache = True

    def __init__(self, authenticator: TokenAuthenticator, **kwargs):
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator),
        )

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        logging.info("COUNT: " + str(self.count))
        self.count += 1
        return f"campaign_targets/{campaign_id}"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        record = response.json()
        record["campaign_id"] = stream_slice["campaign_id"]
        print(record)
        yield record

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        campaigns = Campaigns(authenticator=self._session.auth)
        for campaign in campaigns.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["campaign_id"]}
            continue
