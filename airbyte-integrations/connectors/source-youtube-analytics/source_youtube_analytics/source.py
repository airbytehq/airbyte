#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import csv
import datetime
import io
import json
import pkgutil
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import urljoin

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class ReportResources(HttpStream):
    name = None
    primary_key = "id"
    url_base = "https://youtubereporting.googleapis.com/v1/"

    def __init__(self, name: str, job_id: str, **kwargs):
        self.name = name
        self.job_id = job_id
        return super().__init__(**kwargs)

    def create_job(self, name):
        request_json = {
            "name": "Airbyte reporting job",
            "reportTypeId": name,
        }
        url = urljoin(self.url_base, "jobs")
        response = self._session.post(url, json=request_json)
        response.raise_for_status()
        response_json = response.json()
        return response_json["id"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        reports = []
        for report in response_json.get("reports", []):
            report = {**report}
            report["createTime"] = datetime.datetime.strptime(report["createTime"], "%Y-%m-%dT%H:%M:%S.%f%z")
            report["startTime"] = datetime.datetime.strptime(report["startTime"], "%Y-%m-%dT%H:%M:%S%z")
            report["endTime"] = datetime.datetime.strptime(report["endTime"], "%Y-%m-%dT%H:%M:%S%z")
            reports.append(report)
        reports.sort(key=lambda x: x["startTime"])
        date = kwargs["stream_state"].get("date")
        if date:
            reports = [r for r in reports if int(r["startTime"].date().strftime("%Y%m%d")) >= date]
        return reports

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        if not self.job_id:
            self.job_id = self.create_job(self.name)
            self.logger.info(f"YouTube reporting job is created: '{self.job_id}'")
        return "jobs/{}/reports".format(self.job_id)


class ChannelReports(HttpSubStream):
    name = None
    primary_key = None
    cursor_field = "date"
    url_base = "https://youtubereporting.googleapis.com/v1/"
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, name: str, dimensions: List[str], **kwargs):
        self.name = name
        self.primary_key = dimensions
        return super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        fp = io.StringIO(response.text)
        reader = csv.DictReader(fp)
        for record in reader:
            yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if not current_stream_state:
            return {"date": latest_record["date"]}
        return {"date": max(current_stream_state["date"], latest_record["date"])}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return stream_slice["parent"]["downloadUrl"][len(self.url_base):]


class SourceYoutubeAnalytics(AbstractSource):
    @staticmethod
    def get_authenticator(config):
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        refresh_token = config["refresh_token"]

        return Oauth2Authenticator(
            token_refresh_endpoint="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            scopes=["https://www.googleapis.com/auth/yt-analytics-monetary.readonly"],
        )

    def get_jobs(self, authenticator):
        headers = authenticator.get_auth_header()
        url = urljoin(ReportResources.url_base, "jobs")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("jobs", {})

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = self.get_authenticator(config)

        try:
            self.get_jobs(authenticator)
        except Exception as e:
            return False, str(e)

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self.get_authenticator(config)
        jobs = self.get_jobs(authenticator)
        report_to_job_id = {j["reportTypeId"]: j["id"] for j in jobs}

        channel_reports = json.loads(pkgutil.get_data("source_youtube_analytics", "defaults/channel_reports.json"))

        streams = []
        for channel_report in channel_reports:
            stream_name = channel_report["id"]
            dimensions = channel_report["dimensions"]
            job_id = report_to_job_id.get(stream_name)
            parent = ReportResources(name=stream_name, job_id=job_id, authenticator=authenticator)
            streams.append(ChannelReports(name=stream_name, dimensions=dimensions, parent=parent, authenticator=authenticator))
        return streams
