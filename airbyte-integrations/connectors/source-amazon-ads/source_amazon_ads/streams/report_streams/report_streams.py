#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import re
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from gzip import decompress
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urljoin

import backoff
import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from pendulum import Date
from pydantic import BaseModel
from source_amazon_ads.schemas import CatalogModel, MetricsReport, Profile
from source_amazon_ads.streams.common import BasicAmazonAdsStream
from source_amazon_ads.utils import get_typed_env, iterate_one_by_one


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
    # https://advertising.amazon.com/API/docs/en-us/reporting/v2/faq#what-is-the-available-report-history-for-the-version-2-reporting-api
    REPORTING_PERIOD = 60
    # (Service limits section)
    # Format used to specify metric generation date over Amazon Ads API.
    REPORT_DATE_FORMAT = "YYYYMMDD"
    cursor_field = "reportDate"

    ERRORS = [
        (400, "KDP authors do not have access to Sponsored Brands functionality"),
        (401, re.compile(r"^Not authorized to access scope \d+$")),
        # Check if the connector received an error like: 'Tactic T00020 is not supported for report API in marketplace A1C3SOZRARQ6R3.'
        # https://docs.developer.amazonservices.com/en_UK/dev_guide/DG_Endpoints.html
        (400, re.compile(r"^Tactic T00020 is not supported for report API in marketplace [A-Z\d]+\.$")),
        # Check if the connector received an error: 'Report date is too far in the past. Reports are only available for 60 days.'
        # In theory, it does not have to get such an error because the connector correctly calculates the start date,
        # but from practice, we can still catch such errors from time to time.
        (406, re.compile(r"^Report date is too far in the past\.")),
    ]

    def __init__(self, config: Mapping[str, Any], profiles: List[Profile], authenticator: Oauth2Authenticator):
        super().__init__(config, profiles)
        self._state = {}
        self._authenticator = authenticator
        self._session = requests.Session()
        self._model = self._generate_model()
        self._start_date: Optional[Date] = config.get("start_date")
        self._look_back_window: int = config["look_back_window"]
        # Timeout duration in minutes for Reports. Default is 180 minutes.
        self.report_wait_timeout: int = get_typed_env("REPORT_WAIT_TIMEOUT", 180)
        # Maximum retries Airbyte will attempt for fetching report data. Default is 5.
        self.report_generation_maximum_retries: int = get_typed_env("REPORT_GENERATION_MAX_RETRIES", 5)

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
        self._update_state(profile, report_date)

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
        self.logger.info(f"Waiting for {len(report_infos)} report(s) to be generated")
        self._try_read_records(report_infos)
        return report_infos

    @backoff_max_time
    def _try_read_records(self, report_infos):
        incomplete_report_infos = self._incomplete_report_infos(report_infos)
        self.logger.info(f"Checking report status, {len(incomplete_report_infos)} report(s) remaining")
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

    def get_date_range(self, start_date: Date, timezone: str) -> Iterable[str]:
        while True:
            if start_date > pendulum.today(tz=timezone).date():
                break
            yield start_date.format(self.REPORT_DATE_FORMAT)
            start_date = start_date.add(days=1)

    def get_start_date(self, profile: Profile, stream_state: Mapping[str, Any]) -> Date:
        today = pendulum.today(tz=profile.timezone).date()
        start_date = stream_state.get(str(profile.profileId), {}).get(self.cursor_field)
        if start_date:
            start_date = pendulum.from_format(start_date, self.REPORT_DATE_FORMAT).date()
            return max(start_date, today.subtract(days=self.REPORTING_PERIOD))
        if self._start_date:
            return max(self._start_date, today.subtract(days=self.REPORTING_PERIOD))
        return today

    def stream_profile_slices(self, profile: Profile, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        start_date = self.get_start_date(profile, stream_state)
        for report_date in self.get_date_range(start_date, profile.timezone):
            yield {"profile": profile, self.cursor_field: report_date}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:

        stream_state = stream_state or {}
        no_data = True

        generators = [self.stream_profile_slices(profile, stream_state) for profile in self._profiles]
        for _slice in iterate_one_by_one(*generators):
            no_data = False
            yield _slice

        if no_data:
            yield None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = deepcopy(value)

    def get_updated_state(self, current_stream_state: Dict[str, Any], latest_data: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._state

    def _update_state(self, profile: Profile, report_date: str):
        report_date = pendulum.from_format(report_date, self.REPORT_DATE_FORMAT).date()
        look_back_date = pendulum.today(tz=profile.timezone).date().subtract(days=self._look_back_window - 1)
        start_date = self.get_start_date(profile, self._state)
        updated_state = max(min(report_date, look_back_date), start_date).format(self.REPORT_DATE_FORMAT)

        stream_state_value = self._state.get(str(profile.profileId), {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        self._state.setdefault(str(profile.profileId), {})[self.cursor_field] = updated_state

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
            self.logger.info(f"Initiating report generation for {profile.profileId} profile with {record_type} type for {report_date} date")
            response = self._send_http_request(
                urljoin(self._url, self.report_init_endpoint(record_type)),
                profile.profileId,
                report_init_body,
            )
            if response.status_code != HTTPStatus.ACCEPTED:
                error_msg = f"Unexpected HTTP status code {response.status_code} when registering {record_type}, {type(self).__name__} for {profile.profileId} profile: {response.text}"
                if self._skip_known_errors(response):
                    self.logger.warning(error_msg)
                    break
                raise ReportInitFailure(error_msg)

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
            self.logger.info("Initiated successfully")

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
            return f"Report(s) generation time took more than {self.report_wait_timeout} minutes and failed because of Amazon API issues. Please wait some time and run synchronization again."
        return super().get_error_display_message(exception)

    def _get_response_error_details(self, response) -> Optional[str]:
        try:
            response_json = response.json()
        except ValueError:
            return
        return response_json.get("details")

    def _skip_known_errors(self, response) -> bool:
        """
        return True if we get known error which we need to skip
        """
        response_details = self._get_response_error_details(response)
        if response_details:
            for status_code, details in self.ERRORS:
                if response.status_code == status_code:
                    if isinstance(details, re.Pattern):
                        if details.match(response_details):
                            return True
                    elif details == response_details:
                        return True
        return False
