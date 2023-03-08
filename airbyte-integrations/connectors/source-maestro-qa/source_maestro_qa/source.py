#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import time
import requests
import csv
import codecs
import pendulum
import logging
from urllib.parse import urljoin
from contextlib import closing
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


logger = logging.getLogger("airbyte")

BASE_URL = "https://app.maestroqa.com/api/v1/"


class MaestroQAStream(HttpStream, ABC):
    url_base = BASE_URL
    http_method = "POST"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return super().next_page_token(response)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()["data"]


class MaestroQAExportStream(MaestroQAStream, ABC):
    def _send_http_request(
        self, method: str, url: str, headers: Mapping[str, Any] = None, params: Mapping[str, Any] = None, json: Mapping[str, Any] = None
    ) -> requests.Response:
        args = dict(
            method=method,
            url=url,
            headers={**(headers or {}), **self.authenticator.get_auth_header()},
            params=params,
            json=json,
        )
        request = self._session.prepare_request(requests.Request(**args))
        return self._send_request(request, {})

    def download_data(self, url: str) -> Iterable[Mapping[str, Any]]:
        with closing(self._send_http_request("GET", url)) as response:
            reader = csv.DictReader(codecs.iterdecode(response.iter_lines(), "unicode_escape"))
            yield from reader

    def wait_for_job(self, export_id: str, headers: Mapping[str, Any]) -> str:
        time.sleep(1)
        job_status = "requested"
        export_url = urljoin(self.url_base, "get-export-data")
        headers = {**headers, "exportId": export_id}

        while job_status in ["requested", "in_progress"]:
            response = self._send_http_request("GET", export_url, headers=headers)
            response.raise_for_status()

            result = response.json()
            job_status = result["status"]

            if job_status == "errored":
                raise f"Error running export job. Stream: {self.name}"

            if job_status == "complete":
                return result["dataUrl"]

            time.sleep(0.5)

    def create_export_job(self, path: str, headers: Mapping[str, Any], json: Mapping[str, Any]) -> Optional[str]:
        try:
            url = urljoin(self.url_base, path)
            logger.info(headers)
            response = self._send_http_request("POST", url, headers=headers, json=json)
            return response.json()["exportId"]
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Error creating export job. Stream: {self.name}, error: {e}")

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:

        path = self.path(stream_state=stream_state, stream_slice=stream_slice)
        headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice)
        json = self.request_body_json(stream_state=stream_state, stream_slice=stream_slice)

        export_id = self.create_export_job(path, headers, json)
        if export_id:
            data_url = self.wait_for_job(export_id, headers)
            if data_url:
                yield from self.download_data(data_url)

class AgentGroups(MaestroQAExportStream):
    primary_key = "agent_ids"

    @property
    def use_cache(self):
        return True

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {
            "includeUnavailable": True,
        }

    def path(self, **kwargs) -> str:
        return "request-groups-export"


class IncrementalMaestroQAStream(MaestroQAExportStream, ABC):
    cursor_field = "last_synced_at"
    state_checkpoint_interval = None

    def __init__(self, default_start_date: str, **kwargs):
        self._start_ts = default_start_date
        self._end_ts = pendulum.now("UTC").to_iso8601_string()
        super().__init__(**kwargs)

    @property
    def state(self) -> str:
        return {self.cursor_field: self._cursor_value}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = max(value.get(self.cursor_field), self._cursor_value or self._start_ts)

    def request_body_json(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        stream_state = stream_state or {}
        return {
            "startDate": stream_state.get(self.cursor_field, self._start_ts),
            "endDate": self._end_ts,
        }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)
        self._cursor_value = self._end_ts


class RawExport(IncrementalMaestroQAStream):
    primary_key = "gradable_id"
    report_type = None

    def path(self, **kwargs) -> str:
        return "request-raw-export"

    def request_body_json(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Optional[Mapping]:
        body = super().request_body_json(stream_state)
        return {
            **body,
            "singleFileExport": self.report_type,
            "includeCalibrations": "all",
            "includeGraderQA": True,
        }


class Annotations(RawExport):
    primary_key = ["gradable_id", "annotation_id", "date_reported_as"]
    report_type = "annotations"


class CSAT(RawExport):
    report_type = "csat"


class IndividualAnswers(RawExport):
    primary_key = ["gradable_id", "question_id", "date_reported_as"]
    report_type = "individual_answers"


class SectionScores(RawExport):
    primary_key = ["gradable_id", "section_id", "date_reported_as"]
    report_type = "section_scores"


class TotalScores(RawExport):
    primary_key = ["gradable_id", "date_reported_as"]
    report_type = "total_scores"


class AuditLogs(IncrementalMaestroQAStream):
    primary_key = ["activity_id", "time_stamp", "description"]

    def path(self, **kwargs) -> str:
        return "request-audit-log-export"


class ScreenCaptureUsageStats(MaestroQAStream):
    primary_key = "agentId"
    _group_ids = []

    def __init__(self, parent: MaestroQAStream, **kwargs):
        self.parent = parent
        super().__init__(**kwargs)

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        return {
            "groupIds": self._group_ids,
            "interval": "day",
        }

    def path(self, **kwargs) -> str:
        return "screen-capture-usage-stats"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self._group_ids = list(
            set([rec.get("group_id") for rec in self.parent.read_records(sync_mode, cursor_field, stream_slice, stream_state)])
        )
        return super().read_records(sync_mode, cursor_field, stream_slice, stream_state)


class TokenAuth(TokenAuthenticator):
    """Overwrite to allow token without auth method"""
    @property
    def token(self) -> str:
        return self._token


class SourceMaestroQA(AbstractSource):
    def get_auth(self, config) -> TokenAuth:
        return TokenAuth(token=config.get("api_key"), auth_method="", auth_header="apitoken")

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = self.get_auth(config)
            stream = AgentGroups(authenticator=auth)
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as error:
            return False, f"Unable to connect to MaestroQA API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        default_start_date = config.get("start_date")

        agent_groups = AgentGroups(authenticator=auth)
        return [
            agent_groups,
            Annotations(authenticator=auth, default_start_date=default_start_date),
            CSAT(authenticator=auth, default_start_date=default_start_date),
            IndividualAnswers(authenticator=auth, default_start_date=default_start_date),
            SectionScores(authenticator=auth, default_start_date=default_start_date),
            TotalScores(authenticator=auth, default_start_date=default_start_date),
            AuditLogs(authenticator=auth, default_start_date=default_start_date),
            ScreenCaptureUsageStats(authenticator=auth, parent=agent_groups),
        ]
