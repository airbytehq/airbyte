#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.sources import AbstractSource
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
from source_linkedin_ads.streams import Accounts, AccountUsers, CampaignGroups, Campaigns, Conversions, Creatives

logger = logging.getLogger("airbyte")


class SourceLinkedinAds(AbstractSource):
    """
    Abstract Source inheritance, provides:
    - implementation for `check` connector's connectivity
    - implementation to call each stream with it's input parameters.
    """

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

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Testing connection availability for the connector.
        :: for this check method the Customer must have the "r_liteprofile" scope enabled.
        :: more info: https://docs.microsoft.com/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin
        """
        self._validate_ad_analytics_reports(config)
        config["authenticator"] = self.get_authenticator(config)
        stream = Accounts(config)
        try:
            return stream.check_availability(logger)
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Passing config to the streams.
        """
        self._validate_ad_analytics_reports(config)
        config["authenticator"] = self.get_authenticator(config)
        streams = [
            Accounts(config),
            AccountUsers(config),
            AdCampaignAnalytics(config=config),
            AdCreativeAnalytics(config=config),
            AdImpressionDeviceAnalytics(config=config),
            AdMemberCompanySizeAnalytics(config=config),
            AdMemberCountryAnalytics(config=config),
            AdMemberJobFunctionAnalytics(config=config),
            AdMemberJobTitleAnalytics(config=config),
            AdMemberIndustryAnalytics(config=config),
            AdMemberSeniorityAnalytics(config=config),
            AdMemberRegionAnalytics(config=config),
            AdMemberCompanyAnalytics(config=config),
            CampaignGroups(config=config),
            Campaigns(config=config),
            Creatives(config=config),
            Conversions(config=config),
        ]

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

    def _validate_ad_analytics_reports(self, config: Mapping[str, Any]) -> None:
        report_names = [x["name"] for x in config.get("ad_analytics_reports", [])]
        if len(report_names) != len(set(report_names)):
            report_names = [x["name"] for x in config.get("ad_analytics_reports")]
            message = f"Stream names for Custom Ad Analytics reports should be unique, duplicated streams: {set(name for name in report_names if report_names.count(name) > 1)}"
            raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)
