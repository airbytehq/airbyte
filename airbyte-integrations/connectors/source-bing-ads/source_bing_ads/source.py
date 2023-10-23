#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_bing_ads.client import Client
from source_bing_ads.streams import Accounts, AdGroups, Ads, BudgetSummaryReport, Campaigns


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

    def get_report_streams(self, aggregation_type: str) -> List[Stream]:
        return [
            globals()[f"AccountPerformanceReport{aggregation_type}"],
            globals()[f"KeywordPerformanceReport{aggregation_type}"],
            globals()[f"AdGroupPerformanceReport{aggregation_type}"],
            globals()[f"AdPerformanceReport{aggregation_type}"],
            globals()[f"CampaignPerformanceReport{aggregation_type}"],
            globals()[f"GeographicPerformanceReport{aggregation_type}"],
        ]

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = Client(**config)
        streams = [
            Accounts(client, config),
            AdGroups(client, config),
            Ads(client, config),
            Campaigns(client, config),
        ]

        streams.append(BudgetSummaryReport(client, config))

        streams.extend([c(client, config) for c in self.get_report_streams("Hourly")])
        streams.extend([c(client, config) for c in self.get_report_streams("Daily")])
        streams.extend([c(client, config) for c in self.get_report_streams("Weekly")])
        streams.extend([c(client, config) for c in self.get_report_streams("Monthly")])

        return streams
