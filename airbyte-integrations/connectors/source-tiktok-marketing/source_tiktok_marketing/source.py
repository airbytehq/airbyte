#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AdvancedAuth, AuthFlowType, ConnectorSpecification, OAuthConfigSpecification, SyncMode
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .spec import (
    CompleteOauthOutputSpecification,
    CompleteOauthServerInputSpecification,
    CompleteOauthServerOutputSpecification,
    SourceTiktokMarketingSpec,
)
from .streams import (
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
    Campaigns,
    CampaignsAudienceReportsByCountry,
    CampaignsReports,
    ReportGranularity,
)

DOCUMENTATION_URL = "https://docs.airbyte.io/integrations/sources/tiktok-marketing"


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
    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """Returns the spec for this integration."""
        return ConnectorSpecification(
            documentationUrl=DOCUMENTATION_URL,
            changelogUrl=DOCUMENTATION_URL,
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=SourceTiktokMarketingSpec.schema(),
            additionalProperties=True,
            advanced_auth=AdvancedAuth(
                auth_flow_type=AuthFlowType.oauth2_0,
                predicate_key=["credentials", "auth_type"],
                predicate_value="oauth2.0",
                oauth_config_specification=OAuthConfigSpecification(
                    complete_oauth_output_specification=CompleteOauthOutputSpecification.schema(),
                    complete_oauth_server_input_specification=CompleteOauthServerInputSpecification.schema(),
                    complete_oauth_server_output_specification=CompleteOauthServerOutputSpecification.schema(),
                ),
            ),
        )

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

        # 1. Basic streams:
        streams = [
            Advertisers(**args),
            AdvertiserIds(**args),
            Ads(**args),
            AdGroups(**args),
            Campaigns(**args),
        ]

        # 2. Basic report streams:
        report_granularity = config.get("report_granularity") or ReportGranularity.default()
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
        if not args["advertiser_id"]:
            streams.extend(
                [
                    AdvertisersReports(**report_args),
                    AdvertisersAudienceReports(**report_args),
                ]
            )

        return streams
