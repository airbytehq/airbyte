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
from operator import itemgetter
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
        self._raise_on_http_errors = True

    @property
    def config(self):
        return self._config

    @property
    def raise_on_http_errors(self):
        return self._raise_on_http_errors


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
        return dict(zip(dimensions, [v["value"] for v in row.get("dimensionValues", [])]))

    @staticmethod
    def add_metrics(metrics, metric_types, row) -> dict:
        def _metric_type_to_python(metric_data: Tuple[str, str]) -> Any:
            metric_name, metric_value = metric_data
            python_type = metrics_type_to_python(metric_types[metric_name])
            return metric_name, python_type(metric_value)

        return dict(map(_metric_type_to_python, zip(metrics, [v["value"] for v in row.get("metricValues", [])])))

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
        if not response.ok:
            return {}

        r = response.json()

        dimensions = [h["name"] for h in r.get("dimensionHeaders", [])]
        metrics = [h["name"] for h in r.get("metricHeaders", [])]
        metrics_type_map = {h["name"]: h["type"] for h in r.get("metricHeaders", [])}

        rows = []

        for row in r.get("rows", []):
            chain_row = collections.ChainMap(
                *[
                    self.add_primary_key(),
                    self.add_property_id(self.config["property_id"]),
                    self.add_dimensions(dimensions, row),
                    self.add_metrics(metrics, metrics_type_map, row),
                ]
            )
            rows.append(dict(chain_row))
        r["records"] = rows

        yield r

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429:
            self.logger.info(f"{response.json()['error']['message']}. "
                             f"More info: https://developers.google.com/analytics/devguides/reporting/data/v1/quotas")
            self._raise_on_http_errors = False
            return False
        return super(GoogleAnalyticsDataApiBaseStream, self).should_retry(response)


class FullRefreshGoogleAnalyticsDataApi(GoogleAnalyticsDataApiBaseStream, ABC):
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        start_date = utils.string_to_date(self.config["date_ranges_start_date"])
        end_date = datetime.datetime.now().date()
        return {
            "metrics": [{"name": m} for m in self.config["metrics"]],
            "dimensions": [{"name": d} for d in self.config["dimensions"]],
            "dateRanges": [
                {
                    "startDate": utils.date_to_string(start_date),
                    "endDate": utils.date_to_string(end_date),
                }
            ]
        }


class IncrementalGoogleAnalyticsDataApiStream(GoogleAnalyticsDataApiBaseStream, IncrementalMixin, ABC):
    _date_format: str = "%Y-%m-%d"

    def __init__(self, *args, **kwargs):
        super(IncrementalGoogleAnalyticsDataApiStream, self).__init__(*args, **kwargs)
        self._cursor_value: str = ""


class GoogleAnalyticsDataApiGenericStream(IncrementalGoogleAnalyticsDataApiStream):
    _default_window_in_days: int = 1
    _record_date_format:     str = "%Y%m%d"

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    @property
    def state(self) -> MutableMapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        return {
            self.cursor_field: utils.date_to_string(self._date_parse_probe(self.config["date_ranges_start_date"]), self._record_date_format)
        }

    @state.setter
    def state(self, value: dict):
        self._cursor_value = utils.date_to_string(
            self._date_parse_probe(value[self.cursor_field]) + datetime.timedelta(days=1),
            self._record_date_format
        )

    def _date_parse_probe(self, date_string: str) -> datetime.date:
        try:
            return utils.string_to_date(date_string, self._record_date_format)
        except ValueError:
            return utils.string_to_date(date_string, self._date_format)

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        return {
            "metrics": [{"name": m} for m in self.config["metrics"]],
            "dimensions": [{"name": d} for d in self.config["dimensions"]],
            "dateRanges": [stream_slice]
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
            for row in record.get("records", []):
                self._cursor_value: str = max(self._cursor_value, row[self.cursor_field]) if self._cursor_value else row[self.cursor_field]
                yield row

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        dates = []

        today:      datetime.date = datetime.date.today()
        start_date: datetime.date = utils.string_to_date(self.state[self.cursor_field], self._record_date_format)

        timedelta: int = self.config.get("window_in_days", self._default_window_in_days)

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

    def _validate_custom_reports(self, custom_reports, default_reports):
        """
        Load, validate and return custom reports. Expect custom reports to be a json string of the following format:
        [{"name": "<report name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...]}, ...]
        :param custom_reports: custom reports to be validated
        :return: custom reports
        """
        # Custom report root object is of type list
        if not isinstance(custom_reports, list):
            raise TypeError(f"Expected Custom Reports to be a list of objects. Got {type(custom_reports)}.")

        # Report items are of type dict
        incorrect_report_item_types = [(i, type(report)) for i, report in enumerate(custom_reports) if type(report) is not dict]
        if any(incorrect_report_item_types):
            raise TypeError("Expected Report item to be an object. " + ", ".join([f"Got {t} at report item {i}" for i, t in incorrect_report_item_types]))

        def validate_name(report: dict) -> Optional[str]:
            """Report name is defined as a non-empty string. Returns key name if any problems"""
            if not (
                "name" in report
                and report["name"]
                and type(report['name']) is str
            ):
                return "name"

        def validate_structure(report: dict) -> Optional[str]:
            """Check that either `dimensions` or `metrics` present in report config. Returns an error string"""
            if not (("dimensions" in report and report["dimensions"]) or ("metrics" in report and report["metrics"])):
                return "non-empty `dimensions` or `metrics` must present"

        def validate_dimensions(report: dict) -> Optional[str]:
            """Dimensions are defined as a list of strings. Returns key dimensions if any problems"""
            if "dimensions" in report and report["dimensions"] and not (
                isinstance(report["dimensions"], list)
                and all(type(d) is str and d for d in report["dimensions"])
            ):
                return "dimensions"

        def validate_metrics(report: dict) -> Optional[str]:
            """Metrics are defined as a list of strings. Returns key metrics if any problems"""
            if "metrics" in report and report["metrics"] and not (
                isinstance(report["metrics"], list)
                and all(type(m) is str and m for m in report["metrics"])
            ):
                return "metrics"

        # Collect all invalid reports with their positions and invalid keys. Example: [(1, "name"), (3, "name", "metrics"), ...]
        incorrect_report_item_fields = [
            (i, *filter(lambda x: x, (validate_name(report), validate_structure(report), validate_dimensions(report), validate_metrics(report))))
            for i, report in enumerate(custom_reports)
            if any([validate_name(report), validate_structure(report), validate_dimensions(report), validate_metrics(report)])
        ]
        # Raise an error if any invalid reports provided
        if any(incorrect_report_item_fields):
            msg = 'Report format: [{"name": "<report name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...]}, ...]'
            errors = ", ".join([
                f"Check {missing_fields} at report item {position + 1}"
                for position, *missing_fields in incorrect_report_item_fields
            ])
            raise TypeError(f'{msg}.\n {errors}')

        # Check if custom report names unique
        existing_names = set(map(itemgetter("name"), default_reports)).intersection(set(map(itemgetter("name"), custom_reports)))
        if existing_names:
            raise ValueError(f"Reports {existing_names} already exist as a default reports.")

        return custom_reports

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)

        reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
        if "custom_reports" in config:
            custom_reports = self._validate_custom_reports(json.loads(config["custom_reports"]), reports)
            reports += custom_reports

        # Generate and instantiate a list of dynamically defined streams: [ type(<name>, (Bases,), {attrs})(*args, **kwargs), ... ]
        # Base stream is considered to be a FullRefresh if `date` not present in dimensions, otherwise it considered to be an Incremental
        return [
            type(report["name"], (GoogleAnalyticsDataApiGenericStream if "date" in report.get("dimensions", []) else FullRefreshGoogleAnalyticsDataApi,), {})(
                config=dict(**config, metrics=report.get("metrics", []), dimensions=report.get("dimensions", [])), authenticator=authenticator
            )
            for report in reports
        ]
