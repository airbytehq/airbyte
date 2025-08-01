#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, ResponseAction


@dataclass
class CreationRequester(HttpRequester):
    request_body_json: Optional[RequestInput] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self.request_options_provider = InterpolatedRequestOptionsProvider(
            request_body_json=self.request_body_json,
            config=self.config,
            parameters=parameters or {},
        )
        super().__post_init__(parameters)

    def send_request(self, **kwargs):
        jobs_response = self.get_jobs_response()
        stream_name = self.name.split(" - ")[-1]
        if stream_name not in [job["reportTypeId"] for job in jobs_response.json().get("jobs", [])]:
            super().send_request(**kwargs)
            jobs_response = self.get_jobs_response()
        return jobs_response

    def get_jobs_response(self):
        request, jobs_response = self._http_client.send_request(
            http_method="GET",
            url=self._join_url(self.get_url_base(), "jobs"),
            request_kwargs={"stream": self.stream_response},
        )
        return jobs_response


@dataclass
class PollingRequester(HttpRequester):
    def send_request(self, **kwargs):
        stream_name = self.name.split(" - ")[-1]

        jobs_response = super().send_request(**kwargs)
        jobs_list = jobs_response.json().get("jobs", [])
        job_resource = list(filter(lambda job: job["reportTypeId"] == stream_name, jobs_list))[0]
        job_id = job_resource["id"]

        request, reports_response = self._http_client.send_request(
            http_method=self.get_method().value,
            url=self._join_url(self.get_url_base(), f"jobs/{job_id}/reports"),
            request_kwargs={"stream": self.stream_response},
            params={"createdAfter": self.start_time} if self.start_time else {},
        )
        return reports_response


@dataclass
class StatusExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        reports = response.json().get("reports", [])
        if not reports:
            yield "running"
        else:
            yield "completed"


@dataclass
class DownloadTargetExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        reports = response.json().get("reports", [])
        urls = list(map(lambda report: report.get("downloadUrl", ""), reports))
        return urls
