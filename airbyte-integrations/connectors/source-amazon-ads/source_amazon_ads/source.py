#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from .constants import AmazonAdsRegion
from .schemas import Profile
from .streams import (
    Profiles,
    SponsoredBrandsAdGroups,
    SponsoredBrandsCampaigns,
    SponsoredBrandsKeywords,
    SponsoredBrandsReportStream,
    SponsoredBrandsVideoReportStream,
    SponsoredDisplayAdGroups,
    SponsoredDisplayCampaigns,
    SponsoredDisplayProductAds,
    SponsoredDisplayReportStream,
    SponsoredDisplayTargetings,
    SponsoredProductAdGroups,
    SponsoredProductAds,
    SponsoredProductCampaigns,
    SponsoredProductKeywords,
    SponsoredProductNegativeKeywords,
    SponsoredProductsReportStream,
    SponsoredProductTargetings,
)

# Oauth 2.0 authentication URL for amazon
TOKEN_URL = "https://api.amazon.com/auth/o2/token"


class SourceAmazonAds(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        # Check connection by sending list of profiles request. Its most simple
        # request, not require additional parameters and usually has few data
        # in response body.
        # It doesnt support pagination so there is no sense of reading single
        # record, it would fetch all the data anyway.
        self._set_defaults(config)
        Profiles(config, authenticator=self._make_authenticator(config)).get_all_profiles()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return list of streams for current source
        """
        self._set_defaults(config)
        auth = self._make_authenticator(config)
        stream_args = {"config": config, "authenticator": auth}
        # All data for individual Amazon Ads stream divided into sets of data for
        # each profile. Every API request except profiles has required
        # paramater passed over "Amazon-Advertising-API-Scope" http header and
        # should contain profile id. So every stream is dependant on Profiles
        # stream and should have information about all profiles.
        profiles_stream = Profiles(**stream_args)
        profiles_list = profiles_stream.get_all_profiles()
        stream_args["profiles"] = self._choose_profiles(config, profiles_list)
        non_profile_stream_classes = [
            SponsoredDisplayCampaigns,
            SponsoredDisplayAdGroups,
            SponsoredDisplayProductAds,
            SponsoredDisplayTargetings,
            SponsoredDisplayReportStream,
            SponsoredProductCampaigns,
            SponsoredProductAdGroups,
            SponsoredProductKeywords,
            SponsoredProductNegativeKeywords,
            SponsoredProductAds,
            SponsoredProductTargetings,
            SponsoredProductsReportStream,
            SponsoredBrandsCampaigns,
            SponsoredBrandsAdGroups,
            SponsoredBrandsKeywords,
            SponsoredBrandsReportStream,
            SponsoredBrandsVideoReportStream,
        ]
        return [profiles_stream, *[stream_class(**stream_args) for stream_class in non_profile_stream_classes]]

    @staticmethod
    def _make_authenticator(config: Mapping[str, Any]):
        return Oauth2Authenticator(
            token_refresh_endpoint=TOKEN_URL,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    @staticmethod
    def _set_defaults(config: Mapping[str, Any]):
        config["region"] = AmazonAdsRegion.NA

    @staticmethod
    def _choose_profiles(config: Mapping[str, Any], profiles: List[Profile]):
        if not config.get("profiles"):
            return profiles
        return list(filter(lambda profile: profile.profileId in config["profiles"], profiles))
