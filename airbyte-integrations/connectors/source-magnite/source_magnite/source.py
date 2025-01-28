#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import re
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
import json
import time
from datetime import timedelta, date
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from .auth import CookieAuthenticator
from .utils import (
    date_to_string,
    string_to_date,
    get_dimensions,
    get_metrics
)

DATE_FORMAT = "%Y-%m-%d"
WINDOW_IN_DAYS = 45 #max is 45
POLLING_IN_SECONDS = 30
column_type_dict = {
    "percent": "number",
    "currency": "number"
}

class BaseResourceStream(HttpStream, ABC):
    http_method = "GET"

    def __init__(self, name: str, resource_type: str, **kwargs: Any) -> None:
        self._name = name
        self._path = f"v1/resources/queries/sources/{name}/{resource_type}"
        self._primary_key = None
        super().__init__(**kwargs)

    url_base = "https://api.tremorhub.com/"

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        all_columns = get_dimensions(self.name) + get_metrics(self.name)
        result = [ x for x in response_json if x["id"] in all_columns ]
        yield from result

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self._name

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return self._path

class DimensionsStream(BaseResourceStream):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name, "dimensions", **kwargs)

class MetricsStream(BaseResourceStream):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name, "metrics", **kwargs)

class MagniteStream(HttpStream, ABC):
    http_method = "POST"
    max_retries = 90
    cursor_field = "fromDate"
    # _state: MutableMapping[str, Any] = {}

    def __init__(self, config: Mapping[str, Any], name: str, path: str, primary_key: Union[str, List[str]], data_field: str, **kwargs: Any) -> None:
        self._config = config
        self._name = name
        self._path = path
        self._primary_key = primary_key
        self._data_field = data_field
        self.dimensions_stream = DimensionsStream(name, **kwargs)
        self.metrics_stream = MetricsStream(name, **kwargs)
        self.dimensions_data = None
        self.metrics_data = None
        self.authenticator = kwargs.get("authenticator")
        super().__init__(**kwargs)

    @property
    def config(self):
        return self._config
    
    @property
    def url_base(self) -> str:
        return "https://api.tremorhub.com/"

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key
    
    @property
    def dimensions(self):
        if self.dimensions_data is None:
            self.dimensions_data = list(self.dimensions_stream.read_records(sync_mode=SyncMode.full_refresh))
        return [record['id'] for record in self.dimensions_data]
    
    @property
    def metrics(self):
        if self.metrics_data is None:
            self.metrics_data = list(self.metrics_stream.read_records(sync_mode=SyncMode.full_refresh))
        return [record['id'] for record in self.metrics_data]


    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return self._path

    def get_json_schema(self):  
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {}
        }
        self.dimensions
        self.metrics
        for record in self.dimensions_data + self.metrics_data:
            schema["properties"][re.sub(r'[(). ]', "_", record["name"])] = {"type": column_type_dict.get(record["type"], record["type"])}

        return schema
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if isinstance(response, Exception):
            self.logger.warning(f"Back off due to {type(response)}.")
            return POLLING_IN_SECONDS * 2
        if response.status_code == 412:
            self.logger.warning("Precondition failed! A query is already running.")
            return POLLING_IN_SECONDS * 2
        return super().backoff_time(response)

    def fetch_csv_rows(self, api_url):
        # Open a connection to the API with streaming enabled
        response = requests.get(api_url, headers=self.authenticator.get_auth_header(), stream=True)
        response.raise_for_status()  # Raise an error if the request failed
        self.logger.info(f"Query results fetched")
        
        # Decode the content and iterate over lines
        for line in response.iter_lines(decode_unicode=True):
            if line:  # Skip empty lines
                yield line

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()

        if self._data_field:
            result_url = f"{self.url_base}{self.path()}/{response_json[self._data_field]}"
            self.logger.info(f"Retrieving report {response_json[self._data_field]}...")
            while True:
                result_response = requests.get(result_url, headers=self.authenticator.get_auth_header())
                query_status = result_response.json()['status']
                if result_response.status_code == 412:
                    self.logger.warning("Precondition faild! A query is already running")
                    break
                if query_status == 1 or query_status == 2: # created or running queries
                    self.logger.info(f"Query results are not ready yet. Checking again in {POLLING_IN_SECONDS} seconds...")
                    time.sleep(POLLING_IN_SECONDS)
                elif query_status == 3: # completed query
                    self.logger.info(f"Query results ready")
                    rows = self.fetch_csv_rows(f"{result_url}/results?fmt=csv")
                    # Pass the lines to csv.reader to handle CSV parsing
                    csv_reader = csv.reader(rows)
                    header = next(csv_reader, None)  # Get the first row as the header
                    header = [re.sub(r'[(). ]', "_", column) for column in header]
                    if not header:
                        raise ValueError("The CSV response is empty or invalid.")
                    for row in csv_reader:
                        yield dict(zip(header, row))
                    break
                else: # error(4) or cancelled(5) query
                    self.logger.error(f"Failed to fetch results: {result_response.status_code} - {result_response.text}")
                    raise Exception(f"Failed to fetch results: {result_response.status_code} - {result_response.text}")
        else:
            yield from response_json

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:

        if stream_slice and "fromDate" in stream_slice and "toDate" in stream_slice:
            self.logger.info(f"Fetching {self.name} data from {stream_slice['fromDate']} to {stream_slice['toDate']}")
            date_range = {"fromDate": stream_slice["fromDate"], "toDate": stream_slice["toDate"]}
        else:
            date_range = stream_slice

        request_payload = {
            "source": self.name,
            # "fields": self.dimensions + self.metrics,
            "fields": get_dimensions(self.name) + get_metrics(self.name),
            "range": date_range,
        }
        return request_payload

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        today: date = date.today()
        end_date = string_to_date(self.config.get("toDate", None)) or today
        start_date = string_to_date(self.config["fromDate"])

        while start_date <= end_date:
            yield {
                "fromDate": date_to_string(start_date),
                "toDate": date_to_string(min(start_date + timedelta(days=WINDOW_IN_DAYS - 1), end_date)),
            }
            start_date += timedelta(days=WINDOW_IN_DAYS)

class SourceMagnite(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth_headers = CookieAuthenticator(config).get_auth_header()
            url = "https://api.tremorhub.com/v1/resources/queries"
            test_payload = {
                "source": "adstats-publisher",
                "fields": get_dimensions("adstats-publisher") + get_metrics("adstats-publisher"),
                "constraints": [],
                "orderings": [],
                "range": {
                    "fromDate": date_to_string(date.today() - timedelta(days=WINDOW_IN_DAYS - 1)),
                    "toDate": date_to_string(date.today())
                },
                "fmt": "csv"
            }
            response = requests.request("POST", url=url, headers=auth_headers, data=json.dumps(test_payload))
            if response.status_code != 412:
                response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = CookieAuthenticator(config)
        streams = [
            MagniteStream(config, name="adstats-publisher", path="v1/resources/queries", primary_key=None, data_field="code", authenticator=auth),
            MagniteStream(config, name="deals-publisher", path="v1/resources/queries", primary_key=None, data_field="code", authenticator=auth)
        ]
        return streams