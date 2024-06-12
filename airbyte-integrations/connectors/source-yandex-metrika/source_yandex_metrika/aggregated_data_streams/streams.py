#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from enum import Enum
from typing import Iterable, Mapping, MutableMapping, NamedTuple

import requests
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .translations import attribution_translations, currency_translations, date_group_translations, preset_name_translations
from ..base_stream import YandexMetrikaStream

from ..fields import field_lookup
from .supported_fields import METRICS_FIELDS

logger = logging.getLogger("airbyte")


class DateRangeType(Enum):
    DATE_RANGE = "date_range"
    LAST_DAYS = "last_days"
    DAY_ENUM = "day_enum"


class DateRangeDay(Enum):
    NONE = "none"
    TODAY = "today"
    YESTERDAY = "yesterday"


class DateRange(NamedTuple):
    date_range_type: DateRangeType
    date_from: str | None
    date_to: str | None
    last_days_count: int | None
    load_today: bool | None
    day: DateRangeDay | None


class ReportConfig(NamedTuple):
    name: str
    counter_id: int | None
    preset_name: str | None
    metrics: list[str] | None
    dimensions: list[str] | None
    filters: str | None
    direct_client_logins: list[str] | None
    goal_id: str | int | None
    date_group: str | None
    attribution: str | None
    currency: str | None
    experiment_ab_id: str | None


# Full refresh stream
class AggregateDataYandexMetrikaReport(YandexMetrikaStream, ABC):
    limit = 1000
    primary_key = None
    transformer: TypeTransformer = TypeTransformer(config=TransformConfig.DefaultSchemaNormalization)

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        global_config: dict[str, any],
        report_config: ReportConfig,
        field_name_map: dict[str, any] | None = None,
    ):
        super().__init__(field_name_map)
        self._authenticator = authenticator
        self.global_config = global_config
        self.report_config = report_config

    @property
    def name(self) -> str:
        return self.report_config["name"]

    url_base = "https://api-metrika.yandex.net/stat/v1/data"

    def path(self, *args, **kwargs) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Mapping[str, any] | None:
        data = response.json()
        if len(data["data"]) < self.limit:
            return None
        return {"next_offset": data["query"]["offset"] + self.limit}

    def get_json_schema(self) -> Mapping[str, any]:
        schema = ResourceSchemaLoader(
            package_name_from_class(self.__class__),
        ).get_schema("yandex_metrika_agg_data_stream")

        test_response = self.make_test_request().json()
        if test_response.get("errors"):
            raise Exception(test_response["message"])
        for dimension in test_response["query"]["dimensions"]:
            schema["properties"][dimension] = {"type": ["string", "null"]}
        for metric in test_response["query"]["metrics"]:
            lookup_ok, field_type = field_lookup(metric, METRICS_FIELDS)
            if not lookup_ok:
                raise Exception(f"Field '{metric}' is not supported in the connector")
            schema["properties"][metric] = {"type": [field_type, "null"]}

        super().replace_keys(schema["properties"])
        return schema

    def make_test_request(self):
        test_params = self.request_params()
        test_params["limit"] = 1
        headers = self._authenticator.get_auth_header()
        return requests.get(self.url_base + self.path(), params=test_params, headers=headers)

    def request_params(self, next_page_token: Mapping[str, any] = {}, *args, **kwargs) -> MutableMapping[str, any]:
        params = {
            "ids": self.global_config["counter_id"],
            "limit": self.limit,
        }
        if next_page_token:
            params["offset"] = next_page_token.get("next_offset")

        if self.report_config.get("metrics"):
            params["metrics"] = ",".join(self.report_config.get("metrics"))

        if self.report_config.get("dimensions"):
            params["dimensions"] = ",".join(self.report_config.get("dimensions"))

        params["accuracy"] = "full"

        params["date1"] = self.global_config.get("prepared_date_range", {}).get("date_from").date()
        params["date2"] = self.global_config.get("prepared_date_range", {}).get("date_to").date()

        if self.report_config.get("direct_client_logins"):
            params["direct_client_logins"] = ",".join(self.report_config.get("direct_client_logins"))

        if self.report_config.get("filters"):
            params["filters"] = self.report_config.get("filters")

        preset_name_input = preset_name_translations.get(self.report_config.get("preset_name"))
        if preset_name_input and preset_name_input != "custom_report":
            params["preset"] = preset_name_input

        date_group_input = date_group_translations.get(self.report_config.get("date_group", "день"))
        if date_group_input not in ["day", None]:
            params["group"] = date_group_input
        else:
            params["group"] = "day"

        attribution_input = attribution_translations.get(self.report_config.get("attribution"))
        if attribution_input not in ["default", "lastsign", None]:
            params["attribution"] = attribution_input

        currency_input = currency_translations.get(self.report_config.get("currency"))
        if currency_input not in ["default", None]:
            params["currency"] = currency_input

        if self.report_config.get("experiment_ab_id"):
            params["experiment_ab"] = self.report_config.get("experiment_ab_id")

        if self.report_config.get("goal_id"):
            params["goal_id"] = self.report_config.get("goal_id")

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        logger.info(f"Request url with params: {response.request.url}")
        response_data = response.json()
        data = response_data["data"]
        query = response_data["query"]
        keys = query["dimensions"] + query["metrics"]

        for i in range(len(keys)):
            keys[i] = self.field_name_map.get(keys[i], keys[i])

        for row in data:
            row_values = []
            for dimension_value in row["dimensions"]:
                row_values.append(dimension_value.get("id") or dimension_value.get("name"))
            row_values += row["metrics"]
            yield dict(zip(keys, row_values))
