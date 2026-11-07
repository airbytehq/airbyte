#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import csv
import io
import logging
import re
import time
from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

import pendulum
import requests
from pendulum import DateTime

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams.core import IncrementalMixin, StreamData
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import (
    ErrorHandler,
    ErrorResolution,
    HttpStatusErrorHandler,
    ResponseAction,
)


logger = logging.getLogger("airbyte")


class YandexMetricaErrorHandler(HttpStatusErrorHandler):
    """Retries 429 and 5xx like the default handler, but hands other 4xx responses back to the caller instead of raising."""

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if (
            isinstance(response_or_exception, requests.Response)
            and 400 <= response_or_exception.status_code < 500
            and response_or_exception.status_code != 429
        ):
            return ErrorResolution(
                response_action=ResponseAction.IGNORE,
                failure_type=FailureType.config_error,
                error_message=f"Yandex Metrica API returned HTTP {response_or_exception.status_code}: {response_or_exception.text}",
            )
        return super().interpret_response(response_or_exception)


class YandexMetricaStream(HttpStream, ABC):
    url_base = "https://api-metrica.yandex.net/management/v1/counter/"
    _source = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.counter_id = config.get("counter_id")
        self.params = {}
        self.config = config

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        return True, None

    def get_json_schema(
        self,
    ) -> Mapping[str, any]:
        schema = copy.deepcopy(super().get_json_schema())
        schema["properties"] = {re.sub(r"(ym:s:|ym:pv:)", "", key): value for key, value in schema["properties"].items()}
        return schema

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        pass

    def get_request_fields(self) -> List[str]:
        return list(super().get_json_schema().get("properties"))

    def get_error_handler(self) -> Optional[ErrorHandler]:
        return YandexMetricaErrorHandler(logger=logger)

    def _send(self, http_method: str, path: str, params: Optional[Mapping[str, Any]] = None) -> requests.Response:
        _, response = self._http_client.send_request(
            http_method=http_method,
            url=f"{self.url_base}{self.counter_id}/{path}",
            request_kwargs={},
            headers=self.request_headers(stream_state={}),
            params=params,
        )
        return response

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/x-ymetrika+json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def evaluate_logrequest(self):
        """
        Clean logs of the processed request prepared for downloading.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/clean.html
        """
        request_params = {
            "date1": self.config.get("start_date"),
            "date2": self.config.get("end_date"),
            "source": self._source,
            "fields": self.get_request_fields(),
        }
        response = self._send("GET", "logrequests/evaluate", params=request_params)
        return response.json().get("log_request_evaluation", {}).get("possible") if response.status_code == 200 else False

    def create_logrequest(self):
        """
        Creates logs request.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/createlogrequest.html
        """
        request_params = {
            "date1": self.params["start_date"],
            "date2": self.params["end_date"],
            "source": self._source,
            "fields": self.get_request_fields(),
        }
        response = self._send("POST", "logrequests", params=request_params)
        return response.json().get("log_request", {}).get("request_id")

    def wait_for_job(self, logrequest_id: str) -> Tuple[str, int]:
        """
        Returns information about logs request.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/getlogrequest.html
        """
        wait_timeout_hours = 2
        expiration_time: DateTime = pendulum.now().add(hours=wait_timeout_hours)
        job_status = "created"
        while pendulum.now() < expiration_time:
            response = self._send("GET", f"logrequest/{logrequest_id}").json()
            job_status = response["log_request"]["status"]
            if job_status in ("processed", "processing_failed"):
                if job_status == "processing_failed":
                    logger.error(f"Error while processing {self.counter_id=} {logrequest_id=}")
                parts_count = response["log_request"]["parts"][-1]["part_number"]
                return job_status, parts_count
            logger.info("Sleeping for 60 seconds, waiting for report getting ready")
            time.sleep(60)
        if job_status != "processed":
            raise Exception(f"Export Job processing failed, skipping reading stream {self.name}")

    def download_report_part(self, logrequest_id: str, part_number: int) -> Iterable[Mapping]:
        response = self._send("GET", f"logrequest/{logrequest_id}/part/{part_number}/download")
        reader = csv.DictReader(io.StringIO(response.text), delimiter="\t")
        for row in reader:
            # Remove 'ym:s:' or 'ym:pv:' prefix
            row = {re.sub(r"(ym:s:|ym:pv:)", "", key): value for key, value in row.items()}

            row[self.cursor_field] = pendulum.parse(row[self.cursor_field]).to_rfc3339_string()

            yield row

    def clean_logrequest(self, logrequest_id: str):
        """
        Clean logs of the processed request prepared for downloading.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/clean.html
        """
        self._send("POST", f"logrequest/{logrequest_id}/clean")

    def fetch_records(self, stream_state: Mapping[str, Any] = {}) -> Iterable[Mapping]:
        # Configure state
        self.params["start_date"] = stream_state.get("start_date", self.config["start_date"])
        self.params["end_date"] = stream_state.get("end_date", self.config["end_date"])
        logrequest_id = self.create_logrequest()
        if not logrequest_id:
            yield {}
        # 3. Check logrequest status
        job_status, number_of_parts = self.wait_for_job(logrequest_id=logrequest_id)
        for part in range(number_of_parts + 1):
            yield from self.download_report_part(logrequest_id=logrequest_id, part_number=part)
        self.clean_logrequest(logrequest_id=logrequest_id)


class IncrementalYandexMetricaStream(YandexMetricaStream, IncrementalMixin):
    cursor_field = "dateTime"
    _cursor_value = ""

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: str(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        pass

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> bool:
        record_value = record.get(self.cursor_field)
        cursor_value = max((stream_state or {}).get(self.cursor_field, self.config.get("start_date")), record_value)
        max_state = max(self.state.get(self.cursor_field), cursor_value)
        self.state = {self.cursor_field: max_state}
        return not stream_state or stream_state.get(self.cursor_field, 0) < record_value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        for record in self.fetch_records(stream_state or {}):
            if self.filter_by_state(stream_state=stream_state, record=record):
                yield record


class Views(IncrementalYandexMetricaStream):
    primary_key = "watchID"
    _source = "hits"


class Sessions(IncrementalYandexMetricaStream):
    primary_key = "visitID"
    _source = "visits"
