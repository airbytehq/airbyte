#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
import pkgutil
import time
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from .auth import CredentialsCraftAuthenticator, GoogleAnalyticsServiceOauth2Authenticator

DATA_IS_NOT_GOLDEN_MSG = "Google Analytics data is not golden. Future requests may return different data."

RESULT_IS_SAMPLED_MSG = (
    "Google Analytics data is sampled. Consider using a smaller window_in_days parameter. "
    "For more info check https://developers.google.com/analytics/devguides/reporting/core/v4/basics#sampling"
)


class GoogleAnalyticsV4TypesList(HttpStream):
    """
    Provides functionality to fetch the valid (dimensions, metrics) for the Analytics Reporting API and their data
    types.
    """

    primary_key = None

    # Link to query the metadata for available metrics and dimensions.
    # Those are not provided in the Analytics Reporting API V4.
    # Column id completely match for v3 and v4.
    url_base = "https://www.googleapis.com/analytics/v3/metadata/ga/columns"

    def path(self, **kwargs: Any) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Abstractmethod HTTPStream CDK dependency"""
        return None

    def parse_response(self, response: requests.Response, **kwargs: Any) -> Tuple[dict, dict]:
        """
        Returns a map of (dimensions, metrics) hashes, example:
          ({"ga:userType": "STRING", "ga:sessionCount": "STRING"}, {"ga:pageviewsPerSession": "FLOAT", "ga:sessions": "INTEGER"})

          Each available dimension can be found in dimensions with its data type
            as the value. e.g. dimensions['ga:userType'] == STRING

          Each available metric can be found in metrics with its data type
            as the value. e.g. metrics['ga:sessions'] == INTEGER
        """
        metrics = {}
        dimensions = {}

        results = response.json()

        columns = results.get("items", [])

        for column in columns:
            column_attributes = column.get("attributes", [])

            column_name = column.get("id")
            column_type = column_attributes.get("type")
            column_data_type = column_attributes.get("dataType")

            if column_type == "METRIC":
                metrics[column_name] = column_data_type
            elif column_type == "DIMENSION":
                dimensions[column_name] = column_data_type
            else:
                raise Exception(f"Unsupported column type {column_type}.")

        return dimensions, metrics


class GoogleAnalyticsV4Stream(HttpStream, ABC):
    primary_key = None
    http_method = "POST"

    # The Analytics Core Reporting API returns a maximum of 100,000 rows per request.
    # https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet?hl=en
    page_size = 100000

    url_base = "https://analyticsreporting.googleapis.com/v4/"
    report_field = "reports"

    map_type = dict(INTEGER="integer", FLOAT="number",
                    PERCENT="number", TIME="number")

    def __init__(self, config: MutableMapping):
        super().__init__(authenticator=config["authenticator"])
        self.start_date = config.get("start_date")
        self.end_date = config.get('end_date')

        self.window_in_days: int = config.get("window_in_days", 1)
        self.view_id = config["view_id"]
        self.metrics = config["metrics"]
        self.dimensions = config["dimensions"]
        self._config = config
        self.dimensions_ref, self.metrics_ref = GoogleAnalyticsV4TypesList(
        ).read_records(sync_mode=None)
        self.client_name = config.get('client_name', "")
        self.product_name = config.get('product_name', '')
        self.custom_constants = config.get('custom_constants', {})

        self._raise_on_http_errors: bool = True

    @property
    def state_checkpoint_interval(self) -> int:
        return self.window_in_days

    @staticmethod
    def to_datetime_str(date: datetime) -> str:
        """
        Custom method.
        Returns the formated datetime string.
        :: Output example: '2021-07-15 07' FORMAT : "%Y-%m-%d"
        """
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def to_iso_datetime_str(date: str) -> str:
        return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")

    def path(self, **kwargs: Any) -> str:
        # need add './' for correct urllib.parse.urljoin work due to path contains ':'
        return "./reports:batchGet"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("nextPageToken")
        if next_page:
            return {"pageToken": next_page}

    def should_retry(self, response: requests.Response) -> bool:
        """When the connector gets a custom report which has unknown metric(s) or dimension(s)
        and API returns an error with 400 code, the connector ignores an error with 400 code
        to finish successfully sync and inform the user about an error in logs with an error message."""

        if response.status_code == 400:
            self.logger.info(f"{response.json()['error']['message']}")
            self._raise_on_http_errors = False

        result: bool = HttpStream.should_retry(self, response)
        return result

    @property
    def raise_on_http_errors(self) -> bool:
        return self._raise_on_http_errors

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs: Any
    ) -> Optional[Mapping]:

        metrics = [{"expression": metric} for metric in self.metrics]
        dimensions = [{"name": dimension} for dimension in self.dimensions]

        request_body = {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": [stream_slice],
                    "pageSize": self.page_size,
                    "metrics": metrics,
                    "dimensions": dimensions,
                }
            ]
        }

        if next_page_token:
            request_body["reportRequests"][0].update(next_page_token)
        return request_body

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Override get_json_schema CDK method to retrieve the schema information for GoogleAnalyticsV4 Object dynamically.
        """

        schema: Dict[str, Any] = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": False,
            "properties": {
                "view_id": {"type": ["string"]},
            },
        }

        # Add the dimensions to the schema
        for dimension in self.dimensions:
            data_type = self.lookup_data_type("dimension", dimension)
            data_format = self.lookup_data_format(dimension)
            dimension = dimension.replace("ga:", "ga_")

            dimension_data: Dict[str, Any] = {"type": [data_type]}
            if data_format:
                dimension_data["format"] = data_format
            schema["properties"][dimension] = dimension_data

        # Add the metrics to the schema
        for metric in self.metrics:
            data_type = self.lookup_data_type("metric", metric)
            data_format = self.lookup_data_format(metric)
            metric = metric.replace("ga:", "ga_")

            # metrics are allowed to also have null values
            metric_data: Dict[str, Any] = {"type": ["null", data_type]}
            if data_format:
                metric_data["format"] = data_format
            schema["properties"][metric] = metric_data
        schema["properties"]["isDataGolden"] = {"type": "boolean"}

        # Add custom constants to schema

        extra_properties = ["__productName", "__clientName"]
        custom_keys = self.custom_constants.keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs: Any) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: [{
            "startDate": "2020-01-01",
            "endDate": "2021-01-02"
            },
            {
            "startDate": "2020-01-03",
            "endDate": "2021-01-04"
            },
            ...]
        """
        if self._config['use_backward_compatibility']:
            if stream_state:
                prev_end_date = pendulum.parse(
                    stream_state.get(self.cursor_field)).date()
                # do not include previous `end_date`
                self.start_date = prev_end_date.add(days=1)
            # always resync 2 previous days to be sure data is golden
            # https://support.google.com/analytics/answer/1070983?hl=en#DataProcessingLatency&zippy=%2Cin-this-article
            # https://github.com/airbytehq/airbyte/issues/12013#issuecomment-1111255503
            self.start_date = self.start_date.subtract(days=2)

        date_slices = []
        slice_start_date = self.start_date
        while slice_start_date <= self.end_date:
            slice_end_date = slice_start_date.add(days=self.window_in_days)
            # limit the slice range with end_date
            slice_end_date = min(slice_end_date, self.end_date)
            date_slices.append({"startDate": self.to_datetime_str(
                slice_start_date), "endDate": self.to_datetime_str(slice_end_date)})
            # start next slice 1 day after previous slice ended to prevent duplicate reads
            slice_start_date = slice_end_date.add(days=1)
        return date_slices or [None]

    @staticmethod
    def report_rows(report_body: MutableMapping[Any, Any]) -> List[MutableMapping[Any, Any]]:
        return report_body.get("data", {}).get("rows", [])

    def lookup_data_type(self, field_type: str, attribute: str) -> str:
        """
        Get the data type of a metric or a dimension
        """
        try:
            if field_type == "dimension":
                if attribute.startswith(("ga:dimension", "ga:customVarName", "ga:customVarValue")):
                    # Custom Google Analytics Dimensions that are not part of self.dimensions_ref. They are always
                    # strings
                    return "string"

                attr_type = self.dimensions_ref[attribute]
            elif field_type == "metric":
                # Custom Google Analytics Metrics {ga:goalXXStarts, ga:metricXX, ... }
                # We always treat them as strings as we can not be sure of their data type
                if attribute.startswith("ga:goal") and attribute.endswith(
                    ("Starts", "Completions", "Value",
                     "ConversionRate", "Abandons", "AbandonRate")
                ):
                    return "string"
                elif attribute.startswith("ga:searchGoal") and attribute.endswith("ConversionRate"):
                    # Custom Google Analytics Metrics ga:searchGoalXXConversionRate
                    return "string"
                elif attribute.startswith(("ga:metric", "ga:calcMetric")):
                    return "string"

                attr_type = self.metrics_ref[attribute]
            else:
                attr_type = None
                self.logger.error(f"Unsupported GA type: {field_type}")
        except KeyError:
            attr_type = None
            self.logger.error(f"Unsupported GA {field_type}: {attribute}")

        return self.map_type.get(attr_type, "string")

    @staticmethod
    def lookup_data_format(attribute: str) -> Union[str, None]:
        if attribute == "ga:date":
            return "date"

    def convert_to_type(self, header: str, value: Any, data_type: str) -> Any:
        if data_type == "integer":
            return int(value)
        if data_type == "number":
            return float(value)
        if header == "ga:date":
            return self.to_iso_datetime_str(value)
        return value

    def parse_response(self, response: requests.Response, **kwargs: Any) -> Iterable[Mapping]:
        """
        Default response:

        {
            "reports": [
                {
                    "columnHeader": {
                        "metricHeader": {
                            "metricHeaderEntries": [
                                {
                                    "name": "ga:users",
                                    "type": "INTEGER"
                                }
                            ]
                        }
                    },
                    "data": {
                        "isDataGolden": true,
                        "maximums": [
                            {
                                "values": [
                                    "98"
                                ]
                            }
                        ],
                        "minimums": [
                            {
                                "values": [
                                    "98"
                                ]
                            }
                        ],
                        "rowCount": 1,
                        "rows": [
                            {
                                "metrics": [
                                    {
                                        "values": [
                                            "98"
                                        ]
                                    }
                                ]
                            }
                        ],
                        "totals": [
                            {
                                "values": [
                                    "98"
                                ]
                            }
                        ]
                    }
                }
            ]
        }

        Return record which is a map of metric and dimension names and values, like:

        record = {
                    "view_id":"1111111"
                    "ga_date":"20210212",
                    "ga_users":3,
                    "ga_newUsers":2,
                    "ga_sessions":7,
                    "ga_sessionsPerUser":8.0,
                    "ga_avgSessionDuration":201.0,
                    "ga_pageviews":43,
                    "ga_pageviewsPerSession":12.5,
                    "ga_avgTimeOnPage":83.14035087719298,
                    "ga_bounceRate":0.0,
                    "ga_exitRate":6.523809523809524
        }
        """
        json_response = response.json()
        reports = json_response.get(self.report_field, [])

        for report in reports:
            column_header = report.get("columnHeader", {})
            dimension_headers = column_header.get("dimensions", [])
            metric_headers = column_header.get(
                "metricHeader", {}).get("metricHeaderEntries", [])

            self.check_for_sampled_result(report.get("data", {}))

            for row in self.report_rows(report):
                record = {}
                dimensions = row.get("dimensions", [])
                metrics = row.get("metrics", [])

                for header, dimension in zip(dimension_headers, dimensions):
                    data_type = self.lookup_data_type("dimension", header)
                    value = self.convert_to_type(header, dimension, data_type)

                    record[header.replace("ga:", "ga_")] = value

                for i, values in enumerate(metrics):
                    for metric_header, value in zip(metric_headers, values.get("values")):
                        metric_name = metric_header.get("name")
                        metric_type = self.lookup_data_type(
                            "metric", metric_name)
                        value = self.convert_to_type(
                            metric_name, value, metric_type)

                        record[metric_name.replace("ga:", "ga_")] = value

                record["view_id"] = self.view_id
                record["isDataGolden"] = report.get(
                    "data", {}).get("isDataGolden", False)
                yield self.add_constants_to_record(record)

    def add_constants_to_record(self, record):
        constants = {
            "__productName": self.product_name,
            "__clientName": self.client_name,
        }
        constants.update(self.custom_constants)
        record.update(constants)
        return record

    def check_for_sampled_result(self, data: Mapping) -> None:
        if not data.get("isDataGolden", False):
            self.logger.warning(DATA_IS_NOT_GOLDEN_MSG)
        if data.get("samplesReadCounts", False):
            self.logger.warning(RESULT_IS_SAMPLED_MSG)


class GoogleAnalyticsV4IncrementalObjectsBase(GoogleAnalyticsV4Stream):
    cursor_field = "ga_date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            return []
        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)


class TestStreamConnection(GoogleAnalyticsV4Stream):
    """
    Test the connectivity and permissions to read the data from the stream.
    Because of the nature of the connector, the streams are created dynamicaly.
    We declare the static stream like this to be able to test out the prmissions to read the particular view_id."""

    page_size = 1

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """For test reading pagination is not required"""
        return None

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs: Any) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override this method to fetch records from start_date up to now for testing case
        """
        return [{"startDate": self.to_datetime_str(self.start_date), "endDate": self.to_datetime_str(self.end_date)}]


class SourceGoogleAnalyticsV4(AbstractSource):
    """Google Analytics lets you analyze data about customer engagement with your website or application."""

    @staticmethod
    def get_authenticator(config: Mapping) -> Oauth2Authenticator:
        # backwards compatibility, credentials_json used to be in the top level of the connector
        if config.get("credentials_json"):
            return GoogleAnalyticsServiceOauth2Authenticator(config)

        auth_params = config["credentials"]

        if auth_params["auth_type"] == "Service" or auth_params.get("credentials_json"):
            return GoogleAnalyticsServiceOauth2Authenticator(auth_params)
        elif auth_params["auth_type"] == "CredentialsCraftAuth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=auth_params['credentials_craft_host'],
                credentials_craft_token=auth_params['credentials_craft_token'],
                credentials_craft_token_id=auth_params['credentials_craft_token_id'],
            )
        elif auth_params["auth_type"] == "Client":
            return Oauth2Authenticator(
                token_refresh_endpoint="https://oauth2.googleapis.com/token",
                client_secret=auth_params["client_secret"],
                client_id=auth_params["client_id"],
                refresh_token=auth_params["refresh_token"],
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )
        else:
            raise Exception(
                "Invalid auth_type: Avaliable: Service, Client, CredentialsCraftAuth")

    def transform_config_dates(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # Valid dates options: start_date + end_date, start_date (to keep previous dates behavior), last_days
        config['use_backward_compatibility'] = False
        if config.get('start_date') and config.get('end_date'):
            config['start_date'] = pendulum.parse(config['start_date']).date()
            config['end_date'] = pendulum.parse(config['end_date']).date()
        elif config.get('start_date') and not config.get('end_date'):
            config['use_backward_compatibility'] = True
            config['start_date'] = pendulum.parse(config['start_date']).date()
            config['end_date'] = pendulum.now().date()
        elif config.get('last_days'):
            config['start_date'] = pendulum.now().subtract(
                days=config['last_days']-1).date()
            config['end_date'] = pendulum.now().date()
        elif not config.get('start_date') and not config.get('end_date') and not config.get('last_days'):
            config['start_date'] = pendulum.now().subtract(
                days=4).date()
            config['end_date'] = pendulum.now().date()
        else:
            raise Exception('Invalid dates format or options')
        return config

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        authenticator = self.get_authenticator(config)

        config = self.transform_config_dates(config)
        config["authenticator"] = authenticator
        reports = json.loads(pkgutil.get_data(
            "source_google_analytics_v4", "defaults/default_reports.json"))

        if config.get("custom_reports"):
            custom_reports = json.loads(config["custom_reports"])
            reports += custom_reports

        config['custom_constants'] = json.loads(
            config.get('custom_json', '{}'))

        config["ga_streams"] = reports
        return config

    def check_connection(self, logger: logging.Logger, config: MutableMapping) -> Tuple[bool, Any]:
        # declare additional variables
        try:
            json.loads(config['custom_json'])
        except:
            return False, 'Custom JSON invalid format'

        # Invalid dates options: (start_date or end_date) + last_days, end_date only
        if ((config.get('start_date') or config.get('end_date')) and config.get('last_days')) \
                or ((not config.get('start_date') and not config.get('last_days')) and config.get('end_date')):
            return False, "You must specify either Date From and Date To or just Last Days (or only Date From for backward dates incremental behavior)"

        config = self.transform_config_dates(config)

        authenticator = self.get_authenticator(config)
        if isinstance(authenticator, CredentialsCraftAuthenticator):
            auth_check_result = authenticator.check_connection()
            if not auth_check_result[0]:
                return auth_check_result

        config["authenticator"] = authenticator
        config["metrics"] = ["ga:14dayUsers"]
        config["dimensions"] = ["ga:date"]

        try:
            # test the eligibility of custom_reports input
            custom_reports = config.get("custom_reports")
            if custom_reports:
                json.loads(custom_reports)

            # Read records to check the reading permissions
            read_check = list(TestStreamConnection(
                config).read_records(sync_mode=None))
            if read_check:
                return True, None
            return (
                False,
                f"Please check the permissions for the requested view_id: {config['view_id']}. Cannot retrieve data from that view ID.",
            )

        except ValueError as e:
            return False, f"Invalid custom reports json structure. {e}"

        except requests.exceptions.RequestException as e:
            error_msg = e.response.json().get("error")
            if e.response.status_code == 403:
                return False, f"Please check the permissions for the requested view_id: {config['view_id']}. {error_msg}"
            else:
                return False, f"{error_msg}"

    def streams(self, config: MutableMapping[str, Any]) -> List[Stream]:
        streams: List[GoogleAnalyticsV4Stream] = []

        config = self.transform_config(config)

        for stream in config["ga_streams"]:
            config["metrics"] = stream["metrics"]
            config["dimensions"] = stream["dimensions"]

            # construct GAReadStreams sub-class for each stream
            stream_name = stream["name"]
            stream_bases = (GoogleAnalyticsV4Stream,)

            if "ga:date" in stream["dimensions"] and config['use_backward_compatibility']:
                stream_bases = (GoogleAnalyticsV4IncrementalObjectsBase,)

            stream_class = type(stream_name, stream_bases, {})

            # instantiate a stream with config
            stream_instance = stream_class(config)
            streams.append(stream_instance)

        return streams
