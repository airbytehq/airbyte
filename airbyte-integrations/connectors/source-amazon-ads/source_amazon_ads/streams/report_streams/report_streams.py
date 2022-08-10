#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from gzip import decompress
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urljoin

import backoff
import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from pendulum import Date
from pydantic import BaseModel
from source_amazon_ads.schemas import CatalogModel, MetricsReport, Profile
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
    status: Status
    metric_objects: List[dict]


class RetryableException(Exception):
    pass


class ReportGenerationFailure(RetryableException):
    pass


class ReportGenerationInProgress(RetryableException):
    pass


class ReportStatusFailure(RetryableException):
    pass


class ReportInitFailure(RetryableException):
    pass


class TooManyRequests(Exception):
    """
    Custom exception occured when response with 429 status code received
    """


class ReportStream(BasicAmazonAdsStream, ABC):
    """
    Common base class for report streams
    """

    primary_key = ["profileId", "recordType", "reportDate", "updatedAt"]
    # Amazon ads updates the data for the next 3 days
    LOOK_BACK_WINDOW = 3
    # (Service limits section)
    # Format used to specify metric generation date over Amazon Ads API.
    REPORT_DATE_FORMAT = "YYYYMMDD"
    CONFIG_DATE_FORMAT = "YYYY-MM-DD"
    cursor_field = "reportDate"

    def __init__(self, config: Mapping[str, Any], profiles: List[Profile], authenticator: Oauth2Authenticator):
        self._authenticator = authenticator
        self._session = requests.Session()
        self._model = self._generate_model()
        self.report_wait_timeout = config.get("report_wait_timeout", 30)
        self.report_generation_maximum_retries = config.get("report_generation_max_retries", 5)
        # Set start date from config file
        self._start_date = config.get("start_date")
        if self._start_date:
            self._start_date = pendulum.from_format(self._start_date, self.CONFIG_DATE_FORMAT).date()
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
        profile = stream_slice["profile"]
        report_date = stream_slice[self.cursor_field]
        report_infos = self._init_and_try_read_records(profile, report_date)

        for report_info in report_infos:
            for metric_object in report_info.metric_objects:
                yield self._model(
                    profileId=report_info.profile_id,
                    recordType=report_info.record_type,
                    reportDate=report_date,
                    updatedAt=pendulum.now(tz=profile.timezone).replace(microsecond=0).to_iso8601_string(),
                    metric=metric_object,
                ).dict()

    def backoff_max_time(func):
        def wrapped(self, *args, **kwargs):
            return backoff.on_exception(backoff.constant, RetryableException, max_time=self.report_wait_timeout * 60, interval=10)(func)(
                self, *args, **kwargs
            )

        return wrapped

    def backoff_max_tries(func):
        def wrapped(self, *args, **kwargs):
            return backoff.on_exception(backoff.expo, ReportGenerationFailure, max_tries=self.report_generation_maximum_retries)(func)(
                self, *args, **kwargs
            )

        return wrapped

    @backoff_max_tries
    def _init_and_try_read_records(self, profile: Profile, report_date):
        report_infos = self._init_reports(profile, report_date)
        logger.info(f"Waiting for {len(report_infos)} report(s) to be generated")
        self._try_read_records(report_infos)
        return report_infos

    @backoff_max_time
    def _try_read_records(self, report_infos):
        incomplete_report_infos = self._incomplete_report_infos(report_infos)
        logger.info(f"Checking report status, {len(incomplete_report_infos)} report(s) remaining")
        for report_info in incomplete_report_infos:
            report_status, download_url = self._check_status(report_info)
            report_info.status = report_status

            if report_status == Status.FAILURE:
                message = f"Report for {report_info.profile_id} with {report_info.record_type} type generation failed"
                raise ReportGenerationFailure(message)
            elif report_status == Status.SUCCESS:
                try:
                    report_info.metric_objects = self._download_report(report_info, download_url)
                except requests.HTTPError as error:
                    raise ReportGenerationFailure(error)

        pending_report_status = [(r.profile_id, r.report_id, r.status) for r in self._incomplete_report_infos(report_infos)]
        if len(pending_report_status) > 0:
            message = f"Report generation in progress: {repr(pending_report_status)}"
            raise ReportGenerationInProgress(message)

    def _incomplete_report_infos(self, report_infos):
        return [r for r in report_infos if r.status != Status.SUCCESS]

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

        try:
            resp = ReportStatus.parse_raw(resp.text)
        except ValueError as error:
            raise ReportStatusFailure(error)

        return resp.status, resp.location

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            TooManyRequests,
        ),
        max_tries=10,
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

    def get_date_range(self, start_date: Date, end_date: Date) -> Iterable[str]:
        for days in range((end_date - start_date).days + 1):
            yield start_date.add(days=days).format(ReportStream.REPORT_DATE_FORMAT)

    def get_start_date(self, profile: Profile, stream_state: Mapping[str, Any]) -> Date:
        today = pendulum.today(tz=profile.timezone).date()
        start_date = stream_state.get(str(profile.profileId), {}).get(self.cursor_field)
        if start_date:
            start_date = pendulum.from_format(start_date, self.REPORT_DATE_FORMAT).date()
            return max(start_date, today.subtract(days=60))
        if self._start_date:
            return max(self._start_date, today.subtract(days=60))
        return today

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        stream_state = stream_state or {}

        slices = []
        for profile in self._profiles:
            today = pendulum.today(tz=profile.timezone).date()
            start_date = self.get_start_date(profile, stream_state)
            for report_date in self.get_date_range(start_date, today):
                slices.append({"profile": profile, self.cursor_field: report_date})
        if not slices:
            return [None]
        return slices

    def get_updated_state(self, current_stream_state: Dict[str, Any], latest_data: Mapping[str, Any]) -> Mapping[str, Any]:
        profileId = str(latest_data["profileId"])
        profile = {str(p.profileId): p for p in self._profiles}[profileId]
        record_date = latest_data[self.cursor_field]
        record_date = pendulum.from_format(record_date, self.REPORT_DATE_FORMAT).date()
        look_back_date = pendulum.today(tz=profile.timezone).date().subtract(days=self.LOOK_BACK_WINDOW)
        start_date = self.get_start_date(profile, current_stream_state)
        updated_state = max(min(record_date, look_back_date), start_date).format(self.REPORT_DATE_FORMAT)

        stream_state_value = current_stream_state.get(profileId, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(profileId, {})[self.cursor_field] = updated_state

        return current_stream_state

    @abstractmethod
    def _get_init_report_body(self, report_date: str, record_type: str, profile) -> Dict[str, Any]:
        """
        Override to return dict representing body of POST request for initiating report creation.
        """

    @backoff.on_exception(
        backoff.expo,
        ReportInitFailure,
        max_tries=5,
    )
    def _init_reports(self, profile: Profile, report_date: str) -> List[ReportInfo]:
        """
        Send report generation requests for all profiles and for all record types for specific day.
        :report_date - date for generating metric report.
        :return List of ReportInfo objects each of them has reportId field to check report status.
        """
        report_infos = []
        for record_type, metrics in self.metrics_map.items():
            report_init_body = self._get_init_report_body(report_date, record_type, profile)
            if not report_init_body:
                continue
            # Some of the record types has subtypes. For example asins type
            # for  product report have keyword and targets subtypes and it
            # repseneted as asins_keywords and asins_targets types. Those
            # subtypes have mutualy excluded parameters so we requesting
            # different metric list for each record.
            record_type = record_type.split("_")[0]
            logger.info(f"Initiating report generation for {profile.profileId} profile with {record_type} type for {report_date} date")
            response = self._send_http_request(
                urljoin(self._url, self.report_init_endpoint(record_type)),
                profile.profileId,
                report_init_body,
            )
            if response.status_code != HTTPStatus.ACCEPTED:
                raise ReportInitFailure(
                    f"Unexpected HTTP status code {response.status_code} when registering {record_type}, {type(self).__name__} for {profile.profileId} profile: {response.text}"
                )

            response = ReportInitResponse.parse_raw(response.text)
            report_infos.append(
                ReportInfo(
                    report_id=response.reportId,
                    record_type=record_type,
                    profile_id=profile.profileId,
                    status=Status.IN_PROGRESS,
                    metric_objects=[],
                )
            )
            logger.info("Initiated successfully")

        return report_infos

    @backoff.on_exception(
        backoff.expo,
        requests.HTTPError,
        max_tries=5,
    )
    def _download_report(self, report_info: ReportInfo, url: str) -> List[dict]:
        """
        Download and parse report result
        """
        response = self._send_http_request(url, report_info.profile_id)
        response.raise_for_status()
        raw_string = decompress(response.content).decode("utf")
        return json.loads(raw_string)

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        if isinstance(exception, ReportGenerationInProgress):
            return f'Report(s) generation time took more than {self.report_wait_timeout} minutes, please increase the "report_wait_timeout" parameter in configuration.'
        return super().get_error_display_message(exception)
