from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.models import SyncMode

from requests.auth import AuthBase
from requests import models
import requests
import gzip
import json
from datetime import datetime,timedelta,timezone

TYPE_DICT = {
    "event":"TYPE_EVENT"
    ,"individual":"TYPE_INDIVIDUAL"
}


class FullstoryAuthenticator(AuthBase):
    
    def __init__(self,api_key) -> None:
        super().__init__()
        self._api_key = api_key
    
    def __call__(self, r: models.PreparedRequest) -> models.PreparedRequest:
        r.headers["Authorization"] = f"Basic {self._api_key}"
        return r

class FullstoryStream(HttpStream):
    
    url_base = "https://api.fullstory.com/"
    primary_key = ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {}

    def parse_response(self, response: requests.Response, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Iterable[Mapping]:
        return {}

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return ""

    @staticmethod
    def _parse_gzip_link(url: str):  
        response = requests.get(url)
        data = json.loads(gzip.decompress(response.content))

        return data

    @staticmethod
    def _parse_dttm_str(value: str) -> datetime:
        parsed_dttm = datetime.fromisoformat(value.replace("Z","+00:00"))
        
        return parsed_dttm

    @staticmethod
    def _to_dttm_str(value: datetime) -> str:
        str_dttm = datetime.isoformat(value).replace("+00:00","Z")
        
        return str_dttm

class FullstoryIncrementalStream(FullstoryStream,IncrementalMixin):
    
    cursor_field = "start"
    state_cursor_field = "start"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cursor_value = ""
    
    @property
    def state(self):
        return {self.state_cursor_field: self._to_dttm_str(self._cursor_value) }

    @state.setter
    def state(self,source_state):
        self._cursor_value = self._parse_dttm_str(source_state[self.state_cursor_field])

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        if not self._cursor_value:
            self._cursor_value = datetime(1990,1,1,tzinfo=timezone.utc)
        latest_dttm = self._parse_dttm_str(latest_record[self.cursor_field])
        self._cursor_value = max(self._cursor_value,latest_dttm)
        return {}

class CreateReport(FullstoryIncrementalStream):

    http_method = "POST"

    def __init__(self, data_type: str = 'individual', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_type = TYPE_DICT[data_type]


    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        return "segments/v1/exports"

    def request_body_json(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:
        if stream_state:
            start_time = stream_state[self.cursor_field]
        else:
            start_time = ""
        
        body = {
            "segmentId": "everyone",
            "type": self._data_type,
            "format": "FORMAT_JSON",
            "timeRange": {
                "start": start_time,
                "end": ""
            }
        }
        
        return body

    def parse_response(self, response: requests.Response, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Iterable[Mapping]:
        
        yield response.json()

class GetOperation(FullstoryStream,HttpSubStream):

    max_retries = 20
    
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            yield from parent_records

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        operation_id = stream_slice["operationId"]
        return f"operations/v1/{operation_id}"

    def should_retry(self, response: requests.Response) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        status = response.json()["state"]

        return response.status_code == 429 or 500 <= response.status_code < 600 or status != "COMPLETED"

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return 10

    def parse_response(self, response: requests.Response, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Iterable[Mapping]:
        search_export_id = response.json()["results"]["searchExportId"]
        yield {"searchExportId":search_export_id}

class Individuals(FullstoryIncrementalStream,HttpSubStream):
    
    primary_key = "IndvId"
    cursor_field = "LastEventStart"
    
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            yield from parent_records

    def path(self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
        search_export_id = stream_slice["searchExportId"]
        return f"search/v1/exports/{search_export_id}/results"

    def parse_response(self, response: requests.Response, *, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Iterable[Mapping]:
        gzip_url = response.json()["location"]

        yield from self._parse_gzip_link(gzip_url)

class Events(Individuals):
    
    primary_key = ["PageId", "SessionId", "UserId", "EventStart"]
    cursor_field = "EventStart"