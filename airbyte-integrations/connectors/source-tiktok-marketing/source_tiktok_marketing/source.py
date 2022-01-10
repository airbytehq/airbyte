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
        complete_oauth_output_specification = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"access_token": {"type": "string", "path_in_connector_config": ["credentials", "access_token"]}},
        }
        complete_oauth_server_input_specification = {
            "type": "object",
            "additionalProperties": True,
            "properties": {"app_id": {"type": "string"}, "secret": {"type": "string"}},
        }
        complete_oauth_server_output_specification = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "app_id": {"type": "string", "path_in_connector_config": ["credentials", "app_id"]},
                "secret": {"type": "string", "path_in_connector_config": ["credentials", "secret"]},
            },
        }
        oauth_user_input_from_connector_config_specification = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"rid": {"type": "string", "path_in_connector_config": ["credentials", "rid"]}},
        }

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
                    complete_oauth_output_specification=complete_oauth_output_specification,
                    complete_oauth_server_input_specification=complete_oauth_server_input_specification,
                    complete_oauth_server_output_specification=complete_oauth_server_output_specification,
                    oauth_user_input_from_connector_config_specification=oauth_user_input_from_connector_config_specification,
                ),
            ),
        )

    @staticmethod
    def _prepare_stream_args(config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Converts an input configure to stream arguments"""
        credentials = config.get("credentials")
        if credentials:
            auth_type = credentials["auth_type"]
            if auth_type == "oauth2.0":
                access_token = credentials["access_token"]
                app_id = int(credentials["app_id"])
                secret = credentials["secret"]
                advertiser_id = 0
            elif auth_type == "access_token":
                access_token = credentials["access_token"]
                app_id = int(credentials["environment"].get("app_id", 0))
                secret = credentials["environment"].get("secret")
                advertiser_id = int(credentials["environment"].get("advertiser_id", 0))
            else:
                raise Exception(f"Invalid auth type in config: {auth_type}")
        else:
            access_token = config.get("access_token")
            if not access_token:
                raise Exception("No access_token in config")
            app_id = int(config["environment"].get("app_id", 0))
            secret = config["environment"].get("secret")
            advertiser_id = int(config["environment"].get("advertiser_id", 0))

        return {
            "authenticator": TiktokTokenAuthenticator(access_token),
            "start_date": config.get("start_date") or DEFAULT_START_DATE,
            "advertiser_id": advertiser_id,
            "app_id": app_id,
            "secret": secret,
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
