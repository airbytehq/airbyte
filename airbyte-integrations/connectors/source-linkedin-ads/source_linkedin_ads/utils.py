#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, Iterable, List, Mapping

import pendulum as pdm

# replace `pivot` with `_pivot`, to allow redshift normalization,
# since `pivot` is a reserved keyword for Destination Redshift,
# on behalf of https://github.com/airbytehq/airbyte/issues/13018,
# expand this list, if required.
DESTINATION_RESERVED_KEYWORDS: list = ["pivot"]
# List of Reporting Metrics fields available for fetch
ANALYTICS_FIELDS_V2: List = [
    "actionClicks",
    "adUnitClicks",
    "approximateUniqueImpressions",
    "cardClicks",
    "cardImpressions",
    "clicks",
    "commentLikes",
    "comments",
    "companyPageClicks",
    "conversionValueInLocalCurrency",
    "costInLocalCurrency",
    "costInUsd",
    "dateRange",
    "documentCompletions",
    "documentFirstQuartileCompletions",
    "documentMidpointCompletions",
    "documentThirdQuartileCompletions",
    "downloadClicks",
    "externalWebsiteConversions",
    "externalWebsitePostClickConversions",
    "externalWebsitePostViewConversions",
    "follows",
    "fullScreenPlays",
    "impressions",
    "jobApplications",
    "jobApplyClicks",
    "landingPageClicks",
    "leadGenerationMailContactInfoShares",
    "leadGenerationMailInterestedClicks",
    "likes",
    "oneClickLeadFormOpens",
    "oneClickLeads",
    "opens",
    "otherEngagements",
    "pivotValues",
    "postClickJobApplications",
    "postClickJobApplyClicks",
    "postClickRegistrations",
    "postViewJobApplications",
    "postViewJobApplyClicks",
    "postViewRegistrations",
    "reactions",
    "registrations",
    "sends",
    "shares",
    "talentLeads",
    "textUrlClicks",
    "totalEngagements",
    "validWorkEmailLeads",
    "videoCompletions",
    "videoFirstQuartileCompletions",
    "videoMidpointCompletions",
    "videoStarts",
    "videoThirdQuartileCompletions",
    "videoViews",
    "viralCardClicks",
    "viralCardImpressions",
    "viralClicks",
    "viralCommentLikes",
    "viralComments",
    "viralCompanyPageClicks",
    "viralDocumentCompletions",
    "viralDocumentFirstQuartileCompletions",
    "viralDocumentMidpointCompletions",
    "viralDocumentThirdQuartileCompletions",
    "viralDownloadClicks",
    "viralExternalWebsiteConversions",
    "viralExternalWebsitePostClickConversions",
    "viralExternalWebsitePostViewConversions",
    "viralFollows",
    "viralFullScreenPlays",
    "viralImpressions",
    "viralJobApplications",
    "viralJobApplyClicks",
    "viralLandingPageClicks",
    "viralLikes",
    "viralOneClickLeadFormOpens",
    "viralOneClickLeads",
    "viralOtherEngagements",
    "viralPostClickJobApplications",
    "viralPostClickJobApplyClicks",
    "viralPostClickRegistrations",
    "viralPostViewJobApplications",
    "viralPostViewJobApplyClicks",
    "viralPostViewRegistrations",
    "viralReactions",
    "viralRegistrations",
    "viralShares",
    "viralTotalEngagements",
    "viralVideoCompletions",
    "viralVideoFirstQuartileCompletions",
    "viralVideoMidpointCompletions",
    "viralVideoStarts",
    "viralVideoThirdQuartileCompletions",
    "viralVideoViews",
]
FIELDS_CHUNK_SIZE = 18


def update_specific_key(target_dict, target_key, target_value):
    for key, value in target_dict.items():
        if key == target_key:
            target_dict[key] = target_value
        elif isinstance(value, dict):
            # Recursively update nested dictionaries
            target_dict[key] = update_specific_key(value, target_key, target_value)
        elif isinstance(value, list):
            # Recursively update lists
            target_dict[key] = [update_specific_key(item, target_key, target_value) if isinstance(item, dict) else item for item in value]
    return target_dict
