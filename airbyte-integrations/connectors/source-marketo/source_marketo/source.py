#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import json
import re
from abc import ABC
from time import sleep
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.exceptions import ReadException
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType

from .utils import STRING_TYPES, clean_string, format_value, to_datetime_str


class MarketoStream(HttpStream, ABC):
    primary_key = "id"
    data_field = "result"
    page_size = 300

    def __init__(self, config: Mapping[str, Any], stream_name: str = None, param: Mapping[str, Any] = None, export_id: int = None):
        super().__init__(authenticator=config["authenticator"])
        self.config = config
        self.start_date = config["start_date"]
        # this is done for test purposes, the field is not exposed to spec.json!
        self.end_date = config.get("end_date")
        self.window_in_days = config.get("window_in_days", 30)
        self._url_base = config["domain_url"].rstrip("/") + "/"
        self.stream_name = stream_name
        self.param = param
        self.export_id = export_id

    @property
    def url_base(self) -> str:
        return self._url_base

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def path(self, **kwargs) -> str:
        return f"rest/v1/{self.name}.json"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("nextPageToken")

        if next_page:
            return {"nextPageToken": next_page}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"batchSize": self.page_size}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = response.json().get(self.data_field, [])

        for record in data:
            yield record


class IncrementalMarketoStream(MarketoStream):
    cursor_field = "createdAt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = {}

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> Iterable:
        """
        Endpoint does not provide query filtering params, but they provide us
        cursor field in most cases, so we used that as incremental filtering
        during the parsing.
        """

        if record[self.cursor_field] >= (stream_state or {}).get(self.cursor_field, self.start_date):
            yield record

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[MutableMapping]:
        json_response = response.json().get(self.data_field) or []

        for record in json_response:
            yield from self.filter_by_state(stream_state=stream_state, record=record)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_cursor_value = latest_record.get(self.cursor_field, self.start_date) or self.start_date
        current_cursor_value = current_stream_state.get(self.cursor_field, self.start_date) or self.start_date
        self._state = {self.cursor_field: max(latest_cursor_value, current_cursor_value)}
        return self._state

    def stream_slices(self, sync_mode, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[MutableMapping[str, any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: [{
            "startDate": "2020-01-01T0:0:0Z",
            "endDate": "2021-01-02T0:0:0Z"
            },
            {
            "startDate": "2020-01-03T0:0:0Z",
            "endDate": "2021-01-04T0:0:0Z"
            },
            ...]
        """

        start_date = pendulum.parse(self.start_date)

        # Determine stream_state, if no stream_state we use start_date
        if stream_state:
            start_date = pendulum.parse(stream_state.get(self.cursor_field))

        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, pendulum.now())
        date_slices = []

        end_date = pendulum.parse(self.end_date) if self.end_date else pendulum.now()
        while start_date < end_date:
            # the amount of days for each data-chunk beginning from start_date
            end_date_slice = start_date.add(days=self.window_in_days)

            date_slice = {"startAt": to_datetime_str(start_date), "endAt": to_datetime_str(end_date_slice)}

            date_slices.append(date_slice)
            start_date = end_date_slice

        return date_slices


class MarketoExportBase(IncrementalMarketoStream):
    """
    Base class for all the streams which support bulk extract.
    """

    # Polling Job Status - https://developers.marketo.com/rest-api/bulk-extract/bulk-lead-extract/
    # The status is only updated once every 60 seconds
    poll_interval = 60

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def stream_fields(self):
        return {}

    @property
    def stream_filter(self):
        return {}

    def create_export(self, param):
        return next(MarketoExportCreate(self.config, stream_name=self.stream_name, param=param).read_records(sync_mode=None), {})

    def start_export(self, stream_slice):
        return next(
            MarketoExportStart(self.config, stream_name=self.stream_name, export_id=stream_slice["id"]).read_records(sync_mode=None)
        )

    def get_export_status(self, stream_slice):
        return next(
            MarketoExportStatus(self.config, stream_name=self.stream_name, export_id=stream_slice["id"]).read_records(sync_mode=None)
        )

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"bulk/v1/{self.stream_name}/export/{stream_slice['id']}/file.json"

    def stream_slices(
        self, sync_mode, stream_state: MutableMapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[MutableMapping[str, any]]]:
        date_slices = super().stream_slices(sync_mode, stream_state, **kwargs)

        for date_slice in date_slices:
            param = {"fields": [], "filter": {"createdAt": date_slice}}
            param["fields"].extend(self.stream_fields)
            param["filter"].update(self.stream_filter)

            export = self.create_export(param)

            date_slice["id"] = export["exportId"]
        return date_slices

    def sleep_till_export_completed(self, stream_slice: Mapping[str, Any]) -> bool:
        while True:
            status = self.get_export_status(stream_slice)
            self.logger.info(f"Export {self.name} from {stream_slice['startAt']} to {stream_slice['endAt']} status is {status}")

            if status == "Created":
                # If the status is created, the export has been made but
                # not started, so enqueue the export.
                self.start_export(stream_slice)

            elif status in ["Cancelled", "Failed"]:
                # Cancelled and failed exports fail the current sync.
                raise Exception(status)

            elif status == "Completed":
                return True

            sleep(self.poll_interval)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.text example:

        firstName,lastName,email,cookies
        Russell,Wilson,null,_mch-localhost-1536605780000-12105

        :return an iterable containing each record in the response
        """

        default_prop = {"type": ["null", "string"]}
        schema = self.get_json_schema()["properties"]
        response.encoding = "utf-8"

        response_lines = response.iter_lines(chunk_size=1024, decode_unicode=True)
        filtered_response_lines = self.filter_null_bytes(response_lines)
        reader = self.csv_rows(filtered_response_lines)

        for record in reader:
            new_record = {**record}
            attributes = json.loads(new_record.pop("attributes", "{}"))
            for key, value in attributes.items():
                key = clean_string(key)
                new_record[key] = value

            for key, value in new_record.items():
                if key not in schema:
                    self.logger.warning("Field '%s' not found in stream '%s' spec", key, self.name)
                prop = schema.get(key, default_prop)
                value = format_value(value, prop)
                new_record[key] = value
            yield new_record

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.sleep_till_export_completed(stream_slice)
        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def filter_null_bytes(self, response_lines: Iterable[str]) -> Iterable[str]:
        for line in response_lines:
            res = line.replace("\x00", "")
            if len(res) < len(line):
                self.logger.warning("Filter 'null' bytes from string, size reduced %d -> %d chars", len(line), len(res))
            yield res

    @staticmethod
    def csv_rows(lines: Iterable[str]) -> Iterable[Mapping]:
        reader = csv.reader(lines)
        headers = None
        for row in reader:
            if headers is None:
                headers = row
            else:
                yield dict(zip(headers, row))


class MarketoExportCreate(MarketoStream):
    """
     Provides functionality to create Marketo export.
     Return list with dict, example:
    [
         {
             "exportId": "141bas21-146c-4a43-8c72-280sder596c34",
             "format": "CSV",
             "status": "Created",
             "createdAt": "2021-09-01T10:09:39Z"
         }
     ]
    """

    http_method = "POST"

    def path(self, **kwargs) -> str:
        return f"bulk/v1/{self.stream_name}/export/create.json"

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429 or 500 <= response.status_code < 600:
            return True
        if errors := response.json().get("errors"):
            if errors[0].get("code") == "1029" and re.match("Export daily quota \d+MB exceeded", errors[0].get("message")):
                message = "Daily limit for job extractions has been reached (resets daily at 12:00AM CST)."
                raise AirbyteTracedException(internal_message=response.text, message=message, failure_type=FailureType.config_error)
        result = response.json().get("result")[0]
        status, export_id = result.get("status", "").lower(), result.get("exportId")
        if status != "created" or not export_id:
            self.logger.warning(f"Failed to create export job! Status is {status}!")
            return True
        return False

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        params = {"format": "CSV"}
        if self.param:
            params.update(self.param)

        return params


class MarketoExportStart(MarketoStream):
    """
     Provides functionality to start Marketo export.
     Return list with dict, example:
    [
         {
             "exportId": "1689f995-1397-48b2-b88a-5eed1397299b",
             "format": "CSV",
             "status": "Queued",
             "createdAt": "2021-09-01T10:00:50Z",
             "queuedAt": "2021-09-01T10:01:07Z"
         }
     ]
    """

    http_method = "POST"

    def path(self, **kwargs) -> str:
        return f"bulk/v1/{self.stream_name}/export/{self.export_id}/enqueue.json"


class MarketoExportStatus(MarketoStream):
    """
    Provides functionality to get status of Marketo export.
    Return string with dict, example: "Completed"
    """

    def path(self, **kwargs) -> str:
        return f"bulk/v1/{self.stream_name}/export/{self.export_id}/status.json"

    def parse_response(self, response: requests.Response, **kwargs) -> List[str]:
        return [response.json()[self.data_field][0]["status"]]


class Leads(MarketoExportBase):
    """
    Return list of all leeds.
    API Docs: https://developers.marketo.com/rest-api/bulk-extract/bulk-lead-extract/
    """

    cursor_field = "updatedAt"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(config, self.name)

    @property
    def stream_fields(self):
        standard_properties = set(self.get_json_schema()["properties"])
        resp = self._session.get(f"{self._url_base}rest/v1/leads/describe.json", headers=self._session.auth.get_auth_header())
        available_fields = set(x.get("rest").get("name") for x in resp.json().get("result"))
        return list(standard_properties & available_fields)

    def get_json_schema(self) -> Mapping[str, Any]:
        # TODO: make schema truly dynamic like in stream Activities
        #  now blocked by https://github.com/airbytehq/airbyte/issues/30530 due to potentially > 500 fields in schema (can cause OOM)
        return super().get_json_schema()


class Activities(MarketoExportBase):
    """
    Base class for all the activities streams,
    provides functionality for dynamically created classes as streams of data.
    API Docs: https://developers.marketo.com/rest-api/bulk-extract/bulk-activity-extract/
    """

    primary_key = "marketoGUID"
    cursor_field = "activityDate"

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(config, "activities")

    @property
    def stream_filter(self):
        return {"activityTypeIds": [self.activity["id"]]}

    def get_json_schema(self) -> Mapping[str, Any]:
        properties = {
            "marketoGUID": {"type": ["null", "string"]},
            "leadId": {"type": ["null", "integer"]},
            "activityDate": {"type": ["null", "string"], "format": "date-time"},
            "activityTypeId": {"type": ["null", "integer"]},
            "campaignId": {"type": ["null", "integer"]},
            "primaryAttributeValueId": {"type": ["null", "string"]},
            "primaryAttributeValue": {"type": ["null", "string"]},
        }

        if "attributes" in self.activity:
            for attr in self.activity["attributes"]:
                attr_name = clean_string(attr["name"])

                if attr["dataType"] == "date":
                    field_schema = {"type": "string", "format": "date"}
                elif attr["dataType"] == "datetime":
                    field_schema = {"type": "string", "format": "date-time"}
                elif attr["dataType"] in ["integer", "percent", "score"]:
                    field_schema = {"type": "integer"}
                elif attr["dataType"] in ["float", "currency"]:
                    field_schema = {"type": "number"}
                elif attr["dataType"] == "boolean":
                    field_schema = {"type": "boolean"}
                elif attr["dataType"] in STRING_TYPES:
                    field_schema = {"type": "string"}
                elif attr["dataType"] in ["array"]:
                    field_schema = {"type": "array", "items": {"type": ["integer", "number", "string", "null"]}}
                else:
                    field_schema = {"type": "string"}

                field_schema["type"] = [field_schema["type"], "null"]

                properties[attr_name] = field_schema

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": ["null", "object"],
            "additionalProperties": True,
            "properties": properties,
        }

        return schema


class MarketoAuthenticator(Oauth2Authenticator):
    def __init__(self, config):
        super().__init__(
            token_refresh_endpoint=f"{config['domain_url']}/identity/oauth/token",
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=None,
        )

    def get_refresh_request_params(self) -> Mapping[str, Any]:
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
        }

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(method="GET", url=self.get_token_refresh_endpoint(), params=self.get_refresh_request_params())
            response.raise_for_status()
            response_json = response.json()
            return response_json["access_token"], response_json["expires_in"]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e


class SourceMarketo(YamlDeclarativeSource):
    """
    Source Marketo fetch data of personalized multichannel programs and campaigns to prospects and customers.
    """

    def __init__(self) -> None:
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def _get_declarative_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return super().streams(config)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = MarketoAuthenticator(config)

        streams = self._get_declarative_streams(config)
        streams.append(Leads(config))
        activity_types_stream = [stream for stream in streams if stream.name == "activity_types"][0]

        # dynamically create activities by activity type id
        try:
            for activity in activity_types_stream.read_records(sync_mode=None):
                stream_name = f"activities_{clean_string(activity['name'])}"
                stream_class = type(stream_name, (Activities,), {"activity": activity})

                # instantiate a stream with config
                stream_instance = stream_class(config)
                streams.append(stream_instance)
        except ReadException as e:
            self.logger.warning(f"An error occurred while creating activity streams: {repr(e)}")

        return streams
