#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import csv
import datetime
import io
import json
import pkgutil
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class CustomBackoffMixin:
    def daily_quota_exceeded(self, response: requests.Response) -> bool:
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
                    self.logger.error(f"Exceeded daily quota: {detail.get('metadata', {}).get('quota_limit_value')} reqs/day")
                    return True
                break
        return False

    def should_retry(self, response: requests.Response) -> bool:
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
            return True

        if response.status_code == 429 and not self.daily_quota_exceeded(response):
            return True

        return False

    @property
    def retry_factor(self) -> float:
        """
        Default FreeQuotaRequestsPerMinutePerProject is 60 reqs/min, so reasonable delay is 30 seconds
        """
        return 30


class JobsResource(CustomBackoffMixin, HttpStream):
    """
    https://developers.google.com/youtube/reporting/v1/reference/rest/v1/jobs

    All YouTube Analytics streams require a created reporting job.
    This class allows to `list` all existing reporting jobs or `create` new reporting job for a specific stream. One stream can have only one reporting job.
    By creating a reporting job, you are instructing YouTube to generate stream data on a daily basis. If reporting job is removed YouTube removes all stream data.

    On every connector invocation, it gets a list of all running reporting jobs, if the currently processed stream has a reporting job - connector does nothing,
    but if the currently processed stream does not have a job connector immediately creates one. This connector does not store IDs of reporting jobs.
    If the reporting job was created by the user separately, this connector just uses that job. This connector does not remove reporting jobs it can only create them.

    After reporting job is created, the first data can be available only after up to 48 hours.
    """

    name = None
    primary_key = None
    http_method = None
    raise_on_http_errors = True
    url_base = "https://youtubereporting.googleapis.com/v1/"
    JOB_NAME = "Airbyte reporting job"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def should_retry(self, response: requests.Response) -> bool:
        # if the connected Google account is not bounded with target Youtube account,
        # we receive `401: UNAUTHENTICATED`
        if response.status_code == 401:
            setattr(self, "raise_on_http_errors", False)
            return False
        else:
            return super().should_retry(response)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [response.json()]

    def path(self, **kwargs) -> str:
        return "jobs"

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        if self.name:
            return {"name": self.JOB_NAME, "reportTypeId": self.name}

    def list(self):
        "https://developers.google.com/youtube/reporting/v1/reference/rest/v1/jobs/list"
        self.name = None
        self.http_method = "GET"
        results = list(self.read_records(sync_mode=None))
        result = results[0]
        return result.get("jobs", {})

    def create(self, name):
        "https://developers.google.com/youtube/reporting/v1/reference/rest/v1/jobs/create"
        self.name = name
        self.http_method = "POST"
        results = list(self.read_records(sync_mode=None))
        result = results[0]
        return result["id"]


class ReportResources(CustomBackoffMixin, HttpStream):
    "https://developers.google.com/youtube/reporting/v1/reference/rest/v1/jobs.reports/list"

    name = None
    primary_key = "id"
    url_base = "https://youtubereporting.googleapis.com/v1/"

    def __init__(self, name: str, jobs_resource: JobsResource, job_id: str, start_time: str = None, **kwargs):
        self.name = name
        self.jobs_resource = jobs_resource
        self.job_id = job_id
        self.start_time = start_time
        super().__init__(**kwargs)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if not self.job_id:
            self.job_id = self.jobs_resource.create(self.name)
            self.logger.info(f"YouTube reporting job is created: '{self.job_id}'")
        return "jobs/{}/reports".format(self.job_id)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {"startTimeAtOrAfter": self.start_time} if self.start_time else {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        reports = []
        for report in response_json.get("reports", []):
            report = {**report}
            report["startTime"] = datetime.datetime.strptime(report["startTime"], "%Y-%m-%dT%H:%M:%S%z")
            reports.append(report)
        reports.sort(key=lambda x: x["startTime"])
        date = kwargs["stream_state"].get("date")
        if date:
            reports = [r for r in reports if int(r["startTime"].date().strftime("%Y%m%d")) > date]
        if not reports:
            reports.append(None)
        return reports


class ChannelReports(CustomBackoffMixin, HttpSubStream):
    "https://developers.google.com/youtube/reporting/v1/reports/channel_reports"

    name = None
    primary_key = None
    cursor_field = "date"
    url_base = ""
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, name: str, dimensions: List[str], **kwargs):
        self.name = name
        self.primary_key = dimensions
        super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        fp = io.StringIO(response.text)
        reader = csv.DictReader(fp)
        for record in reader:
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            return {self.cursor_field: latest_record[self.cursor_field]}
        return {self.cursor_field: max(current_stream_state[self.cursor_field], latest_record[self.cursor_field])}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return stream_slice["parent"]["downloadUrl"]

    def read_records(self, *, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        parent = stream_slice.get("parent")
        if parent:
            yield from super().read_records(stream_slice=stream_slice, **kwargs)
        else:
            self.logger.info("no data from parent stream")
            yield from []


class SourceYoutubeAnalytics(AbstractSource):
    @staticmethod
    def get_authenticator(config):
        credentials = config["credentials"]
        client_id = credentials["client_id"]
        client_secret = credentials["client_secret"]
        refresh_token = credentials["refresh_token"]

        return Oauth2Authenticator(
            token_refresh_endpoint="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = self.get_authenticator(config)
        jobs_resource = JobsResource(authenticator=authenticator)
        result = jobs_resource.list()
        if result:
            return True, None
        else:
            return (
                False,
                "The Youtube account is not valid. Please make sure you're trying to use the active Youtube Account connected to your Google Account.",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        jobs_resource = JobsResource(authenticator=authenticator)
        jobs = jobs_resource.list()
        report_to_job_id = {j["reportTypeId"]: j["id"] for j in jobs}

        # By default, API returns reports for last 60 days. Report for each day requires a separate request.
        # Full scan of all 18 streams requires ~ 1100 requests (18+18*60), so we can hit 'default' API quota limits:
        # - 60 reqs per minute
        # - 20000 reqs per day
        # For SAT: scan only last N days ('testing_period' option) in order to decrease a number of requests and avoid API limits
        start_time = None
        testing_period = config.get("testing_period")
        if testing_period:
            start_time = pendulum.today().add(days=-int(testing_period)).to_rfc3339_string()

        channel_reports = json.loads(pkgutil.get_data("source_youtube_analytics", "defaults/channel_reports.json"))

        streams = []
        for channel_report in channel_reports:
            stream_name = channel_report["id"]
            dimensions = channel_report["dimensions"]
            job_id = report_to_job_id.get(stream_name)
            parent = ReportResources(
                name=stream_name, jobs_resource=jobs_resource, job_id=job_id, start_time=start_time, authenticator=authenticator
            )
            streams.append(ChannelReports(name=stream_name, dimensions=dimensions, parent=parent, authenticator=authenticator))
        return streams
