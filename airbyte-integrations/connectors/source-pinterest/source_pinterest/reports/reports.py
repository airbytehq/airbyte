#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from abc import abstractmethod
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import urljoin

import airbyte_cdk.sources.utils.casing as casing
import backoff
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from source_pinterest.streams import PinterestAnalyticsStream
from source_pinterest.utils import get_analytics_columns

from .errors import ReportGenerationFailure, ReportGenerationInProgress, ReportStatusError, RetryableException
from .models import ReportInfo, ReportStatus, ReportStatusDetails


class PinterestAnalyticsReportStream(PinterestAnalyticsStream):
    """Class defining the stream of Pinterest Analytics Report
    Details - https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report"""

    http_method = "POST"
    report_wait_timeout = 60 * 10
    report_generation_maximum_retries = 5

    @property
    def window_in_days(self):
        return 185  # Set window_in_days to 186 days date range

    @property
    @abstractmethod
    def level(self):
        """:return: level on which report should be run"""

    @staticmethod
    def _build_api_path(account_id: str) -> str:
        """Build the API path for the given account id."""
        return f"ad_accounts/{account_id}/reports"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        """Get the path (i.e. URL) for the stream."""
        return self._build_api_path(stream_slice["parent"]["id"])

    def _construct_request_body(self, start_date: str, end_date: str, granularity: str, columns: str) -> dict:
        """Construct the body of the API request."""
        return {
            "start_date": start_date,
            "end_date": end_date,
            "granularity": granularity,
            "columns": columns.split(","),
            "level": self.level,
        }

    def request_body_json(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        """Return the body of the API request in JSON format."""
        return self._construct_request_body(stream_slice["start_date"], stream_slice["end_date"], self.granularity, get_analytics_columns())

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """Return the request parameters."""
        return {}

    def backoff_max_time(func):
        def wrapped(self, *args, **kwargs):
            return backoff.on_exception(backoff.constant, RetryableException, max_time=self.report_wait_timeout, interval=10)(func)(
                self, *args, **kwargs
            )

        return wrapped

    def backoff_max_tries(func):
        def wrapped(self, *args, **kwargs):
            return backoff.on_exception(
                backoff.expo, ReportGenerationFailure, max_tries=self.report_generation_maximum_retries, max_time=self.report_wait_timeout
            )(func)(self, *args, **kwargs)

        return wrapped

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """Read the records from the stream."""
        report_infos = self._init_reports(super().read_records(sync_mode, cursor_field, stream_slice, stream_state))
        self._try_read_records(report_infos, stream_slice)

        for report_info in report_infos:
            metrics = report_info.metrics
            for campaign_id, records in metrics.items():
                self.logger.info(f"Reports for campaign id: {campaign_id}:")
                yield from records

    @backoff_max_time
    def _try_read_records(self, report_infos, stream_slice):
        """Try to read the records and raise appropriate exceptions in case of failure or in-progress status."""
        incomplete_report_infos = self._incomplete_report_infos(report_infos)
        for report_info in incomplete_report_infos:
            report_status, report_url = self._verify_report_status(report_info, stream_slice)
            report_info.report_status = report_status
            if report_status in {ReportStatus.DOES_NOT_EXIST, ReportStatus.EXPIRED, ReportStatus.FAILED, ReportStatus.CANCELLED}:
                message = "Report generation failed."
                raise ReportGenerationFailure(message)
            elif report_status == ReportStatus.FINISHED:
                try:
                    report_info.metrics = self._fetch_report_data(report_url)
                except requests.HTTPError as error:
                    raise ReportGenerationFailure(error)

        pending_report_status = [report_info for report_info in report_infos if report_info.report_status != ReportStatus.FINISHED]

        if len(pending_report_status) > 0:
            message = "Report generation in progress."
            raise ReportGenerationInProgress(message)

    def _incomplete_report_infos(self, report_infos):
        """Return the report infos which are not yet finished."""
        return [r for r in report_infos if r.report_status != ReportStatus.FINISHED]

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """Parse the API response."""
        yield response.json()

    @backoff_max_tries
    def _init_reports(self, init_reports) -> List[ReportInfo]:
        """Initialize the reports and return them as a list."""
        report_infos = []
        for init_report in init_reports:
            status = ReportInfo.parse_raw(json.dumps(init_report))
            report_infos.append(
                ReportInfo(
                    token=status.token,
                    report_status=ReportStatus.IN_PROGRESS,
                    metrics=[],
                )
            )
        self.logger.info("Initiated successfully.")
        return report_infos

    def _http_get(self, url, params=None, headers=None):
        """Make a GET request to the given URL and return the response as a JSON."""
        response = self._session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _verify_report_status(self, report: dict, stream_slice: Mapping[str, Any]) -> tuple:
        """Verify the report status and return it along with the report URL."""
        api_path = self._build_api_path(stream_slice["parent"]["id"])
        response_data = self._http_get(
            urljoin(self.url_base, api_path), params={"token": report.token}, headers=self.authenticator.get_auth_header()
        )
        try:
            report_status = ReportStatusDetails.parse_raw(json.dumps(response_data))
        except ValueError as error:
            raise ReportStatusError(error)
        return report_status.report_status, report_status.url

    def _fetch_report_data(self, url: str) -> dict:
        """Fetch the report data from the given URL."""
        return self._http_get(url)

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.

        Schema is the same for all *Report and *TargetingReport streams
        """

        return ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("reports")


class PinterestAnalyticsTargetingReportStream(PinterestAnalyticsReportStream):
    def request_body_json(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        """Return the body of the API request in JSON format."""
        columns = get_analytics_columns().split(",")
        # remove keys which are lot suitable for targeting report
        for odd_value in ["TOTAL_IMPRESSION_FREQUENCY", "TOTAL_IMPRESSION_USER"]:
            if odd_value in columns:
                columns.remove(odd_value)
        columns = ",".join(columns)
        return self._construct_request_body(stream_slice["start_date"], stream_slice["end_date"], self.granularity, columns)


class CampaignAnalyticsReport(PinterestAnalyticsReportStream):
    @property
    def level(self):
        return "CAMPAIGN"


class CampaignTargetingReport(PinterestAnalyticsTargetingReportStream):
    @property
    def level(self):
        return "CAMPAIGN_TARGETING"


class AdvertiserReport(PinterestAnalyticsReportStream):
    @property
    def level(self):
        return "ADVERTISER"


class AdvertiserTargetingReport(PinterestAnalyticsTargetingReportStream):
    @property
    def level(self):
        return "ADVERTISER_TARGETING"


class AdGroupReport(PinterestAnalyticsReportStream):
    @property
    def level(self):
        return "AD_GROUP"


class AdGroupTargetingReport(PinterestAnalyticsTargetingReportStream):
    @property
    def level(self):
        return "AD_GROUP_TARGETING"


class PinPromotionReport(PinterestAnalyticsReportStream):
    @property
    def level(self):
        return "PIN_PROMOTION"


class PinPromotionTargetingReport(PinterestAnalyticsTargetingReportStream):
    @property
    def level(self):
        return "PIN_PROMOTION_TARGETING"


class ProductGroupReport(PinterestAnalyticsReportStream):
    @property
    def level(self):
        return "PRODUCT_GROUP"


class ProductGroupTargetingReport(PinterestAnalyticsTargetingReportStream):
    @property
    def level(self):
        return "PRODUCT_GROUP_TARGETING"


class ProductItemReport(PinterestAnalyticsReportStream):
    @property
    def level(self):
        return "PRODUCT_ITEM"


class KeywordReport(PinterestAnalyticsTargetingReportStream):
    @property
    def level(self):
        return "KEYWORD"


class CustomReport(PinterestAnalyticsTargetingReportStream):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._custom_class_name = f"Custom_{self.config['name']}"
        self._level = self.config["level"]
        self.granularity = self.config["granularity"]
        self.click_window_days = self.config["click_window_days"]
        self.engagement_window_days = self.config["engagement_window_days"]
        self.view_window_days = self.config["view_window_days"]
        self.conversion_report_time = self.config["conversion_report_time"]
        self.attribution_types = self.config["attribution_types"]
        self.columns = self.config["columns"]

    @property
    def level(self):
        return self._level

    @property
    def name(self) -> str:
        """We override stream name to let the user change it via configuration."""
        name = self._custom_class_name or self.__class__.__name__
        return casing.camel_to_snake(name)

    def request_body_json(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Optional[Mapping]:
        """Return the body of the API request in JSON format."""
        return {
            "start_date": stream_slice["start_date"],
            "end_date": stream_slice["end_date"],
            "level": self.level,
            "granularity": self.granularity,
            "click_window_days": self.click_window_days,
            "engagement_window_days": self.engagement_window_days,
            "view_window_days": self.view_window_days,
            "conversion_report_time": self.conversion_report_time,
            "attribution_types": self.attribution_types,
            "columns": self.columns,
        }

    @property
    def window_in_days(self):
        """Docs: https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report"""
        if self.granularity == "HOUR":
            return 2
        elif self.level == "PRODUCT_ITEM":
            return 31
        else:
            return 185
