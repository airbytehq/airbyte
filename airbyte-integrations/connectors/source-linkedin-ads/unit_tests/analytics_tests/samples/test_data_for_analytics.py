#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List

"""
This is the example of input record for the test_make_analytics_slices.
"""
test_input_record: Dict = {
    "id": 123,
    "audienceExpansionEnabled": True,
    "test": False,
    "format": "STANDARD_UPDATE",
    "servingStatuses": ["CAMPAIGN_GROUP_TOTAL_BUDGET_HOLD"],
    "version": {"versionTag": "2"},
    "objectiveType": "TEST_TEST",
    "associatedEntity": "urn:li:organization:456",
    "offsitePreferences": {
        "iabCategories": {"exclude": []},
        "publisherRestrictionFiles": {"exclude": []},
    },
    "campaignGroup": "urn:li:sponsoredCampaignGroup:1234567",
    "account": "urn:li:sponsoredAccount:123456",
    "status": "ACTIVE",
    "created": "2021-08-06 06:03:52",
    "lastModified": "2021-08-06 06:09:04",
}


"""
This is the expected output from the `make_analytics_slices` method.
VALID PARAMETERS FOR THE OUTPUT ARE:
: TEST_KEY_VALUE_MAP = {"campaign_id": "id"}
: TEST_START_DATE = "2021-08-01"
: TEST_END_DATE = "2021-09-30"

Change the input parameters inside of test_make_analytics_slices.py unit test.
Make sure for valid KEY_VALUE_MAP references inside of the `test_input_record`
"""
test_output_slices: List = [
    {
        "camp_id": 123,
        "fields": "actionClicks,adUnitClicks,approximateUniqueImpressions,cardClicks,cardImpressions,clicks,commentLikes,comments,companyPageClicks,conversionValueInLocalCurrency,costInLocalCurrency,costInUsd,dateRange,externalWebsiteConversions,externalWebsitePostClickConversions,externalWebsitePostViewConversions,follows,pivot,pivotValue",
        "dateRange": {
            "start.day": 1,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 31,
            "end.month": 8,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "actionClicks,adUnitClicks,approximateUniqueImpressions,cardClicks,cardImpressions,clicks,commentLikes,comments,companyPageClicks,conversionValueInLocalCurrency,costInLocalCurrency,costInUsd,dateRange,externalWebsiteConversions,externalWebsitePostClickConversions,externalWebsitePostViewConversions,follows,pivot,pivotValue",
        "dateRange": {
            "start.day": 31,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 30,
            "end.month": 9,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "fullScreenPlays,impressions,landingPageClicks,leadGenerationMailContactInfoShares,leadGenerationMailInterestedClicks,likes,oneClickLeadFormOpens,oneClickLeads,opens,otherEngagements,pivot,pivotValue,pivotValues,reactions,sends,shares,textUrlClicks,dateRange",
        "dateRange": {
            "start.day": 1,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 31,
            "end.month": 8,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "fullScreenPlays,impressions,landingPageClicks,leadGenerationMailContactInfoShares,leadGenerationMailInterestedClicks,likes,oneClickLeadFormOpens,oneClickLeads,opens,otherEngagements,pivot,pivotValue,pivotValues,reactions,sends,shares,textUrlClicks,dateRange",
        "dateRange": {
            "start.day": 31,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 30,
            "end.month": 9,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "totalEngagements,videoCompletions,videoFirstQuartileCompletions,videoMidpointCompletions,videoStarts,videoThirdQuartileCompletions,videoViews,viralCardClicks,viralCardImpressions,viralClicks,viralCommentLikes,viralComments,viralCompanyPageClicks,viralExternalWebsiteConversions,viralExternalWebsitePostClickConversions,viralExternalWebsitePostViewConversions,viralFollows,dateRange,pivot,pivotValue",
        "dateRange": {
            "start.day": 1,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 31,
            "end.month": 8,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "totalEngagements,videoCompletions,videoFirstQuartileCompletions,videoMidpointCompletions,videoStarts,videoThirdQuartileCompletions,videoViews,viralCardClicks,viralCardImpressions,viralClicks,viralCommentLikes,viralComments,viralCompanyPageClicks,viralExternalWebsiteConversions,viralExternalWebsitePostClickConversions,viralExternalWebsitePostViewConversions,viralFollows,dateRange,pivot,pivotValue",
        "dateRange": {
            "start.day": 31,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 30,
            "end.month": 9,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "viralFullScreenPlays,viralImpressions,viralLandingPageClicks,viralLikes,viralOneClickLeadFormOpens,viralOneClickLeads,viralOtherEngagements,viralReactions,viralShares,viralTotalEngagements,viralVideoCompletions,viralVideoFirstQuartileCompletions,viralVideoMidpointCompletions,viralVideoStarts,viralVideoThirdQuartileCompletions,viralVideoViews,dateRange,pivot,pivotValue",
        "dateRange": {
            "start.day": 1,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 31,
            "end.month": 8,
            "end.year": 2021,
        },
    },
    {
        "camp_id": 123,
        "fields": "viralFullScreenPlays,viralImpressions,viralLandingPageClicks,viralLikes,viralOneClickLeadFormOpens,viralOneClickLeads,viralOtherEngagements,viralReactions,viralShares,viralTotalEngagements,viralVideoCompletions,viralVideoFirstQuartileCompletions,viralVideoMidpointCompletions,viralVideoStarts,viralVideoThirdQuartileCompletions,viralVideoViews,dateRange,pivot,pivotValue",
        "dateRange": {
            "start.day": 31,
            "start.month": 8,
            "start.year": 2021,
            "end.day": 30,
            "end.month": 9,
            "end.year": 2021,
        },
    },
]


""" This is the example of the input chunks for the `test_merge_chunks` """
test_input_result_record_chunks = [
    [
        {
            "field_1": "test1",
            "start_date": "2021-08-06",
            "end_date": "2021-08-06",
        },
        {
            "field_1": "test2",
            "start_date": "2021-08-07",
            "end_date": "2021-08-07",
        },
        {
            "field_1": "test3",
            "start_date": "2021-08-08",
            "end_date": "2021-08-08",
        },
    ],
    [
        {
            "field_2": "test1",
            "start_date": "2021-08-06",
            "end_date": "2021-08-06",
        },
        {
            "field_2": "test2",
            "start_date": "2021-08-07",
            "end_date": "2021-08-07",
        },
        {
            "field_2": "test3",
            "start_date": "2021-08-08",
            "end_date": "2021-08-08",
        },
    ],
    [
        {
            "field_3": "test1",
            "start_date": "2021-08-06",
            "end_date": "2021-08-06",
        },
        {
            "field_3": "test2",
            "start_date": "2021-08-07",
            "end_date": "2021-08-07",
        },
        {
            "field_3": "test3",
            "start_date": "2021-08-08",
            "end_date": "2021-08-08",
        },
    ],
]

""" This is the expected test ouptput from the `merge_chunks` method from analytics module """
test_output_merged_chunks = [
    {
        "field_1": "test1",
        "start_date": "2021-08-06",
        "end_date": "2021-08-06",
        "field_2": "test1",
        "field_3": "test1",
    },
    {
        "field_1": "test2",
        "start_date": "2021-08-07",
        "end_date": "2021-08-07",
        "field_2": "test2",
        "field_3": "test2",
    },
    {
        "field_1": "test3",
        "start_date": "2021-08-08",
        "end_date": "2021-08-08",
        "field_2": "test3",
        "field_3": "test3",
    },
]
