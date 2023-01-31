#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_huawei_ads.auth import CredentialsCraftAuthenticator
from airbyte_cdk.sources.streams.http.http import SyncMode
from enum import Enum


class Region(Enum):
    ASIA_AFRICA_LATIN_AMERICA = "Asia, Africa, and Latin America"
    RUSSIA = 'Russia'
    EUROPE = 'Europe'


class StatTimeGranularity(Enum):
    STAT_TIME_GRANULARITY_HOURLY = 'Hourly'
    STAT_TIME_GRANULARITY_DAILY = 'Daily'
    STAT_TIME_GRANULARITY_MONTHLY = 'Monthly'


# Basic full refresh stream
class HuaweiAdsStream(HttpStream, ABC):
    api_datetime_format = '%Y-%m-%d'
    page_size = 1000

    def __init__(
        self,
        *,
        authenticator: Union[
            TokenAuthenticator,
            CredentialsCraftAuthenticator
        ] = None,
        region: Region,
        time_granularity: StatTimeGranularity,
        date_from: datetime,
        date_to: datetime
    ):
        super().__init__(authenticator)
        self.region = region
        self.time_granularity = time_granularity
        self.date_from = date_from
        self.date_to = date_to
        self._authenticator = authenticator

    @property
    def http_method(self) -> str:
        return 'POST'

    @property
    def url_base(self) -> str:
        region_url_mapping = {
            Region.ASIA_AFRICA_LATIN_AMERICA: "https://ads-dra.cloud.huawei.com/openapi/v2/",
            Region.RUSSIA: "https://ads-drru.cloud.huawei.ru/openapi/v2/",
            Region.EUROPE: "https://ads-dre.cloud.huawei.com/openapi/v2/",
        }
        return region_url_mapping[self.region]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        page_info = response.json()['data']['page_info']
        if page_info['page'] < page_info['total_page']:
            return page_info['page'] + 1

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, *args, **kwargs) -> Optional[Mapping]:
        return {
            "date_from": self.date_from.strftime(self.api_datetime_format),
            "date_to": self.date_to.strftime(self.api_datetime_format),
            "page": next_page_token.get("next_page") if next_page_token else 1,
            "page_size": self.page_size,
            "time_granularity": self.time_granularity.value
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data: Dict[str, Any] = response.json()
        print(response.request.body)
        print(response.request.url)
        print(response.request.headers)
        print(response.text)
        if message := data.get('message'):
            raise Exception(f"{message} (API Error code: {data.get('code')})")
        yield from data['data']['list']


class Advertiser(HuaweiAdsStream):
    primary_key = ["advertiser_id", "stat_datetime"]

    def path(
        self, *args, **kwargs
    ) -> str:
        return "reports/advertiser/query"


# Source
class SourceHuaweiAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth
        
        sample_stream = self.streams(config)[0]
        try:
            next(sample_stream.read_records(sync_mode=SyncMode.full_refresh))
        except Exception as e:
            return False, str(e)

        return True, None

    def get_auth(self, config: Mapping[str, Any]) -> TokenAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return TokenAuthenticator(config["credentials"]["access_token"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception("Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range_type = config["date_range"]["date_range_type"]
        if date_range_type == 'custom_date':
            config['date_from'] = datetime.strptime(
                config["date_range"].get("date_from"),
                HuaweiAdsStream.api_datetime_format
            )
            config['date_to'] = datetime.strptime(
                config["date_range"].get("date_to"),
                HuaweiAdsStream.api_datetime_format
            )
        elif date_range_type == 'last_n_days':
            config['date_from'] = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=config["date_range"]['last_days_count'])
            config['date_to'] = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            raise Exception(f'Invalid date_range_type: {date_range_type}')
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        auth = self.get_auth(config)
        args = dict(
            authenticator=auth,
            region=Region(config['region']),
            time_granularity=StatTimeGranularity(config['time_granularity']),
            date_from=config['date_from'],
            date_to=config['date_to'],
        )
        return [Advertiser(**args)]
