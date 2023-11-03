#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from itertools import product
from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
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
    BudgetSummaryReport,
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


class SourceBingAds(AbstractSource):
    """
    Source implementation of Bing Ads API. Fetches advertising data from accounts
    """

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = Client(**config)
            account_ids = {str(account["Id"]) for account in Accounts(client, config).read_records(SyncMode.full_refresh)}
            if account_ids:
                return True, None
            else:
                raise Exception("You don't have accounts assigned to this user.")
        except Exception as error:
            return False, error

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
            "GeographicPerformanceReport",
            "SearchQueryPerformanceReport",
            "UserLocationPerformanceReport",
        )
        report_aggregation = ("Hourly", "Daily", "Weekly", "Monthly")
        streams.extend([eval(f"{report}{aggregation}")(client, config) for (report, aggregation) in product(reports, report_aggregation)])
        return streams
