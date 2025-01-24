#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
    RequestInput,
)
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester

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
        request, jobs_response = self._http_client.send_request(
                http_method="GET",
                url=self._join_url(self.get_url_base(), "jobs"),
                request_kwargs={"stream": self.stream_response},
            )
        jobs_list = jobs_response.json().get("jobs", [])
        stream_name = self.name.split(" - ")[-1]
        if stream_name in [job["reportTypeId"] for job in jobs_list]:
            return jobs_response
        else:
            return super().send_request(**kwargs)

class PollingRequester(HttpRequester):

    def send_request(self, stream_state = None, stream_slice = None, next_page_token = None, path = None, request_headers = None, request_params = None, request_body_data = None, request_body_json = None, log_formatter = None):
        response = {
            "status": "pending"
        }
        jobs_response = super().send_request(stream_state, stream_slice, next_page_token, path, request_headers, request_params, request_body_data, request_body_json, log_formatter)
        jobs_list = jobs_response.json().get("jobs", [])
        job_resource = [job for job in jobs_list if job["reportTypeId"] == self.name][0]
        job_id = job_resource["id"]

        try:
            request, reports_response = self._http_client.send_request(
                http_method=self.get_method().value,
                url=self._join_url(self.get_url_base(), f"jobs/{job_id}/reports"),
                request_kwargs={"stream": self.stream_response},
                params={"startTimeAtOrAfter": self.start_time} if self.start_time else {},
            )

            urls = [report["downloadUrl"] for report in reports_response.json()["reports"]]
            response["urls"] = urls
            response["status"] = "ready"
        except:
            pass

        return response
