#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Tuple

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
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
)

logger = logging.getLogger("airbyte")
DOCUMENTATION_URL = "https://docs.airbyte.com/integrations/sources/tiktok-marketing"


def get_report_stream(report: BasicReports, granularity: ReportGranularity) -> BasicReports:
    """Fabric method to generate final class with name like: AdsReports + Hourly"""
    report_class_name = f"{report.__name__}{granularity.__name__}"
    return type(report_class_name, (granularity, report), {})


class TiktokTokenAuthenticator(TokenAuthenticator):
    """
    Docs: https://business-api.tiktok.com/marketing_api/docs?rid=sta6fe2yww&id=1701890922708994
    """

    def __init__(self, token: str, **kwargs):
        super().__init__(token, **kwargs)
        self.token = token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Access-Token": self.token}


class SourceTiktokMarketing(AbstractSource):
    @staticmethod
    def _prepare_stream_args(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Converts an input configure to stream arguments"""

        credentials = config.get("credentials")

        if credentials:
            # used for new config format
            is_sandbox = credentials["auth_type"] == "sandbox_access_token"
            access_token = credentials["access_token"]
            secret = credentials.get("secret")
            app_id = int(credentials.get("app_id", 0))
            advertiser_id = credentials.get("advertiser_id")
        else:
            # old config only has advertiser id in environment object
            # if there is a secret it is a prod config
            access_token = config["access_token"]
            secret = config.get("environment", {}).get("secret")
            is_sandbox = secret is None
            app_id = int(config.get("environment", {}).get("app_id", 0))
            advertiser_id = config.get("environment", {}).get("advertiser_id")

        start_date = config.get("start_date") or DEFAULT_START_DATE
        if pendulum.parse(start_date) < pendulum.parse(MINIMUM_START_DATE):
            logger.warning(f"The start date is too far in the past. Setting it to {MINIMUM_START_DATE}.")
            start_date = MINIMUM_START_DATE
        stream_args = {
            "authenticator": TiktokTokenAuthenticator(access_token),
            "start_date": start_date,
            "end_date": config.get("end_date") or DEFAULT_END_DATE,
            "app_id": app_id,
            "secret": secret,
            "access_token": access_token,
            "is_sandbox": is_sandbox,
            "attribution_window": config.get("attribution_window"),
            "include_deleted": config.get("include_deleted"),
        }

        if advertiser_id:
            stream_args.update(**{"advertiser_id": advertiser_id})

        return stream_args

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """
        try:
            advertisers = Advertisers(**self._prepare_stream_args(config))
            for slice_ in advertisers.stream_slices():
                next(advertisers.read_records(SyncMode.full_refresh, stream_slice=slice_))
        except Exception as err:
            return False, err
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self._prepare_stream_args(config)

        is_production = not (args["is_sandbox"])

        report_granularity = config.get("report_granularity")

        # 1. Basic streams:
        streams = [
            Advertisers(**args),
            Ads(**args),
            AdGroups(**args),
            Audiences(**args),
            Campaigns(**args),
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
