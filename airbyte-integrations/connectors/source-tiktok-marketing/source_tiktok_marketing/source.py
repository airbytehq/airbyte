#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .spec import SourceTiktokMarketingSpec
from .streams import (
    DEFAULT_START_DATE,
    AdGroups,
    AdGroupsReports,
    Ads,
    AdsReports,
    Advertisers,
    AdvertisersReports,
    Campaigns,
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
        )

    @staticmethod
    def _prepare_stream_args(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Converts an input configure to stream arguments"""
        return {
            "authenticator": TiktokTokenAuthenticator(config["access_token"]),
            "start_date": config.get("start_date") or DEFAULT_START_DATE,
            "advertiser_id": int(config["environment"].get("advertiser_id", 0)),
            "app_id": int(config["environment"].get("app_id", 0)),
            "secret": config["environment"].get("secret"),
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
        report_granularity = config.get("report_granularity") or ReportGranularity.default()
        report_args = dict(report_granularity=report_granularity, **args)
        advertisers_reports = AdvertisersReports(**report_args)
        streams = [
            Ads(**args),
            AdsReports(**report_args),
            Advertisers(**args),
            advertisers_reports if not advertisers_reports.is_sandbox else None,
            AdGroups(**args),
            AdGroupsReports(**report_args),
            Campaigns(**args),
            CampaignsReports(**report_args),
        ]
        return [stream for stream in streams if stream]
