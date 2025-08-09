#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)


@dataclass
class CreationRequester(HttpRequester):

    # CreationRequester checks if the job exists first before attempting to create the job
    # This is because If the job exists, creating the job returns an error
    # CreationRequester achieves this by first pulling a list of all jobs. It then checks if the job is in the list.
    # If the job is not in the list, CreationRequester goes ahead to create the job as configured.
    # Essentially, CreationRequester sends two requests in the worst case.

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

    # PollingRequester gets the job id first before pulling the job's reports
    # It achieves this by first pulling a list of all jobs, extracting the job and getting its id
    # PollingRequester then uses the id to pull the job's reports
    # Essentially, PollingRequester sends two requests in cases.

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
            # params={"createdAfter": self.start_time} if self.start_time else {},
        )
        return reports_response


@dataclass
class StatusExtractor(RecordExtractor):

    # The API doesn't explicitly state the status of the job's reports creation.
    # Hence, StatusExtractor improvises by returning "running" if the reports are not available i.e the reports list is empty
    # It then returns "completed" if the reports list contains items.

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        reports = response.json().get("reports", [])
        if not reports:
            yield "running"
        else:
            yield "completed"


@dataclass
class DownloadTargetExtractor(RecordExtractor):

    # There are usually more than one report url for a job returned as items in a json
    # DownloadTargetExtractor extracts these urls as a list

    def extract_records(self, response: requests.Response) -> Iterable[MutableMapping[Any, Any]]:
        reports = response.json().get("reports", {})
        urls = list(map(lambda report: report.get("downloadUrl", ""), reports))
        return urls
