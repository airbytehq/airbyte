#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import logging
import pkgutil
import uuid
from abc import ABC
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple

import dpath
import jsonschema
import requests
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.utils import AirbyteTracedException
from requests import HTTPError
from source_google_analytics_data_api import utils
from source_google_analytics_data_api.utils import DATE_FORMAT, WRONG_DIMENSIONS, WRONG_JSON_SYNTAX, WRONG_METRICS

from .api_quota import GoogleAnalyticsApiQuota
from .utils import (
    authenticator_class_map,
    check_invalid_property_error,
    check_no_property_error,
    get_dimensions_type,
    get_metrics_type,
    get_source_defined_primary_key,
    metrics_type_to_python,
)

# set the quota handler globaly since limitations are the same for all streams
# the initial values should be saved once and tracked for each stream, inclusivelly.
GoogleAnalyticsQuotaHandler: GoogleAnalyticsApiQuota = GoogleAnalyticsApiQuota()

LOOKBACK_WINDOW = datetime.timedelta(days=2)


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
                "dimensions": {m.get("apiName"): m for m in metadata.get("dimensions", [{}])},
                "metrics": {m.get("apiName"): m for m in metadata.get("metrics", [{}])},
            }

        return self._metadata


class GoogleAnalyticsDataApiAbstractStream(HttpStream, ABC):
    url_base = "https://analyticsdata.googleapis.com/v1beta/"
    http_method = "POST"
    raise_on_http_errors = True

    def __init__(self, *, config: Mapping[str, Any], page_size: int = 100_000, **kwargs):
        super().__init__(**kwargs)
        self._config = config
        self._source_defined_primary_key = get_source_defined_primary_key(self.name)
        # default value is 100 000 due to determination of maximum limit value in official documentation
        # https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination
        self._page_size = page_size

    @property
    def config(self):
        return self._config

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value: int):
        self._page_size = value

    # handle the quota errors with prepared values for:
    # `should_retry`, `backoff_time`, `raise_on_http_errors`, `stop_iter` based on quota scenario.
    @GoogleAnalyticsQuotaHandler.handle_quota()
    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == requests.codes.too_many_requests:
            setattr(self, "raise_on_http_errors", GoogleAnalyticsQuotaHandler.raise_on_http_errors)
            return GoogleAnalyticsQuotaHandler.should_retry
        # for all other cases not covered by GoogleAnalyticsQuotaHandler
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # handle the error with prepared GoogleAnalyticsQuotaHandler backoff value
        if response.status_code == requests.codes.too_many_requests:
            return GoogleAnalyticsQuotaHandler.backoff_time
        # for all other cases not covered by GoogleAnalyticsQuotaHandler
        return super().backoff_time(response)


class GoogleAnalyticsDataApiBaseStream(GoogleAnalyticsDataApiAbstractStream):
    """
    https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport
    """

    _record_date_format = "%Y%m%d"
    offset = 0

    metadata = MetadataDescriptor()

    @property
    def cursor_field(self) -> Optional[str]:
        return "date" if "date" in self.config.get("dimensions", []) else []

    @property
    def primary_key(self):
        pk = ["property_id"] + self.config.get("dimensions", [])
        if "cohort_spec" not in self.config and "date" not in pk:
            pk.append("startDate")
            pk.append("endDate")
        return pk

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
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": {
                "property_id": {"type": ["string"]},
            },
        }

        schema["properties"].update(
            {
                d: {"type": get_dimensions_type(d), "description": self.metadata["dimensions"].get(d, {}).get("description", d)}
                for d in self.config["dimensions"]
            }
        )
        # skipping startDate and endDate fields for cohort stream, because it doesn't support startDate and endDate fields
        if "cohort_spec" not in self.config and "date" not in self.config["dimensions"]:
            schema["properties"].update(
                {
                    "startDate": {"type": ["null", "string"], "format": "date"},
                    "endDate": {"type": ["null", "string"], "format": "date"},
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

        if "rowCount" in r:
            total_rows = r["rowCount"]

            if self.offset == 0:
                self.offset = self.page_size
            else:
                self.offset += self.page_size

            if total_rows <= self.offset:
                self.offset = 0
                return

            return {"offset": self.offset}

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

        dimensions = [h.get("name") for h in r.get("dimensionHeaders", [{}])]
        metrics = [h.get("name") for h in r.get("metricHeaders", [{}])]
        metrics_type_map = {h.get("name"): h.get("type") for h in r.get("metricHeaders", [{}])}

        for row in r.get("rows", []):
            record = {
                "property_id": self.config["property_id"],
                **self.add_dimensions(dimensions, row),
                **self.add_metrics(metrics, metrics_type_map, row),
            }

            # https://github.com/airbytehq/airbyte/pull/26283
            # We pass the uuid field for synchronizations which still have the old
            # configured_catalog with the old primary key. We need it to avoid of removal of rows
            # in the deduplication process. As soon as the customer press "refresh source schema"
            # this part is no longer needed.
            if self._source_defined_primary_key == [["uuid"]]:
                record["uuid"] = str(uuid.uuid4())

            if "cohort_spec" not in self.config and "date" not in record:
                record["startDate"] = stream_slice["startDate"]
                record["endDate"] = stream_slice["endDate"]
            yield record

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

        payload = {
            "metrics": [{"name": m} for m in self.config["metrics"]],
            "dimensions": [{"name": d} for d in self.config["dimensions"]],
            "dateRanges": [stream_slice],
            "returnPropertyQuota": True,
            "offset": str(0),
            "limit": str(self.page_size),
        }
        if next_page_token and next_page_token.get("offset") is not None:
            payload.update({"offset": str(next_page_token["offset"])})
        return payload

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        today: datetime.date = datetime.date.today()

        start_date = stream_state and stream_state.get(self.cursor_field)
        if start_date:
            start_date = utils.string_to_date(start_date, self._record_date_format, old_format=DATE_FORMAT)
            start_date -= LOOKBACK_WINDOW
            start_date = max(start_date, self.config["date_ranges_start_date"])
        else:
            start_date = self.config["date_ranges_start_date"]

        while start_date <= today:
            # stop producing slices if 429 + specific scenario is hit
            # see GoogleAnalyticsQuotaHandler for more info.
            if GoogleAnalyticsQuotaHandler.stop_iter:
                return []
            else:
                yield {
                    "startDate": utils.date_to_string(start_date),
                    "endDate": utils.date_to_string(min(start_date + datetime.timedelta(days=self.config["window_in_days"] - 1), today)),
                }
                start_date += datetime.timedelta(days=self.config["window_in_days"])


class PivotReport(GoogleAnalyticsDataApiBaseStream):
    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        payload = super().request_body_json(stream_state, stream_slice, next_page_token)

        # remove offset and limit fields according to their absence in
        # https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runPivotReport
        payload.pop("offset", None)
        payload.pop("limit", None)
        payload["pivots"] = self.config["pivots"]
        return payload

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"properties/{self.config['property_id']}:runPivotReport"


class CohortReportMixin:
    cursor_field = []

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [None]

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        # https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/CohortSpec#Cohort.FIELDS.date_range
        # In a cohort request, this dateRange is required and the dateRanges in the RunReportRequest or RunPivotReportRequest
        # must be unspecified.
        payload = super().request_body_json(stream_state, stream_slice, next_page_token)
        payload.pop("dateRanges")
        payload["cohortSpec"] = self.config["cohort_spec"]
        return payload


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
            if isinstance(config["custom_reports"], str):
                try:
                    config["custom_reports"] = json.loads(config["custom_reports"])
                    if not isinstance(config["custom_reports"], list):
                        raise ValueError
                except ValueError:
                    raise ConfigurationError(WRONG_JSON_SYNTAX)
        else:
            config["custom_reports"] = []

        schema = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/custom_reports_schema.json"))
        try:
            jsonschema.validate(instance=config["custom_reports"], schema=schema)
        except jsonschema.ValidationError as e:
            if message := check_no_property_error(e):
                raise ConfigurationError(message)
            if message := check_invalid_property_error(e):
                report_name = dpath.util.get(config["custom_reports"], str(e.absolute_path[0])).get("name")
                raise ConfigurationError(message.format(fields=e.message, report_name=report_name))

            key_path = "custom_reports"
            if e.path:
                key_path += "." + ".".join(map(str, e.path))
            raise ConfigurationError(f"{key_path}: {e.message}")

        existing_names = {r["name"] for r in config["custom_reports"]} & report_names
        if existing_names:
            existing_names = ", ".join(existing_names)
            raise ConfigurationError(f"custom_reports: {existing_names} already exist as a default report(s).")

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

        metadata = None
        try:
            # explicitly setting small page size for the check operation not to cause OOM issues
            stream = GoogleAnalyticsDataApiMetadataStream(config=config, authenticator=config["authenticator"])
            metadata = next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
        except HTTPError as e:
            error_list = [HTTPStatus.BAD_REQUEST, HTTPStatus.FORBIDDEN]
            if e.response.status_code in error_list:
                internal_message = f"Incorrect Property ID: {config['property_id']}"
                property_id_docs_url = (
                    "https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id"
                )
                message = f"Access was denied to the property ID entered. Check your access to the Property ID or use Google Analytics {property_id_docs_url} to find your Property ID."

                wrong_property_id_error = AirbyteTracedException(
                    message=message, internal_message=internal_message, failure_type=FailureType.config_error
                )
                raise wrong_property_id_error

        if not metadata:
            return False, "failed to get metadata, over quota, try later"

        dimensions = {d["apiName"] for d in metadata["dimensions"]}
        metrics = {d["apiName"] for d in metadata["metrics"]}

        for report in config["custom_reports"]:
            invalid_dimensions = set(report["dimensions"]) - dimensions
            if invalid_dimensions:
                invalid_dimensions = ", ".join(invalid_dimensions)
                return False, WRONG_DIMENSIONS.format(fields=invalid_dimensions, report_name=report["name"])
            invalid_metrics = set(report["metrics"]) - metrics
            if invalid_metrics:
                invalid_metrics = ", ".join(invalid_metrics)
                return False, WRONG_METRICS.format(fields=invalid_metrics, report_name=report["name"])
            report_stream = self.instantiate_report_class(report, config, page_size=100)
            # check if custom_report dimensions + metrics can be combined and report generated
            stream_slice = next(report_stream.stream_slices(sync_mode=SyncMode.full_refresh))
            next(report_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice), None)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
        config = self._validate_and_transform(config, report_names={r["name"] for r in reports})
        config["authenticator"] = self.get_authenticator(config)
        return [self.instantiate_report_class(report, config) for report in reports + config["custom_reports"]]

    @staticmethod
    def instantiate_report_class(report: dict, config: Mapping[str, Any], **extra_kwargs) -> GoogleAnalyticsDataApiBaseStream:
        cohort_spec = report.get("cohortSpec")
        pivots = report.get("pivots")
        stream_config = {
            "metrics": report["metrics"],
            "dimensions": report["dimensions"],
            **config,
        }
        report_class_tuple = (GoogleAnalyticsDataApiBaseStream,)
        if pivots:
            stream_config["pivots"] = pivots
            report_class_tuple = (PivotReport,)
        if cohort_spec:
            stream_config["cohort_spec"] = cohort_spec
            report_class_tuple = (CohortReportMixin, *report_class_tuple)
        return type(report["name"], report_class_tuple, {})(config=stream_config, authenticator=config["authenticator"], **extra_kwargs)
