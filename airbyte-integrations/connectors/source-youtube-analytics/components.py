#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Union

import requests

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


@dataclass
class PollingRequester(HttpRequester):
    def send_request(self, **kwargs):
        jobs_response = super().send_request(**kwargs)
        jobs_list = jobs_response.json().get("jobs", [])
        job_resource = [job for job in jobs_list if job["reportTypeId"] == self.name][0]
        job_id = job_resource["id"]

        request, reports_response = self._http_client.send_request(
            http_method=self.get_method().value,
            url=self._join_url(self.get_url_base(), f"jobs/{job_id}/reports"),
            request_kwargs={"stream": self.stream_response},
            params={"startTimeAtOrAfter": self.start_time} if self.start_time else {},
        )
        return reports_response


@dataclass
class YoutubeAnalyticsErrorHandler(DefaultErrorHandler):
    def daily_quota_exceeded(self, response: requests.Response):
        """Response example:
            {
              "error": {
                "code": 429,
                "message": "Quota exceeded for quota metric 'Free requests' and limit 'Free requests per minute' of service 'youtubereporting.googleapis.com' for consumer 'project_number:863188056127'.",
                "status": "RESOURCE_EXHAUSTED",
                "details": [
                  {
                    "reason": "RATE_LIMIT_EXCEEDED",
                    "metadata": {
                      "consumer": "projects/863188056127",
                      "quota_limit": "FreeQuotaRequestsPerMinutePerProject",
                      "quota_limit_value": "60",
                      "quota_metric": "youtubereporting.googleapis.com/free_quota_requests",
                      "service": "youtubereporting.googleapis.com",
                    }
                  },
                ]
              }
            }

        :param response:
        :return:
        """
        details = response.json().get("error", {}).get("details", [])
        for detail in details:
            if detail.get("reason") == "RATE_LIMIT_EXCEEDED":
                if detail.get("metadata", {}).get("quota_limit") == "FreeQuotaRequestsPerDayPerProject":
                    return True, f"Exceeded daily quota: {detail.get('metadata', {}).get('quota_limit_value')} reqs/day"
                break
        return False, ""

    def should_retry(self, response: requests.Response):
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 500s to handle transient server errors
         - 429 (Too Many Requests) indicating rate limiting:
            Different behavior in case of 'RATE_LIMIT_EXCEEDED':

            Requests Per Minute:
            "message": "Quota exceeded for quota metric 'Free requests' and limit 'Free requests per minute' of service 'youtubereporting.googleapis.com' for consumer 'project_number:863188056127'."
            "quota_limit": "FreeQuotaRequestsPerMinutePerProject",
            "quota_limit_value": "60",

            --> use increased retry_factor (30 seconds)

            Requests Per Day:
            "message": "Quota exceeded for quota metric 'Free requests' and limit 'Free requests per day' of service 'youtubereporting.googleapis.com' for consumer 'project_number:863188056127"
            "quota_limit": "FreeQuotaRequestsPerDayPerProject
            "quota_limit_value": "20000",

            --> just throw an error, next scan is reasonable to start only in 1 day.
        """
        if 500 <= response.status_code < 600:
            return True, ""

        if response.status_code == 429 and not self.daily_quota_exceeded(response):
            return True, ""

        return False, ""

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        """
        Interprets responses and exceptions, providing custom error resolutions for specific exceptions.
        """
        if_retry, error_message = self.should_retry(response_or_exception)
        if if_retry:
            return ErrorResolution(
                response_action=ResponseAction.RETRY,
                error_message=error_message,
            )
        return super().interpret_response(response_or_exception)

    def backoff_time(
        self,
        response_or_exception: Optional[Union[requests.Response, requests.RequestException]],
        attempt_count: int = 0,
    ) -> Optional[float]:
        """
        Default FreeQuotaRequestsPerMinutePerProject is 60 reqs/min, so reasonable delay is 30 seconds
        """
        return 30
