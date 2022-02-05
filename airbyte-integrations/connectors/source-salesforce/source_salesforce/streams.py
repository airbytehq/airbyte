#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import csv
import ctypes
import io
import math
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from pendulum import DateTime
from requests import codes, exceptions

from .api import UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .rate_limiting import default_backoff_handler

# https://stackoverflow.com/a/54517228
CSV_FIELD_SIZE_LIMIT = int(ctypes.c_ulong(-1).value // 2)
csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)


class SalesforceStream(HttpStream, ABC):
    page_size = 2000
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, sf_api: Salesforce, pk: str, stream_name: str, schema: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.sf_api = sf_api
        self.pk = pk
        self.stream_name = stream_name
        self.schema = schema

    @property
    def name(self) -> str:
        return self.stream_name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.pk

    @property
    def url_base(self) -> str:
        return self.sf_api.instance_url

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> str:
        if next_page_token:
            """
            If `next_page_token` is set, subsequent requests use `nextRecordsUrl`.
            """
            return next_page_token
        return f"/services/data/{self.sf_api.version}/queryAll"

    def next_page_token(self, response: requests.Response) -> str:
        response_data = response.json()
        return response_data.get("nextRecordsUrl")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Salesforce SOQL Query: https://developer.salesforce.com/docs/atlas.en-us.232.0.api_rest.meta/api_rest/dome_queryall.htm
        """
        if next_page_token:
            """
            If `next_page_token` is set, subsequent requests use `nextRecordsUrl`, and do not include any parameters.
            """
            return {}

        selected_properties = self.get_json_schema().get("properties", {})
        query = f"SELECT {','.join(selected_properties.keys())} FROM {self.name} "

        if self.primary_key and self.name not in UNSUPPORTED_FILTERING_STREAMS:
            query += f"ORDER BY {self.primary_key} ASC"

        return {"q": query}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["records"]

    def get_json_schema(self) -> Mapping[str, Any]:
        if not self.schema:
            self.schema = self.sf_api.generate_schema([self.name])
        return self.schema

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(**kwargs)
        except exceptions.HTTPError as error:
            """
            There are several types of Salesforce sobjects that require additional processing:
              1. Sobjects for which the user, after setting up the data using Airbyte, restricted access,
                 and we will receive 403 HTTP errors.
              2. There are streams that do not allow you to make a sample using Salesforce `query` or `queryAll`.
                 And since we use a dynamic method of generating streams for Salesforce connector - at the stage of discover,
                 we cannot filter out these streams, so we catch them at the stage of reading data.
            """
            error_data = error.response.json()[0]
            if error.response.status_code in [codes.FORBIDDEN, codes.BAD_REQUEST]:
                error_code = error_data.get("errorCode", "")
                if error_code != "REQUEST_LIMIT_EXCEEDED" or error_code == "INVALID_TYPE_FOR_OPERATION":
                    self.logger.error(f"Cannot receive data for stream '{self.name}', error message: '{error_data.get('message')}'")
                    return
            raise error


class BulkSalesforceStream(SalesforceStream):
    page_size = 30000
    DEFAULT_WAIT_TIMEOUT_MINS = 10
    MAX_CHECK_INTERVAL_SECONDS = 2.0
    MAX_RETRY_NUMBER = 3

    def __init__(self, wait_timeout: Optional[int], **kwargs):
        super().__init__(**kwargs)
        self._wait_timeout = wait_timeout or self.DEFAULT_WAIT_TIMEOUT_MINS

    def path(self, **kwargs) -> str:
        return f"/services/data/{self.sf_api.version}/jobs/query"

    transformer = TypeTransformer(TransformConfig.CustomSchemaNormalization | TransformConfig.DefaultSchemaNormalization)

    @transformer.registerCustomTransform
    def transform_empty_string_to_none(instance, schema):
        """
        BULK API returns a `csv` file, where all values are initially as string type.
        This custom transformer replaces empty lines with `None` value.
        """
        if isinstance(instance, str) and not instance.strip():
            instance = None
        return instance

    @default_backoff_handler(max_tries=5, factor=15)
    def _send_http_request(self, method: str, url: str, json: dict = None):
        headers = self.authenticator.get_auth_header()
        response = self._session.request(method, url=url, headers=headers, json=json)
        if response.status_code not in [200, 204]:
            self.logger.error(f"error body: {response.text}")
        response.raise_for_status()
        return response

    def create_stream_job(self, query: str, url: str) -> Optional[str]:
        """
        docs: https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/create_job.htm
        """
        json = {"operation": "queryAll", "query": query, "contentType": "CSV", "columnDelimiter": "COMMA", "lineEnding": "LF"}

        try:
            response = self._send_http_request("POST", url, json=json)
            job_id = response.json()["id"]
            self.logger.info(f"Created Job: {job_id} to sync {self.name}")
            return job_id
        except exceptions.HTTPError as error:
            if error.response.status_code in [codes.FORBIDDEN, codes.BAD_REQUEST]:
                # A part of streams can't be used by BULK API. Every API version can have a custom list of
                # these sobjects. Another part of them can be generated dynamically. That's why we can't track
                # them preliminarily and there is only one way is to except error with necessary messages about
                # their limitations. Now we know about 3 different reasons of similar errors:
                # 1) some SaleForce sobjects(streams) is not supported by the BULK API simply (as is).
                # 2) Access to a sobject(stream) is not available
                # 3) sobject is not queryable. It means this sobject can't be called directly.
                #    We can call it as part of response from another sobject only.  E.g.:
                #        initial query: "Select Id, Subject from ActivityHistory" -> error
                #        updated query: "Select Name, (Select Subject,ActivityType from ActivityHistories) from Contact"
                #    The second variant forces customisation for every case (ActivityHistory, ActivityHistories etc).
                #    And the main problem is these subqueries doesn't support CSV response format.
                error_data = error.response.json()[0]
                error_code = error_data.get("errorCode")
                error_message = error_data.get("message", "")
                if error_message == "Selecting compound data not supported in Bulk Query" or (
                    error_code == "INVALIDENTITY" and "is not supported by the Bulk API" in error_message
                ):
                    self.logger.error(f"Cannot receive data for stream '{self.name}' using BULK API, error message: '{error_message}'")
                elif error.response.status_code == codes.FORBIDDEN and error_code != "REQUEST_LIMIT_EXCEEDED":
                    self.logger.error(f"Cannot receive data for stream '{self.name}', error message: '{error_message}'")
                elif error.response.status_code == codes.BAD_REQUEST and error_message.endswith("does not support query"):
                    self.logger.error(f"The stream '{self.name}' is not queryable, error message: '{error_message}'")
                else:
                    raise error
            else:
                raise error
        return None

    def wait_for_job(self, url: str) -> str:
        # using "seconds" argument because self._wait_timeout can be changed by tests
        expiration_time: DateTime = pendulum.now().add(seconds=int(self._wait_timeout * 60.0))
        job_status = "InProgress"
        delay_timeout = 0
        delay_cnt = 0
        job_info = None
        # minimal starting delay is 0.5 seconds.
        # this value was received empirically
        time.sleep(0.5)
        while pendulum.now() < expiration_time:
            job_info = self._send_http_request("GET", url=url).json()
            job_status = job_info["state"]
            if job_status in ["JobComplete", "Aborted", "Failed"]:
                if job_status != "JobComplete":
                    # this is only job metadata without payload
                    self.logger.error(f"JobStatus: {job_status}, full job response: {job_info}")

                return job_status

            if delay_timeout < self.MAX_CHECK_INTERVAL_SECONDS:
                delay_timeout = 0.5 + math.exp(delay_cnt) / 1000.0
                delay_cnt += 1

            time.sleep(delay_timeout)
            job_id = job_info["id"]
            self.logger.info(
                f"Sleeping {delay_timeout} seconds while waiting for Job: {self.name}/{job_id}" f" to complete. Current state: {job_status}"
            )

        self.logger.warning(f"Not wait the {self.name} data for {self._wait_timeout} minutes, data: {job_info}!!")
        return job_status

    def execute_job(self, query: str, url: str) -> str:
        job_status = "Failed"
        for i in range(0, self.MAX_RETRY_NUMBER):
            job_id = self.create_stream_job(query=query, url=url)
            if not job_id:
                return None
            job_full_url = f"{url}/{job_id}"
            job_status = self.wait_for_job(url=job_full_url)
            if job_status not in ["UploadComplete", "InProgress"]:
                break
            self.logger.error(f"Waiting error. Try to run this job again {i + 1}/{self.MAX_RETRY_NUMBER}...")
            self.abort_job(url=job_full_url)
            job_status = "Aborted"

        if job_status in ["Aborted", "Failed"]:
            self.delete_job(url=job_full_url)
            raise Exception(f"Job for {self.name} stream using BULK API was failed.")
        return job_full_url

    def filter_null_bytes(self, s: str):
        """
        https://github.com/airbytehq/airbyte/issues/8300
        """
        res = s.replace("\x00", "")
        if len(res) < len(s):
            self.logger.warning("Filter 'null' bytes from string, size reduced %d -> %d chars", len(s), len(res))
        return res

    def download_data(self, url: str) -> Tuple[int, dict]:
        job_data = self._send_http_request("GET", f"{url}/results")
        decoded_content = self.filter_null_bytes(job_data.content.decode("utf-8"))
        fp = io.StringIO(decoded_content, newline="")
        csv_data = csv.DictReader(fp, dialect="unix")
        for n, row in enumerate(csv_data, 1):
            yield n, row

    def abort_job(self, url: str):
        data = {"state": "Aborted"}
        self._send_http_request("PATCH", url=url, json=data)
        self.logger.warning("Broken job was aborted")

    def delete_job(self, url: str):
        self._send_http_request("DELETE", url=url)

    def next_page_token(self, last_record: dict) -> str:
        if self.primary_key and self.name not in UNSUPPORTED_FILTERING_STREAMS:
            return f"WHERE {self.primary_key} >= '{last_record[self.primary_key]}' "

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Salesforce SOQL Query: https://developer.salesforce.com/docs/atlas.en-us.232.0.api_rest.meta/api_rest/dome_queryall.htm
        """

        selected_properties = self.get_json_schema().get("properties", {})
        query = f"SELECT {','.join(selected_properties.keys())} FROM {self.name} "
        if next_page_token:
            query += next_page_token

        if self.primary_key and self.name not in UNSUPPORTED_FILTERING_STREAMS:
            query += f"ORDER BY {self.primary_key} ASC LIMIT {self.page_size}"

        return {"q": query}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        next_page_token = None

        while True:
            params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            path = self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            job_full_url = self.execute_job(query=params["q"], url=f"{self.url_base}{path}")
            if not job_full_url:
                return

            count = 0
            for count, record in self.download_data(url=job_full_url):
                yield record
            self.delete_job(url=job_full_url)

            if count < self.page_size:
                # this is a last page
                break

            next_page_token = self.next_page_token(record)
            if not next_page_token:
                # not found a next page data.
                break


class IncrementalSalesforceStream(SalesforceStream, ABC):
    state_checkpoint_interval = 500

    def __init__(self, replication_key: str, start_date: Optional[str], **kwargs):
        super().__init__(**kwargs)
        self.replication_key = replication_key
        self.start_date = self.format_start_date(start_date)

    @staticmethod
    def format_start_date(start_date: Optional[str]) -> Optional[str]:
        """Transform the format `2021-07-25` into the format `2021-07-25T00:00:00Z`"""
        if start_date:
            return pendulum.parse(start_date).strftime("%Y-%m-%dT%H:%M:%SZ")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            """
            If `next_page_token` is set, subsequent requests use `nextRecordsUrl`, and do not include any parameters.
            """
            return {}

        selected_properties = self.get_json_schema().get("properties", {})

        stream_date = stream_state.get(self.cursor_field)
        start_date = stream_date or self.start_date

        query = f"SELECT {','.join(selected_properties.keys())} FROM {self.name} "
        if start_date:
            query += f"WHERE {self.cursor_field} >= {start_date} "
        if self.name not in UNSUPPORTED_FILTERING_STREAMS:
            query += f"ORDER BY {self.cursor_field} ASC"
        return {"q": query}

    @property
    def cursor_field(self) -> str:
        return self.replication_key

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state
        object and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}


class BulkIncrementalSalesforceStream(BulkSalesforceStream, IncrementalSalesforceStream):
    def next_page_token(self, last_record: dict) -> str:
        if self.name not in UNSUPPORTED_FILTERING_STREAMS:
            return last_record[self.cursor_field]

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        selected_properties = self.get_json_schema().get("properties", {})

        stream_date = stream_state.get(self.cursor_field)
        start_date = next_page_token or stream_date or self.start_date

        query = f"SELECT {','.join(selected_properties.keys())} FROM {self.name} "
        if start_date:
            query += f"WHERE {self.cursor_field} >= {start_date} "
        if self.name not in UNSUPPORTED_FILTERING_STREAMS:
            query += f"ORDER BY {self.cursor_field} ASC LIMIT {self.page_size}"
        return {"q": query}
