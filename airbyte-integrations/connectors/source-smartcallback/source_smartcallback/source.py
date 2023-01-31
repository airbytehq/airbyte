#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC
from datetime import date
from hashlib import md5
from json import JSONDecodeError

from typing import Any, Iterable, List, Mapping, Optional, Tuple

from .utils import (
    date_to_timestamp,
    get_last_month_timestamp,
    get_today_minus_n_days_timestamp,
    get_yesterday_timestamp,
)

import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream


# Basic full refresh stream
class SmartcallbackStream(HttpStream, ABC):
    http_method = "POST"
    url_base = "http://smartcallback.ru/api/v2/"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=None)
        self.config = config

    def get_signed_data(self, data: Mapping[str, Any]) -> Mapping[str, Any]:
        all = ""
        for key in data:
            if key == "apiSignature":
                continue
            all += str(data[key])
        data["apiSignature"] = md5(
            (all + self.config["signature"]).encode()
        ).hexdigest()
        return data

    def get_json_schema(self):
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName"]
        custom_keys = (
            json.loads(self.config["custom_json"]).keys()
            if self.config.get("custom_json")
            else []
        )
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.config["product_name"],
            "__clientName": self.config["client_name"],
        }
        constants.update(json.loads(self.config.get("custom_json", "{}")))
        record.update(constants)
        return record

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        print("queries response", response.json())
        return map(self.add_constants_to_record, response.json()["response"]["queries"])


class Queries(SmartcallbackStream):
    primary_key = "query_id"

    def path(self, **kwargs) -> str:
        return "getQueryList/"

    def request_body_data(self, **kwargs) -> Optional[Mapping]:
        data = {
            "token": self.config["client_token"],
            "apiToken": self.config["api_token"],
            "date_from": self.config["date_from_timestamp"],
            "date_to": self.config["date_to_timestamp"],
        }
        return self.get_signed_data(data)


class QueriesStatus(Queries):
    def path(self, **kwargs) -> str:
        return "getQueriesStatus/"


class Statuses(SmartcallbackStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "StatusesGetList/"

    def request_body_data(self, **kwargs) -> Optional[Mapping]:
        data = {"apiToken": self.config["api_token"]}
        return self.get_signed_data(data)

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        return map(self.add_constants_to_record, response.json()["response"].values())


class Types(Statuses):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "TypesGetList/"


class MQueries(Queries):
    def path(self, **kwargs) -> str:
        return "getMQueryList/"


class Tags(SmartcallbackStream):
    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "getTagsList/"

    def request_body_data(self, **kwargs) -> Optional[Mapping]:
        data = {
            "apiToken": self.config["api_token"],
            "token": self.config["client_token"],
        }
        return self.get_signed_data(data)

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        return map(self.add_constants_to_record, response.json()["response"]["tags"])


# Source
class SourceSmartcallback(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            custom_constants = json.loads(config.get("custom_constants", "{}"))
            if not isinstance(custom_constants, dict):
                return (
                    False,
                    'Custom Constants must be string of JSON object like {"foo": "bar"}',
                )
        except:
            return (
                False,
                'Custom Constants must be string of JSON object like {"foo": "bar"}',
            )

        config["date_from_timestamp"] = get_today_minus_n_days_timestamp(2)
        config["date_to_timestamp"] = get_yesterday_timestamp()
        stream = self.streams(config)[0]

        try:
            generator = stream.read_records(SyncMode.full_refresh)
            print(list(generator))
        except:
            return (
                False,
                "Connector can't connect with your credentials. Please check if it is valid and retry.",
            )

        return True, None

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if not config.get("date_from") and not config.get("date_to"):
            config["date_from_timestamp"] = (
                get_today_minus_n_days_timestamp(config["last_days"])
                if config.get("last_days", 0) > 0
                else get_last_month_timestamp()
            )
            config["date_to_timestamp"] = get_yesterday_timestamp()
        else:
            config["date_from_timestamp"] = date_to_timestamp(config["date_from"])
            config["date_to_timestamp"] = date_to_timestamp(config["date_to"])
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        print(config)
        return [
            Queries(config=config),
            QueriesStatus(config=config),
            Statuses(config=config),
            Types(config=config),
            MQueries(config=config),
            Tags(config=config),
        ]
