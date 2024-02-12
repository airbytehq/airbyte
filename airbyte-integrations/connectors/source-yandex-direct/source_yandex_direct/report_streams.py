from abc import ABC
from datetime import datetime
from functools import lru_cache
from time import sleep
from typing import Any, Iterable, List, Mapping, Optional, Union

import requests
from airbyte_cdk import logger as airbyte_logger
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import (
    DefaultBackoffException,
    UserDefinedBackoffException,
)
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader

from .schema_fields import CUSTOM_SCHEMA_FIELDS, build_goal_fields
from .utils import HttpAvailabilityStrategy, random_name, split_date_by_chunks

logger = airbyte_logger.AirbyteLogger()

from http.client import HTTPConnection

HTTPConnection._http_vsn_str = "HTTP/1.0"

CONFIG_DATE_FORMAT = "%Y-%m-%d"


# Basic full refresh stream
class YandexDirectStream(HttpStream, ABC):
    url_base = "https://api.direct.yandex.com/json/v5/reports"
    http_method = "POST"
    availability_strategy = HttpAvailabilityStrategy

    def __init__(
        self,
        auth: TokenAuthenticator,
        client_login: str,
        report_name: str,
        fields: list[str],
        additional_fields: list[str],
        goal_ids: list[str],
        attribution_models: list[str],
        parsed_filters: list[dict[str, Any]],
        date_range: dict[str, Any],
        split_range_days_count: int,
        replace_keys_config: dict[str, Any] = None,
    ):
        super().__init__(authenticator=auth)
        self.client_login = client_login
        self.report_name = report_name
        self.fields = fields
        self.additional_fields = additional_fields
        self.goal_ids = goal_ids
        self.attribution_models = attribution_models
        self.parsed_filters = parsed_filters
        self.date_range = date_range
        self.split_range_days_count = split_range_days_count
        self.replace_keys_config = replace_keys_config

    @property
    def name(self) -> str:
        return self.report_name

    def _send(
        self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]
    ) -> requests.Response:
        while True:
            response = self._session.send(request, **request_kwargs)
            response.encoding = "utf-8"
            self.logger.info(
                f"Request {response.url} (Kwargs: {request_kwargs}, request body: {response.request.body})"
            )
            sleep_time = int(response.headers.get("retryIn", 5))
            if response.status_code == 200:
                return response
            elif response.status_code == 201:
                sleep(sleep_time)
                logger.info(
                    "Report is creating in offline mode. Re-check after "
                    + str(sleep_time)
                    + " seconds"
                )
            elif response.status_code == 202:
                sleep(sleep_time)
                logger.info(
                    "Report is creating in offline mode. Re-check after "
                    + str(sleep_time)
                    + " seconds"
                )
            else:
                if self.should_retry(response):
                    custom_backoff_time = self.backoff_time(response)
                    if custom_backoff_time:
                        raise UserDefinedBackoffException(
                            backoff=custom_backoff_time,
                            request=request,
                            response=response,
                        )
                    else:
                        raise DefaultBackoffException(request=request, response=response)
                elif self.raise_on_http_errors:
                    # Raise any HTTP exceptions that happened in case there were unexpected ones
                    logger.error(
                        f"Request {response.url} (Kwargs: {request_kwargs}, response body: {response.text})"
                    )
                    response.raise_for_status()

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        kwargs = super().request_kwargs(stream_state, stream_slice, next_page_token)
        kwargs.update({"stream": True})
        return kwargs

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def replace_record_key(self, key: str) -> str:
        if self.replace_keys_config:
            key_replace_config = next(
                (c for c in self.replace_keys_config if c["old_key"] == key), None
            )
            if key_replace_config:
                return key_replace_config["new_key"]
        return key

    def parse_response(
        self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        # parse raw TSV data to list of named dicts
        raw_data_lines = response.iter_lines(delimiter=b"\n")
        header = []
        records_counter = 0
        for line_n, line in enumerate(raw_data_lines):
            line_values = line.decode().split("\t")

            # skip empty rows
            if not line.strip():
                continue

            # grab header and skip if it is first line
            if line_n == 0:
                header = line_values
                continue

            # zip values list to named dict
            data_item = {}
            header = list(map(self.replace_record_key, header))
            for value_n, value in enumerate(line_values):
                data_item[header[value_n]] = value
            records_counter += 1
            if records_counter == 1_000_000:
                self.logger.warn(
                    f"Reached 1.000.000th record on stream_slice {stream_slice}. It can be Direct Reports API restriction of 1 million records per report."
                )
            yield data_item
        self.logger.info(f"Loaded {records_counter} records for stream_slice {stream_slice}")


class CustomReport(YandexDirectStream):
    def path(self, **kwargs) -> str:
        return ""

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.fields[0]

    def request_body_json(
        self, stream_slice: Mapping[str, Any], *args, **kwargs
    ) -> Optional[Mapping]:
        date_range = stream_slice["transformed_date_range"]
        params = {
            "params": {
                "SelectionCriteria": {
                    "DateFrom": datetime.strftime(date_range["date_from"], "%Y-%m-%d"),
                    "DateTo": datetime.strftime(date_range["date_to"], "%Y-%m-%d"),
                },
                "FieldNames": self.fields + self.additional_fields,
                "ReportName": stream_slice["report_name"],
                "ReportType": "CUSTOM_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "NO",
                "IncludeDiscount": "NO",
            }
        }

        if self.goal_ids:
            params["params"]["Goals"] = self.goal_ids

        if self.attribution_models:
            params["params"]["AttributionModels"] = self.attribution_models

        if self.parsed_filters:
            params["params"]["SelectionCriteria"]["Filter"] = self.parsed_filters
        return params

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        headers = {
            "Accept-Language": "ru",
            "processingMode": "auto",
            "skipReportHeader": "true",
            "skipReportSummary": "true",
        }
        headers.update(self.authenticator.get_auth_header())
        if self.client_login:
            headers["Client-Login"] = self.client_login
        return headers

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(
            "custom_report"
        )
        for field_name in self.fields:
            if self.goal_ids and field_name in [
                "ConversionRate",
                "Conversions",
                "CostPerConversion",
                "GoalsRoi",
                "Revenue",
            ]:
                built_fields = build_goal_fields(field_name, self.goal_ids, self.attribution_models)
                for built_field in built_fields:
                    schema["properties"][built_field] = {"type": ["null", "string"]}
            else:
                field_schema_type = CUSTOM_SCHEMA_FIELDS.get(field_name, None)
                if field_schema_type:
                    schema["properties"][field_name] = {"type": ["null", field_schema_type]}

        for property_key in list(schema["properties"].keys()):
            new_property_key = self.replace_record_key(property_key)
            if new_property_key != property_key:
                schema["properties"][new_property_key] = schema["properties"].pop(property_key)

        return schema

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if not self.split_range_days_count:
            slices = [{"transformed_date_range": self.date_range, "report_name": random_name(10)}]
            yield from slices
        else:
            range = self.date_range
            dates_generator = split_date_by_chunks(
                datetime.strptime(range["date_from"], "%Y-%m-%d"),
                datetime.strptime(range["date_to"], "%Y-%m-%d"),
                self.split_range_days_count,
            )
            for date_from, date_to in dates_generator:
                yield {
                    "transformed_date_range": {
                        "date_range_title": "CUSTOM_DATE",
                        "date_from": str(date_from.date()),
                        "date_to": str(date_to.date()),
                    },
                    "report_name": random_name(10),
                }
