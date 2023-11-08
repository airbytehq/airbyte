#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from itertools import product
from typing import Any, List, Mapping, Tuple, Optional

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException
from source_bing_ads.client import Client
from source_bing_ads.streams import (  # noqa: F401
    BingAdsReportingServiceStream,
    CustomReport,
    AccountImpressionPerformanceReportDaily,
    AccountImpressionPerformanceReportHourly,
    AccountImpressionPerformanceReportMonthly,
    AccountImpressionPerformanceReportWeekly,
    AccountPerformanceReportDaily,
    AccountPerformanceReportHourly,
    AccountPerformanceReportMonthly,
    AccountPerformanceReportWeekly,
    Accounts,
    AdGroupImpressionPerformanceReportDaily,
    AdGroupImpressionPerformanceReportHourly,
    AdGroupImpressionPerformanceReportMonthly,
    AdGroupImpressionPerformanceReportWeekly,
    AdGroupLabels,
    AdGroupPerformanceReportDaily,
    AdGroupPerformanceReportHourly,
    AdGroupPerformanceReportMonthly,
    AdGroupPerformanceReportWeekly,
    AdGroups,
    AdPerformanceReportDaily,
    AdPerformanceReportHourly,
    AdPerformanceReportMonthly,
    AdPerformanceReportWeekly,
    Ads,
    AgeGenderAudienceReportDaily,
    AgeGenderAudienceReportHourly,
    AgeGenderAudienceReportMonthly,
    AgeGenderAudienceReportWeekly,
    AppInstallAdLabels,
    AppInstallAds,
    BudgetSummaryReport,
    CampaignImpressionPerformanceReportDaily,
    CampaignImpressionPerformanceReportHourly,
    CampaignImpressionPerformanceReportMonthly,
    CampaignImpressionPerformanceReportWeekly,
    CampaignLabels,
    CampaignPerformanceReportDaily,
    CampaignPerformanceReportHourly,
    CampaignPerformanceReportMonthly,
    CampaignPerformanceReportWeekly,
    Campaigns,
    GeographicPerformanceReportDaily,
    GeographicPerformanceReportHourly,
    GeographicPerformanceReportMonthly,
    GeographicPerformanceReportWeekly,
    KeywordLabels,
    KeywordPerformanceReportDaily,
    KeywordPerformanceReportHourly,
    KeywordPerformanceReportMonthly,
    KeywordPerformanceReportWeekly,
    Keywords,
    Labels,
    SearchQueryPerformanceReportDaily,
    SearchQueryPerformanceReportHourly,
    SearchQueryPerformanceReportMonthly,
    SearchQueryPerformanceReportWeekly,
    UserLocationPerformanceReportDaily,
    UserLocationPerformanceReportHourly,
    UserLocationPerformanceReportMonthly,
    UserLocationPerformanceReportWeekly,
)
from suds import TypeNotFound, WebFault


class SourceBingAds(AbstractSource):
    """
    Source implementation of Bing Ads API. Fetches advertising data from accounts
    """

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = Client(**config)
            account_ids = {str(account["Id"]) for account in Accounts(client, config).read_records(SyncMode.full_refresh)}
            self.validate_custom_reposts(config, client)
            if account_ids:
                return True, None
            else:
                raise AirbyteTracedException(
                    message="Config validation error: You don't have accounts assigned to this user. Please verify your developer token.",
                    internal_message="You don't have accounts assigned to this user.",
                    failure_type=FailureType.config_error,
                )
        except Exception as error:
            return False, error

    def validate_custom_reposts(self, config: Mapping[str, Any], client: Client):
        custom_reports = self.get_custom_reports(config, client)
        for custom_report in custom_reports:
            try:
                for account in Accounts(client, config).read_records(SyncMode.full_refresh):
                    list(custom_report.read_records(sync_mode=SyncMode.full_refresh,
                                                    stream_slice={"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}))
            except TypeNotFound:
                raise AirbyteTracedException(
                    message=f"Config validation error: You have provided invalid Reporting Object: {custom_report.report_name}. "
                            f"Please verify it in Bing Ads Docs"
                            f" https://learn.microsoft.com/en-us/advertising/reporting-service/reporting-service-reference?view=bingads-13",
                    internal_message="invalid reporting object was provided.",
                    failure_type=FailureType.config_error,
                )
            except WebFault as e:
                raise AirbyteTracedException(
                    message=f"Config validation error: You have provided invalid Reporting Columns: {custom_report.custom_report_columns}. "
                            f"Make sure that you provided right columns for this report, not all columns can be added/removed."
                            f"Please, verify it",
                    internal_message=f"invalid reporting columns were provided. {e}",
                    failure_type=FailureType.config_error,
                )

    def _validate_reporting_object_name(self, report_object: str) -> str:
        # reporting mixin adds it if user didn't provide it
        if report_object.endswith("Request"):
            return report_object.replace("Request", "")
        return report_object

    def get_custom_reports(self, config: Mapping[str, Any], client: Client) -> List[Optional[Stream]]:
        return [
            type(report["name"], (CustomReport,),
                 {"report_name": self._validate_reporting_object_name(report["reporting_object"]),
                  "custom_report_columns": report["report_columns"],
                  "report_aggregation": report["report_aggregation"]})(client, config)
            for report in config.get("custom_reports", [])
        ]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = Client(**config)
        streams = [
            Accounts(client, config),
            AdGroups(client, config),
            AdGroupLabels(client, config),
            AppInstallAds(client, config),
            AppInstallAdLabels(client, config),
            Ads(client, config),
            Campaigns(client, config),
            BudgetSummaryReport(client, config),
            Labels(client, config),
            KeywordLabels(client, config),
            Keywords(client, config),
            CampaignLabels(client, config),
        ]

        reports = (
            "AgeGenderAudienceReport",
            "AccountImpressionPerformanceReport",
            "AccountPerformanceReport",
            "KeywordPerformanceReport",
            "AdGroupPerformanceReport",
            "AdPerformanceReport",
            "AdGroupImpressionPerformanceReport",
            "CampaignPerformanceReport",
            "CampaignImpressionPerformanceReport",
            "GeographicPerformanceReport",
            "SearchQueryPerformanceReport",
            "UserLocationPerformanceReport",
        )
        report_aggregation = ("Hourly", "Daily", "Weekly", "Monthly")
        streams.extend([eval(f"{report}{aggregation}")(client, config) for (report, aggregation) in product(reports, report_aggregation)])

        custom_reports = self.get_custom_reports(config, client)
        streams.extend(custom_reports)
        return streams
