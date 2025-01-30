#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Optional, Tuple

import pendulum

from airbyte_cdk import TState
from airbyte_cdk.models import AdvancedAuth, AuthFlowType, ConfiguredAirbyteCatalog, ConnectorSpecification, OAuthConfigSpecification
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from .spec import SourceAmazonAdsSpec
from .streams import Profiles, SponsoredDisplayReportStream, SponsoredProductsReportStream


# Oauth 2.0 authentication URL for amazon
TOKEN_URL = "https://api.amazon.com/auth/o2/token"


class SourceAmazonAds(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def _validate_and_transform(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if not config.get("region"):
            source_spec = self.spec(logging.getLogger("airbyte"))
            config["region"] = source_spec.connectionSpecification["properties"]["region"]["default"]
        if not config.get("look_back_window"):
            source_spec = self.spec(logging.getLogger("airbyte"))
            config["look_back_window"] = source_spec.connectionSpecification["properties"]["look_back_window"]["default"]
        config["report_record_types"] = config.get("report_record_types", [])
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully,
        (False, error) otherwise.
        """
        try:
            config = self._validate_and_transform(config)
        except Exception as e:
            return False, str(e)
        # Check connection by sending list of profiles request. Its most simple
        # request, not require additional parameters and usually has few data
        # in response body.
        # It doesn't support pagination so there is no sense of reading single
        # record, it would fetch all the data anyway.
        profiles_list = Profiles(config, authenticator=self._make_authenticator(config)).get_all_profiles()
        filtered_profiles = self._choose_profiles(config, profiles_list)
        if not filtered_profiles:
            return False, (
                "No profiles with seller or vendor type found after filtering by Profile ID and Marketplace ID."
                " If you have only agency profile, please use accounts associated with the profile of seller/vendor type."
            )
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: list of streams for current source
        """
        config = self._validate_and_transform(config)
        auth = self._make_authenticator(config)
        stream_args = {"config": config, "authenticator": auth}
        # All data for individual Amazon Ads stream divided into sets of data for
        # each profile. Every API request except profiles has required
        # parameter passed over "Amazon-Advertising-API-Scope" http header and
        # should contain profile id. So every stream is dependent on Profiles
        # stream and should have information about all profiles.
        profiles_stream = Profiles(**stream_args)
        profiles_list = profiles_stream.get_all_profiles()
        stream_args["profiles"] = self._choose_profiles(config, profiles_list)
        non_profile_stream_classes = [
            SponsoredDisplayReportStream,
            SponsoredProductsReportStream,
        ]
        return super().streams(config=config) + [
            *[stream_class(**stream_args) for stream_class in non_profile_stream_classes],
        ]

    @staticmethod
    def _make_authenticator(config: Mapping[str, Any]):
        return Oauth2Authenticator(
            token_refresh_endpoint=TOKEN_URL,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    @staticmethod
    def _choose_profiles(config: Mapping[str, Any], available_profiles: List[dict[str, Any]]):
        requested_profiles = config.get("profiles", [])
        requested_marketplace_ids = config.get("marketplace_ids", [])
        if requested_profiles or requested_marketplace_ids:
            return [
                profile
                for profile in available_profiles
                if profile["profileId"] in requested_profiles or profile["accountInfo"]["marketplaceStringId"] in requested_marketplace_ids
            ]
        return available_profiles

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/amazon-ads",
            connectionSpecification=SourceAmazonAdsSpec.schema(),
            supportsDBT=False,
            advanced_auth=AdvancedAuth(
                auth_flow_type=AuthFlowType.oauth2_0,
                predicate_key=["auth_type"],
                predicate_value="oauth2.0",
                oauth_config_specification=OAuthConfigSpecification(
                    oauth_user_input_from_connector_config_specification={
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {"region": {"type": "string", "path_in_connector_config": ["region"]}},
                    },
                    complete_oauth_output_specification={
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {"refresh_token": {"type": "string", "path_in_connector_config": ["refresh_token"]}},
                    },
                    complete_oauth_server_input_specification={
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
                    },
                    complete_oauth_server_output_specification={
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {
                            "client_id": {"type": "string", "path_in_connector_config": ["client_id"]},
                            "client_secret": {"type": "string", "path_in_connector_config": ["client_secret"]},
                        },
                    },
                ),
            ),
        )
