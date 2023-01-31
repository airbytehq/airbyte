#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from cgi import test
from enum import Enum
from typing import Any, Iterable, List, Mapping, MutableMapping, NamedTuple, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
import json
from . import supported_fields
from .auth import CredentialsCraftAuthenticator


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
    date_from: Optional[str]
    date_to: Optional[str]
    last_days_count: Optional[int]
    load_today: Optional[bool]
    day: Optional[DateRangeDay]


class ReportConfig(NamedTuple):
    name: str
    preset_name: Optional[str]
    metrics: Optional[list[str]]
    dimensions: Optional[list[str]]
    filters: Optional[str]
    specific_counter_ids: Optional[list[int]]
    specific_direct_client_logins: Optional[list[str]]
    goal_id: Optional[str | int]
    date_group: Optional[str]
    attribution: Optional[str]
    currency: Optional[str]
    experiment_ab_id: Optional[str]


class YandexMetrikaReportConfig(NamedTuple):
    global_counter_ids: Optional[list[str]]
    global_direct_client_logins: Optional[list[str]]
    tables: list[ReportConfig]
    date: DateRange
    client_name: Optional[str]
    product_name: Optional[str]
    custom_constants: Optional[str]


# Full refresh stream
class YandexMetrikaReport(HttpStream, ABC):
    limit = 1000
    primary_key = None
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization)

    def __init__(
        self,
        authenticator: TokenAuthenticator,
        global_config: YandexMetrikaReportConfig,
        report_config: ReportConfig
    ):
        super().__init__()
        self._authenticator = authenticator
        self.global_config = global_config
        self.report_config = report_config

    @property
    def name(self) -> str:
        return self.report_config.name

    url_base = "https://api-metrika.yandex.net/stat/v1/data"

    def path(self, *args, **kwargs) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if len(data['data']) < self.limit:
            return None
        return {"next_offset": data["query"]["offset"] + self.limit}

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(
            self.__class__)).get_schema("yandex_metrika_report")
        test_response = self.make_test_request().json()
        for dimension in test_response["query"]["dimensions"]:
            schema["properties"][dimension] = {"type": ["string", "null"]}
        for metric in test_response["query"]["metrics"]:
            lookup = supported_fields.field_lookup(
                metric, supported_fields.METRICS_FIELDS)
            if not lookup[0]:
                raise Exception(
                    f"Field '{metric}' is not supported in the connector"
                )
            schema["properties"][metric] = {"type": [lookup[1][1], "null"]}

        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.global_config.custom_constants).keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.global_config.product_name,
            "__clientName": self.global_config.client_name,
        }
        constants.update(json.loads(self.global_config.custom_constants))
        record.update(constants)
        return record

    def make_test_request(self):
        test_params = self.request_params()
        test_params["limit"] = 1
        headers = self._authenticator.get_auth_header()
        return requests.get(
            self.url_base + self.path(), params=test_params, headers=headers
        )

    def request_params(self, next_page_token: Mapping[str, Any] = {}, *args, **kwargs) -> MutableMapping[str, Any]:
        params = {
            "ids": ",".join(list(map(str, self.report_config.specific_counter_ids or self.global_config.global_counter_ids))),
            "limit": self.limit,
        }
        if next_page_token:
            params["offset"] = next_page_token.get("next_offset")

        if self.report_config.metrics:
            params["metrics"] = ",".join(self.report_config.metrics)

        if self.report_config.dimensions:
            params["dimensions"] = ",".join(self.report_config.dimensions)

        params["accuracy"] = 'full'

        if self.global_config.date.date_range_type == DateRangeType.DATE_RANGE:
            params["date1"] = self.global_config.date.date_from
            params["date2"] = self.global_config.date.date_to
        if self.global_config.date.date_range_type == DateRangeType.LAST_DAYS:
            params["date1"] = str(
                self.global_config.date.last_days_count) + "daysAgo"
            params["date2"] = "today" if self.global_config.date.load_today else "yesterday"
        if self.global_config.date.date_range_type == DateRangeType.DAY_ENUM:
            params["date1"] = self.global_config.date.day.value
            params["date2"] = self.global_config.date.day.value

        if self.report_config.specific_direct_client_logins or self.global_config.global_direct_client_logins:
            params["direct_client_logins"] = ",".join(
                self.report_config.specific_direct_client_logins or self.global_config.global_direct_client_logins
            )

        if self.report_config.filters:
            params["filters"] = self.report_config.filters

        if self.report_config.preset_name:
            params["preset"] = self.report_config.preset_name

        if self.report_config.date_group not in ['day', None]:
            params["group"] = self.report_config.date_group
        else:
            params["group"] = 'day'

        if self.report_config.attribution not in ['default', 'lastsign', None]:
            params["attribution"] = self.report_config.attribution

        if self.report_config.currency not in ['default', None]:
            params["currency"] = self.report_config.currency

        if self.report_config.experiment_ab_id:
            params["experiment_ab"] = self.report_config.experiment_ab_id

        if self.report_config.goal_id:
            params["goal_id"] = self.report_config.goal_id

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        print(f'Request url with params: {response.request.url}')
        response_data = response.json()
        sampling_info = {
            "sampled": response_data['sampled'],
            "sample_share": response_data['sample_share'],
            "sample_size": response_data['sample_size'],
            "sample_space": response_data['sample_space'],
            "data_lag": response_data['data_lag'],
            "total_rows": response_data['total_rows'],
            "total_rows_rounded": response_data['total_rows_rounded'],
            "totals": response_data['totals'],
            "min": response_data['min'],
            "max": response_data['max'],
        }
        print(f'Response sampling info: {sampling_info}')
        data = response_data["data"]
        query = response_data["query"]
        keys = query["dimensions"] + query["metrics"]

        for row in data:
            row_values = []
            for dimension_value in row["dimensions"]:
                row_values.append(dimension_value.get(
                    "id") or dimension_value.get("name"))
            row_values += row["metrics"]
            yield self.add_constants_to_record(dict(zip(keys, row_values)))


# Source
class SourceYandexMetrikaReport(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth

        for stream_n, stream in enumerate(self.streams(config)):
            test_response = stream.make_test_request()
            test_response_data = test_response.json()
            if test_response_data.get("errors"):
                return False, f"Table #{stream_n} ({stream.name}) error: " + test_response_data.get("message")
        return True, None

    def transform_config(self, config: Mapping[str, Any]) -> YandexMetrikaReportConfig:
        return YandexMetrikaReportConfig(
            global_counter_ids=config.get("global_counter_ids"),
            global_direct_client_logins=config.get(
                "global_direct_client_logins"),
            tables=[
                ReportConfig(
                    name=raw_report_config.get("name"),
                    preset_name=raw_report_config.get("preset_name"),
                    metrics=raw_report_config.get("metrics"),
                    dimensions=raw_report_config.get("dimensions"),
                    filters=raw_report_config.get("filters"),
                    specific_counter_ids=raw_report_config.get(
                        "specific_counter_ids"),
                    specific_direct_client_logins=raw_report_config.get(
                        "specific_direct_client_logins"),
                    attribution=raw_report_config.get("attribution"),
                    goal_id=raw_report_config.get("goal_id"),
                    date_group=raw_report_config.get("date_group"),
                    currency=raw_report_config.get('currency'),
                    experiment_ab_id=raw_report_config.get('experiment_ab_id')
                )
                for raw_report_config in config.get("tables")
            ],
            date=DateRange(
                date_range_type=DateRangeType(
                    config.get("date", {}).get("date_range_type")),
                date_from=config.get("date", {}).get("date_from"),
                date_to=config.get("date", {}).get("date_to"),
                last_days_count=config.get("date", {}).get("last_days_count"),
                load_today=config.get("date", {}).get("load_today"),
                day=DateRangeDay(config.get("date", {}).get("day", "none")),
            ),
            client_name=config.get("client_name", ""),
            product_name=config.get("product_name", ""),
            custom_constants=config.get("custom_constants", "{}"),
        )

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
            raise Exception(
                "Invalid Auth type. Available: access_token_auth and credentials_craft_auth")

    def streams(self, config: Mapping[str, Any]) -> List[YandexMetrikaReport]:
        transformed_config = self.transform_config(config)
        auth = self.get_auth(config)
        return [
            YandexMetrikaReport(
                authenticator=auth,
                global_config=transformed_config,
                report_config=stream_config
            ) for stream_config in transformed_config.tables
        ]
