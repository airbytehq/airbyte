#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from collections import defaultdict
from typing import Any, Iterable, List, Mapping

import pendulum as pdm

from .utils import get_parent_stream_values

# LinkedIn has a max of 20 fields per request. We make chunks by size of 17 fields
# to have the `dateRange`, `pivot`, and `pivotValue` be included as well.
FIELDS_CHUNK_SIZE = 17
# Number of days ahead for date slices, from start date.
WINDOW_IN_DAYS = 30
# List of adAnalyticsV2 fields available for fetch
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
    "externalWebsiteConversions",
    "externalWebsitePostClickConversions",
    "externalWebsitePostViewConversions",
    "follows",
    "fullScreenPlays",
    "impressions",
    "landingPageClicks",
    "leadGenerationMailContactInfoShares",
    "leadGenerationMailInterestedClicks",
    "likes",
    "oneClickLeadFormOpens",
    "oneClickLeads",
    "opens",
    "otherEngagements",
    "pivot",
    "pivotValue",
    "pivotValues",
    "reactions",
    "sends",
    "shares",
    "textUrlClicks",
    "totalEngagements",
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
    "viralExternalWebsiteConversions",
    "viralExternalWebsitePostClickConversions",
    "viralExternalWebsitePostViewConversions",
    "viralFollows",
    "viralFullScreenPlays",
    "viralImpressions",
    "viralLandingPageClicks",
    "viralLikes",
    "viralOneClickLeadFormOpens",
    "viralOneClickLeads",
    "viralOtherEngagements",
    "viralReactions",
    "viralShares",
    "viralTotalEngagements",
    "viralVideoCompletions",
    "viralVideoFirstQuartileCompletions",
    "viralVideoMidpointCompletions",
    "viralVideoStarts",
    "viralVideoThirdQuartileCompletions",
    "viralVideoViews",
]

# Fields that are always present in fields_set chunks
BASE_ANALLYTICS_FIELDS = ["dateRange", "pivot", "pivotValue"]


def chunk_analytics_fields(
    fields: List = ANALYTICS_FIELDS_V2,
    base_fields: List = BASE_ANALLYTICS_FIELDS,
    fields_chunk_size: int = FIELDS_CHUNK_SIZE,
) -> Iterable[List]:
    """
    Chunks the list of available fields into the chunks of equal size.
    """
    # Make chunks
    chunks = list((fields[f : f + fields_chunk_size] for f in range(0, len(fields), fields_chunk_size)))
    # Make sure base_fields are within the chunks
    for chunk in chunks:
        for field in base_fields:
            if field not in chunk:
                chunk.append(field)
    yield from chunks


def make_date_slices(start_date: str, end_date: str = None, window_in_days: int = WINDOW_IN_DAYS) -> Iterable[List]:
    """
    Produces date slices from start_date to end_date (if specified),
    otherwise end_date will be present time.
    """
    start = pdm.parse(start_date)
    end = pdm.parse(end_date) if end_date else pdm.now()
    date_slices = []
    while start < end:
        slice_end_date = start.add(days=window_in_days)
        date_slice = {
            "start.day": start.day,
            "start.month": start.month,
            "start.year": start.year,
            "end.day": slice_end_date.day,
            "end.month": slice_end_date.month,
            "end.year": slice_end_date.year,
        }
        date_slices.append({"dateRange": date_slice})
        start = slice_end_date
    yield from date_slices


def make_analytics_slices(
    record: Mapping[str, Any], key_value_map: Mapping[str, Any], start_date: str, end_date: str = None
) -> Iterable[Mapping[str, Any]]:
    """
    We drive the ability to directly pass the prepared parameters inside the stream_slice.
    The output of this method is ready slices for analytics streams:
    """
    # define the base_slice
    base_slice = get_parent_stream_values(record, key_value_map)
    # add chunked fields, date_slices to the base_slice
    analytics_slices = []
    for fields_set in chunk_analytics_fields():
        base_slice["fields"] = ",".join(map(str, fields_set))
        for date_slice in make_date_slices(start_date, end_date):
            base_slice.update(**date_slice)
            analytics_slices.append(base_slice.copy())
    yield from analytics_slices


def update_analytics_params(stream_slice: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Produces the date range parameters from input stream_slice
    """
    return {
        # Start date range
        "dateRange.start.day": stream_slice["dateRange"]["start.day"],
        "dateRange.start.month": stream_slice["dateRange"]["start.month"],
        "dateRange.start.year": stream_slice["dateRange"]["start.year"],
        # End date range
        "dateRange.end.day": stream_slice["dateRange"]["end.day"],
        "dateRange.end.month": stream_slice["dateRange"]["end.month"],
        "dateRange.end.year": stream_slice["dateRange"]["end.year"],
        # Chunk of fields
        "fields": stream_slice["fields"],
    }


def merge_chunks(chunked_result: Iterable[Mapping[str, Any]], merge_by_key: str) -> Iterable[Mapping[str, Any]]:
    """
    We need to merge the chunked API responses
    into the single structure using any available unique field.
    """
    # Merge the pieces together
    merged = defaultdict(dict)
    for chunk in chunked_result:
        for item in chunk:
            merged[item[merge_by_key]].update(item)
    # Clean up the result by getting out the values of the merged keys
    result = []
    for item in merged:
        result.append(merged.get(item))
    yield from result
