#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from itertools import product
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException
from source_bing_ads.client import Client
from source_bing_ads.streams import (  # noqa: F401
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
    BingAdsReportingServiceStream,
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
    CustomReport,
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
            is_valid, reason = custom_report.validate_report_configuration()
            if not is_valid:
                raise AirbyteTracedException(
                    message=f"Config validation error: {custom_report.name}: {reason}",
                    internal_message=f"{custom_report.name}: {reason}",
                    failure_type=FailureType.config_error,
                )

    def _clear_reporting_object_name(self, report_object: str) -> str:
        # reporting mixin adds it
        if report_object.endswith("Request"):
            return report_object.replace("Request", "")
        return report_object

    def get_custom_reports(self, config: Mapping[str, Any], client: Client) -> List[Optional[Stream]]:
        return [
            type(
                report["name"],
                (CustomReport,),
                {
                    "report_name": self._clear_reporting_object_name(report["reporting_object"]),
                    "custom_report_columns": report["report_columns"],
                    "report_aggregation": report["report_aggregation"],
                },
            )(client, config)
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
