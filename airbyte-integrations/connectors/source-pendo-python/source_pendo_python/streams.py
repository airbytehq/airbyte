from abc import ABC
import ujson as json
from typing import Any, Iterable, Mapping, MutableMapping, Optional
import time

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.core import CheckpointMixin


class PendoPythonStream(HttpStream, ABC):
    url_base = "https://app.pendo.io/api/v1/"
    primary_key = None

    def path(self, **kwargs) -> str:
        return self.name

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()

    # Method to get an Airbyte field schema for a given Pendo field type
    def get_valid_field_info(self, field_type) -> dict:
        output_types = []
        if field_type == "time":
            output_types = ["null", "integer"]
        elif field_type == "float":
            output_types = ["null", "number"]
        elif field_type == "list":
            output_types = ["null", "array", "string"]
        elif field_type == "":
            output_types = ["null", "array", "string", "integer", "boolean"]
        else:
            output_types = ["null", field_type]
        return {"type": output_types}

    # Build the Airbyte stream schema from Pendo metadata
    def build_schema(self, full_schema, metadata):
        for key in metadata:
            if key != "auto" and key != "auto__323232":  # Skipping for now while we understand Pendo schema and what auto_323232 is
                fields = {}
                for field in metadata[key]:
                    field_type = metadata[key][field]["Type"]
                    # TODO: Hardcoding these fields for now until we understand the Pendo schema better
                    # These fields are being returned by the Pendo API in multiple formats.
                    if field == "pricingtiersf":
                        fields[field] = {"type": ["null", "integer", "string"]}
                    elif field == "accountnumbersf":
                        fields[field] = {"type": ["null", "string", "number"]}
                    else:
                        fields[field] = self.get_valid_field_info(field_type)

                full_schema["properties"]["metadata"]["properties"][key] = {"type": ["null", "object"], "properties": fields}
        return full_schema


# Airbyte Streams using the Pendo /aggregation endpoint (Currently only Account and Visitor)
class PendoAggregationStream(PendoPythonStream):
    json_schema = None  # Field to store dynamically built Airbyte Stream Schema
    page_size = 100000 # Increasing the page size to 100000 for faster sync

    @property
    def http_method(self) -> str:
        return "POST"

    def path(self, **kwargs) -> str:
        return "aggregation"

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json().get("results", [])
        if len(data) < self.page_size:
            return None
        return data[-1][self.primary_key]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        response.encoding = "UTF-8"
        yield from response.json().get("results", [])

    # Build /aggregation endpoint payload with pagination for a given source and requestId
    def build_request_body(self, requestId, source, next_page_token) -> Optional[Mapping[str, Any]]:
        request_body = {
            "response": {"mimeType": "application/json"},
            "request": {
                "requestId": requestId,
                "pipeline": [
                    {"source": source},
                    {"sort": [self.primary_key]},
                    {"limit": self.page_size},
                ],
            },
        }

        if next_page_token is not None:
            # Some primary keys are already wrapped in quotation marks - strip them when building filter query
            next_page_token = next_page_token.strip('"')
            request_body["request"]["pipeline"].insert(2, {"filter": f'{self.primary_key} > "{next_page_token}"'})

        return request_body


# Airbyte Streams using the Pendo /aggregation endpoint (Currently only Account and Visitor)
class PendoTimeSeriesAggregationStream(PendoPythonStream, CheckpointMixin):
    json_schema = None  # Field to store dynamically built Airbyte Stream Schema
    DAY_MILLISECONDS = 60 * 60 * 24 * 1000
    source_name = None

    @property
    def http_method(self) -> str:
        return "POST"

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = {}

    def path(self, **kwargs) -> str:
        return "aggregation"

    def request_body_json(self, stream_slice: Mapping[str, Any] = {}, **kwargs) -> Optional[Mapping[str, Any]]:
        start_timestamp = stream_slice.get("start_timestamp") or self.start_date_in_unix()

        request_body = {
            "response": { "mimeType": "application/json" },
            "request": {
                "pipeline": [
                    {
                        "source": {
                            self.source_name: { "appId": 'expandAppIds("*")' },
                            "timeSeries": {
                                "first": start_timestamp,
                                "count": self.day_page_size,
                                "period": "dayRange"
                            },
                        }
                    },
                ],
            },
        }

        self.logger.info(f"stream: `{self.source_name}` start_timestamp: `{start_timestamp}`") 

        return request_body

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        self.state = {"start_timestamp": stream_slice["start_timestamp"]}
        response.encoding = "UTF-8"
        yield from json.loads(response.text).get("results", [])

    def stream_slices(self, stream_state: Mapping[str, Any] = {}, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        # TODO round timestamp to start of day?
        start_timestamp = stream_state.get("start_timestamp", self.start_date_in_unix())

        # End one day page size window ago to prevent a partial day read, range is end exclusive
        end_timestamp = (int(time.time()) * 1000) - (self.day_page_size * self.DAY_MILLISECONDS)
        for slice_timestamp in range(start_timestamp, end_timestamp, self.DAY_MILLISECONDS * self.day_page_size):
            yield {"start_timestamp": slice_timestamp}

class Feature(PendoPythonStream):
    name = "feature"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"expand": "*"}

class Guide(PendoPythonStream):
    name = "guide"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"expand": "*"}

class Page(PendoPythonStream):
    name = "page"

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"expand": "*"}

class Report(PendoPythonStream):
    name = "report"

class ReportResult(PendoPythonStream):
    json_schema = None  # Field to store dynamically built Airbyte Stream Schema
    primary_key = "reportId"

    def __init__(self, report: str, **kwargs):
        super().__init__(**kwargs)
        self.report = report
        self.report_name = f"report_result_{report}"

    @property
    def name(self):
        return self.report_name

    def path(self, **kwargs) -> str:
        return f"report/{self.report}/results.json"

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,
    ) -> Iterable[Mapping]:
        for record in response.json():
            yield self.transform(record=record)

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        record["reportId"] = self.report
        return record

    # Method to infer schema types from JSON response
    def infer_type(self, value: Any):
        if isinstance(value, str):
            return {"type": ["null", "string"]}
        if isinstance(value, bool):
            return {"type": ["null", "boolean"]}
        if isinstance(value, float):
            return {"type": ["null", "number"]}
        if isinstance(value, int):
            return {"type": ["null", "integer"]}
        if isinstance(value, list):
            return {"type": ["null", "array"]}
        if isinstance(value, dict):
            return {"type": ["null", "object"]}
        return {"type": ["null", "string"]}

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is None:
            schema = {
                "type": "object",
                "$schema": "http://json-schema.org/schema#",
                "properties": {
                    "reportId": {
                        "type": "string"
                    }
                }
            }

            url = f"{PendoPythonStream.url_base}{self.path()}"
            auth_headers = self.authenticator.get_auth_header()
            try:
                session = requests.get(url, headers=auth_headers)
                if session.status_code != 200:
                    raise Exception(f"{session.status_code} Response from Pendo: {session.text}")
                else:
                    body = session.json()
                    if body is not None and len(body) != 0:
                        for result in body:
                            for field in result:
                                if result[field] is not None:
                                    schema["properties"][field] = self.infer_type(result[field])
            except Exception as e:
                print(f"Error fetching sample Pendo Report Results: {e}")
            self.json_schema = schema

        return self.json_schema


class VisitorMetadata(PendoPythonStream):
    name = "visitor_metadata"
    primary_key = []

    def path(self, **kwargs) -> str:
        return "metadata/schema/visitor"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]


class AccountMetadata(PendoPythonStream):
    name = "account_metadata"
    primary_key = []

    def path(self, **kwargs) -> str:
        return "metadata/schema/account"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from [response.json()]


class Visitor(PendoAggregationStream):
    primary_key = "visitorId"
    name = "visitor"

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is not None:
            return self.json_schema

        base_schema = super().get_json_schema()
        url = f"{PendoPythonStream.url_base}metadata/schema/visitor"
        auth_headers = self.authenticator.get_auth_header()
        try:
            session = requests.get(url, headers=auth_headers)
            body = session.json()

            full_schema = base_schema

            # Not all fields are getting returned by Pendo's metadata apis so we need to do some manual construction
            full_schema["properties"]["metadata"]["properties"]["auto__323232"] = {"type": ["null", "object"]}

            auto_fields = {
                "lastupdated": {"type": ["null", "integer"]},
                "idhash": {"type": ["null", "integer"]},
                "lastuseragent": {"type": ["null", "string"]},
                "lastmetadataupdate_agent": {"type": ["null", "integer"]},
            }
            for key in body["auto"]:
                auto_fields[key] = self.get_valid_field_info(body["auto"][key]["Type"])
            full_schema["properties"]["metadata"]["properties"]["auto"]["properties"] = auto_fields
            full_schema["properties"]["metadata"]["properties"]["auto__323232"]["properties"] = auto_fields

            full_schema = self.build_schema(full_schema, body)
            self.json_schema = full_schema
        except requests.exceptions.RequestException:
            self.json_schema = base_schema
        return self.json_schema

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping[str, Any]]:
        source = {"visitors": {"identified": True}}
        return self.build_request_body("visitor-list", source, next_page_token)


class Account(PendoAggregationStream):
    primary_key = "accountId"
    name = "account"

    def get_json_schema(self) -> Mapping[str, Any]:
        if self.json_schema is not None:
            return self.json_schema

        base_schema = super().get_json_schema()
        url = f"{PendoPythonStream.url_base}metadata/schema/account"
        auth_headers = self.authenticator.get_auth_header()
        try:
            session = requests.get(url, headers=auth_headers)
            body = session.json()

            full_schema = base_schema

            # Not all fields are getting returned by Pendo's metadata apis so we need to do some manual construction
            full_schema["properties"]["metadata"]["properties"]["auto__323232"] = {"type": ["null", "object"]}

            auto_fields = {"lastupdated": {"type": ["null", "integer"]}, "idhash": {"type": ["null", "integer"]}}
            for key in body["auto"]:
                auto_fields[key] = self.get_valid_field_info(body["auto"][key]["Type"])
            full_schema["properties"]["metadata"]["properties"]["auto"]["properties"] = auto_fields
            full_schema["properties"]["metadata"]["properties"]["auto__323232"]["properties"] = auto_fields

            full_schema = self.build_schema(full_schema, body)
            self.json_schema = full_schema
        except requests.exceptions.RequestException:
            self.json_schema = base_schema
        return self.json_schema

    def request_body_json(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping[str, Any]]:
        source = {"accounts": {}}
        return self.build_request_body("account-list", source, next_page_token)


class PageEvents(PendoTimeSeriesAggregationStream):
    name = "page_events"
    source_name = "pageEvents"
    cursor_field = "day"

    def __init__(self, start_date: str, day_page_size: int, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.day_page_size = day_page_size
    
    def start_date_in_unix(self):
        return int(time.mktime(time.strptime(self.start_date, "%Y-%m-%dT%H:%M:%SZ"))) * 1000

class FeatureEvents(PendoTimeSeriesAggregationStream):
    name = "feature_events"
    source_name = "featureEvents"
    cursor_field = "day"

    def __init__(self, start_date: str, day_page_size: int, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.day_page_size = day_page_size
    
    def start_date_in_unix(self):
        return int(time.mktime(time.strptime(self.start_date, "%Y-%m-%dT%H:%M:%SZ"))) * 1000

class GuideEvents(PendoTimeSeriesAggregationStream):
    name = "guide_events"
    source_name = "guideEvents"
    cursor_field = "browserTime"

    def __init__(self, start_date: str, day_page_size: int, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.day_page_size = day_page_size
    
    def start_date_in_unix(self):
        return int(time.mktime(time.strptime(self.start_date, "%Y-%m-%dT%H:%M:%SZ"))) * 1000
