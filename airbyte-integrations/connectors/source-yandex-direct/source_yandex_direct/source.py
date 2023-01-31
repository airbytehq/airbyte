#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
import json
from abc import ABC
from time import sleep
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.exceptions import (
    DefaultBackoffException,
    UserDefinedBackoffException,
)

from .auth import CredentialsCraftAuthenticator
from .schema_fields import CUSTOM_SCHEMA_FIELDS
from .utils import random_name, last_n_days_dates, split_date_by_chunks, today, yesterday

from airbyte_cdk import logger as airbyte_logger

logger = airbyte_logger.AirbyteLogger()

from http.client import HTTPConnection

HTTPConnection._http_vsn_str = "HTTP/1.0"

# Basic full refresh stream
class YandexDirectStream(HttpStream, ABC):

    url_base = "https://api.direct.yandex.com/json/v5/reports"
    http_method = "POST"

    def __init__(self, auth: TokenAuthenticator, config: Mapping[str, Any]):
        super().__init__(authenticator=auth)
        self.config = config
        print("self.config", self.config)
        self.custom_constants = json.loads(self.config.get("custom_json", "{}"))

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        while True:
            response = self._session.send(request, **request_kwargs)
            response.encoding = "utf-8"
            self.logger.info(f"Request {response.url} (Kwargs: {request_kwargs}, request body: {response.request.body})")
            sleep_time = int(response.headers.get("retryIn", 5))
            if response.status_code == 200:
                return response
            elif response.status_code == 201:
                sleep(sleep_time)
                logger.info("Report is creating in offline mode. Re-check after " + str(sleep_time) + " seconds")
            elif response.status_code == 202:
                sleep(sleep_time)
                logger.info("Report is creating in offline mode. Re-check after " + str(sleep_time) + " seconds")
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
                    response.raise_for_status()

    def request_kwargs(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        kwargs = super().request_kwargs(stream_state, stream_slice, next_page_token)
        kwargs.update({"stream": True})
        return kwargs

    def add_constants_to_record(self, record: Mapping[str, Any]):
        constants = {
            "__productName": self.config.get("product_name"),
            "__clientName": self.config.get("client_name"),
        }
        constants.update(self.custom_constants)
        record.update(constants)
        return record

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
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
            for value_n, value in enumerate(line_values):
                data_item[header[value_n]] = value
            records_counter += 1
            if records_counter == 1_000_000:
                self.logger.warn(
                    f"Reached 1000000th record on stream_slice {stream_slice}. It can be Direct Reports API restriction of 1 million records per report."
                )
            yield self.add_constants_to_record(data_item)
        self.logger.info(f"Loaded {records_counter} records for stream_slice {stream_slice}")


class CustomReport(YandexDirectStream):
    def path(self, **kwargs) -> str:
        return ""

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.config["fields"][0]

    def request_body_json(self, stream_slice: Mapping[str, Any], *args, **kwargs) -> Optional[Mapping]:
        date_range = stream_slice["transformed_date_range"]
        params = {
            "params": {
                "SelectionCriteria": {},
                "FieldNames": self.config["fields"],
                "ReportName": stream_slice["report_name"],
                "ReportType": "CUSTOM_REPORT",
                "DateRangeType": date_range["date_range_title"],
                "Format": "TSV",
                "IncludeVAT": "NO",
                "IncludeDiscount": "NO",
            }
        }
        if date_range["date_range_title"] == "CUSTOM_DATE":
            params["params"]["SelectionCriteria"].update(
                {
                    "DateFrom": date_range["date_from"],
                    "DateTo": date_range["date_to"],
                }
            )

        if self.config.get("parsed_filters"):
            params["params"]["SelectionCriteria"]["Filter"] = self.config.get("parsed_filters")
        return params

    def request_headers(self, *args, **kwargs) -> Mapping[str, Any]:
        headers = {
            "Accept-Language": "ru",
            "processingMode": "auto",
            "skipReportHeader": "true",
            "skipReportSummary": "true",
        }
        headers.update(self.authenticator.get_auth_header())
        if self.config.get("client_login"):
            headers["Client-Login"] = self.config["client_login"]
        return headers

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        for field_name in self.config["fields"]:
            field_schema_type = CUSTOM_SCHEMA_FIELDS.get(field_name, None)
            if field_schema_type:
                schema["properties"][field_name] = {"type": ["null", field_schema_type]}

        extra_properties = ["__productName", "__clientName"]
        custom_keys = json.loads(self.config["custom_json"]).keys() if self.config.get("custom_json") else []
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}

        return schema

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        split_shunks_mode = self.config.get("chunk_reports", {}).get("split_mode_type")
        if split_shunks_mode == "do_not_split_mode":
            slices = [{"transformed_date_range": self.config["transformed_date_range"], "report_name": random_name(10)}]
            yield from slices
        elif split_shunks_mode == "split_date_mode":
            range = self.config["transformed_date_range"]
            dates_generator = split_date_by_chunks(
                datetime.strptime(range["date_from"], "%Y-%m-%d"),
                datetime.strptime(range["date_to"], "%Y-%m-%d"),
                self.config.get("chunk_reports", {}).get("split_range_days_count"),
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
        else:
            raise ValueError(f'split_mode_type "{split_shunks_mode}" is invalid. Available: "do_not_split_mode" and "split_date_mode".')


# Source
class SourceYandexDirect(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        date_exclusive_fields = []
        for field_name in config["fields"]:
            if field_name not in CUSTOM_SCHEMA_FIELDS.keys():
                return (
                    False,
                    f"Unknown field name {field_name}. Check https://yandex.ru/dev/' \
                    'direct/doc/reports/fields-list.html for available fields (CUSTOM_REPORT column).",
                )
            if not CUSTOM_SCHEMA_FIELDS[field_name]:
                return (
                    False,
                    f"Field name {field_name} can't be used for CUSTOM_REPORT. Check ' \
                    'https://yandex.ru/dev/direct/doc/reports/fields-list.html for ' \
                    'available fields (CUSTOM_REPORT column).",
                )
            if CUSTOM_SCHEMA_FIELDS[field_name] == "filter":
                return (
                    False,
                    f"Field name {field_name} is only used for filter data and can't ' \
                    'be shown as report field. Check https://yandex.ru/dev/direct/doc/' \
                    'reports/fields-list.html for available fields (CUSTOM_REPORT column).",
                )
            if field_name in ["Date", "Week", "Month", "Quarter", "Year"]:
                date_exclusive_fields.append(field_name)
            if (
                field_name
                in [
                    "Impressions",
                    "Ctr",
                    "AvgImpressionPosition",
                    "WeightedImpressions",
                    "WeightedCtr",
                    "AvgTrafficVolume",
                ]
                and "ClickType" in config["fields"]
            ):
                return (
                    False,
                    f"ClickType field is incompatible with {field_name} field. Check' \
                    ' https://yandex.ru/dev/direct/doc/reports/compatibility.html",
                )
            if (
                field_name
                in [
                    "AdFormat",
                    "AdId",
                    "Age",
                    "CarrierType",
                    "Gender",
                    "MobilePlatform",
                    "RlAdjustmentId",
                ]
                and "ImpressionShare" in config["fields"]
            ):
                return (
                    False,
                    f"ImpressionShare field is incompatible with {field_name} field. Check ' \
                    'https://yandex.ru/dev/direct/doc/reports/compatibility.html",
                )
        if len(date_exclusive_fields) > 1:
            date_fields = ", ".join(date_exclusive_fields)
            return (
                False,
                f"{date_fields} fields are mutually exclusive: only one of them can be' \
                ' present in the report. Check https://yandex.ru/dev/direct/doc/reports/compatibility.html",
            )

        if set(config["fields"]).intersection(["Criterion", "CriterionId", "CriterionType"]) and set(config["fields"]).intersection(
            ["Criteria", "CriteriaId", "CriteriaType"]
        ):
            return (
                False,
                "Criterion, CriterionId, CriterionType fields are incompatible' \
                ' with Criteria, CriteriaId, CriteriaType fields.",
            )

        do_dates_split = config.get("chunk_reports", {}).get("split_mode_type", "") == "split_date_mode"

        if config["date_range"].get("last_days_count"):
            if not do_dates_split:
                if not config["date_range"].get("last_days_count") in [
                    3,
                    5,
                    7,
                    14,
                    30,
                    90,
                    365,
                ]:
                    return (
                        False,
                        "Last N days field only can be 3, 5, 7, 14, 30, 90 or 365.",
                    )

        date_range_type = config["date_range"]["date_range_type"]
        if date_range_type not in ["custom_date", "last_n_days"] and do_dates_split:
            raise ValueError(
                f'You can\'t use "{date_range_type}" date range with Split Report Into'
                "Chunks option. Only last_n_days and custom_date_range available."
            )

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            check_auth = auth.check_connection()
            if not check_auth[0]:
                return check_auth

        try:  # YYYY-MM-DD
            CLIENT_LOGIN = config.get("client_login", "")
            FIELD_NAMES = [
                "Date",
                "CampaignName",
                "LocationOfPresenceName",
                "Impressions",
                "Clicks",
                "Cost",
            ]
            REPORT_NAME = random_name(9)

            body = {
                "params": {
                    "SelectionCriteria": {},
                    "FieldNames": FIELD_NAMES,
                    "ReportName": REPORT_NAME,
                    "ReportType": "CUSTOM_REPORT",
                    "DateRangeType": "TODAY",
                    "Format": "TSV",
                    "IncludeVAT": "NO",
                    "IncludeDiscount": "NO",
                }
            }

            headers = {
                "Accept-Language": "ru",
                "processingMode": "auto",
                "skipReportHeader": "true",
                "skipReportSummary": "true",
            }
            headers.update(auth.get_auth_header())
            if CLIENT_LOGIN:
                headers["Client-Login"] = CLIENT_LOGIN

            req = requests.post(
                url="https://api.direct.yandex.com/json/v5/reports",
                json=body,
                headers=headers,
            )
            req.encoding = "utf-8"
            if req.status_code not in [200, 201, 202]:
                return (
                    False,
                    f"Test request status code - {req.status_code}. Body: {req.text}",
                )
        except Exception as e:
            return False, e

        if config.get("filters_json"):
            try:
                filter_objects = json.loads(config["filters_json"])
                if not isinstance(filter_objects, list):
                    return (
                        False,
                        'Filter JSON must be array of filter objects like this: [{"Fiield": "Year",'
                        ' "Operator": "EQUALS", "Values": ["2021"]}, {...}, {...} ...]. Check '
                        "https://yandex.ru/dev/direct/doc/reports/filters.html",
                    )
                for filter_object in filter_objects:
                    if not isinstance(filter_object, dict):
                        return (
                            False,
                            f"Filter JSON must be array of filter objects like this: "
                            f'[{{"Fiield": "Year", "Operator": "EQUALS", "Values": ["2021"]}}, '
                            f'{{...}}, {{...}} ...]. "{filter_object}" filter has validation errors.'
                            f" Check https://yandex.ru/dev/direct/doc/reports/filters.html",
                        )
            except Exception as e:
                return False, e

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
        available_date_range = {
            "today": {"date_range_title": "TODAY"},
            "yesterday": {"date_range_title": "YESTERDAY"},
            "custom_date": {
                "date_range_title": "CUSTOM_DATE",
                "date_from": config["date_range"].get("date_from"),
                "date_to": config["date_range"].get("date_to"),
            },
            "from_start_date_to_today": {
                "date_range_title": "CUSTOM_DATE",
                "date_from": config["date_range"].get("date_from"),
            },
            "last_n_days": {"date_range_title": f"LAST_" + str(config["date_range"].get("last_days_count")) + "_DAYS"},
            "all_time": {"date_range_title": "ALL_TIME"},
            "auto": {"date_range_title": "AUTO"},
        }
        config["transformed_date_range"] = available_date_range[date_range_type]

        if date_range_type == "from_start_date_to_today":
            if config["date_range"]["should_load_today"]:
                config["transformed_date_range"]["date_to"] = str(today())
            else:
                config["transformed_date_range"]["date_to"] = str(yesterday())

        if config.get("chunk_reports", {}).get("split_mode_type", "") == "split_date_mode":
            date_range_title: str = config["transformed_date_range"]["date_range_title"]
            if date_range_title.startswith("LAST_"):
                date_from, date_to = last_n_days_dates(config["date_range"].get("last_days_count"))
                config["transformed_date_range"] = {
                    "date_range_title": "CUSTOM_DATE",
                    "date_from": str(date_from.date()),
                    "date_to": str(date_to.date()),
                }
            elif date_range_title == "CUSTOM_DATE":
                pass
            else:
                raise ValueError(
                    f'You can\'t use "{date_range_title}" date range with Split '
                    "Report Into Chunks option. Only last_n_days and custom_date_range available."
                )

        config["parsed_filters"] = json.loads(config["filters_json"]) if config.get("filters_json") else None
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Any]:
        return [CustomReport(auth=self.get_auth(config), config=self.transform_config(config))]
