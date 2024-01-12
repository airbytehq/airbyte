#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

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
    [
        {"campaign_id": 123,
         "dateRange": {"end.day": 31,
                       "end.month": 1,
                       "end.year": 2021,
                       "start.day": 1,
                       "start.month": 1,
                       "start.year": 2021},
         "fields": "actionClicks,adUnitClicks,approximateUniqueImpressions,cardClicks,cardImpressions,clicks,commentLikes,comments,companyPageClicks,conversionValueInLocalCurrency,costInLocalCurrency,costInUsd,dateRange,documentCompletions,documentFirstQuartileCompletions,documentMidpointCompletions,documentThirdQuartileCompletions,downloadClicks,externalWebsiteConversions"},
        {"campaign_id": 123,
         "dateRange": {"end.day": 31,
                       "end.month": 1,
                       "end.year": 2021,
                       "start.day": 1,
                       "start.month": 1,
                       "start.year": 2021},
         "fields": "externalWebsitePostClickConversions,externalWebsitePostViewConversions,follows,fullScreenPlays,impressions,jobApplications,jobApplyClicks,landingPageClicks,leadGenerationMailContactInfoShares,leadGenerationMailInterestedClicks,likes,oneClickLeadFormOpens,oneClickLeads,opens,otherEngagements,pivotValues,postClickJobApplications,postClickJobApplyClicks,postClickRegistrations,dateRange"},
        {"campaign_id": 123,
         "dateRange": {"end.day": 31,
                       "end.month": 1,
                       "end.year": 2021,
                       "start.day": 1,
                       "start.month": 1,
                       "start.year": 2021},
         "fields": "postViewJobApplications,postViewJobApplyClicks,postViewRegistrations,reactions,registrations,sends,shares,talentLeads,textUrlClicks,totalEngagements,validWorkEmailLeads,videoCompletions,videoFirstQuartileCompletions,videoMidpointCompletions,videoStarts,videoThirdQuartileCompletions,videoViews,viralCardClicks,viralCardImpressions,dateRange"},
        {"campaign_id": 123,
         "dateRange": {"end.day": 31,
                       "end.month": 1,
                       "end.year": 2021,
                       "start.day": 1,
                       "start.month": 1,
                       "start.year": 2021},
         "fields": "viralClicks,viralCommentLikes,viralComments,viralCompanyPageClicks,viralDocumentCompletions,viralDocumentFirstQuartileCompletions,viralDocumentMidpointCompletions,viralDocumentThirdQuartileCompletions,viralDownloadClicks,viralExternalWebsiteConversions,viralExternalWebsitePostClickConversions,viralExternalWebsitePostViewConversions,viralFollows,viralFullScreenPlays,viralImpressions,viralJobApplications,viralJobApplyClicks,viralLandingPageClicks,viralLikes,dateRange"},
        {"campaign_id": 123,
         "dateRange": {"end.day": 31,
                       "end.month": 1,
                       "end.year": 2021,
                       "start.day": 1,
                       "start.month": 1,
                       "start.year": 2021},
         "fields": "viralOneClickLeadFormOpens,viralOneClickLeads,viralOtherEngagements,viralPostClickJobApplications,viralPostClickJobApplyClicks,viralPostClickRegistrations,viralPostViewJobApplications,viralPostViewJobApplyClicks,viralPostViewRegistrations,viralReactions,viralRegistrations,viralShares,viralTotalEngagements,viralVideoCompletions,viralVideoFirstQuartileCompletions,viralVideoMidpointCompletions,viralVideoStarts,viralVideoThirdQuartileCompletions,viralVideoViews,dateRange"}
    ],
    [
        {'campaign_id': 123,
         'dateRange': {'end.day': 2,
                       'end.month': 3,
                       'end.year': 2021,
                       'start.day': 31,
                       'start.month': 1,
                       'start.year': 2021},
         'fields': 'actionClicks,adUnitClicks,approximateUniqueImpressions,cardClicks,cardImpressions,clicks,commentLikes,comments,companyPageClicks,conversionValueInLocalCurrency,costInLocalCurrency,costInUsd,dateRange,documentCompletions,documentFirstQuartileCompletions,documentMidpointCompletions,documentThirdQuartileCompletions,downloadClicks,externalWebsiteConversions'},
        {'campaign_id': 123,
         'dateRange': {'end.day': 2,
                       'end.month': 3,
                       'end.year': 2021,
                       'start.day': 31,
                       'start.month': 1,
                       'start.year': 2021},
         'fields': 'externalWebsitePostClickConversions,externalWebsitePostViewConversions,follows,fullScreenPlays,impressions,jobApplications,jobApplyClicks,landingPageClicks,leadGenerationMailContactInfoShares,leadGenerationMailInterestedClicks,likes,oneClickLeadFormOpens,oneClickLeads,opens,otherEngagements,pivotValues,postClickJobApplications,postClickJobApplyClicks,postClickRegistrations,dateRange'},
        {'campaign_id': 123,
         'dateRange': {'end.day': 2,
                       'end.month': 3,
                       'end.year': 2021,
                       'start.day': 31,
                       'start.month': 1,
                       'start.year': 2021},
         'fields': 'postViewJobApplications,postViewJobApplyClicks,postViewRegistrations,reactions,registrations,sends,shares,talentLeads,textUrlClicks,totalEngagements,validWorkEmailLeads,videoCompletions,videoFirstQuartileCompletions,videoMidpointCompletions,videoStarts,videoThirdQuartileCompletions,videoViews,viralCardClicks,viralCardImpressions,dateRange'},
        {'campaign_id': 123,
         'dateRange': {'end.day': 2,
                       'end.month': 3,
                       'end.year': 2021,
                       'start.day': 31,
                       'start.month': 1,
                       'start.year': 2021},
         'fields': 'viralClicks,viralCommentLikes,viralComments,viralCompanyPageClicks,viralDocumentCompletions,viralDocumentFirstQuartileCompletions,viralDocumentMidpointCompletions,viralDocumentThirdQuartileCompletions,viralDownloadClicks,viralExternalWebsiteConversions,viralExternalWebsitePostClickConversions,viralExternalWebsitePostViewConversions,viralFollows,viralFullScreenPlays,viralImpressions,viralJobApplications,viralJobApplyClicks,viralLandingPageClicks,viralLikes,dateRange'},
        {'campaign_id': 123,
         'dateRange': {'end.day': 2,
                       'end.month': 3,
                       'end.year': 2021,
                       'start.day': 31,
                       'start.month': 1,
                       'start.year': 2021},
         'fields': 'viralOneClickLeadFormOpens,viralOneClickLeads,viralOtherEngagements,viralPostClickJobApplications,viralPostClickJobApplyClicks,viralPostClickRegistrations,viralPostViewJobApplications,viralPostViewJobApplyClicks,viralPostViewRegistrations,viralReactions,viralRegistrations,viralShares,viralTotalEngagements,viralVideoCompletions,viralVideoFirstQuartileCompletions,viralVideoMidpointCompletions,viralVideoStarts,viralVideoThirdQuartileCompletions,viralVideoViews,dateRange'}]]

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

""" This is the expected test output from the `merge_chunks` method from analytics module """
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
