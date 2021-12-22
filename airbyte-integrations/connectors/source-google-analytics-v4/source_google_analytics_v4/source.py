#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import pkgutil
import time
from abc import ABC
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import jwt
import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator


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

    def path(self, **kwargs) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """Abstractmethod HTTPStream CDK dependency"""
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Tuple[dict, dict]:
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
    data_fields = ["data", "rows"]

    map_type = dict(INTEGER="integer", FLOAT="number", PERCENT="number", TIME="number")

    def __init__(self, config: Dict):
        super().__init__(authenticator=config["authenticator"])
        self.start_date = config["start_date"]
        self.window_in_days = config.get("window_in_days", 90)
        self.view_id = config["view_id"]
        self.metrics = config["metrics"]
        self.dimensions = config["dimensions"]
        self._config = config
        self.dimensions_ref, self.metrics_ref = GoogleAnalyticsV4TypesList().read_records(sync_mode=None)

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

    def path(self, **kwargs) -> str:
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
            self.raise_on_http_errors = False

        return super().should_retry(response)

    def raise_on_http_errors(self) -> bool:
        return True

    def request_body_json(
        self, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
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

        schema = {
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

            dimension_data = {"type": [data_type]}
            if data_format:
                dimension_data["format"] = data_format
            schema["properties"][dimension] = dimension_data

        # Add the metrics to the schema
        for metric in self.metrics:
            data_type = self.lookup_data_type("metric", metric)
            data_format = self.lookup_data_format(metric)
            metric = metric.replace("ga:", "ga_")

            # metrics are allowed to also have null values
            metric_data = {"type": ["null", data_type]}
            if data_format:
                metric_data["format"] = data_format
            schema["properties"][metric] = metric_data

        return schema

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
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

        start_date = pendulum.parse(self.start_date).date()
        end_date = pendulum.now().date()

        # Determine stream_state, if no stream_state we use start_date
        if stream_state:
            start_date = pendulum.parse(stream_state.get(self.cursor_field)).date()

        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, end_date)
        date_slices = []
        while start_date <= end_date:
            end_date_slice = start_date.add(days=self.window_in_days)
            # limit the slice range with end_date
            end_date_slice = min(end_date_slice, end_date)
            date_slices.append({"startDate": self.to_datetime_str(start_date), "endDate": self.to_datetime_str(end_date_slice)})
            # add 1 day for start next slice from next day and not duplicate data from previous slice end date.
            start_date = end_date_slice.add(days=1)
        return date_slices

    def get_data(self, data):
        for data_field in self.data_fields:
            if data and isinstance(data, dict):
                data = data.get(data_field, [])
            else:
                return []
        return data

    def lookup_data_type(self, field_type, attribute):
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
                # We always treat them as as strings as we can not be sure of their data type
                if attribute.startswith("ga:goal") and attribute.endswith(
                    ("Starts", "Completions", "Value", "ConversionRate", "Abandons", "AbandonRate")
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
                self.logger.error(f"Unsuported GA type: {field_type}")
        except KeyError:
            attr_type = None
            self.logger.error(f"Unsuported GA {field_type}: {attribute}")

        data_type = self.map_type.get(attr_type, "string")

        return data_type

    @staticmethod
    def lookup_data_format(attribute: str) -> Union[str, None]:
        if attribute == "ga:date":
            return "date"
        return

    def convert_to_type(self, header, value, data_type):
        if data_type == "integer":
            return int(value)
        if data_type == "number":
            return float(value)
        if header == "ga:date":
            return self.to_iso_datetime_str(value)
        return value

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
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
            metric_headers = column_header.get("metricHeader", {}).get("metricHeaderEntries", [])

            for row in self.get_data(report):
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
                        metric_type = self.lookup_data_type("metric", metric_name)
                        value = self.convert_to_type(metric_name, value, metric_type)

                        record[metric_name.replace("ga:", "ga_")] = value

                record["view_id"] = self.view_id

                yield record


class GoogleAnalyticsV4IncrementalObjectsBase(GoogleAnalyticsV4Stream):
    cursor_field = "ga_date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Update the state value, default CDK method.
        """
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}


class GoogleAnalyticsServiceOauth2Authenticator(Oauth2Authenticator):
    """Request example for API token extraction:
    curl --location --request POST
    https://oauth2.googleapis.com/token?grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=signed_JWT
    """

    def __init__(self, config):
        self.credentials_json = json.loads(config["credentials_json"])
        self.client_email = self.credentials_json["client_email"]
        self.scope = "https://www.googleapis.com/auth/analytics.readonly"

        super().__init__(
            token_refresh_endpoint="https://oauth2.googleapis.com/token",
            client_secret=self.credentials_json["private_key"],
            client_id=self.credentials_json["private_key_id"],
            refresh_token=None,
        )

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Calling the Google OAuth 2.0 token endpoint. Used for authorizing signed JWT.
        Returns tuple with access token and token's time-to-live
        """
        response_json = None
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, params=self.get_refresh_request_params())

            response_json = response.json()
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if response_json and "error" in response_json:
                raise Exception(
                    "Error refreshing access token {}. Error: {}; Error details: {}; Exception: {}".format(
                        response_json, response_json["error"], response_json["error_description"], e
                    )
                ) from e
            raise Exception(f"Error refreshing access token: {e}") from e
        else:
            return response_json["access_token"], response_json["expires_in"]

    def get_refresh_request_params(self) -> Mapping[str, any]:
        """
        Sign the JWT with RSA-256 using the private key found in service account JSON file.
        """
        token_lifetime = 3600  # token lifetime is 1 hour

        issued_at = time.time()
        expiration_time = issued_at + token_lifetime

        payload = {
            "iss": self.client_email,
            "sub": self.client_email,
            "scope": self.scope,
            "aud": self.token_refresh_endpoint,
            "iat": issued_at,
            "exp": expiration_time,
        }
        headers = {"kid": self.client_id}
        signed_jwt = jwt.encode(payload, self.client_secret, headers=headers, algorithm="RS256")
        return {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": str(signed_jwt)}


class TestStreamConnection(GoogleAnalyticsV4Stream):
    """
    Test the connectivity and permissions to read the data from the stream.
    Because of the nature of the connector, the streams are created dynamicaly.
    We declare the static stream like this to be able to test out the prmissions to read the particular view_id."""

    page_size = 1

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """For test reading pagination is not required"""
        return None

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override this method to fetch records from start_date up to now for testing case
        """
        start_date = pendulum.parse(self.start_date).date()
        end_date = pendulum.now().date()
        return [{"startDate": self.to_datetime_str(start_date), "endDate": self.to_datetime_str(end_date)}]


class SourceGoogleAnalyticsV4(AbstractSource):
    """Google Analytics lets you analyze data about customer engagement with your website or application."""

    @staticmethod
    def get_authenticator(config):
        # backwards compatibility, credentials_json used to be in the top level of the connector
        if config.get("credentials_json"):
            return GoogleAnalyticsServiceOauth2Authenticator(config)

        auth_params = config.get("credentials")

        if auth_params.get("auth_type") == "Service" or auth_params.get("credentials_json"):
            return GoogleAnalyticsServiceOauth2Authenticator(auth_params)
        else:
            return Oauth2Authenticator(
                token_refresh_endpoint="https://oauth2.googleapis.com/token",
                client_secret=auth_params.get("client_secret"),
                client_id=auth_params.get("client_id"),
                refresh_token=auth_params.get("refresh_token"),
                scopes=["https://www.googleapis.com/auth/analytics.readonly"],
            )

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        # declare additional variables
        authenticator = self.get_authenticator(config)
        config["authenticator"] = authenticator
        config["metrics"] = ["ga:14dayUsers"]
        config["dimensions"] = ["ga:date"]

        try:
            # test the eligibility of custom_reports input
            custom_reports = config.get("custom_reports")
            if custom_reports:
                json.loads(custom_reports)

            # Read records to check the reading permissions
            read_check = list(TestStreamConnection(config).read_records(sync_mode=None))
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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams: List[GoogleAnalyticsV4Stream] = []

        authenticator = self.get_authenticator(config)

        config["authenticator"] = authenticator

        reports = json.loads(pkgutil.get_data("source_google_analytics_v4", "defaults/default_reports.json"))

        if config.get("custom_reports"):
            custom_reports = json.loads(config["custom_reports"])
            reports += custom_reports

        config["ga_streams"] = reports

        for stream in config["ga_streams"]:
            config["metrics"] = stream["metrics"]
            config["dimensions"] = stream["dimensions"]

            # construct GAReadStreams sub-class for each stream
            stream_name = stream["name"]
            stream_bases = (GoogleAnalyticsV4Stream,)

            if "ga:date" in stream["dimensions"]:
                stream_bases = (GoogleAnalyticsV4IncrementalObjectsBase,)

            stream_class = type(stream_name, stream_bases, {})

            # instantiate a stream with config
            stream_instance = stream_class(config)
            streams.append(stream_instance)

        return streams
