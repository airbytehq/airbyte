#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    MINIMUM_START_DATE,
    AdGroupAudienceReports,
    AdGroupAudienceReportsByCountry,
    AdGroupAudienceReportsByPlatform,
    AdGroups,
    AdGroupsReports,
    Ads,
    AdsAudienceReports,
    AdsAudienceReportsByCountry,
    AdsAudienceReportsByPlatform,
    AdsAudienceReportsByProvince,
    AdsReports,
    AdvertiserIds,
    Advertisers,
    AdvertisersAudienceReports,
    AdvertisersAudienceReportsByCountry,
    AdvertisersAudienceReportsByPlatform,
    AdvertisersReports,
    Audiences,
    BasicReports,
    Campaigns,
    CampaignsAudienceReports,
    CampaignsAudienceReportsByCountry,
    CampaignsAudienceReportsByPlatform,
    CampaignsReports,
    CreativeAssetsImages,
    CreativeAssetsMusic,
    CreativeAssetsPortfolios,
    CreativeAssetsVideos,
    Daily,
    Hourly,
    Lifetime,
    ReportGranularity,
    SmartPerformanceCampaigns,
    Acos
)

logger = logging.getLogger("airbyte")
DOCUMENTATION_URL = "https://docs.airbyte.com/integrations/sources/tiktok-marketing"
SANDBOX_STREAM_NAMES = [
    "ad_group_audience_reports_by_country_daily",
    "ad_group_audience_reports_by_platform_daily",
    "ad_group_audience_reports_daily",
    "ad_groups",
    "ad_groups_reports_daily",
    "ad_groups_reports_hourly",
    "ad_groups_reports_lifetime",
    "ads",
    "ads_audience_reports_by_country_daily",
    "ads_audience_reports_by_platform_daily",
    "ads_audience_reports_by_province_daily",
    "ads_audience_reports_daily",
    "ads_reports_daily",
    "ads_reports_hourly",
    "ads_reports_lifetime",
    "advertisers",
    "audiences",
    "campaigns",
    "campaigns_audience_reports_by_country_daily",
    "campaigns_audience_reports_by_platform_daily",
    "campaigns_audience_reports_daily",
    "campaigns_reports_daily",
    "campaigns_reports_hourly",
    "campaigns_reports_lifetime",
    "creative_assets_images",
    "creative_assets_music",
    "creative_assets_portfolios",
    "creative_assets_videos",
]
REPORT_GRANULARITY = {"DAY": "daily", "HOUR": "hourly", "LIFETIME": "lifetime"}


class SourceTiktokMarketing(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def _is_sandbox(config: Mapping[str, Any]) -> bool:
        credentials = config.get("credentials")
        if credentials:
            is_sandbox = credentials["auth_type"] == "sandbox_access_token"
        else:
            secret = config.get("environment", {}).get("secret")
            is_sandbox = secret is None

        return is_sandbox

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        granularity = config.get("report_granularity")
        streams = super().streams(config)

        if self._is_sandbox(config):
            streams = [stream for stream in streams if stream.name in SANDBOX_STREAM_NAMES]

        report_granularity = config.get("report_granularity")

        # 1. Basic streams:
        streams = [
            Advertisers(**args),
            Ads(**args),
            AdGroups(**args),
            Audiences(**args),
            Campaigns(**args),
            SmartPerformanceCampaigns(**args),
            Acos(**args),
            CreativeAssetsImages(**args),
            CreativeAssetsMusic(**args),
            CreativeAssetsPortfolios(**args),
            CreativeAssetsVideos(**args),
        ]

        if is_production:
            streams.append(AdvertiserIds(**args))

        # Report streams in different connector version:
        # for < 0.1.13 - expose report streams initialized with 'report_granularity' argument, like:
        #     AdsReports(report_granularity='DAILY')
        #     AdsReports(report_granularity='LIFETIME')
        # for >= 0.1.13 - expose report streams in format: <report_type>_<granularity>, like:
        #     AdsReportsDaily(Daily, AdsReports)
        #     AdsReportsLifetime(Lifetime, AdsReports)

        if report_granularity:
            # for version < 0.1.13 - compatibility with old config with 'report_granularity' option

            # 2. Basic report streams:
            report_args = dict(report_granularity=report_granularity, **args)
            streams.extend(
                [
                    AdsReports(**report_args),
                    AdGroupsReports(**report_args),
                    CampaignsReports(**report_args),
                ]
            )

            # 3. Audience report streams:
            if not report_granularity == ReportGranularity.LIFETIME:
                # https://ads.tiktok.com/marketing_api/docs?id=1707957217727489
                # Audience report only supports lifetime metrics at the ADVERTISER level.
                streams.extend(
                    [
                        AdsAudienceReports(**report_args),
                        AdGroupAudienceReports(**report_args),
                        CampaignsAudienceReportsByCountry(**report_args),
                    ]
                )

            # 4. streams work only in prod env
            if is_production:
                streams.extend(
                    [
                        AdvertisersReports(**report_args),
                        AdvertisersAudienceReports(**report_args),
                    ]
                )

        else:
            # for version >= 0.1.13:

            # 2. Basic report streams:
            reports = [AdsReports, AdGroupsReports, CampaignsReports]
            audience_reports = [
                AdsAudienceReports,
                AdsAudienceReportsByCountry,
                AdsAudienceReportsByPlatform,
                AdsAudienceReportsByProvince,
                AdGroupAudienceReports,
                AdGroupAudienceReportsByCountry,
                AdGroupAudienceReportsByPlatform,
                CampaignsAudienceReports,
                CampaignsAudienceReportsByCountry,
                CampaignsAudienceReportsByPlatform,
            ]
            if is_production:
                # 2.1 streams work only in prod env
                reports.append(AdvertisersReports)
                audience_reports.extend(
                    [
                        AdvertisersAudienceReports,
                        AdvertisersAudienceReportsByCountry,
                        AdvertisersAudienceReportsByPlatform,
                    ]
                )

            for Report in reports:
                for Granularity in [Hourly, Daily, Lifetime]:
                    streams.append(get_report_stream(Report, Granularity)(**args))
                    # add a for loop here for the other dimension to split by

            # 3. Audience report streams:
            for Report in audience_reports:
                # As per TikTok's documentation, audience reports only support daily (not hourly) time dimension for metrics
                streams.append(get_report_stream(Report, Daily)(**args))

                # Audience report supports lifetime metrics only at the ADVERTISER level (see 2.1).
                if Report == AdvertisersAudienceReports:
                    streams.append(get_report_stream(Report, Lifetime)(**args))

        return streams
