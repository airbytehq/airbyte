#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


CONFIG_date_FORMAT = '%Y-%m-%dT%H:%M:%S'


class UrlBase(Enum):
    HYBRID = 'https://api.hybrid.ai'
    VOX = 'https://api.hybrid.ru'

# Basic full refresh stream


class HybridAdsStream(HttpStream, ABC):
    def __init__(self, authenticator: TokenAuthenticator = None, service_url_base: UrlBase = UrlBase.HYBRID):
        HttpStream.__init__(self, authenticator)
        self.service_url_base = service_url_base

    @property
    def url_base(self) -> str:
        return self.service_url_base.value + '/v3.0/'

    def path(self, *args, **kwargs) -> str:
        return self.endpoint

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Advertisers(HybridAdsStream):
    use_cache = True
    primary_key = "Id"
    endpoint = "agency/advertisers"
    object_name = 'advertiser'


class HybridAdsSubStream(HybridAdsStream, HttpSubStream, ABC):
    def __init__(self, parent: HybridAdsStream, authenticator: TokenAuthenticator = None, service_url_base: UrlBase = UrlBase.HYBRID):
        HttpSubStream.__init__(self, parent=parent)
        HybridAdsStream.__init__(self, authenticator, service_url_base)


class Campaigns(HybridAdsSubStream):
    primary_key = "Id"
    use_cache = True
    endpoint = "advertiser/campaigns"
    object_name = 'campaign'

    def request_params(
        self,
        stream_slice: Mapping[str, any] = None,
        *args, **kwargs
    ) -> MutableMapping[str, Any]:
        return {"advertiserId": stream_slice['parent']['Id']}

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, any] = None,
        *args, **kwargs,
    ) -> Iterable[Mapping]:
        for object in super().parse_response(response, *args, **kwargs):
            yield {**object, "advertiserId": stream_slice['parent']['Id']}


class Banners(HybridAdsSubStream):
    primary_key = "Id"
    endpoint = "campaign/banners"
    use_cache = True
    object_name = 'banner'

    def request_params(
        self,
        stream_slice: Mapping[str, any] = None,
        *args, **kwargs,
    ) -> MutableMapping[str, Any]:
        return {"campaignId": stream_slice['parent']['Id']}

    def parse_response(
        self,
        response: requests.Response,
        stream_slice: Mapping[str, any] = None,
        *args, **kwargs,
    ) -> Iterable[Mapping]:
        for object in super().parse_response(response, *args, **kwargs):
            yield {**object, "campaignId": stream_slice['parent']['Id']}


class StatisticsStream(HybridAdsStream, HttpSubStream, ABC):
    def __init__(
        self,
        *,
        authenticator: TokenAuthenticator = None,
        service_url_base: UrlBase = UrlBase.HYBRID,
        parent: HttpStream,
        date_from: datetime,
        date_to: datetime
    ):
        if not isinstance(parent, self.parent_stream_class):
            raise AssertionError(
                f"{self.name} can accept only {self.parent_stream_class.__name__}"
                f" object as parent. {parent.__class__.__name__} provided"
            )
        HttpSubStream.__init__(self, parent=parent)
        HybridAdsStream.__init__(
            self, authenticator=authenticator, service_url_base=service_url_base)
        self.date_from = date_from
        self.date_to = date_to

    def path(self, stream_slice: Mapping[str, any], **kwargs) -> str:
        return self.endpoint + "/" + "Day"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return super().next_page_token(response)

    def transform_date(self, dt: datetime) -> str:
        return dt.replace(microsecond=0).isoformat()

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        return {
            "from": self.transform_date(self.date_from),
            "to": self.transform_date(self.date_to),
            f"{self.parent.object_name}Id": stream_slice['parent']['Id']
        }

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, any] = None, **kwargs) -> Iterable[Mapping]:
        for record in response.json()['Statistic']:
            yield {
                f"{self.parent.object_name}Id": stream_slice['parent']['Id'],
                **record
            }


class AdvertisersStatistics(StatisticsStream):
    endpoint = "advertiser"
    parent_stream_class = Advertisers
    primary_key = ["advertiserId", "Day"]


class CampaignsStatistics(StatisticsStream):
    endpoint = "campaign"
    parent_stream_class = Campaigns
    primary_key = ["campaignId", "Day"]


class BannersStatistics(StatisticsStream):
    endpoint = "banner"
    parent_stream_class = Banners
    primary_key = ["bannerId", "Day"]


class SourceHybridAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        self.get_access_token(config)
        return True, None

    def get_access_token(self, config: Mapping[str, Any]) -> str:
        url_base: UrlBase = getattr(UrlBase, config['service'], None)
        if not url_base:
            raise ValueError(
                f'Unavailable service name in config: {config["service"]}')
        response = requests.post(
            url_base.value + '/token',
            data={
                "client_id": config['client_id'],
                "client_secret": config['client_secret'],
                "grant_type": "client_credentials",
            }
        )
        if response.status_code == 404:
            raise Exception("Auth error (404): invalid client_id")
        elif response.status_code == 400:
            raise Exception("Auth error (400): invalid client_secret")
        else:
            response.raise_for_status()

        try:
            return response.json()['access_token']
        except:
            raise Exception(
                f"Auth error ({response.status_code}): {response.text}")

    @staticmethod
    def prepare_config_datetime(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range = config["date_range"]
        range_type = config["date_range"]["date_range_type"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_date":
            prepared_range["date_from"] = date_range["date_from"]
            prepared_range["date_to"] = date_range["date_to"]
        elif range_type == "from_date_from_to_today":
            prepared_range["date_from"] = date_range["date_from"]
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        elif range_type == "last_n_days":
            prepared_range["date_from"] = today - \
                timedelta(days=date_range["last_days_count"])
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.strptime(
                prepared_range["date_from"], CONFIG_date_FORMAT)

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.strptime(
                prepared_range["date_to"], CONFIG_date_FORMAT)
        config["prepared_date_range"] = prepared_range
        return config

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        return self.prepare_config_datetime(config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config=config)
        auth = TokenAuthenticator(token=self.get_access_token(config))

        shared_kwargs = {"authenticator": auth,
                         "service_url_base": getattr(UrlBase, config['service'])}
        shared_statistics_streams_kwargs = {
            **shared_kwargs,
            "date_from": config["prepared_date_range"]['date_from'],
            "date_to": config["prepared_date_range"]['date_to']
        }

        advertisers_stream = Advertisers(**shared_kwargs)
        campaigns_stream = Campaigns(
            parent=advertisers_stream, **shared_kwargs)
        banners_stream = Banners(parent=campaigns_stream, **shared_kwargs)
        return [
            advertisers_stream,
            campaigns_stream,
            banners_stream,
            AdvertisersStatistics(
                **shared_statistics_streams_kwargs,
                parent=advertisers_stream,
            ),
            CampaignsStatistics(
                **shared_statistics_streams_kwargs,
                parent=campaigns_stream,
            ),
            BannersStatistics(
                **shared_statistics_streams_kwargs,
                parent=banners_stream,
            )
        ]
