#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import datetime
import json
import logging
import pkgutil
import re
import uuid
from abc import ABC
from datetime import timedelta
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Type, Union

import dpath
import jsonschema
import pendulum
import requests
from requests import HTTPError

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy, ErrorHandler, HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution
from airbyte_cdk.sources.streams.http.exceptions import BaseBackoffException
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors
from airbyte_cdk.utils import AirbyteTracedException
from source_google_analytics_data_api import utils
from source_google_analytics_data_api.google_analytics_data_api_base_error_mapping import get_google_analytics_data_api_base_error_mapping
from source_google_analytics_data_api.google_analytics_data_api_metadata_error_mapping import (
    get_google_analytics_data_api_metadata_error_mapping,
)
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
    serialize_to_date_string,
    transform_json,
)


# set the quota handler globally since limitations are the same for all streams
# the initial values should be saved once and tracked for each stream, inclusively.
GoogleAnalyticsQuotaHandler: GoogleAnalyticsApiQuota = GoogleAnalyticsApiQuota()

DEFAULT_LOOKBACK_WINDOW = 2


class ConfigurationError(Exception):
    pass


class MetadataDescriptor:
    def __init__(self):
        self._metadata = None

    def __get__(self, instance, owner):
        if not self._metadata:
            stream = GoogleAnalyticsDataApiMetadataStream(config=instance.config, authenticator=instance.config["authenticator"])

            metadata = None
            try:
                metadata = next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            except HTTPError as e:
                if e.response.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
                    internal_message = "Unauthorized error reached."
                    message = "Can not get metadata with unauthorized credentials. Try to re-authenticate in source settings."

                    unauthorized_error = AirbyteTracedException(
                        message=message, internal_message=internal_message, failure_type=FailureType.config_error
                    )
                    raise unauthorized_error

            if not metadata:
                raise Exception("failed to get metadata, over quota, try later")
            self._metadata = {
                "dimensions": {m.get("apiName"): m for m in metadata.get("dimensions", [{}])},
                "metrics": {m.get("apiName"): m for m in metadata.get("metrics", [{}])},
            }

        return self._metadata


class GoogleAnalyticsDataApiBackoffStrategy(BackoffStrategy):
    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            # handle the error with prepared GoogleAnalyticsQuotaHandler backoff value
            if response_or_exception.status_code == requests.codes.too_many_requests:
                return GoogleAnalyticsQuotaHandler.backoff_time
        return None


class GoogleAnalyticsDatApiErrorHandler(HttpStatusErrorHandler):
    QUOTA_RECOVERY_TIME = 3600

    def __init__(
        self,
        logger: logging.Logger,
        error_mapping: Optional[Mapping[Union[int, str, type[Exception]], ErrorResolution]] = None,
    ) -> None:
        super().__init__(
            logger=logger,
            error_mapping=error_mapping,
            max_retries=5,
            max_time=timedelta(seconds=GoogleAnalyticsDatApiErrorHandler.QUOTA_RECOVERY_TIME),
        )

    @GoogleAnalyticsQuotaHandler.handle_quota()
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if not isinstance(response_or_exception, Exception) and response_or_exception.status_code == requests.codes.too_many_requests:
            return ErrorResolution(
                response_action=GoogleAnalyticsQuotaHandler.response_action,
                failure_type=FailureType.transient_error,
                error_message=GoogleAnalyticsQuotaHandler.error_message,
            )
        return super().interpret_response(response_or_exception)


class GoogleAnalyticsDataApiAbstractStream(HttpStream, ABC):
    url_base = "https://analyticsdata.googleapis.com/v1beta/"
    http_method = "POST"

    def __init__(self, *, config: Mapping[str, Any], page_size: int = 100_000, **kwargs):
        self._config = config
        self._source_defined_primary_key = get_source_defined_primary_key(self.name)
        # default value is 100 000 due to determination of maximum limit value in official documentation
        # https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination
        self._page_size = page_size
        super().__init__(**kwargs)

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
    def get_backoff_strategy(self) -> Optional[Union[BackoffStrategy, List[BackoffStrategy]]]:
        return GoogleAnalyticsDataApiBackoffStrategy()

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return GoogleAnalyticsDatApiErrorHandler(logger=self.logger, error_mapping=self.get_error_mapping())

    def get_error_mapping(self) -> Mapping[Union[int, str, Type[Exception]], ErrorResolution]:
        return DEFAULT_ERROR_MAPPING


class GoogleAnalyticsDataApiBaseStream(GoogleAnalyticsDataApiAbstractStream):
    """
    https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport
    """

    _record_date_format = "%Y%m%d"
    offset = 0

    metadata = MetadataDescriptor()

    def get_error_mapping(self) -> Mapping[Union[int, str, Type[Exception]], ErrorResolution]:
        return get_google_analytics_data_api_base_error_mapping(self.name)

    @property
    def cursor_field(self) -> Optional[str]:
        date_fields = ["date", "yearWeek", "yearMonth", "year"]
        for field in date_fields:
            if field in self.config.get("dimensions", []):
                return field
        return []

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

            # Google Analytics sometimes returns float for integer metrics.
            # So this is a workaround for this issue: https://github.com/airbytehq/oncall/issues/4130
            if python_type == int:
                return metric_name, round(float(metric_value))
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
                d: {
                    "type": get_dimensions_type(d),
                    "description": self.metadata["dimensions"].get(d, {}).get("description", d),
                }
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

        # change the type of `conversions:*` metrics from int to float: https://github.com/airbytehq/oncall/issues/4130
        if self.config.get("convert_conversions_event", False):
            for schema_field in schema["properties"]:
                if schema_field.startswith("conversions:"):
                    schema["properties"][schema_field]["type"] = ["null", "float"]

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
        metrics_type_map = {h.get("name"): h.get("type") for h in r.get("metricHeaders", [{}]) if "name" in h}

        # change the type of `conversions:*` metrics from int to float: https://github.com/airbytehq/oncall/issues/4130
        if self.config.get("convert_conversions_event", False):
            for schema_field in metrics_type_map:
                if schema_field.startswith("conversions:"):
                    metrics_type_map[schema_field] = "TYPE_FLOAT"

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

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        if not self.cursor_field:
            # Some implementations of the GoogleAnalyticsDataApiBaseStream might not have a cursor because it's
            # based on the `dimensions` config setting. This results in a full_refresh only stream that implements
            # get_updated_state(), but does not define a cursor. For this scenario, there is no state value to extract
            return {}

        updated_state = (
            utils.string_to_date(latest_record[self.cursor_field], self._record_date_format)
            if self.cursor_field == "date"
            else latest_record[self.cursor_field]
        )
        stream_state_value = current_stream_state.get(self.cursor_field)
        if stream_state_value:
            stream_state_value = (
                utils.string_to_date(stream_state_value, self._record_date_format, old_format=DATE_FORMAT)
                if self.cursor_field == "date"
                else stream_state_value
            )
            updated_state = max(updated_state, stream_state_value)
        current_stream_state[self.cursor_field] = (
            updated_state.strftime(self._record_date_format) if self.cursor_field == "date" else updated_state
        )
        return current_stream_state

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        if stream_slice and "startDate" in stream_slice and "endDate" in stream_slice:
            date_range = {"startDate": stream_slice["startDate"], "endDate": stream_slice["endDate"]}
        else:
            date_range = stream_slice
        payload = {
            "metrics": [{"name": m} for m in self.config["metrics"]],
            "dimensions": [{"name": d} for d in self.config["dimensions"]],
            "dateRanges": [date_range],
            "returnPropertyQuota": True,
            "offset": str(0),
            "limit": str(self.page_size),
            "keepEmptyRows": self.config.get("keep_empty_rows", False),
        }

        dimension_filter = self.config.get("dimensionFilter")
        if dimension_filter:
            payload.update({"dimensionFilter": dimension_filter})

        metrics_filter = self.config.get("metricsFilter")
        if metrics_filter:
            payload.update({"metricsFilter": metrics_filter})

        if next_page_token and next_page_token.get("offset") is not None:
            payload.update({"offset": str(next_page_token["offset"])})
        return payload

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        today: datetime.date = datetime.date.today()
        start_date = None
        if self.cursor_field:
            start_date = stream_state and stream_state.get(self.cursor_field)
        if start_date:
            start_date = (
                serialize_to_date_string(start_date, DATE_FORMAT, self.cursor_field) if not self.cursor_field == "date" else start_date
            )
            start_date = utils.string_to_date(start_date, self._record_date_format, old_format=DATE_FORMAT)
            start_date = start_date - datetime.timedelta(days=self.config.get("lookback_window", DEFAULT_LOOKBACK_WINDOW))
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
        yield from [{}]

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

    def get_error_mapping(self):
        return get_google_analytics_data_api_metadata_error_mapping(self.config.get("property_id"))


class SourceGoogleAnalyticsDataApi(AbstractSource):
    @property
    def default_date_ranges_start_date(self) -> str:
        # set default date ranges start date to 2 years ago
        return pendulum.now(tz="UTC").subtract(years=2).format("YYYY-MM-DD")

    @property
    def raise_exception_on_missing_stream(self) -> bool:
        # reference issue: https://github.com/airbytehq/airbyte-internal-issues/issues/8315
        # This has been added, because there is a risk of removing the `Custom Stream` from the `input configuration`,
        # which brings the error about `missing stream` present in the CATALOG but not in the `input configuration`.
        return False

    def _validate_and_transform_start_date(self, start_date: str) -> datetime.date:
        start_date = self.default_date_ranges_start_date if not start_date else start_date

        try:
            start_date = utils.string_to_date(start_date)
        except ValueError as e:
            raise ConfigurationError(str(e))

        return start_date

    def _validate_custom_reports(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if "custom_reports_array" in config:
            if isinstance(config["custom_reports_array"], str):
                try:
                    config["custom_reports_array"] = json.loads(config["custom_reports_array"])
                    if not isinstance(config["custom_reports_array"], list):
                        raise ValueError
                except ValueError:
                    raise ConfigurationError(WRONG_JSON_SYNTAX)
        else:
            config["custom_reports_array"] = []

        return config

    def _validate_and_transform(self, config: Mapping[str, Any], report_names: Set[str]):
        config = self._validate_custom_reports(config)

        schema = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/custom_reports_schema.json"))
        try:
            jsonschema.validate(instance=config["custom_reports_array"], schema=schema)
        except jsonschema.ValidationError as e:
            if message := check_no_property_error(e):
                raise ConfigurationError(message)
            if message := check_invalid_property_error(e):
                report_name = dpath.get(config["custom_reports_array"], str(e.absolute_path[0])).get("name")
                raise ConfigurationError(message.format(fields=e.message, report_name=report_name))

        existing_names = {r["name"] for r in config["custom_reports_array"]} & report_names
        if existing_names:
            existing_names = ", ".join(existing_names)
            raise ConfigurationError(f"Custom reports: {existing_names} already exist as a default report(s).")

        if "credentials_json" in config["credentials"]:
            try:
                config["credentials"]["credentials_json"] = json.loads(config["credentials"]["credentials_json"])
            except ValueError:
                raise ConfigurationError("credentials.credentials_json is not valid JSON")

        config["date_ranges_start_date"] = self._validate_and_transform_start_date(config.get("date_ranges_start_date"))

        if not config.get("window_in_days"):
            source_spec = self.spec(logging.getLogger("airbyte"))
            config["window_in_days"] = source_spec.connectionSpecification["properties"]["window_in_days"]["default"]

        return config

    def get_authenticator(self, config: Mapping[str, Any]):
        credentials = config["credentials"]
        authenticator_class, get_credentials = authenticator_class_map[credentials["auth_type"]]
        return authenticator_class(**get_credentials(credentials))

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        for property_id in config["property_ids"]:
            reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
            try:
                config = self._validate_and_transform(config, report_names={r["name"] for r in reports})
            except ConfigurationError as e:
                return False, str(e)
            config["authenticator"] = self.get_authenticator(config)

            _config = config.copy()
            _config["property_id"] = property_id

            metadata = None
            try:
                # explicitly setting small page size for the check operation not to cause OOM issues
                stream = GoogleAnalyticsDataApiMetadataStream(config=_config, authenticator=_config["authenticator"])
                metadata = next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            except (MessageRepresentationAirbyteTracedErrors, BaseBackoffException) as ex:
                if hasattr(ex, "failure_type") and ex.failure_type == FailureType.config_error:
                    # bad request and forbidden are set in mapper as config errors
                    raise ex
                logger.error(f"Check failed", exc_info=ex)

            if not metadata:
                return False, "Failed to get metadata, over quota, try later"

            dimensions = {d["apiName"] for d in metadata["dimensions"]}
            metrics = {d["apiName"] for d in metadata["metrics"]}

            for report in _config["custom_reports_array"]:
                # Check if custom report dimensions supported. Compare them with dimensions provided by GA API
                invalid_dimensions = set(report["dimensions"]) - dimensions
                if invalid_dimensions:
                    invalid_dimensions = ", ".join(invalid_dimensions)
                    return False, WRONG_DIMENSIONS.format(fields=invalid_dimensions, report_name=report["name"])

                # Check if custom report metrics supported. Compare them with metrics provided by GA API
                invalid_metrics = set(report["metrics"]) - metrics
                if invalid_metrics:
                    invalid_metrics = ", ".join(invalid_metrics)
                    return False, WRONG_METRICS.format(fields=invalid_metrics, report_name=report["name"])

                report_stream = self.instantiate_report_class(report, False, _config, page_size=100)
                # check if custom_report dimensions + metrics can be combined and report generated
                try:
                    stream_slice = next(report_stream.stream_slices(sync_mode=SyncMode.full_refresh))
                    next(report_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice), None)
                except MessageRepresentationAirbyteTracedErrors as e:
                    return False, f"{e.message} {self._extract_internal_message_error_response(e.internal_message)}"

            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        reports = json.loads(pkgutil.get_data("source_google_analytics_data_api", "defaults/default_reports.json"))
        config = self._validate_and_transform(config, report_names={r["name"] for r in reports})
        config["authenticator"] = self.get_authenticator(config)
        return [stream for report in reports + config["custom_reports_array"] for stream in self.instantiate_report_streams(report, config)]

    def instantiate_report_streams(
        self, report: dict, config: Mapping[str, Any], **extra_kwargs
    ) -> Iterable[GoogleAnalyticsDataApiBaseStream]:
        add_name_suffix = False
        for property_id in config["property_ids"]:
            yield self.instantiate_report_class(
                report=report, add_name_suffix=add_name_suffix, config={**config, "property_id": property_id}
            )
            # Append property ID to stream name only for the second and subsequent properties.
            # This will make a release non-breaking for users with a single property.
            # This is a temporary solution until https://github.com/airbytehq/airbyte/issues/30926 is implemented.
            add_name_suffix = True

    @staticmethod
    def instantiate_report_class(
        report: dict, add_name_suffix: bool, config: Mapping[str, Any], **extra_kwargs
    ) -> GoogleAnalyticsDataApiBaseStream:
        cohort_spec = report.get("cohortSpec", {})
        pivots = report.get("pivots")
        stream_config = {
            **config,
            "metrics": report["metrics"],
            "dimensions": report["dimensions"],
            "dimensionFilter": transform_json(report.get("dimensionFilter", {})),
            "metricsFilter": transform_json(report.get("metricsFilter", {})),
        }
        report_class_tuple = (GoogleAnalyticsDataApiBaseStream,)
        if pivots:
            stream_config["pivots"] = pivots
            report_class_tuple = (PivotReport,)
        if cohort_spec.pop("enabled", "") == "true":
            stream_config["cohort_spec"] = cohort_spec
            report_class_tuple = (CohortReportMixin, *report_class_tuple)
        name = report["name"]
        if add_name_suffix:
            name = f"{name}Property{config['property_id']}"
        return type(name, report_class_tuple, {})(config=stream_config, authenticator=config["authenticator"], **extra_kwargs)

    @staticmethod
    def _extract_internal_message_error_response(message):
        pattern = r"error message '(.*?)'"
        match = re.search(pattern, message)
        if match:
            error_message = match.group(1)
            return error_message
        return ""
