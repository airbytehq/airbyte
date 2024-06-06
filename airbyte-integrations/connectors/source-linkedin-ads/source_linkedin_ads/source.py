#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType
from source_linkedin_ads.analytics_streams import (
    AdCampaignAnalytics,
    AdCreativeAnalytics,
    AdImpressionDeviceAnalytics,
    AdMemberCompanyAnalytics,
    AdMemberCompanySizeAnalytics,
    AdMemberCountryAnalytics,
    AdMemberIndustryAnalytics,
    AdMemberJobFunctionAnalytics,
    AdMemberJobTitleAnalytics,
    AdMemberRegionAnalytics,
    AdMemberSeniorityAnalytics,
)

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceLinkedinAds(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Assessing the availability of the connector's connection.

        For this check method, the Customer must have the "r_liteprofile" scope enabled.
        More info: https://docs.microsoft.com/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin

        :param logger: Logger object to log the information.
        :param config: Configuration mapping containing necessary parameters.
        :return: A tuple containing a boolean indicating success or failure and an optional message or object.
        """
        self._validate_ad_analytics_reports(config)
        return super().check_connection(logger, config)

    @staticmethod
    def _validate_ad_analytics_reports(config: Mapping[str, Any]) -> None:
        report_names = [x["name"] for x in config.get("ad_analytics_reports", [])]
        if len(report_names) != len(set(report_names)):
            report_names = [x["name"] for x in config.get("ad_analytics_reports")]
            message = f"Stream names for Custom Ad Analytics reports should be unique, duplicated streams: {set(name for name in report_names if report_names.count(name) > 1)}"
            raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

    @classmethod
    def get_authenticator(cls, config: Mapping[str, Any]) -> Union[TokenAuthenticator, Oauth2Authenticator]:
        """
        Validate input parameters and generate a necessary Authentication object
        This connectors support 2 auth methods:
        1) direct access token with TTL = 2 months
        2) refresh token (TTL = 1 year) which can be converted to access tokens,
           Every new refresh revokes all previous access tokens
        """
        auth_method = config.get("credentials", {}).get("auth_method")
        if not auth_method or auth_method == "access_token":
            # support of backward compatibility with old exists configs
            access_token = config["credentials"]["access_token"] if auth_method else config["access_token"]
            return TokenAuthenticator(token=access_token)
        elif auth_method == "oAuth2.0":
            return Oauth2Authenticator(
                token_refresh_endpoint="https://www.linkedin.com/oauth/v2/accessToken",
                client_id=config["credentials"]["client_id"],
                client_secret=config["credentials"]["client_secret"],
                refresh_token=config["credentials"]["refresh_token"],
            )
        raise Exception("incorrect input parameters")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Passing config to the streams.
        """
        self._validate_ad_analytics_reports(config)
        config["authenticator"] = self.get_authenticator(config)

        streams = super().streams(config=config)
        streams.extend(
            [
                AdImpressionDeviceAnalytics(config=config),
                AdMemberCompanySizeAnalytics(config=config),
                AdMemberCountryAnalytics(config=config),
                AdMemberJobFunctionAnalytics(config=config),
                AdMemberJobTitleAnalytics(config=config),
                AdMemberIndustryAnalytics(config=config),
                AdMemberSeniorityAnalytics(config=config),
                AdMemberRegionAnalytics(config=config),
                AdMemberCompanyAnalytics(config=config),
            ]
        )

        return streams + self.get_custom_ad_analytics_reports(config)

    def get_custom_ad_analytics_reports(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = []

        for ad_report in config.get("ad_analytics_reports", []):
            stream = AdCampaignAnalytics(
                name=f"Custom{ad_report.get('name')}",
                pivot_by=ad_report.get("pivot_by"),
                time_granularity=ad_report.get("time_granularity"),
                config=config,
            )
            streams.append(stream)

        return streams
