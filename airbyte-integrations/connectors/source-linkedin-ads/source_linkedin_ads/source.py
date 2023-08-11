#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from source_linkedin_ads.streams import (
    Accounts,
    AccountUsers,
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
    CampaignGroups,
    Campaigns,
    Creatives,
)

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

        config["authenticator"] = self.get_authenticator(config)
        stream = Accounts(config)
        # need to load the first item only
        stream.records_limit = 1
        try:
            next(stream.read_records(sync_mode=SyncMode.full_refresh), None)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Mapping a input config of the user input configuration as defined in the connector spec.
        Passing config to the streams.
        """
        config["authenticator"] = self.get_authenticator(config)
        return [
            Accounts(config),
            AccountUsers(config),
            AdCampaignAnalytics(config),
            AdCreativeAnalytics(config),
            AdImpressionDeviceAnalytics(config),
            AdMemberCompanySizeAnalytics(config),
            AdMemberCountryAnalytics(config),
            AdMemberJobFunctionAnalytics(config),
            AdMemberJobTitleAnalytics(config),
            AdMemberIndustryAnalytics(config),
            AdMemberSeniorityAnalytics(config),
            AdMemberRegionAnalytics(config),
            AdMemberCompanyAnalytics(config),
            CampaignGroups(config),
            Campaigns(config),
            Creatives(config),
        ]
