#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from gzip import decompress
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urljoin

import backoff
import pendulum
import pytz
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from pydantic import BaseModel
from source_amazon_ads.schemas import CatalogModel, MetricsReport, Profile
from source_amazon_ads.spec import AmazonAdsConfig
from source_amazon_ads.streams.common import BasicAmazonAdsStream

logger = AirbyteLogger()


class RecordType(str, Enum):
    CAMPAIGNS = "campaigns"
    ADGROUPS = "adGroups"
    PRODUCTADS = "productAds"
    TARGETS = "targets"
    ASINS = "asins"


class Status(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class ReportInitResponse(BaseModel):
    reportId: str
    status: str


class ReportStatus(BaseModel):
    status: str
    location: Optional[str]


@dataclass
class ReportInfo:
    report_id: str
    profile_id: int
    record_type: str


class TooManyRequests(Exception):
    """
    Custom exception occured when response with 429 status code received
    """


class ReportStream(BasicAmazonAdsStream, ABC):
    """
    Common base class for report streams
    """

    primary_key = None
    CHECK_INTERVAL_SECONDS = 30
    # Async report generation time is 15 minutes according to docs:
    # https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes
    # (Service limits section)
    REPORT_WAIT_TIMEOUT = timedelta(minutes=20)
    # Format used to specify metric generation date over Amazon Ads API.
    REPORT_DATE_FORMAT = "%Y%m%d"
    cursor_field = "reportDate"

    def __init__(self, config: AmazonAdsConfig, profiles: List[Profile], authenticator: Oauth2Authenticator):
        self._authenticator = authenticator
        self._session = requests.Session()
        self._model = self._generate_model()
        # Set start date from config file, should be in UTC timezone.
        self._start_date = pendulum.parse(config.start_date).set(tz="UTC") if config.start_date else None
        super().__init__(config, profiles)

    @property
    def model(self) -> CatalogModel:
        return self._model

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        This is base method of CDK Stream class for getting metrics report. It
        collects metrics for all profiles and record types. Amazon Ads metric
        generation works in async way: First we need to initiate creating report
        for specific profile/record type/date and then constantly check for report
        generation status - when it will have "SUCCESS" status then download the
        report and parse result.
        """

        if not stream_slice:
            # In case of stream_slices method returned [None] object and
            # stream_slice is None.
            # This may occure if we have abnormal stream state with start_date
            # parameter pointing to the future. In this case we dont need to
            # take any action and just return.
            return
        report_date = stream_slice[self.cursor_field]
        report_infos = self._init_reports(report_date)
        logger.info(f"Waiting for {len(report_infos)} report(s) to be generated")
        # According to Amazon Ads API docs metric generation takes maximum 15
        # minutes. But in case reports wont be generated we dont want this stream to
        # hung forever. Store timepoint when report generation has started to
        # check if it takes to long to break a loop.
        start_time_point = datetime.now()
        while report_infos and datetime.now() <= start_time_point + self.REPORT_WAIT_TIMEOUT:
            completed_reports = []
            logger.info(f"Checking report status, {len(report_infos)} report(s) remained")
            for report_info in report_infos:
                report_status, download_url = self._check_status(report_info)
                if report_status == Status.FAILURE:
                    raise Exception(f"Report for {report_info.profile_id} with {report_info.record_type} type generation failed")
                elif report_status == Status.SUCCESS:
                    metric_objects = self._download_report(report_info, download_url)
                    for metric_object in metric_objects:
                        yield self._model(
                            profileId=report_info.profile_id,
                            recordType=report_info.record_type,
                            reportDate=report_date,
                            metric=metric_object,
                        ).dict()
                    completed_reports.append(report_info)
            for completed_report in completed_reports:
                report_infos.remove(completed_report)
            if report_infos:
                logger.info(f"{len(report_infos)} report(s) remained, taking {self.CHECK_INTERVAL_SECONDS} seconds timeout")
                time.sleep(self.CHECK_INTERVAL_SECONDS)
        if not report_infos:
            logger.info("All reports have been processed")
        else:
            raise Exception("Not all reports has been processed due to timeout")

    def _generate_model(self):
        """
        Generate pydantic model based on combined list of all the metrics
        attributes for particular stream. This model later will be used for
        discover schema generation.
        """
        metrics = set()
        for metric_list in self.metrics_map.values():
            metrics.update(set(metric_list))
        return MetricsReport.generate_metric_model(metrics)

    def _get_auth_headers(self, profile_id: int):
        return {
            "Amazon-Advertising-API-ClientId": self._client_id,
            "Amazon-Advertising-API-Scope": str(profile_id),
            **self._authenticator.get_auth_header(),
        }

    @abstractmethod
    def report_init_endpoint(self, record_type: str) -> str:
        """
        :param record_type - type of report to generate. Depending on stream
        type it colud be campaigns, targets, asins and so on (see RecordType enum).
        :return: endpoint to initial report generating process.
        """

    @property
    @abstractmethod
    def metrics_map(self) -> Dict[str, List]:
        """
        :return: Map record type to list of available metrics
        """

    def _check_status(self, report_info: ReportInfo) -> Tuple[Status, str]:
        """
        Check report status and return download link if report generated successfuly
        """
        check_endpoint = f"/v2/reports/{report_info.report_id}"
        resp = self._send_http_request(urljoin(self._url, check_endpoint), report_info.profile_id)
        resp = ReportStatus.parse_raw(resp.text)
        return resp.status, resp.location

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            TooManyRequests,
        ),
        max_tries=5,
    )
    def _send_http_request(self, url: str, profile_id: int, json: dict = None):
        headers = self._get_auth_headers(profile_id)
        if json:
            response = self._session.post(url, headers=headers, json=json)
        else:
            response = self._session.get(url, headers=headers)
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise TooManyRequests()
        return response

    @staticmethod
    def get_report_date_ranges(start_report_date: Optional[datetime]) -> Iterable[str]:
        """
        Generates dates in YYYYMMDD format for each day started from
        start_report_date until current date (current date included)
        :param start_report_date Starting date to generate report date list. In
        case it is None it would return today's date.
        :return List of days from start_report_date up until today in format
        specified by REPORT_DATE_FORMAT variable.
        """
        now = datetime.utcnow()
        if not start_report_date:
            start_report_date = now

        for days in range(0, (now - start_report_date).days + 1):
            next_date = start_report_date + timedelta(days=days)
            next_date = next_date.strftime(ReportStream.REPORT_DATE_FORMAT)
            yield next_date

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if sync_mode == SyncMode.full_refresh:
            # For full refresh stream use date from config start_date field.
            start_date = self._start_date
        else:
            # incremental stream
            stream_state = stream_state or {}
            start_date = stream_state.get(self.cursor_field)
            if start_date:
                start_date = pendulum.from_format(start_date, ReportStream.REPORT_DATE_FORMAT, tz="UTC")
                # We already processed records for date specified in stream state, move to the day after
                start_date += timedelta(days=1)
            else:
                start_date = self._start_date

        return [{self.cursor_field: date} for date in ReportStream.get_report_date_ranges(start_date)] or [None]

    def get_updated_state(self, current_stream_state: Dict[str, Any], latest_data: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"reportDate": latest_data["reportDate"]}

    @abstractmethod
    def _get_init_report_body(self, report_date: str, record_type: str, profile) -> Dict[str, Any]:
        """
        Override to return dict representing body of POST request for initiating report creation.
        """

    def _init_reports(self, report_date: str) -> List[ReportInfo]:
        """
        Send report generation requests for all profiles and for all record types for specific day.
        :report_date - date for generating metric report.
        :return List of ReportInfo objects each of them has reportId field to check report status.
        """
        report_infos = []
        for profile in self._profiles:
            for record_type, metrics in self.metrics_map.items():
                metric_date = self._calc_report_generation_date(report_date, profile)

                report_init_body = self._get_init_report_body(metric_date, record_type, profile)
                if not report_init_body:
                    continue
                # Some of the record types has subtypes. For example asins type
                # for  product report have keyword and targets subtypes and it
                # repseneted as asins_keywords and asins_targets types. Those
                # subtypes have mutualy excluded parameters so we requesting
                # different metric list for each record.
                record_type = record_type.split("_")[0]
                logger.info(f"Initiating report generation for {profile.profileId} profile with {record_type} type for {metric_date} date")
                response = self._send_http_request(
                    urljoin(self._url, self.report_init_endpoint(record_type)),
                    profile.profileId,
                    report_init_body,
                )
                if response.status_code != HTTPStatus.ACCEPTED:
                    logger.warn(f"Unexpected error when registering {record_type} for {profile.profileId} profile: {response.text}")
                    continue

                response = ReportInitResponse.parse_raw(response.text)
                report_infos.append(
                    ReportInfo(
                        report_id=response.reportId,
                        record_type=record_type,
                        profile_id=profile.profileId,
                    )
                )
                logger.info("Initiated successfully")

        return report_infos

    @staticmethod
    def _calc_report_generation_date(report_date: str, profile) -> str:
        """
        According to reference time zone is specified by the profile used to
        request the report. If specified date is today, then the performance
        report may contain partial information. Based on this we generating
        reports from day before specified report date and we should take into
        account timezone for each profile.
        :param report_date requested date that stored in stream state.
        :return date parameter for Amazon Ads generate report. It equial to day
        before current day for the profile's timezone.
        """
        report_date = datetime.strptime(report_date, ReportStream.REPORT_DATE_FORMAT)
        profile_tz = pytz.timezone(profile.timezone)
        profile_time = report_date.astimezone(profile_tz)
        profile_yesterday = profile_time - timedelta(days=1)
        return profile_yesterday.strftime(ReportStream.REPORT_DATE_FORMAT)

    def _download_report(self, report_info: ReportInfo, url: str) -> List[dict]:
        """
        Download and parse report result
        """
        response = self._send_http_request(url, report_info.profile_id)
        raw_string = decompress(response.content).decode("utf")
        return json.loads(raw_string)
