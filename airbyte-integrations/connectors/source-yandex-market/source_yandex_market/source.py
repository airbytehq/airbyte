#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from pendulum import yesterday

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from .auth import CredentialsCraftAuthenticator, YandexMarketAuthenticator
import json
from datetime import date, datetime, timedelta

# Basic full refresh stream
class YandexMarketStream(HttpStream, ABC):
    url_base = "https://api.partner.market.yandex.ru/v2/"
    primary_key = "id"
    response_data_key = None
    endpoint = None

    def __init__(self, authenticator: YandexMarketAuthenticator, config: Mapping[str, Any]):
        self.config = config
        HttpStream.__init__(self, authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.config["product_name"],
            "__clientName": self.config["client_name"],
        }
        constants.update(json.loads(self.config.get("custom_json", "{}")))
        record.update(constants)
        return record

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()[self.response_data_key]
        yield from map(self.add_constants_to_record, data)

    def path(self, *args, **kwargs) -> str:
        return self.endpoint

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.config["custom_json"]).keys() if self.config.get("custom_json") else []
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema


class Campaigns(YandexMarketStream):
    use_cache = True
    response_data_key = "campaigns"
    endpoint = "campaigns.json"


class CampaignsRelated(YandexMarketStream):
    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        parent_campaign_id = stream_slice["parent"]["id"]

        for record in super().parse_response(response, **kwargs):
            record["campaignId"] = parent_campaign_id
            yield record


class StatisticsStream(YandexMarketStream):
    def __init__(self, authenticator: YandexMarketAuthenticator, config: Mapping[str, Any], date_range: Tuple[str, str]):
        HttpSubStream.__init__(self, parent=Campaigns(authenticator, config))
        YandexMarketStream.__init__(self, authenticator=authenticator, config=config)
        self.date_range = date_range

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"fromDate": self.date_range[0], "toDate": self.date_range[1]}


class Offers(CampaignsRelated, YandexMarketStream, HttpSubStream):
    response_data_key = "offers"
    primary_key = ["campaignId", "id"]

    def __init__(self, authenticator: YandexMarketAuthenticator, config: Mapping[str, Any]):
        HttpSubStream.__init__(self, parent=Campaigns(authenticator, config))
        YandexMarketStream.__init__(self, authenticator=authenticator, config=config)

    def path(self, stream_slice: Mapping[str, Any], *args, **kwargs) -> str:
        parent_campaign_id = stream_slice["parent"]["id"]
        return f"campaigns/{parent_campaign_id}/offers.json"


class CampaignStatistics(CampaignsRelated, StatisticsStream, HttpSubStream):
    response_data_key = "mainStats"
    primary_key = ["campaignId", "date"]

    def path(self, stream_slice: Mapping[str, Any], *args, **kwargs) -> str:
        parent_campaign_id = stream_slice["parent"]["id"]
        return f"campaigns/{parent_campaign_id}/stats/main.json"


class OffersStatistics(CampaignsRelated, StatisticsStream, HttpSubStream):
    response_data_key = "offersStats"


class SourceYandexMarket(AbstractSource):
    DATE_FORMAT = "%d-%m-%Y"

    @staticmethod
    def parse_date(date: str):
        return datetime.strptime(date, SourceYandexMarket.DATE_FORMAT)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        date_range = config.get("date_range")
        if date_range["data_range_type"] == "last_n_days":
            if date_range.get("last_days_count"):
                if date_range.get("last_days_count") > 180:
                    return False, "Date range can't be more than 180 days"
            else:
                return False, "Last Days Count is not specified"
        elif date_range["data_range_type"] == "custom_date":
            if date_range.get("date_from") and date_range.get("date_to"):
                date_delta = (self.parse_date(date_range["date_to"]) - self.parse_date(date_range["date_from"])).days
                if date_delta > 180:
                    return False, "Date range can't be more than 180 days"
            else:
                return False, "Date From or Date To is not specified"
        else:
            raise Exception("Invalid Date Range type. Available: custom_date and last_n_days")

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth

        return True, None

    def get_date_range(self, config: Mapping[str, Any]) -> Tuple[str, str]:
        date_range = config["date_range"]
        if date_range["data_range_type"] == "custom_date":
            return (date_range["date_from"], date_range["date_to"])
        elif date_range["data_range_type"] == "last_n_days":
            yesterday = (datetime.now() - timedelta(1)).date().strftime(self.DATE_FORMAT)
            date_from = (datetime.now() - timedelta(date_range["last_days_count"])).date().strftime(self.DATE_FORMAT)
            return (date_from, yesterday)
        else:
            raise Exception("Invalid Date Range type. Available: custom_date and last_n_days")

    def get_auth(self, config: Mapping[str, Any]) -> YandexMarketAuthenticator:
        if config["credentials"]["auth_type"] == "access_token_auth":
            return YandexMarketAuthenticator(config["credentials"]["access_token"], config["client_id"])
        elif config["credentials"]["auth_type"] == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
                oauth_client_id=config["client_id"],
            )
        else:
            raise Exception("Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        date_range = self.get_date_range(config)
        return [
            Campaigns(authenticator=auth, config=config),
            Offers(authenticator=auth, config=config),
            CampaignStatistics(authenticator=auth, config=config, date_range=date_range),
        ]
