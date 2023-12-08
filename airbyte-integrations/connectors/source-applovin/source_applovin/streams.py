import logging
from time import sleep
from typing import Iterable, Mapping, Optional, Any, List, Union
from itertools import islice

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
            logging.warning("URL:", response.url)
            logging.warning("Status Code:", response.status_code)
            logging.warning("Reason:", response.reason)
            logging.warning("HTTP Version:", response.raw.version)

            logging.warning("\n---- HEADERS ----")
            for key, value in response.headers.items():
                logging.warning(f"{key}: {value}")

            logging.warning("\n---- COOKIES ----")
            for name, value in response.cookies.items():
                logging.warning(f"{name}: {value}")

            logging.warning("\n---- CONTENT ----")
            logging.warning(response.text)

            logging.warning("\n---- REDIRECT HISTORY ----")
            for resp in response.history:
                logging.warning(f"Redirected to {resp.url} with status code {resp.status_code}")

            logging.warning("\n---- REQUEST INFO ----")
            logging.warning("Request Method:", response.request.method)
            logging.warning("Request URL:", response.request.url)
            logging.warning("Request Headers:")
            for key, value in response.request.headers.items():
                logging.warning(f"  {key}: {value}")

            if response.request.body:
                logging.warning("\nRequest Body:", response.request.body)

            logging.warning("\n---- OTHER INFO ----")
            logging.warning("Elapsed Time:", response.elapsed)
            logging.warning("Encoding:", response.encoding)
            logging.warning("Content Length:", len(response.content))

            return False
        if response.status_code == 429 or 501 <= response.status_code < 600:
            return True
        else:
            return False


class Campaigns(ApplovinStream):
    primary_key = "campaign_id"
    use_cache = True

    def __init__(self, authenticator: TokenAuthenticator, config, **kwargs):
        self.config = config
        super().__init__(
            authenticator=authenticator,
        )

    def path(self, **kwargs) -> str:
        return "campaigns"


class CampaignsSubStream(HttpSubStream, ApplovinStream):
    backoff = 120
    raise_on_http_errors = False
    use_cache = False

    def __init__(self, authenticator: TokenAuthenticator, config, **kwargs):
        self.config = config
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator, config=config),
        )

    # as of now Applovin's rate limit is around 2000 request per *hour*
    @property
    def max_retries(self) -> Union[int, None]:
        return 10

    @property
    def retry_factor(self) -> float:
        return 120.0

    @property
    def max_time(self) -> float:
        return 14400

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        campaigns = Campaigns(authenticator=self._session.auth, config=self.config)
        campaigns_records = list(campaigns.read_records(sync_mode=SyncMode.full_refresh))
        tracking_method_filter = self.config["filter_campaigns_tracking_methods"]
        for campaign in campaigns_records:
            if (not tracking_method_filter or
                    (tracking_method_filter and campaign["tracking_method"] in tracking_method_filter)):
                yield {"campaign_id": campaign["campaign_id"]}
                continue


class Creatives(CampaignsSubStream):
    primary_key = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"creative_sets/{campaign_id}"


class Targets(CampaignsSubStream):
    primary_key = "campaign_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"campaign_targets/{campaign_id}"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        record = response.json()
        record["campaign_id"] = stream_slice["campaign_id"]
        yield record
