#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    AdGroupAudienceReports,
    AdGroups,
    AdGroupsReports,
    Ads,
    AdsAudienceReports,
    AdsReports,
    AdvertiserIds,
    Advertisers,
    AdvertisersAudienceReports,
    AdvertisersReports,
    BasicReports,
    Campaigns,
    CampaignsAudienceReportsByCountry,
    CampaignsReports,
    Daily,
    Hourly,
    Lifetime,
    ReportGranularity,
)

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
            access_token = credentials["access_token"]
            secret = credentials.get("secret")
            app_id = int(credentials.get("app_id", 0))
            advertiser_id = int(credentials.get("advertiser_id", 0))
        else:
            access_token = config["access_token"]
            secret = config.get("environment", {}).get("secret")
            app_id = int(config.get("environment", {}).get("app_id", 0))
            advertiser_id = int(config.get("environment", {}).get("advertiser_id", 0))

        return {
            "authenticator": TiktokTokenAuthenticator(access_token),
            "start_date": config.get("start_date") or DEFAULT_START_DATE,
            "end_date": config.get("end_date") or DEFAULT_END_DATE,
            "advertiser_id": advertiser_id,
            "app_id": app_id,
            "secret": secret,
            "access_token": access_token,
        }

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """
        try:
            next(Advertisers(**self._prepare_stream_args(config)).read_records(SyncMode.full_refresh))
        except Exception as err:
            return False, err
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        args = self._prepare_stream_args(config)

        is_production = not (args["advertiser_id"])

        report_granularity = config.get("report_granularity")

        # 1. Basic streams:
        streams = [
            Advertisers(**args),
            Ads(**args),
            AdGroups(**args),
            Campaigns(**args),
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
            audience_reports = [AdsAudienceReports, AdGroupAudienceReports, CampaignsAudienceReportsByCountry]
            if is_production:
                # 2.1 streams work only in prod env
                reports.append(AdvertisersReports)
                audience_reports.append(AdvertisersAudienceReports)

            for Report in reports:
                for Granularity in [Hourly, Daily, Lifetime]:
                    streams.append(get_report_stream(Report, Granularity)(**args))

            # 3. Audience report streams:
            for Report in audience_reports:
                # As per TikTok's documentation, audience reports only support daily (not hourly) time dimension for metrics
                streams.append(get_report_stream(Report, Daily)(**args))

                # Audience report supports lifetime metrics only at the ADVERTISER level (see 2.1).
                if Report == AdvertisersAudienceReports:
                    streams.append(get_report_stream(Report, Lifetime)(**args))

        return streams
