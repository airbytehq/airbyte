#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import logging
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import logger as airbyte_logger
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_yandex_direct.ads_streams import AdImages, Ads, Campaigns, YandexDirectAdsStream
from source_yandex_direct.report_streams import CustomReport

from .auth import CredentialsCraftAuthenticator
from .schema_fields import CUSTOM_SCHEMA_FIELDS
from .utils import HttpAvailabilityStrategy, random_name

logger = airbyte_logger.AirbyteLogger()

from http.client import HTTPConnection

HTTPConnection._http_vsn_str = "HTTP/1.0"

CONFIG_DATE_FORMAT = "%Y-%m-%d"


# Source
class SourceYandexDirect(AbstractSource):
    ads_streams_classes = [Ads, AdImages, Campaigns]
    availability_strategy = HttpAvailabilityStrategy

    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        spec_fields_names_for_streams = self.get_spec_fields_names_for_streams(
            self.ads_streams_classes
        )
        for stream_class, spec_field_name in spec_fields_names_for_streams:
            try:
                json.loads(config.get(spec_field_name, "{}"))
            except:
                return False, f"Invalid JSON in {spec_field_name}. See example."
            if not config.get(spec_field_name):
                continue
            stream_class_default_fields = stream_class.default_fields_names
            stream_fields_params_from_config = json.loads(config[spec_field_name])
            if not isinstance(stream_class_default_fields, dict):
                return (
                    False,
                    f"{spec_field_name} is not of valid structire. It must be object of field names. See example.",
                )
            for key in stream_fields_params_from_config:
                if key not in stream_class_default_fields:
                    return (
                        False,
                        f"{spec_field_name}: Key {key} is not available for this stream params customization. See example.",
                    )
                key_default_fields_list = stream_class_default_fields[key]
                config_key_fields_list = stream_fields_params_from_config[key]
                for field_name in config_key_fields_list:
                    if field_name not in key_default_fields_list:
                        return (
                            False,
                            f'{spec_field_name} (key {key}): field "field_name" is not available. See example.',
                        )

        for report_config in config.get("reports"):
            report_name = report_config["name"]

            date_exclusive_fields = []
            for field_name in report_config["fields"]:
                if field_name not in CUSTOM_SCHEMA_FIELDS.keys():
                    return (
                        False,
                        f"Отчёт {report_name}: Неизвестное имя поля - {field_name}. "
                        "Доступные поля: https://yandex.ru/dev/"
                        "direct/doc/reports/fields-list.html (колонка CUSTOM_REPORT).",
                    )
                if not CUSTOM_SCHEMA_FIELDS[field_name]:
                    return (
                        False,
                        f"Отчёт {report_name}: Поле {field_name} не может быть "
                        "использовано для отчёта CUSTOM_REPORT. "
                        "Доступные поля: https://yandex.ru/dev/"
                        "direct/doc/reports/fields-list.html (колонка CUSTOM_REPORT).",
                    )
                if CUSTOM_SCHEMA_FIELDS[field_name] == "filter":
                    return (
                        False,
                        f"Отчёт {report_name}: Поле {field_name} может быть "
                        "использовано только для фильтрации отчёта "
                        "и не может находиться в списке отображаемых полей. "
                        "Доступные поля: https://yandex.ru/dev/"
                        "direct/doc/reports/fields-list.html (колонка CUSTOM_REPORT).",
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
                    and "ClickType" in report_config["fields"]
                ):
                    return (
                        False,
                        f"Отчёт {report_name}: Поле ClickType несовместимо с полем {field_name}. См. "
                        "https://yandex.ru/dev/direct/doc/reports/compatibility.html",
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
                    and "ImpressionShare" in report_config["fields"]
                ):
                    return (
                        False,
                        f"Отчёт {report_name}: Поле ImpressionShare несовместимо с полем {field_name}. См. "
                        "https://yandex.ru/dev/direct/doc/reports/compatibility.html",
                    )
            if len(date_exclusive_fields) > 1:
                date_fields = ", ".join(date_exclusive_fields)
                return (
                    False,
                    f"Отчёт {report_name}: Поля {date_fields} являются взаимоисключающими: "
                    "только одно из них может быть использовано в отчёте."
                    "См. https://yandex.ru/dev/direct/doc/reports/compatibility.html",
                )

            if set(report_config["fields"]).intersection(
                [
                    "Criterion",
                    "CriterionId",
                    "CriterionType",
                ]
            ) and set(report_config["fields"]).intersection(
                ["Criteria", "CriteriaId", "CriteriaType"]
            ):
                return (
                    False,
                    f"Отчёт {report_name}: Поля Criterion, CriterionId, CriterionType "
                    "несовместимы с полями Criteria, CriteriaId, CriteriaType.",
                )

            if report_config.get("filters_json"):
                try:
                    filter_objects = json.loads(report_config["filters_json"])
                    if not isinstance(filter_objects, list):
                        return (
                            False,
                            f'Отчёт {report_name}: Фильтры (JSON) должны содержать список JSON-объектов: [{{"Field": "Year",'
                            ' "Operator": "EQUALS", "Values": ["2021"]}, {...}, {...} ...]. См. '
                            "https://yandex.ru/dev/direct/doc/reports/filters.html",
                        )
                    for filter_object in filter_objects:
                        if not isinstance(filter_object, dict):
                            return (
                                False,
                                f"Отчёт {report_name}: Фильтры (JSON) должны содержать список JSON-объектов: "
                                f'[{{"Field": "Year", "Operator": "EQUALS", "Values": ["2021"]}}, '
                                f'{{...}}, {{...}} ...]. "{filter_object}" фильтр имеет ошибки валидации.'
                                f" См. https://yandex.ru/dev/direct/doc/reports/filters.html",
                            )
                except Exception as e:
                    return False, e

        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            is_success, message = auth.check_connection()
            if not is_success:
                return is_success, message

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
            raise Exception(
                "Неверный тип авторизации. Доступные: access_token_auth and credentials_craft_auth"
            )

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
        elif range_type == "last_days":
            prepared_range["date_from"] = today - timedelta(days=date_range["last_days_count"])
            if date_range.get("should_load_today", False):
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.strptime(
                prepared_range["date_from"], CONFIG_DATE_FORMAT
            )

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.strptime(
                prepared_range["date_to"], CONFIG_DATE_FORMAT
            )
        config["prepared_date_range"] = prepared_range
        return config

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = self.prepare_config_datetime(config)
        return config

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        spec = super().spec(logger)
        properties = spec.connectionSpecification["properties"]
        extra_spec_fields = self.generate_spec_fields_for_streams(self.ads_streams_classes)

        for property_order, property_key in enumerate(extra_spec_fields, len(properties)):
            new_property = extra_spec_fields[property_key]
            new_property["order"] = property_order
            properties[property_key] = new_property

        reports_fields_property = properties["reports"]["items"]["properties"]["fields"]
        reports_fields_property["items"] = {
            "title": "ReportField",
            "enum": list(CUSTOM_SCHEMA_FIELDS.keys()),
        }

        return spec

    def generate_spec_fields_for_streams(
        self, ads_streams_classes: List[YandexDirectAdsStream]
    ) -> List[Mapping[str, Any]]:
        streams_spec_fields = {}
        for stream_class in ads_streams_classes:
            spec_field = {
                "description": f"Поля для стрима {stream_class.__name__}. Для полей по умолчанию - оставьте пустыми.",
                "title": f"Поля стрима {stream_class.__name__} (JSON, необязательно)",
                "type": "string",
                "examples": [
                    '{"FieldNames": ["CampaignId", "Id"], "MobileAppAdFieldNames": ["Text", "Title"]}'
                ],
                "order": 4,
            }
            streams_spec_fields[stream_class.__name__.lower() + "_fields_params"] = spec_field
        return streams_spec_fields

    def get_spec_fields_names_for_streams(
        self,
        streams: List[YandexDirectAdsStream],
    ) -> List[Tuple[YandexDirectAdsStream, str]]:
        for stream in streams:
            yield (stream, stream.__name__.lower() + "_fields_params")

    def get_spec_property_name_for_stream(self, stream: YandexDirectAdsStream) -> Mapping[str, Any]:
        for stream_class, spec_field_name in self.get_spec_fields_names_for_streams(
            self.ads_streams_classes
        ):
            if stream.__name__ == stream_class.__name__:
                return spec_field_name

    def streams(self, config: Mapping[str, Any]) -> List[Any]:
        config = self.transform_config(config)
        auth = self.get_auth(config)
        report_streams = []
        for report_config in config.get("reports"):
            report_streams.append(
                CustomReport(
                    auth=auth,
                    client_login=config["client_login"],
                    report_name=report_config["name"],
                    fields=report_config.get("fields"),
                    additional_fields=report_config.get("additional_fields", []),
                    goal_ids=report_config.get("goal_ids", []),
                    attribution_models=report_config.get("attribution_models", []),
                    parsed_filters=json.loads(report_config["filters_json"])
                    if report_config.get("filters_json")
                    else None,
                    date_range=config["prepared_date_range"],
                    split_range_days_count=report_config.get("split_range_days_count"),
                    replace_keys_config=report_config.get("replace_keys_config", []),
                )
            )
        ads_streams = []
        for stream_class in self.ads_streams_classes:
            stream_kwargs = {
                "auth": auth,
                "client_login": config.get("client_login"),
            }
            if stream_class == AdImages:
                stream_kwargs["use_simple_loader"] = config.get("adimages_use_simple_loader", False)
            for _, spec_fields_name in self.get_spec_fields_names_for_streams(
                self.ads_streams_classes
            ):
                stream_kwargs[spec_fields_name] = json.loads(config.get(spec_fields_name, "{}"))
            ads_streams.append(stream_class(**stream_kwargs))
        return [*report_streams, *ads_streams]
