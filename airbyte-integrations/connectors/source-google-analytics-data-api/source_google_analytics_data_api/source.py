#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import collections
import datetime
import json
import logging
import pkgutil
import uuid
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream, auth
from source_google_analytics_data_api import utils
from source_google_analytics_data_api.authenticator import GoogleServiceKeyAuthenticator

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
    "Service": (GoogleServiceKeyAuthenticator, lambda credentials: {"credentials": json.loads(credentials["credentials_json"])}),
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


def get_authenticator(credentials):
    try:
        authenticator_class, get_credentials = authenticator_class_map[credentials["auth_type"]]
    except KeyError as e:
        raise e
    return authenticator_class(**get_credentials(credentials))


class MetadataDescriptor:
    def __init__(self):
        self._metadata = None

    def __get__(self, instance, owner):
        if not self._metadata:
            authenticator = (
                instance.authenticator
                if not isinstance(instance.authenticator, auth.NoAuth)
                else get_authenticator(instance.config["credentials"])
            )
            stream = GoogleAnalyticsDataApiTestConnectionStream(config=instance.config, authenticator=authenticator)
            try:
                metadata = next(iter(stream.read_records(sync_mode=SyncMode.full_refresh)))
            except Exception as e:
                raise e

            self._metadata = {
                "dimensions": {m["apiName"]: m for m in metadata["dimensions"]},
                "metrics": {m["apiName"]: m for m in metadata["metrics"]},
            }

        return self._metadata


class GoogleAnalyticsDataApiAbstractStream(HttpStream, ABC):
    url_base = "https://analyticsdata.googleapis.com/v1beta/"
    http_method = "POST"

    def __init__(self, config: Mapping[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config

    @property
    def config(self):
        return self._config


class GoogleAnalyticsDataApiBaseStream(GoogleAnalyticsDataApiAbstractStream):
    row_limit = 100000

    metadata = MetadataDescriptor()

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "uuid"

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

        rows = []

        for row in r.get("rows", []):
            rows.append(
                collections.ChainMap(
                    *[
                        self.add_primary_key(),
                        self.add_property_id(self.config["property_id"]),
                        self.add_dimensions(dimensions, row),
                        self.add_metrics(metrics, metrics_type_map, row),
                    ]
                )
            )
        r["records"] = rows

        yield r


class IncrementalGoogleAnalyticsDataApiStream(GoogleAnalyticsDataApiBaseStream, IncrementalMixin, ABC):
    _date_format = "%Y-%m-%d"

    def __init__(self, *args, **kwargs):
        super(IncrementalGoogleAnalyticsDataApiStream, self).__init__(*args, **kwargs)
        self._cursor_value = None


class GoogleAnalyticsDataApiGenericStream(IncrementalGoogleAnalyticsDataApiStream):
    _default_window_in_days = 1
    _record_date_format = "%Y%m%d"

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return {self.cursor_field: self._cursor_value or utils.string_to_date(self.config["date_ranges_start_date"], self._date_format)}

    @state.setter
    def state(self, value):
        self._cursor_value = utils.string_to_date(value[self.cursor_field], self._date_format) + datetime.timedelta(days=1)

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

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            return []
        records = super().read_records(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state)
        for record in records:
            for row in record["records"]:
                next_cursor_value = utils.string_to_date(row[self.cursor_field], self._record_date_format)
                self._cursor_value = max(self._cursor_value, next_cursor_value) if self._cursor_value else next_cursor_value
                yield row

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        dates = []

        today: datetime.date = datetime.date.today()
        start_date: datetime.date = self.state[self.cursor_field]

        timedelta: int = self.config["window_in_days"] or self._default_window_in_days

        while start_date <= today:
            end_date: datetime.date = start_date + datetime.timedelta(days=timedelta)
            if timedelta > 1 and end_date > today:
                end_date: datetime.date = start_date + datetime.timedelta(days=timedelta - (end_date - today).days)

            dates.append(
                {
                    "startDate": utils.date_to_string(start_date, self._date_format),
                    "endDate": utils.date_to_string(end_date, self._date_format),
                }
            )

            start_date: datetime.date = end_date + datetime.timedelta(days=1)

        return dates or [None]


class GoogleAnalyticsDataApiTestConnectionStream(GoogleAnalyticsDataApiAbstractStream):
    primary_key = None
    http_method = "GET"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"properties/{self.config['property_id']}/metadata"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        yield response.json()


class SourceGoogleAnalyticsDataApi(AbstractSource):
    def __init__(self, *args, **kwargs):
        super(SourceGoogleAnalyticsDataApi, self).__init__(*args, **kwargs)

        self._authenticator = None

    def get_authenticator(self, config: Mapping[str, Any]):
        if not self._authenticator:
            self._authenticator = get_authenticator(config["credentials"])
        return self._authenticator

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        authenticator = self.get_authenticator(config)
        stream = GoogleAnalyticsDataApiTestConnectionStream(config=config, authenticator=authenticator)
        try:
            next(iter(stream.read_records(sync_mode=SyncMode.full_refresh)))
        except Exception as e:
            return False, str(e)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)

        reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
        if "custom_reports" in config:
            custom_reports = json.loads(config["custom_reports"])
            reports += custom_reports

        return [
            type(report["name"], (GoogleAnalyticsDataApiGenericStream,), {})(
                config=dict(**config, metrics=report["metrics"], dimensions=report["dimensions"]), authenticator=authenticator
            )
            for report in reports
        ]
