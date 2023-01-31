#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .utils import (
    date_to_request_report_date,
    get_today_minus_n_days_date_dmy,
    get_today_minus_n_days_date_mdy,
    get_yesterday_date_dmy,
    get_yesterday_date_mdy,
)


# Basic full refresh stream
class CalltouchStream(HttpStream, ABC):
    url_base = "https://api.calltouch.ru/"

    def __init__(
        self,
        authenticator: Any = None,
        config: Mapping[str, Any] = {},
    ):
        super().__init__(authenticator=authenticator)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        last_response_data = response.json()
        if not last_response_data:
            return None

        next_page = {}
        if last_response_data["pageTotal"] > last_response_data["page"]:
            next_page = {"next_page": response.json()["page"] + 1}
        else:
            next_page = None
        return next_page

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.config["product_name"],
            "__clientName": self.config["client_name"],
        }
        constants.update(json.loads(self.config.get("custom_json", "{}")))
        record.update(constants)
        return record

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        next_page = next_page_token.get("next_page") if next_page_token else 1
        params = {
            "clientApiId": self.config["token"],
            "dateFrom": self.config["start_date"],
            "dateTo": self.config["end_date"],
            "page": next_page,
            "limit": 1000,
        }
        return params

    def get_json_schema(self):
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.config.get("custom_json", "{}")).keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema


class Calls(CalltouchStream):
    primary_key = "callId"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params["withCallTags"] = True
        return params

    def path(self, **kwargs) -> str:
        site_id = self.config["site_id"]
        return f"calls-service/RestAPI/{site_id}/calls-diary/calls"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return map(self.add_constants_to_record, response.json()["records"])


class Requests(CalltouchStream):
    primary_key = "requestId"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(
            **kwargs,
        )
        # params["withMapVisits"] = True
        params["withRequestTags"] = True
        return params

    def path(self, **kwargs) -> str:
        return f"calls-service/RestAPI/requests"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return map(self.add_constants_to_record, response.json())


# Source
class SourceCalltouch(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        calls_stream = self.streams(config)[0]
        try:
            stream_params = calls_stream.request_params().copy()
            stream_params["limit"] = 1
            stream_params["dateFrom"] = get_yesterday_date_dmy()
            stream_params["dateTo"] = get_yesterday_date_dmy()
            test_response = requests.get(calls_stream.url_base + calls_stream.path(), params=stream_params)
            if test_response.status_code != 200:
                return False, test_response.text
            else:
                return True, None
        except Exception as e:
            return False, e

    def transform_config(self, user_config, stream) -> MutableMapping[str, Any]:
        config = user_config.copy()
        if not config.get("start_date") and not config.get("end_date"):
            if stream.__name__ == "Calls":
                config["start_date"] = (
                    get_today_minus_n_days_date_dmy(config["last_days"])
                    if config.get("last_days", 0) > 0
                    else get_today_minus_n_days_date_dmy(30)
                )
                config["end_date"] = get_yesterday_date_dmy()
            if stream.__name__ == "Requests":
                config["start_date"] = (
                    get_today_minus_n_days_date_mdy(config["last_days"])
                    if config.get("last_days", 0) > 0
                    else get_today_minus_n_days_date_mdy(30)
                )
                config["end_date"] = get_yesterday_date_mdy()
        else:
            if stream.__name__ == "Requests":
                config["start_date"] = date_to_request_report_date(config["start_date"])
                config["end_date"] = date_to_request_report_date(config["end_date"])
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [
            Calls(authenticator=None, config=self.transform_config(config, Calls)),
            Requests(authenticator=None, config=self.transform_config(config, Requests)),
        ]
