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
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from gzip import decompress
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, Optional
from urllib.parse import urljoin

import backoff
import pendulum
import pytz
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from airbyte_cdk.sources.async_source import AsyncJob

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


class TooManyRequests(Exception):
    """
    Custom exception occurred when response with 429 status code received
    """


class ReportAsyncJob(AsyncJob):
    # Async report generation time is 15 minutes according to docs:
    # https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes
    # (Service limits section)
    job_wait_timeout = pendulum.duration(minutes=20)
    job_sleep_interval = pendulum.duration(seconds=30)

    def __init__(self, profile: BasicAmazonAdsStream, record_type: RecordType, report_date: str):
        self._profile = profile
        self._record_type = record_type
        self._report_date = report_date
        self._report_id = None
        self._status = None
        self._result = None

    @abstractmethod
    def start_job(self) -> None:
        """Send report generation requests for all profiles and for all record types for specific day."""
        metric_date = self._calc_report_generation_date(self._report_date, self._profile)
        # Some of the record types has subtypes. For example asins type
        # for  product report have keyword and targets subtypes and it
        # represented as asins_keywords and asins_targets types. Those
        # subtypes have mutually excluded parameters so we requesting
        # different metric list for each record.
        record_type = self._record_type.split("_")[0]
        logger.info(
            f"Initiating report generation for {self._profile.profileId} profile with {record_type} type for {metric_date} date")
        response = self._send_http_request(
            urljoin(self._url, self.report_init_endpoint(record_type)),
            self._profile.profileId,
            self._get_init_report_body(),
        )
        if response.status_code != HTTPStatus.ACCEPTED:
            raise Exception(
                f"Unexpected error when registering {record_type}, {self.__class__.__name__} for {self._profile.profileId} profile: {response.text}"
            )

        response = ReportInitResponse.parse_raw(response.text)
        self._report_id = response.reportId
        logger.info("Initiated successfully")

    @abstractmethod
    def completed_successfully(self) -> bool:
        """Something that will tell if job was successful"""
        check_endpoint = f"/v2/reports/{self._report_id}"
        resp = self._send_http_request(urljoin(self._url, check_endpoint), self._profile.profileId)
        self._status = ReportStatus.parse_raw(resp.text)

        if self._status.status == Status.FAILURE:
            raise Exception(f"Report for {self._profile.profileId} with {self._record_type} type generation failed")
        elif self._status.status == Status.SUCCESS:
            return True

        return False

    def fetch_result(self):
        if not self._result:
            super().fetch_result()
            self._result = self._download_report()
        return self._result

    @abstractmethod
    def _get_init_report_body(self) -> Dict[str, Any]:
        """
        Override to return dict representing body of POST request for initiating report creation.
        """

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

    def _download_report(self) -> List[dict]:
        """
        Download and parse report result
        """
        response = self._send_http_request(self._status.location, self._report_info.profile_id)
        raw_string = decompress(response.content).decode("utf")
        return json.loads(raw_string)

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


class ReportStream(BasicAmazonAdsStream, ABC):
    """
    Common base class for report streams
    """

    primary_key = None
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
        stream_slice: ReportAsyncJob = None,
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
            # This may occurs if we have abnormal stream state with start_date
            # parameter pointing to the future. In this case we dont need to
            # take any action and just return.
            return

        for metric_object in stream_slice.get_result():
            yield self._model(
                profileId=stream_slice._profile_id,
                recordType=stream_slice._record_type,
                reportDate=stream_slice._report_date,
                metric=metric_object,
            ).dict()

    def _get_auth_headers(self, profile_id: int):
        return {
            "Amazon-Advertising-API-ClientId": self._client_id,
            "Amazon-Advertising-API-Scope": str(profile_id),
            **self._authenticator.get_auth_header(),
        }

    @property
    @abstractmethod
    def metrics_map(self) -> Dict[str, List]:
        """
        :return: Map record type to list of available metrics
        """

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
                start_date = pendulum.from_format(start_date, self.REPORT_DATE_FORMAT, tz="UTC")
                # We already processed records for date specified in stream state, move to the day after
                start_date += timedelta(days=1)
            else:
                start_date = self._start_date

        for profile in self._profiles:
            for date in self.get_report_date_ranges(start_date):
                yield ReportAsyncJob(profile=profile, record_type=None, report_date=date)

    def get_updated_state(self, current_stream_state: Dict[str, Any], latest_data: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"reportDate": latest_data["reportDate"]}
