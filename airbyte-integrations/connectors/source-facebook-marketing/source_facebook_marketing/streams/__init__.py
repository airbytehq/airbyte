#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from .streams import (
    AdsInsights,
    AdsInsightsActionType,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
)
from .streams import AdCreatives, Ads, AdSets, Campaigns, Videos

__all__ = [
    "AdCreatives",
    "Ads",
    "AdSets",
    "AdsInsights",
    "AdsInsightsActionType",
    "AdsInsightsAgeAndGender",
    "AdsInsightsCountry",
    "AdsInsightsDma",
    "AdsInsightsPlatformAndDevice",
    "AdsInsightsRegion",
    "Campaigns",
    "Videos",
]
