#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import logging
import pkgutil
import uuid
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple

import jsonschema
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, auth
from source_google_analytics_data_api import utils
from source_google_analytics_data_api.authenticator import GoogleServiceKeyAuthenticator
from source_google_analytics_data_api.utils import DATE_FORMAT

metrics_data_types_map: Dict = {
    "METRIC_TYPE_UNSPECIFIED": "string",
    "TYPE_INTEGER": "integer",
    "TYPE_FLOAT": "number",
    "TYPE_SECONDS": "number",
    "TYPE_MILLISECONDS": "number",
    "TYPE_MINUTES": "number",
    "TYPE_HOURS": "number",
    "TYPE_STANDARD": "number",
    "TYPE_CURRENCY": "number",
    "TYPE_FEET": "number",
    "TYPE_MILES": "number",
    "TYPE_METERS": "number",
    "TYPE_KILOMETERS": "number",
}


def get_metrics_type(t: str) -> str:
    return metrics_data_types_map.get(t, "number")


metrics_data_native_types_map: Dict = {
    "METRIC_TYPE_UNSPECIFIED": str,
    "TYPE_INTEGER": int,
    "TYPE_FLOAT": float,
    "TYPE_SECONDS": float,
    "TYPE_MILLISECONDS": float,
    "TYPE_MINUTES": float,
    "TYPE_HOURS": float,
    "TYPE_STANDARD": float,
    "TYPE_CURRENCY": float,
    "TYPE_FEET": float,
    "TYPE_MILES": float,
    "TYPE_METERS": float,
    "TYPE_KILOMETERS": float,
}


def metrics_type_to_python(t: str) -> type:
    return metrics_data_native_types_map.get(t, str)


def get_dimensions_type(d: str) -> str:
    return "string"


authenticator_class_map: Dict = {
    "Service": (GoogleServiceKeyAuthenticator, lambda credentials: {"credentials": credentials["credentials_json"]}),
    "Client": (
        auth.Oauth2Authenticator,
        lambda credentials: {
            "token_refresh_endpoint": "https://oauth2.googleapis.com/token",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "client_secret": credentials["client_secret"],
            "client_id": credentials["client_id"],
            "refresh_token": credentials["refresh_token"],
        },
    ),
}


class ConfigurationError(Exception):
    pass


class MetadataDescriptor:
    def __init__(self):
        self._metadata = None

    def __get__(self, instance, owner):
        if not self._metadata:
            stream = GoogleAnalyticsDataApiMetadataStream(config=instance.config, authenticator=instance.config["authenticator"])
            metadata = next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            if not metadata:
                raise Exception("failed to get metadata, over quota, try later")
            self._metadata = {
                "dimensions": {m["apiName"]: m for m in metadata["dimensions"]},
                "metrics": {m["apiName"]: m for m in metadata["metrics"]},
            }

        return self._metadata


class GoogleAnalyticsDataApiAbstractStream(HttpStream, ABC):
    url_base = "https://analyticsdata.googleapis.com/v1beta/"
    http_method = "POST"

    def __init__(self, *, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self._config = config
        self._stop_iteration = False

    @property
    def config(self):
        return self._config

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429:
            return False
        return super().should_retry(response)

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except requests.exceptions.HTTPError as e:
            self._stop_iteration = True
            if e.response.status_code != 429:
                raise e


class GoogleAnalyticsDataApiBaseStream(GoogleAnalyticsDataApiAbstractStream):
    """
    https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport
    """

    _record_date_format = "%Y%m%d"
    primary_key = "uuid"
    cursor_field = "date"

    metadata = MetadataDescriptor()

    @staticmethod
    def add_primary_key() -> dict:
        return {"uuid": str(uuid.uuid4())}

    @staticmethod
    def add_property_id(property_id):
        return {"property_id": property_id}

    @staticmethod
    def add_dimensions(dimensions, row) -> dict:
        return dict(zip(dimensions, [v["value"] for v in row["dimensionValues"]]))

    @staticmethod
    def add_metrics(metrics, metric_types, row) -> dict:
        def _metric_type_to_python(metric_data: Tuple[str, str]) -> Any:
            metric_name, metric_value = metric_data
            python_type = metrics_type_to_python(metric_types[metric_name])
            return metric_name, python_type(metric_value)

        return dict(map(_metric_type_to_python, zip(metrics, [v["value"] for v in row["metricValues"]])))

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Override get_json_schema CDK method to retrieve the schema information for GoogleAnalyticsV4 Object dynamically.
        """
        schema: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": {
                "property_id": {"type": ["string"]},
                "uuid": {"type": ["string"], "description": "Custom unique identifier for each record, to support primary key"},
            },
        }

        schema["properties"].update(
            {
                d: {"type": get_dimensions_type(d), "description": self.metadata["dimensions"].get(d, {}).get("description", d)}
                for d in self.config["dimensions"]
            }
        )

        schema["properties"].update(
            {
                m: {
                    "type": ["null", get_metrics_type(self.metadata["metrics"].get(m, {}).get("type"))],
                    "description": self.metadata["metrics"].get(m, {}).get("description", m),
                }
                for m in self.config["metrics"]
            }
        )

        return schema

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        r = response.json()

        if all(key in r for key in ["limit", "offset", "rowCount"]):
            limit, offset, total_rows = r["limit"], r["offset"], r["rowCount"]

            if total_rows <= offset:
                return None

            return {"limit": limit, "offset": offset + limit}

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"properties/{self.config['property_id']}:runReport"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        r = response.json()

        dimensions = [h["name"] for h in r["dimensionHeaders"]]
        metrics = [h["name"] for h in r["metricHeaders"]]
        metrics_type_map = {h["name"]: h["type"] for h in r["metricHeaders"]}

        for row in r.get("rows", []):
            yield self.add_primary_key() | self.add_property_id(self.config["property_id"]) | self.add_dimensions(
                dimensions, row
            ) | self.add_metrics(metrics, metrics_type_map, row)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        updated_state = utils.string_to_date(latest_record[self.cursor_field], self._record_date_format)
        stream_state_value = current_stream_state.get(self.cursor_field)
        if stream_state_value:
            stream_state_value = utils.string_to_date(stream_state_value, self._record_date_format, old_format=DATE_FORMAT)
            updated_state = max(updated_state, stream_state_value)
        current_stream_state[self.cursor_field] = updated_state.strftime(self._record_date_format)
        return current_stream_state

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return {
            "metrics": [{"name": m} for m in self.config["metrics"]],
            "dimensions": [{"name": d} for d in self.config["dimensions"]],
            "dateRanges": [stream_slice],
        }

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        today: datetime.date = datetime.date.today()

        start_date = stream_state and stream_state.get(self.cursor_field)
        if start_date:
            start_date = utils.string_to_date(start_date, self._record_date_format, old_format=DATE_FORMAT)
            start_date = max(start_date, self.config["date_ranges_start_date"])
        else:
            start_date = self.config["date_ranges_start_date"]

        while start_date <= today:
            if self._stop_iteration:
                return

            yield {
                "startDate": utils.date_to_string(start_date),
                "endDate": utils.date_to_string(min(start_date + datetime.timedelta(days=self.config["window_in_days"] - 1), today)),
            }
            start_date += datetime.timedelta(days=self.config["window_in_days"])


class GoogleAnalyticsDataApiMetadataStream(GoogleAnalyticsDataApiAbstractStream):
    """
    https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/getMetadata
    """

    primary_key = None
    http_method = "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"properties/{self.config['property_id']}/metadata"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield response.json()


class SourceGoogleAnalyticsDataApi(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any], report_names: Set[str]):
        if "custom_reports" in config:
            try:
                config["custom_reports"] = json.loads(config["custom_reports"])
            except ValueError:
                raise ConfigurationError("custom_reports is not valid JSON")
        else:
            config["custom_reports"] = []

        schema = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/custom_reports_schema.json"))
        try:
            jsonschema.validate(instance=config["custom_reports"], schema=schema)
        except jsonschema.ValidationError as e:
            key_path = "custom_reports"
            if e.path:
                key_path += "." + ".".join(map(str, e.path))
            raise ConfigurationError(f"{key_path}: {e.message}")

        existing_names = {r["name"] for r in config["custom_reports"]} & report_names
        if existing_names:
            existing_names = ", ".join(existing_names)
            raise ConfigurationError(f"custom_reports: {existing_names} already exist as a default report(s).")

        for report in config["custom_reports"]:
            # "date" dimension is mandatory because it's cursor_field
            if "date" not in report["dimensions"]:
                report["dimensions"].append("date")

        if "credentials_json" in config["credentials"]:
            try:
                config["credentials"]["credentials_json"] = json.loads(config["credentials"]["credentials_json"])
            except ValueError:
                raise ConfigurationError("credentials.credentials_json is not valid JSON")

        try:
            config["date_ranges_start_date"] = utils.string_to_date(config["date_ranges_start_date"])
        except ValueError as e:
            raise ConfigurationError(str(e))

        if not config.get("window_in_days"):
            source_spec = self.spec(logging.getLogger("airbyte"))
            config["window_in_days"] = source_spec.connectionSpecification["properties"]["window_in_days"]["default"]

        return config

    def get_authenticator(self, config: Mapping[str, Any]):
        credentials = config["credentials"]
        authenticator_class, get_credentials = authenticator_class_map[credentials["auth_type"]]
        return authenticator_class(**get_credentials(credentials))

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
        try:
            config = self._validate_and_transform(config, report_names={r["name"] for r in reports})
        except ConfigurationError as e:
            return False, str(e)
        config["authenticator"] = self.get_authenticator(config)

        stream = GoogleAnalyticsDataApiMetadataStream(config=config, authenticator=config["authenticator"])
        metadata = next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
        if not metadata:
            return False, "failed to get metadata, over quota, try later"

        dimensions = {d["apiName"] for d in metadata["dimensions"]}
        metrics = {d["apiName"] for d in metadata["metrics"]}

        for report in config["custom_reports"]:
            invalid_dimensions = set(report["dimensions"]) - dimensions
            if invalid_dimensions:
                invalid_dimensions = ", ".join(invalid_dimensions)
                return False, f"custom_reports: invalid dimension(s): {invalid_dimensions} for the custom report: {report['name']}"
            invalid_metrics = set(report["metrics"]) - metrics
            if invalid_metrics:
                invalid_metrics = ", ".join(invalid_metrics)
                return False, f"custom_reports: invalid metric(s): {invalid_metrics} for the custom report: {report['name']}"
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
        config = self._validate_and_transform(config, report_names={r["name"] for r in reports})
        config["authenticator"] = self.get_authenticator(config)

        return [
            type(report["name"], (GoogleAnalyticsDataApiBaseStream,), {})(
                config=dict(**config, metrics=report["metrics"], dimensions=report["dimensions"]), authenticator=config["authenticator"]
            )
            for report in reports + config["custom_reports"]
        ]
