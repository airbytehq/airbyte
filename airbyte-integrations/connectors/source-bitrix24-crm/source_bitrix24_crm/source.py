#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from abc import ABC
import queue
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from .utils import get_today_minus_n_days_date, get_yesterday_date


# Basic full refresh stream
class Bitrix24CrmStream(HttpStream, ABC):
    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=None)
        self.config = config

    @property
    def url_base(self) -> str:
        return self.config["webhook_endpoint"]

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {"select[]": ["*", "UF_*"]}
        if next_page_token:
            params["start"] = next_page_token["next"]
        return params

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.config["product_name"],
            "__clientName": self.config["client_name"],
        }
        constants.update(json.loads(self.config.get("custom_json", "{}")))
        record.update(constants)
        return record

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        return map(self.add_constants_to_record, response.json()["result"])

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.config.get("custom_json", "{}")).keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema


class ObjectListStream(Bitrix24CrmStream):
    primary_key = "ID"

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        last_response_data = response.json()
        if last_response_data.get("next"):
            return {"next": last_response_data.get("next")}
        else:
            return None

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        response_data = []
        try:
            response_data = requests.get(
                self.url_base + self.path(), params=self.request_params()
            ).json()
            sample_data_keys = response_data["result"][0].keys()
        except:
            raise Exception("Schema sample request returns bad data")

        for key in sample_data_keys:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def request_params(
        self, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, **kwargs)
        extended_params = {
            "filter[>DATE_CREATE]": self.config["date_from"],
            "filter[<DATE_CREATE]": self.config["date_to"],
        }
        params.update(extended_params)
        return params


class Leads(ObjectListStream):
    def path(self, **kwargs) -> str:
        return "crm.lead.list.json"


class Deals(ObjectListStream):
    def path(self, **kwargs) -> str:
        return "crm.deal.list.json"


class LeadsStatuses(Bitrix24CrmStream):
    primary_key = "STATUS_ID"

    def path(self, **kwargs) -> str:
        return "crm.status.list"

    def next_page_token(self, *args, **kwargs) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        return {"filter[ENTITY_ID]": "SOURCE"}


class DealsStatuses(Bitrix24CrmStream):
    primary_key = "ID"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(config)
        self.deals_categories = queue.LifoQueue()
        self.init_request_passed = False
        self.current_category = None

    def path(self, **kwargs) -> str:
        if not self.init_request_passed:
            return "crm.dealcategory.list"
        return "crm.dealcategory.stage.list"

    def next_page_token(
        self, response: requests.Response, **kwargs
    ) -> Optional[Mapping[str, Any]]:
        if self.deals_categories.empty() and not self.init_request_passed:
            self.deals_categories.put({"ID": "0", "NAME": "Default"})
            for category in response.json()["result"]:
                self.deals_categories.put(category)
            self.init_request_passed = True
        try:
            self.current_category = self.deals_categories.get(block=False)
            return self.current_category
        except queue.Empty:
            self.current_category = None
            return None

    def request_params(
        self, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = {}
        if not self.init_request_passed:
            params = {"select[]": ["ID", "NAME"]}
        else:
            params = {"entityTypeId": self.current_category["ID"]}
        return params

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        if not self.init_request_passed:
            return []
        stages = []
        for category_stage in response.json()["result"]:
            category_stage.update(
                {
                    "CATEGORY_ID": self.current_category["ID"],
                    "CATEGORY_NAME": self.current_category["NAME"],
                }
            )
            stages.append(self.add_constants_to_record(category_stage))
        return stages


class SourceBitrix24Crm(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        leads_statuses_stream = self.streams(config)[-1]
        try:
            stream_params = leads_statuses_stream.request_params()
            test_response = requests.get(
                leads_statuses_stream.url_base + leads_statuses_stream.path(),
                params=stream_params,
            )
            if test_response.status_code != 200:
                return False, test_response.text
            else:
                return True, None
        except Exception as e:
            return False, e

    def transform_config(self, user_config) -> MutableMapping[str, Any]:
        config = user_config.copy()
        if not config.get("start_date") and not config.get("end_date"):
            config["date_from"] = (
                get_today_minus_n_days_date(config["last_days"])
                if config.get("last_days", 0) > 0
                else get_today_minus_n_days_date(30)
            )
            config["date_to"] = get_yesterday_date()
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Leads(config=self.transform_config(config)),
            Deals(config=self.transform_config(config)),
            DealsStatuses(config=self.transform_config(config)),
            LeadsStatuses(config=self.transform_config(config)),
        ]
