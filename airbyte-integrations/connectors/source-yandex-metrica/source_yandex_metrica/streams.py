#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import io
import logging
import re
import time

import pendulum
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union, Tuple
from pendulum import DateTime
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream

logger = logging.getLogger("airbyte")
STATE_CHECKPOINT_INTERVAL = 20


class YandexMetricaStream(HttpStream, ABC):
    url_base = "https://api-metrica.yandex.net/management/v1/counter/"

    def __init__(self, counter_id: str, params: dict, **kwargs):
        self.counter_id = counter_id
        self.params = params
        super().__init__(**kwargs)

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        # Disable check_availability due to complex request flow
        # TODO: move evaluate_logrequest method to availability strategy
        return True, None

    def get_json_schema(self, ) -> Mapping[str, any]:
        schema = super().get_json_schema()
        schema["properties"] = {re.sub(r"(ym:s:|ym:pv:)", "", key): schema["properties"].pop(key) for key in
                                schema["properties"].copy()}
        return schema

    def get_request_fields(self) -> List[str]:
        return list(super().get_json_schema().get("properties"))

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {"Content-Type": "application/x-ymetrika+json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def evaluate_logrequest(self, counter_id: str):
        """
        Clean logs of the processed request prepared for downloading.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/clean.html
        """
        request_headers = self.request_headers(stream_state={})
        request_params = {
            "date1": self.params["start_date"],
            "date2": self.params["end_date"],
            "source": self.params["source"],
            "fields": self.params["fields"],
        }
        request = requests.Request("GET", f"{self.url_base}{counter_id}/logrequests/evaluate",
                                   headers=dict(request_headers, **self.authenticator.get_auth_header()),
                                   params=request_params)
        prepared_request = self._session.prepare_request(request)
        response = self._send_request(prepared_request, {})
        return response.json().get("log_request_evaluation", {}).get("possible")

    def create_logrequest(self, counter_id: str):
        """
        Creates logs request.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/createlogrequest.html
        """
        request_headers = self.request_headers(stream_state={})
        request_params = {
            "date1": self.params["start_date"],
            "date2": self.params["end_date"],
            "source": self.params["source"],
            "fields": self.params["fields"],
        }
        request = requests.Request("POST", f"{self.url_base}{counter_id}/logrequests",
                                   headers=dict(request_headers, **self.authenticator.get_auth_header()),
                                   params=request_params)
        prepared_request = self._session.prepare_request(request)
        response = self._send_request(prepared_request, {})
        return response.json().get("log_request", {}).get("request_id")

    def wait_for_job(self, counter_id: str, logrequest_id: str) -> Tuple[str, int]:
        """
        Returns information about logs request.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/getlogrequest.html
        """
        DEFAULT_WAIT_TIMEOUT_SECONDS = 300
        expiration_time: DateTime = pendulum.now().add(seconds=DEFAULT_WAIT_TIMEOUT_SECONDS)
        request_headers = self.request_headers(stream_state={})
        request = requests.Request("GET", f"{self.url_base}{counter_id}/logrequest/{logrequest_id}",
                                   headers=dict(request_headers, **self.authenticator.get_auth_header()))
        prepared_request = self._session.prepare_request(request)
        job_status = "created"
        while pendulum.now() < expiration_time:
            response = self._send_request(prepared_request, {}).json()
            job_status = response["log_request"]["status"]
            if job_status in ("processed", "processing_failed"):
                if job_status == "processing_failed":
                    logger.error(f"Error while processing {counter_id=} {logrequest_id=}")
                parts_count = response["log_request"]["parts"][-1]["part_number"]
                return job_status, parts_count
            logger.info(f"Sleeping for 30 seconds, waiting for report creation")
            time.sleep(30)
        if job_status != "processed":
            raise Exception(f"Export Job processing failed, skipping reading stream {self.name}")

    def download_report_part(self, counter_id: str, logrequest_id: str, part_number: int)-> Iterable[Mapping]:
        request_headers = self.request_headers(stream_state={})
        request = requests.Request("GET", f"{self.url_base}{counter_id}/logrequest/{logrequest_id}/part/{part_number}/download",
                                   headers=dict(request_headers, **self.authenticator.get_auth_header()))
        prepared_request = self._session.prepare_request(request)
        response = self._send_request(prepared_request, {})
        reader = csv.DictReader(io.StringIO(response.text), delimiter="\t")
        for row in reader:
            # Remove 'ym:s:' or 'ym:pv:' prefix
            row = {re.sub(r"(ym:s:|ym:pv:)", "", key): value for key, value in row.items()}

            row[self.cursor_field] = pendulum.parse(row[self.cursor_field]).to_rfc3339_string()

            yield row

    def clean_logrequest(self, counter_id: str, logrequest_id: str):
        """
        Clean logs of the processed request prepared for downloading.

        See: https://yandex.com/dev/metrika/doc/api2/logs/queries/clean.html
        """
        request_headers = self.request_headers(stream_state={})
        request = requests.Request("POST", f"{self.url_base}{counter_id}/logrequest/{logrequest_id}/clean",
                                   headers=dict(request_headers, **self.authenticator.get_auth_header()))
        prepared_request = self._session.prepare_request(request)
        self._send_request(prepared_request, {})

    def fetch_records(self, stream_state: Mapping[str, Any] = {}) -> Iterable[Mapping]:
        # Configure state
        self.params["start_date"] = stream_state.get("start_date", self.params["start_date"])
        self.params["end_date"] = stream_state.get("end_date", self.params["end_date"])
        if not self.evaluate_logrequest(self.counter_id):
            logger.warning(f"Log request for counter_id={self.counter_id} cannot be made with provided dates")
            yield {}
        logrequest_id = self.create_logrequest(self.counter_id)
        if not logrequest_id:
            yield {}
        # 3. Check logrequest status
        job_status, number_of_parts = self.wait_for_job(counter_id=self.counter_id, logrequest_id=logrequest_id)
        for part in range(number_of_parts+1):
            yield from self.download_report_part(counter_id=self.counter_id, logrequest_id=logrequest_id, part_number=part)
        self.clean_logrequest(counter_id=self.counter_id, logrequest_id=logrequest_id)



class IncrementalYandexMetricaStream(YandexMetricaStream, IncrementalMixin):
    state_checkpoint_interval = STATE_CHECKPOINT_INTERVAL
    cursor_field = "dateTime"

    def __init__(self, counter_id: str, params: dict, **kwargs):
        super().__init__(counter_id, params, **kwargs)
        self._cursor_value = ""

    @property  # State getter
    def state(self) -> MutableMapping[str, Any]:
        return (
            {self.cursor_field: self._cursor_value, "start_date": self._start_date, "end_date": self._end_date}
            if self._cursor_value
            else {}
        )

    @state.setter  # State setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field, "1970-01-01T00:00:00")
        self._start_date = value.get("start_date", self.params["start_date"])
        self._end_date = value.get("end_date", self.params["end_date"])

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        return {
            "date1": stream_state.get("start_date", self.params["start_date"]),
            "date2": stream_state.get("end_date", self.params["end_date"]),
            "source": self.params["source"],
            "fields": self.params["fields"],
        }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
        ):
            yield record
            # self._cursor_value = max(record[self.cursor_field], self._cursor_value)

        self._start_date = self.params["end_date"]
        self._end_date = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")


class Views(IncrementalYandexMetricaStream):
    primary_key = "watchID"
    def __init__(self, counter_id: str, params: dict, **kwargs):
        fields = self.get_request_fields()
        params["source"] = "hits"
        params["fields"] = fields
        super().__init__(counter_id, params, **kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequests/evaluate"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state=stream_state)

    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        yield from self.fetch_records(stream_state)


class Sessions(IncrementalYandexMetricaStream):
    primary_key = "visitID"

    def __init__(self, counter_id: str, params: dict, **kwargs):
        params["source"] = "visits"
        params["fields"] = self.get_request_fields()
        super().__init__(counter_id, params, **kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.counter_id}/logrequests/evaluate"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return super().request_params(stream_state=stream_state)

    @property
    def raise_on_http_errors(self) -> bool:
        return False

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        yield from self.fetch_records(stream_state)
