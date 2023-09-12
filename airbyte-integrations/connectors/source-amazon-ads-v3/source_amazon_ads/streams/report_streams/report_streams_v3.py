#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import time
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
from datetime import datetime, timedelta

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
    ADGROUPS = "campaigns_adGroups"
    PLACEMENT = "campaigns_placement"
    TARGETS = "targeting"
    SEARCHTERM = "search_term"
    ADVERTISEDPRODUCT= "advertised_product"
    PURCHASEDPRODUCT = "purchased_product"



class Status(str, Enum):
    IN_PROGRESS = "PROCESSING"
    SUCCESS = "COMPLETED"
    FAILURE = "FAILURE"


class ReportInitResponse(BaseModel):
    reportId: str
    status: str


class ReportStatus(BaseModel):
    status: str
    url: Optional[str]


@dataclass
class ReportInfo:
    report_id: str
    profile_id: int
    record_type: str
    status: Status
    ts: str
    reportper: str
    version: str
    variant: str
    request_date: str
    customer_id: str
    region: str
    report_sub_type: str
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


class ReportStreamV3(BasicAmazonAdsStream, ABC):
    """
    Common base class for report streams
    """

    primary_key = ["profileId", "recordType", "reportDate", "recordId"]
    # https://advertising.amazon.com/API/docs/en-us/reporting/v2/faq#what-is-the-available-report-history-for-the-version-2-reporting-api
    REPORTING_PERIOD = 95
    # (Service limits section)
    # Format used to specify metric generation date over Amazon Ads API.
    REPORT_DATE_FORMAT = "YYYY-MM-DD"
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
        self._report_sub_type = ''
        self._variant = ''
        self._version = 'v3'
        self._start_date: Optional[Date] = config.get("start_date")
        self._end_date: Optional[Date] = config.get("end_date")
        self._last_month: Optional[bool] = config.get("last_month")
        self._customer_id: Optional[str] = 'NA'
        self._region: Optional[str] = config.get("region")
        self._look_back_window: int = 0
        # Timeout duration in minutes for Reports. Default is 180 minutes.
        self.report_wait_timeout: int = get_typed_env("REPORT_WAIT_TIMEOUT", 180)
        # Maximum retries Airbyte will attempt for fetching report data. Default is 5.
        self.report_generation_maximum_retries: int = get_typed_env("REPORT_GENERATION_MAX_RETRIES", 5)
        self._report_record_types = ''

    @property
    def report_sub_type(self) -> str:
        return self._report_sub_type

    @property
    def variant(self) -> str:
        return self._variant

    @property
    def version(self) -> str:
        return self._version
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
        try:
            if not stream_slice:
                # In case of stream_slices method returned [None] object and
                # stream_slice is None.
                # This may occure if we have abnormal stream state with start_date
                # parameter pointing to the future. In this case we dont need to
                # take any action and just return.
                return
            profile = stream_slice["profile"]
            report_date = stream_slice[self.cursor_field]
            start_date,end_date = stream_slice["start_date"],stream_slice["end_date"]
            report_infos = self._init_and_try_read_records(profile, report_date, start_date, end_date)
            self._update_state(profile, report_date)

            for report_info in report_infos:
                for metric_object in report_info.metric_objects:
                    input_dict = {"startDate":start_date,
                        "endDate":end_date,
                        "profileId":str(report_info.profile_id),
                        "recordType":report_info.record_type,
                        "reportDate":report_date,
                        "ts":report_info.ts,
                        "reportper":report_info.reportper,
                        "ver":report_info.version,
                        "variant":report_info.variant,
                        "request_date":report_info.request_date,
                        "customer_id":report_info.customer_id,
                        "region":report_info.region,
                        "report_sub_type":report_info.report_sub_type,
                        "recordId":metric_object[self.metrics_type_to_id_map[report_info.record_type]],
                        **metric_object
                        }
                    yield self._model(
                        **input_dict
                    ).dict()
                    '''yield self._model(
                        startDate=start_date,
                        endDate=end_date,
                        profileId=str(report_info.profile_id),
                        recordType=report_info.record_type,
                        reportDate=report_date,
                        ts=report_info.ts,
                        reportper=report_info.reportper,
                        ver=report_info.version,
                        variant=report_info.variant,
                        request_date=report_info.request_date,
                        customer_id=report_info.customer_id,
                        region=report_info.region,
                        report_sub_type=report_info.report_sub_type,
                        recordId=metric_object[self.metrics_type_to_id_map[report_info.record_type]],
                        metric=metric_object,
                    ).dict()'''
        except Exception as ex:
            self.logger.exception(f"Encountered an exception while reading stream {ex}")
            raise ex    

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
    def _init_and_try_read_records(self, profile: Profile, report_date, start_date, end_date):
        report_infos = self._init_reports(profile, report_date, start_date, end_date)
        self.logger.info(f"Waiting for {len(report_infos)} report(s) to be generated")
        self._try_read_records(report_infos)
        return report_infos

    @backoff_max_time
    def _try_read_records(self, report_infos):
        incomplete_report_infos = self._incomplete_report_infos(report_infos)
        self.logger.info(f"Checking report status, {len(incomplete_report_infos)} report(s) remaining")
        #self.logger.info(f"abhinandan 1,{incomplete_report_infos} ")
        for report_info in incomplete_report_infos:
            report_status, download_url = self._check_status(report_info)
            #self.logger.info(f"abhinandan 3,{report_status} ")

            report_info.status = report_status

            if report_status == Status.FAILURE:
                message = f"Report for {report_info.profile_id} with {report_info.record_type} type generation failed"
                self.logger.debug(f"{message}")
                raise ReportGenerationFailure(message)
            elif report_status == Status.SUCCESS:
                try:
                    report_info.metric_objects = self._download_report(report_info, download_url)
                except requests.HTTPError as error:
                    self.logger.error(f"{error}")
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
    def report_init_endpoint(self) -> str:
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

    @property
    @abstractmethod
    def metrics_type_to_id_map(self) -> Dict[str, List]:
        """
        :return: Map record type to to its unique identifier in metrics
        """

    def _check_status(self, report_info: ReportInfo) -> Tuple[Status, str]:
        """
        Check report status and return download link if report generated successfuly
        """
        check_endpoint = f"/reporting/reports/{report_info.report_id}"
        resp = self._send_http_request(urljoin(self._url, check_endpoint), report_info.profile_id)
        try:
            resp = ReportStatus.parse_raw(resp.text)

        except ValueError as error:
            self.logger.error(f"{error}")
            raise ReportStatusFailure(error)

        return resp.status, resp.url

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            TooManyRequests,
        ),
        max_tries=10,
    )
    def _send_http_request(self, url: str, profile_id: int, json: dict = None , headers=None):
        if headers is None:
            headers = self._get_auth_headers(profile_id)
        if json:
            
            response = self._session.post(url, headers=headers, json=json)
        else:
            response = self._session.get(url, headers=headers)
        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise TooManyRequests()
        return response

    def get_current_month_dates(self):
        from datetime import datetime, timedelta

        # Get the current date
        current_date = datetime.now()

        # Get the first day of the current month
        start_date = current_date.replace(day=1)
        # Format the dates as yyyy-MM-dd
        first_day_current_month_str = start_date.strftime('%Y-%m-%d')
        last_day_current_month_str = current_date.strftime('%Y-%m-%d')

        return first_day_current_month_str,last_day_current_month_str

    def get_last_month_dates(self):
        from datetime import datetime, timedelta

        # Get the current date
        current_date = datetime.now()

        # Get the first day of the current month
        first_day_current_month = current_date.replace(day=1)

        # Get the last day of the previous month
        last_day_previous_month = first_day_current_month - timedelta(days=1)

        # Get the first day of the previous month
        first_day_previous_month = last_day_previous_month.replace(day=1)

        # Format the dates as yyyy-MM-dd
        first_day_previous_month_str = first_day_previous_month.strftime('%Y-%m-%d')
        last_day_previous_month_str = last_day_previous_month.strftime('%Y-%m-%d')

        # Print the results
        #print("First day of the previous month:", first_day_previous_month_str)
        #print("Last day of the previous month:", last_day_previous_month_str)
        return first_day_previous_month_str,last_day_previous_month_str

    def get_date_range(self, start_date: Date, timezone: str) -> Iterable[str]:
        if not self._end_date or self._end_date < start_date:
            #self._end_date = pendulum.today(tz=timezone).date()
            yield None
        if self._end_date - start_date >31:
            yield None 
        if start_date > self._end_date:
            yield None
        yield start_date.format(self.REPORT_DATE_FORMAT)
        

    def get_start_date(self, profile: Profile, stream_state: Mapping[str, Any]) -> Date:
        if self._last_month:
            dates = self.get_last_month_dates()
            start_date, end_date=dates[0],dates[1]
            return start_date,end_date
        elif not self._start_date or not self._end_date :
            dates = self.get_current_month_dates()
            start_date, end_date=dates[0],dates[1]
            return start_date,end_date 
        else:
            today = pendulum.today(tz=profile.timezone).date()
            if not self._end_date or self._end_date < self._start_date:
                #self._end_date = pendulum.today(tz=timezone).date()
                return None,None
            if self._start_date < today.subtract(days=self.REPORTING_PERIOD):
                return None,None
            if (self._end_date - self._start_date).days >31:
                return None,None
            if self._start_date > self._end_date:
                return None,None
            return self._start_date.format(self.REPORT_DATE_FORMAT),self._end_date.format(self.REPORT_DATE_FORMAT)
        
            '''today = pendulum.today(tz=profile.timezone).date()
            start_date = stream_state.get(str(profile.profileId), {}).get(self.cursor_field)
            if start_date:
                start_date = pendulum.from_format(start_date, self.REPORT_DATE_FORMAT).date()
                # Taking date from state if it's not older than 95 days
                return max(start_date, today.subtract(days=self.REPORTING_PERIOD))
            if self._start_date:
                return max(self._start_date, today.subtract(days=self.REPORTING_PERIOD))
            return today'''

    def stream_profile_slices(self, profile: Profile, stream_state: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        start_date,end_date = self.get_start_date(profile, stream_state)
        yield {"profile": profile, self.cursor_field: start_date,"start_date": start_date,"end_date": end_date}
        '''for report_date in self.get_date_range(start_date, profile.timezone):
            yield {"profile": profile, self.cursor_field: report_date}'''

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        try:
            stream_state = stream_state or {}
            no_data = True

            generators = [self.stream_profile_slices(profile, stream_state) for profile in self._profiles]
            for _slice in iterate_one_by_one(*generators):
                no_data = False
                yield _slice

            if no_data:
                yield None
        except Exception as e:

            self.logger.exception(f"Encountered an exception while reading stream {e}")

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
        start_date,end_date = self.get_start_date(profile, self._state)
        end_date_obj = pendulum.from_format(start_date, self.REPORT_DATE_FORMAT).date()

        updated_state = max(min(report_date, look_back_date), end_date_obj).format(self.REPORT_DATE_FORMAT)

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
    def _init_reports(self, profile: Profile, report_date: str, start_date: str, end_date: str) -> List[ReportInfo]:
        """
        Send report generation requests for all profiles and for all record types for specific day.
        :report_date - date for generating metric report.
        :return List of ReportInfo objects each of them has reportId field to check report status.
        """
        report_infos = []
        ts = int(time.time())
        reportper = "DAY"
        version = self.version
        report_sub_type = self.report_sub_type
        variant = self.variant
        region = self._region
        current_time = time.localtime()
        customer_id = self._customer_id
        request_date = time.strftime("%Y%m%d", current_time)
        for record_type, metrics in self.metrics_map.items():
            if len(self._report_record_types) > 0 and record_type not in self._report_record_types:
                continue

            report_init_body = self._get_init_report_body(start_date, end_date, record_type, profile)
            if not report_init_body:
                continue
            # Some of the record types has subtypes. For example asins type
            # for  product report have keyword and targets subtypes and it
            # represented as asins_keywords and asins_targets types. Those
            # subtypes have mutually excluded parameters so we requesting
            # different metric list for each record.
            request_record_type = record_type.split("_")[0]
            self.logger.info(f"Initiating report generation for {profile.profileId} profile with {record_type} type for {report_date} date")
            response = self._send_http_request(
                urljoin(self._url, self.report_init_endpoint()),
                profile.profileId,
                report_init_body,
            )
            if response.status_code != 200:
                error_msg = f"Unexpected HTTP status code {response.status_code} when registering {record_type}, {type(self).__name__} for {profile.profileId} profile: {response.text}"
                if self._skip_known_errors(response):
                    self.logger.warning(error_msg)
                    break
                self.logger.error(error_msg)
                raise ReportInitFailure(error_msg)

            response = ReportInitResponse.parse_raw(response.text)
            #print("response",response)
            report_infos.append(
                ReportInfo(
                    ts=ts,
                    reportper=reportper,
                    version=version,
                    variant=variant,
                    request_date=request_date,
                    customer_id=customer_id,
                    region=region,
                    report_sub_type=report_sub_type,
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
        #print("url",url)
        response = self._send_http_request(url, report_info.profile_id,None,{})
        response.raise_for_status()
        raw_string = decompress(response.content).decode("utf")
        self.logger.info("Initiated successfully.")
        #self.logger.info(f"abhinandan 4,{json.loads(raw_string)} ")
        return json.loads(raw_string)

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        if isinstance(exception, ReportGenerationInProgress):
            return f"Report(s) generation time took more than {self.report_wait_timeout} minutes and failed because of Amazon API issues. Please wait some time and run synchronization again."
        return super().get_error_display_message(exception)

    def _get_response_error_details(self, response) -> Optional[str]:
        try:
            response_json = response.json()
        except ValueError as ex:
            self.logger.error(ex)
            raise ex
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
