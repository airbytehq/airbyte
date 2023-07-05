#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from .schemas import Profile
from .streams import (
    AttributionReportPerformanceAdgroup,
    AttributionReportPerformanceCampaign,
    AttributionReportPerformanceCreative,
    AttributionReportProducts,
    Portfolios,
    Profiles,
    SponsoredBrandsAdGroups,
    SponsoredBrandsCampaigns,
    SponsoredBrandsKeywords,
    SponsoredBrandsReportStream,
    SponsoredBrandsV3ReportStream,
    SponsoredBrandsVideoReportStream,
    SponsoredDisplayAdGroups,
    SponsoredDisplayBudgetRules,
    SponsoredDisplayCampaigns,
    SponsoredDisplayProductAds,
    SponsoredDisplayReportStream,
    SponsoredDisplayTargetings,
    SponsoredProductAdGroups,
    SponsoredProductAds,
    SponsoredProductCampaignNegativeKeywords,
    SponsoredProductCampaigns,
    SponsoredProductKeywords,
    SponsoredProductNegativeKeywords,
    SponsoredProductsReportStream,
    SponsoredProductTargetings,
)

# Oauth 2.0 authentication URL for amazon
TOKEN_URL = "https://api.amazon.com/auth/o2/token"
CONFIG_DATE_FORMAT = "YYYY-MM-DD"


class SourceAmazonAds(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any]):
        start_date = config.get("start_date")
        if start_date:
            config["start_date"] = pendulum.from_format(start_date, CONFIG_DATE_FORMAT).date()
        else:
            config["start_date"] = None
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
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            config = self._validate_and_transform(config)
        except Exception as e:
            return False, str(e)
        # Check connection by sending list of profiles request. Its most simple
        # request, not require additional parameters and usually has few data
        # in response body.
        # It doesnt support pagination so there is no sense of reading single
        # record, it would fetch all the data anyway.
        Profiles(config, authenticator=self._make_authenticator(config)).get_all_profiles()
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return list of streams for current source
        """
        config = self._validate_and_transform(config)
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
            SponsoredDisplayBudgetRules,
            SponsoredProductCampaigns,
            SponsoredProductAdGroups,
            SponsoredProductKeywords,
            SponsoredProductNegativeKeywords,
            SponsoredProductCampaignNegativeKeywords,
            SponsoredProductAds,
            SponsoredProductTargetings,
            SponsoredProductsReportStream,
            SponsoredBrandsCampaigns,
            SponsoredBrandsAdGroups,
            SponsoredBrandsKeywords,
            SponsoredBrandsReportStream,
            SponsoredBrandsV3ReportStream,
            SponsoredBrandsVideoReportStream,
            AttributionReportPerformanceAdgroup,
            AttributionReportPerformanceCampaign,
            AttributionReportPerformanceCreative,
            AttributionReportProducts,
        ]
        portfolios_stream = Portfolios(**stream_args)
        return [profiles_stream, portfolios_stream, *[stream_class(**stream_args) for stream_class in non_profile_stream_classes]]

    @staticmethod
    def _make_authenticator(config: Mapping[str, Any]):
        return Oauth2Authenticator(
            token_refresh_endpoint=TOKEN_URL,
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=config["refresh_token"],
        )

    @staticmethod
    def _choose_profiles(config: Mapping[str, Any], profiles: List[Profile]):
        if not config.get("profiles"):
            return profiles
        return list(filter(lambda profile: profile.profileId in config["profiles"], profiles))
