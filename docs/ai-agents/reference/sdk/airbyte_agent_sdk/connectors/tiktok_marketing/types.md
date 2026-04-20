---
id: airbyte_agent_sdk-connectors-tiktok_marketing-types
title: airbyte_agent_sdk.connectors.tiktok_marketing.types
---

Module airbyte_agent_sdk.connectors.tiktok_marketing.types
==========================================================
Type definitions for tiktok-marketing connector.

Classes
-------

`AdGroupsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

`AdGroupsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: Any`
    :   The unique identifier of the ad group

    `adgroup_name: Any`
    :   The name of the ad group

    `advertiser_id: Any`
    :   The unique identifier of the advertiser

    `budget: Any`
    :   The allocated budget for the ad group

    `budget_mode: Any`
    :   The mode for managing the budget

    `campaign_id: Any`
    :   The unique identifier of the campaign

    `create_time: Any`
    :   The timestamp for when the ad group was created

    `modify_time: Any`
    :   The timestamp for when the ad group was last modified

    `operation_status: Any`
    :   The status of the operation

    `optimization_goal: Any`
    :   The goal set for optimization

    `placement_type: Any`
    :   The type of ad placement

    `promotion_type: Any`
    :   The type of promotion

    `secondary_status: Any`
    :   The secondary status of the ad group

`AdGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsInFilter`
    :   The type of the None singleton.

`AdGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: list[int]`
    :   The unique identifier of the ad group

    `adgroup_name: list[str]`
    :   The name of the ad group

    `advertiser_id: list[int]`
    :   The unique identifier of the advertiser

    `budget: list[float]`
    :   The allocated budget for the ad group

    `budget_mode: list[str]`
    :   The mode for managing the budget

    `campaign_id: list[int]`
    :   The unique identifier of the campaign

    `create_time: list[str]`
    :   The timestamp for when the ad group was created

    `modify_time: list[str]`
    :   The timestamp for when the ad group was last modified

    `operation_status: list[str]`
    :   The status of the operation

    `optimization_goal: list[str]`
    :   The goal set for optimization

    `placement_type: list[str]`
    :   The type of ad placement

    `promotion_type: list[str]`
    :   The type of promotion

    `secondary_status: list[str]`
    :   The secondary status of the ad group

`AdGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsStringFilter`
    :   The type of the None singleton.

`AdGroupsListParams(*args, **kwargs)`
:   Parameters for ad_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AdGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSearchFilter`
    :   The type of the None singleton.

`AdGroupsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

`AdGroupsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAnyCondition]`
    :   The type of the None singleton.

`AdGroupsReportsDailyAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAnyCondition]`
    :   The type of the None singleton.

`AdGroupsReportsDailyAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: Any`
    :   The unique identifier for the ad group.

    `adgroup_name: Any`
    :   The name of the ad group.

    `app_install: Any`
    :   Number of app installations.

    `average_video_play: Any`
    :   Average video play duration.

    `average_video_play_per_user: Any`
    :   Average video play duration per user.

    `campaign_id: Any`
    :   The unique identifier for the campaign.

    `campaign_name: Any`
    :   The name of the marketing campaign.

    `clicks: Any`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Any`
    :   Number of clicks on the music disc.

    `comments: Any`
    :   Number of comments.

    `conversion: Any`
    :   Number of conversions.

    `conversion_rate: Any`
    :   Rate of conversions.

    `cost_per_1000_reached: Any`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: Any`
    :   Cost per conversion.

    `cost_per_result: Any`
    :   Cost per result.

    `cost_per_secondary_goal_result: Any`
    :   Cost per secondary goal result.

    `cpc: Any`
    :   Cost per click.

    `cpm: Any`
    :   Cost per thousand impressions.

    `ctr: Any`
    :   Click-through rate.

    `follows: Any`
    :   Number of follows.

    `frequency: Any`
    :   Average number of times each person saw the ad.

    `impressions: Any`
    :   Number of times the ad was displayed.

    `likes: Any`
    :   Number of likes.

    `placement_type: Any`
    :   Type of ad placement.

    `profile_visits: Any`
    :   Number of profile visits.

    `reach: Any`
    :   Total number of unique users reached.

    `real_time_app_install: Any`
    :   Real-time app installations.

    `real_time_app_install_cost: Any`
    :   Cost of real-time app installations.

    `real_time_conversion: Any`
    :   Real-time conversions.

    `real_time_conversion_rate: Any`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: Any`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: Any`
    :   Real-time cost per result.

    `real_time_result: Any`
    :   Real-time results.

    `real_time_result_rate: Any`
    :   Real-time result rate.

    `result: Any`
    :   Number of results.

    `result_rate: Any`
    :   Rate of results.

    `secondary_goal_result: Any`
    :   Results for secondary goals.

    `secondary_goal_result_rate: Any`
    :   Rate of secondary goal results.

    `shares: Any`
    :   Number of shares.

    `spend: Any`
    :   Total amount of money spent.

    `stat_time_day: Any`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Any`
    :   Number of video play actions.

    `video_views_p100: Any`
    :   Number of times video was watched to 100%.

    `video_views_p25: Any`
    :   Number of times video was watched to 25%.

    `video_views_p50: Any`
    :   Number of times video was watched to 50%.

    `video_views_p75: Any`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Any`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Any`
    :   Number of times video was watched for at least 6 seconds.

`AdGroupsReportsDailyContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyStringFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyInFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: list[int]`
    :   The unique identifier for the ad group.

    `adgroup_name: list[str]`
    :   The name of the ad group.

    `app_install: list[float]`
    :   Number of app installations.

    `average_video_play: list[float]`
    :   Average video play duration.

    `average_video_play_per_user: list[float]`
    :   Average video play duration per user.

    `campaign_id: list[int]`
    :   The unique identifier for the campaign.

    `campaign_name: list[str]`
    :   The name of the marketing campaign.

    `clicks: list[str]`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: list[float]`
    :   Number of clicks on the music disc.

    `comments: list[float]`
    :   Number of comments.

    `conversion: list[str]`
    :   Number of conversions.

    `conversion_rate: list[str]`
    :   Rate of conversions.

    `cost_per_1000_reached: list[str]`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: list[str]`
    :   Cost per conversion.

    `cost_per_result: list[str]`
    :   Cost per result.

    `cost_per_secondary_goal_result: list[str]`
    :   Cost per secondary goal result.

    `cpc: list[str]`
    :   Cost per click.

    `cpm: list[str]`
    :   Cost per thousand impressions.

    `ctr: list[str]`
    :   Click-through rate.

    `follows: list[float]`
    :   Number of follows.

    `frequency: list[str]`
    :   Average number of times each person saw the ad.

    `impressions: list[str]`
    :   Number of times the ad was displayed.

    `likes: list[float]`
    :   Number of likes.

    `placement_type: list[str]`
    :   Type of ad placement.

    `profile_visits: list[float]`
    :   Number of profile visits.

    `reach: list[str]`
    :   Total number of unique users reached.

    `real_time_app_install: list[float]`
    :   Real-time app installations.

    `real_time_app_install_cost: list[float]`
    :   Cost of real-time app installations.

    `real_time_conversion: list[str]`
    :   Real-time conversions.

    `real_time_conversion_rate: list[str]`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: list[str]`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: list[str]`
    :   Real-time cost per result.

    `real_time_result: list[str]`
    :   Real-time results.

    `real_time_result_rate: list[str]`
    :   Real-time result rate.

    `result: list[str]`
    :   Number of results.

    `result_rate: list[str]`
    :   Rate of results.

    `secondary_goal_result: list[str]`
    :   Results for secondary goals.

    `secondary_goal_result_rate: list[str]`
    :   Rate of secondary goal results.

    `shares: list[float]`
    :   Number of shares.

    `spend: list[str]`
    :   Total amount of money spent.

    `stat_time_day: list[str]`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: list[float]`
    :   Number of video play actions.

    `video_views_p100: list[float]`
    :   Number of times video was watched to 100%.

    `video_views_p25: list[float]`
    :   Number of times video was watched to 25%.

    `video_views_p50: list[float]`
    :   Number of times video was watched to 50%.

    `video_views_p75: list[float]`
    :   Number of times video was watched to 75%.

    `video_watched_2s: list[float]`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: list[float]`
    :   Number of times video was watched for at least 6 seconds.

`AdGroupsReportsDailyKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyStringFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyStringFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyListParams(*args, **kwargs)`
:   Parameters for ad_groups_reports_daily.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `data_level: str`
    :   The type of the None singleton.

    `dimensions: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `metrics: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `report_type: str`
    :   The type of the None singleton.

    `service_type: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

`AdGroupsReportsDailyLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdGroupsReportsDailyNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAnyCondition`
    :   The type of the None singleton.

`AdGroupsReportsDailyOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAnyCondition]`
    :   The type of the None singleton.

`AdGroupsReportsDailySearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_groups_reports_daily search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: int | None`
    :   The unique identifier for the ad group.

    `adgroup_name: str | None`
    :   The name of the ad group.

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `campaign_id: int | None`
    :   The unique identifier for the campaign.

    `campaign_name: str | None`
    :   The name of the marketing campaign.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `conversion: str | None`
    :   Number of conversions.

    `conversion_rate: str | None`
    :   Rate of conversions.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: str | None`
    :   Cost per conversion.

    `cost_per_result: str | None`
    :   Cost per result.

    `cost_per_secondary_goal_result: str | None`
    :   Cost per secondary goal result.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `placement_type: str | None`
    :   Type of ad placement.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `real_time_conversion: str | None`
    :   Real-time conversions.

    `real_time_conversion_rate: str | None`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: str | None`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: str | None`
    :   Real-time cost per result.

    `real_time_result: str | None`
    :   Real-time results.

    `real_time_result_rate: str | None`
    :   Real-time result rate.

    `result: str | None`
    :   Number of results.

    `result_rate: str | None`
    :   Rate of results.

    `secondary_goal_result: str | None`
    :   Results for secondary goals.

    `secondary_goal_result_rate: str | None`
    :   Rate of secondary goal results.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

`AdGroupsReportsDailySearchQuery(*args, **kwargs)`
:   Search query for ad_groups_reports_daily entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailyAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsReportsDailySortFilter]`
    :   The type of the None singleton.

`AdGroupsReportsDailySortFilter(*args, **kwargs)`
:   Available fields for sorting ad_groups_reports_daily search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: Literal['asc', 'desc']`
    :   The unique identifier for the ad group.

    `adgroup_name: Literal['asc', 'desc']`
    :   The name of the ad group.

    `app_install: Literal['asc', 'desc']`
    :   Number of app installations.

    `average_video_play: Literal['asc', 'desc']`
    :   Average video play duration.

    `average_video_play_per_user: Literal['asc', 'desc']`
    :   Average video play duration per user.

    `campaign_id: Literal['asc', 'desc']`
    :   The unique identifier for the campaign.

    `campaign_name: Literal['asc', 'desc']`
    :   The name of the marketing campaign.

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Literal['asc', 'desc']`
    :   Number of clicks on the music disc.

    `comments: Literal['asc', 'desc']`
    :   Number of comments.

    `conversion: Literal['asc', 'desc']`
    :   Number of conversions.

    `conversion_rate: Literal['asc', 'desc']`
    :   Rate of conversions.

    `cost_per_1000_reached: Literal['asc', 'desc']`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: Literal['asc', 'desc']`
    :   Cost per conversion.

    `cost_per_result: Literal['asc', 'desc']`
    :   Cost per result.

    `cost_per_secondary_goal_result: Literal['asc', 'desc']`
    :   Cost per secondary goal result.

    `cpc: Literal['asc', 'desc']`
    :   Cost per click.

    `cpm: Literal['asc', 'desc']`
    :   Cost per thousand impressions.

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate.

    `follows: Literal['asc', 'desc']`
    :   Number of follows.

    `frequency: Literal['asc', 'desc']`
    :   Average number of times each person saw the ad.

    `impressions: Literal['asc', 'desc']`
    :   Number of times the ad was displayed.

    `likes: Literal['asc', 'desc']`
    :   Number of likes.

    `placement_type: Literal['asc', 'desc']`
    :   Type of ad placement.

    `profile_visits: Literal['asc', 'desc']`
    :   Number of profile visits.

    `reach: Literal['asc', 'desc']`
    :   Total number of unique users reached.

    `real_time_app_install: Literal['asc', 'desc']`
    :   Real-time app installations.

    `real_time_app_install_cost: Literal['asc', 'desc']`
    :   Cost of real-time app installations.

    `real_time_conversion: Literal['asc', 'desc']`
    :   Real-time conversions.

    `real_time_conversion_rate: Literal['asc', 'desc']`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: Literal['asc', 'desc']`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: Literal['asc', 'desc']`
    :   Real-time cost per result.

    `real_time_result: Literal['asc', 'desc']`
    :   Real-time results.

    `real_time_result_rate: Literal['asc', 'desc']`
    :   Real-time result rate.

    `result: Literal['asc', 'desc']`
    :   Number of results.

    `result_rate: Literal['asc', 'desc']`
    :   Rate of results.

    `secondary_goal_result: Literal['asc', 'desc']`
    :   Results for secondary goals.

    `secondary_goal_result_rate: Literal['asc', 'desc']`
    :   Rate of secondary goal results.

    `shares: Literal['asc', 'desc']`
    :   Number of shares.

    `spend: Literal['asc', 'desc']`
    :   Total amount of money spent.

    `stat_time_day: Literal['asc', 'desc']`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Literal['asc', 'desc']`
    :   Number of video play actions.

    `video_views_p100: Literal['asc', 'desc']`
    :   Number of times video was watched to 100%.

    `video_views_p25: Literal['asc', 'desc']`
    :   Number of times video was watched to 25%.

    `video_views_p50: Literal['asc', 'desc']`
    :   Number of times video was watched to 50%.

    `video_views_p75: Literal['asc', 'desc']`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 6 seconds.

`AdGroupsReportsDailyStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: str`
    :   The unique identifier for the ad group.

    `adgroup_name: str`
    :   The name of the ad group.

    `app_install: str`
    :   Number of app installations.

    `average_video_play: str`
    :   Average video play duration.

    `average_video_play_per_user: str`
    :   Average video play duration per user.

    `campaign_id: str`
    :   The unique identifier for the campaign.

    `campaign_name: str`
    :   The name of the marketing campaign.

    `clicks: str`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: str`
    :   Number of clicks on the music disc.

    `comments: str`
    :   Number of comments.

    `conversion: str`
    :   Number of conversions.

    `conversion_rate: str`
    :   Rate of conversions.

    `cost_per_1000_reached: str`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: str`
    :   Cost per conversion.

    `cost_per_result: str`
    :   Cost per result.

    `cost_per_secondary_goal_result: str`
    :   Cost per secondary goal result.

    `cpc: str`
    :   Cost per click.

    `cpm: str`
    :   Cost per thousand impressions.

    `ctr: str`
    :   Click-through rate.

    `follows: str`
    :   Number of follows.

    `frequency: str`
    :   Average number of times each person saw the ad.

    `impressions: str`
    :   Number of times the ad was displayed.

    `likes: str`
    :   Number of likes.

    `placement_type: str`
    :   Type of ad placement.

    `profile_visits: str`
    :   Number of profile visits.

    `reach: str`
    :   Total number of unique users reached.

    `real_time_app_install: str`
    :   Real-time app installations.

    `real_time_app_install_cost: str`
    :   Cost of real-time app installations.

    `real_time_conversion: str`
    :   Real-time conversions.

    `real_time_conversion_rate: str`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: str`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: str`
    :   Real-time cost per result.

    `real_time_result: str`
    :   Real-time results.

    `real_time_result_rate: str`
    :   Real-time result rate.

    `result: str`
    :   Number of results.

    `result_rate: str`
    :   Rate of results.

    `secondary_goal_result: str`
    :   Results for secondary goals.

    `secondary_goal_result_rate: str`
    :   Rate of secondary goal results.

    `shares: str`
    :   Number of shares.

    `spend: str`
    :   Total amount of money spent.

    `stat_time_day: str`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: str`
    :   Number of video play actions.

    `video_views_p100: str`
    :   Number of times video was watched to 100%.

    `video_views_p25: str`
    :   Number of times video was watched to 25%.

    `video_views_p50: str`
    :   Number of times video was watched to 50%.

    `video_views_p75: str`
    :   Number of times video was watched to 75%.

    `video_watched_2s: str`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: str`
    :   Number of times video was watched for at least 6 seconds.

`AdGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ad_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: int | None`
    :   The unique identifier of the ad group

    `adgroup_name: str | None`
    :   The name of the ad group

    `advertiser_id: int | None`
    :   The unique identifier of the advertiser

    `budget: float | None`
    :   The allocated budget for the ad group

    `budget_mode: str | None`
    :   The mode for managing the budget

    `campaign_id: int | None`
    :   The unique identifier of the campaign

    `create_time: str | None`
    :   The timestamp for when the ad group was created

    `modify_time: str | None`
    :   The timestamp for when the ad group was last modified

    `operation_status: str | None`
    :   The status of the operation

    `optimization_goal: str | None`
    :   The goal set for optimization

    `placement_type: str | None`
    :   The type of ad placement

    `promotion_type: str | None`
    :   The type of promotion

    `secondary_status: str | None`
    :   The secondary status of the ad group

`AdGroupsSearchQuery(*args, **kwargs)`
:   Search query for ad_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdGroupsSortFilter]`
    :   The type of the None singleton.

`AdGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting ad_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: Literal['asc', 'desc']`
    :   The unique identifier of the ad group

    `adgroup_name: Literal['asc', 'desc']`
    :   The name of the ad group

    `advertiser_id: Literal['asc', 'desc']`
    :   The unique identifier of the advertiser

    `budget: Literal['asc', 'desc']`
    :   The allocated budget for the ad group

    `budget_mode: Literal['asc', 'desc']`
    :   The mode for managing the budget

    `campaign_id: Literal['asc', 'desc']`
    :   The unique identifier of the campaign

    `create_time: Literal['asc', 'desc']`
    :   The timestamp for when the ad group was created

    `modify_time: Literal['asc', 'desc']`
    :   The timestamp for when the ad group was last modified

    `operation_status: Literal['asc', 'desc']`
    :   The status of the operation

    `optimization_goal: Literal['asc', 'desc']`
    :   The goal set for optimization

    `placement_type: Literal['asc', 'desc']`
    :   The type of ad placement

    `promotion_type: Literal['asc', 'desc']`
    :   The type of promotion

    `secondary_status: Literal['asc', 'desc']`
    :   The secondary status of the ad group

`AdGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adgroup_id: str`
    :   The unique identifier of the ad group

    `adgroup_name: str`
    :   The name of the ad group

    `advertiser_id: str`
    :   The unique identifier of the advertiser

    `budget: str`
    :   The allocated budget for the ad group

    `budget_mode: str`
    :   The mode for managing the budget

    `campaign_id: str`
    :   The unique identifier of the campaign

    `create_time: str`
    :   The timestamp for when the ad group was created

    `modify_time: str`
    :   The timestamp for when the ad group was last modified

    `operation_status: str`
    :   The status of the operation

    `optimization_goal: str`
    :   The goal set for optimization

    `placement_type: str`
    :   The type of ad placement

    `promotion_type: str`
    :   The type of promotion

    `secondary_status: str`
    :   The secondary status of the ad group

`AdsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAnyCondition]`
    :   The type of the None singleton.

`AdsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

`AdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_format: Any`
    :   The format of the ad

    `ad_id: Any`
    :   The unique identifier of the ad

    `ad_name: Any`
    :   The name of the ad

    `ad_text: Any`
    :   The text content of the ad

    `adgroup_id: Any`
    :   The unique identifier of the ad group

    `adgroup_name: Any`
    :   The name of the ad group

    `advertiser_id: Any`
    :   The unique identifier of the advertiser

    `campaign_id: Any`
    :   The unique identifier of the campaign

    `campaign_name: Any`
    :   The name of the campaign

    `create_time: Any`
    :   The timestamp when the ad was created

    `landing_page_url: Any`
    :   The URL of the landing page for the ad

    `modify_time: Any`
    :   The timestamp when the ad was last modified

    `operation_status: Any`
    :   The operational status of the ad

    `secondary_status: Any`
    :   The secondary status of the ad

    `video_id: Any`
    :   The unique identifier of the video

`AdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

`AdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsInFilter`
    :   The type of the None singleton.

`AdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_format: list[str]`
    :   The format of the ad

    `ad_id: list[int]`
    :   The unique identifier of the ad

    `ad_name: list[str]`
    :   The name of the ad

    `ad_text: list[str]`
    :   The text content of the ad

    `adgroup_id: list[int]`
    :   The unique identifier of the ad group

    `adgroup_name: list[str]`
    :   The name of the ad group

    `advertiser_id: list[int]`
    :   The unique identifier of the advertiser

    `campaign_id: list[int]`
    :   The unique identifier of the campaign

    `campaign_name: list[str]`
    :   The name of the campaign

    `create_time: list[str]`
    :   The timestamp when the ad was created

    `landing_page_url: list[str]`
    :   The URL of the landing page for the ad

    `modify_time: list[str]`
    :   The timestamp when the ad was last modified

    `operation_status: list[str]`
    :   The operational status of the ad

    `secondary_status: list[str]`
    :   The secondary status of the ad

    `video_id: list[str]`
    :   The unique identifier of the video

`AdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

`AdsListParams(*args, **kwargs)`
:   Parameters for ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

`AdsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

`AdsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAnyCondition]`
    :   The type of the None singleton.

`AdsReportsDailyAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAnyCondition]`
    :   The type of the None singleton.

`AdsReportsDailyAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`AdsReportsDailyAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: Any`
    :   The unique identifier for the ad.

    `ad_name: Any`
    :   The name of the ad.

    `ad_text: Any`
    :   The text content of the ad.

    `adgroup_id: Any`
    :   The unique identifier for the ad group.

    `adgroup_name: Any`
    :   The name of the ad group.

    `app_install: Any`
    :   Number of app installations.

    `average_video_play: Any`
    :   Average video play duration.

    `average_video_play_per_user: Any`
    :   Average video play duration per user.

    `campaign_id: Any`
    :   The unique identifier for the campaign.

    `campaign_name: Any`
    :   The name of the marketing campaign.

    `clicks: Any`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Any`
    :   Number of clicks on the music disc.

    `comments: Any`
    :   Number of comments.

    `conversion: Any`
    :   Number of conversions.

    `conversion_rate: Any`
    :   Rate of conversions.

    `cost_per_1000_reached: Any`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: Any`
    :   Cost per conversion.

    `cost_per_result: Any`
    :   Cost per result.

    `cost_per_secondary_goal_result: Any`
    :   Cost per secondary goal result.

    `cpc: Any`
    :   Cost per click.

    `cpm: Any`
    :   Cost per thousand impressions.

    `ctr: Any`
    :   Click-through rate.

    `follows: Any`
    :   Number of follows.

    `frequency: Any`
    :   Average number of times each person saw the ad.

    `impressions: Any`
    :   Number of times the ad was displayed.

    `likes: Any`
    :   Number of likes.

    `placement_type: Any`
    :   Type of ad placement.

    `profile_visits: Any`
    :   Number of profile visits.

    `reach: Any`
    :   Total number of unique users reached.

    `real_time_app_install: Any`
    :   Real-time app installations.

    `real_time_app_install_cost: Any`
    :   Cost of real-time app installations.

    `real_time_conversion: Any`
    :   Real-time conversions.

    `real_time_conversion_rate: Any`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: Any`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: Any`
    :   Real-time cost per result.

    `real_time_result: Any`
    :   Real-time results.

    `real_time_result_rate: Any`
    :   Real-time result rate.

    `result: Any`
    :   Number of results.

    `result_rate: Any`
    :   Rate of results.

    `secondary_goal_result: Any`
    :   Results for secondary goals.

    `secondary_goal_result_rate: Any`
    :   Rate of secondary goal results.

    `shares: Any`
    :   Number of shares.

    `spend: Any`
    :   Total amount of money spent.

    `stat_time_day: Any`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Any`
    :   Number of video play actions.

    `video_views_p100: Any`
    :   Number of times video was watched to 100%.

    `video_views_p25: Any`
    :   Number of times video was watched to 25%.

    `video_views_p50: Any`
    :   Number of times video was watched to 50%.

    `video_views_p75: Any`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Any`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Any`
    :   Number of times video was watched for at least 6 seconds.

`AdsReportsDailyContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`AdsReportsDailyEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdsReportsDailyFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyStringFilter`
    :   The type of the None singleton.

`AdsReportsDailyGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdsReportsDailyGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdsReportsDailyInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyInFilter`
    :   The type of the None singleton.

`AdsReportsDailyInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: list[int]`
    :   The unique identifier for the ad.

    `ad_name: list[str]`
    :   The name of the ad.

    `ad_text: list[str]`
    :   The text content of the ad.

    `adgroup_id: list[int]`
    :   The unique identifier for the ad group.

    `adgroup_name: list[str]`
    :   The name of the ad group.

    `app_install: list[float]`
    :   Number of app installations.

    `average_video_play: list[float]`
    :   Average video play duration.

    `average_video_play_per_user: list[float]`
    :   Average video play duration per user.

    `campaign_id: list[int]`
    :   The unique identifier for the campaign.

    `campaign_name: list[str]`
    :   The name of the marketing campaign.

    `clicks: list[str]`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: list[float]`
    :   Number of clicks on the music disc.

    `comments: list[float]`
    :   Number of comments.

    `conversion: list[str]`
    :   Number of conversions.

    `conversion_rate: list[str]`
    :   Rate of conversions.

    `cost_per_1000_reached: list[str]`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: list[str]`
    :   Cost per conversion.

    `cost_per_result: list[str]`
    :   Cost per result.

    `cost_per_secondary_goal_result: list[str]`
    :   Cost per secondary goal result.

    `cpc: list[str]`
    :   Cost per click.

    `cpm: list[str]`
    :   Cost per thousand impressions.

    `ctr: list[str]`
    :   Click-through rate.

    `follows: list[float]`
    :   Number of follows.

    `frequency: list[str]`
    :   Average number of times each person saw the ad.

    `impressions: list[str]`
    :   Number of times the ad was displayed.

    `likes: list[float]`
    :   Number of likes.

    `placement_type: list[str]`
    :   Type of ad placement.

    `profile_visits: list[float]`
    :   Number of profile visits.

    `reach: list[str]`
    :   Total number of unique users reached.

    `real_time_app_install: list[float]`
    :   Real-time app installations.

    `real_time_app_install_cost: list[float]`
    :   Cost of real-time app installations.

    `real_time_conversion: list[str]`
    :   Real-time conversions.

    `real_time_conversion_rate: list[str]`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: list[str]`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: list[str]`
    :   Real-time cost per result.

    `real_time_result: list[str]`
    :   Real-time results.

    `real_time_result_rate: list[str]`
    :   Real-time result rate.

    `result: list[str]`
    :   Number of results.

    `result_rate: list[str]`
    :   Rate of results.

    `secondary_goal_result: list[str]`
    :   Results for secondary goals.

    `secondary_goal_result_rate: list[str]`
    :   Rate of secondary goal results.

    `shares: list[float]`
    :   Number of shares.

    `spend: list[str]`
    :   Total amount of money spent.

    `stat_time_day: list[str]`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: list[float]`
    :   Number of video play actions.

    `video_views_p100: list[float]`
    :   Number of times video was watched to 100%.

    `video_views_p25: list[float]`
    :   Number of times video was watched to 25%.

    `video_views_p50: list[float]`
    :   Number of times video was watched to 50%.

    `video_views_p75: list[float]`
    :   Number of times video was watched to 75%.

    `video_watched_2s: list[float]`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: list[float]`
    :   Number of times video was watched for at least 6 seconds.

`AdsReportsDailyKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyStringFilter`
    :   The type of the None singleton.

`AdsReportsDailyLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyStringFilter`
    :   The type of the None singleton.

`AdsReportsDailyListParams(*args, **kwargs)`
:   Parameters for ads_reports_daily.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `data_level: str`
    :   The type of the None singleton.

    `dimensions: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `metrics: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `report_type: str`
    :   The type of the None singleton.

    `service_type: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

`AdsReportsDailyLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdsReportsDailyLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdsReportsDailyNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySearchFilter`
    :   The type of the None singleton.

`AdsReportsDailyNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAnyCondition`
    :   The type of the None singleton.

`AdsReportsDailyOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAnyCondition]`
    :   The type of the None singleton.

`AdsReportsDailySearchFilter(*args, **kwargs)`
:   Available fields for filtering ads_reports_daily search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: int | None`
    :   The unique identifier for the ad.

    `ad_name: str | None`
    :   The name of the ad.

    `ad_text: str | None`
    :   The text content of the ad.

    `adgroup_id: int | None`
    :   The unique identifier for the ad group.

    `adgroup_name: str | None`
    :   The name of the ad group.

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `campaign_id: int | None`
    :   The unique identifier for the campaign.

    `campaign_name: str | None`
    :   The name of the marketing campaign.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `conversion: str | None`
    :   Number of conversions.

    `conversion_rate: str | None`
    :   Rate of conversions.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: str | None`
    :   Cost per conversion.

    `cost_per_result: str | None`
    :   Cost per result.

    `cost_per_secondary_goal_result: str | None`
    :   Cost per secondary goal result.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `placement_type: str | None`
    :   Type of ad placement.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `real_time_conversion: str | None`
    :   Real-time conversions.

    `real_time_conversion_rate: str | None`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: str | None`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: str | None`
    :   Real-time cost per result.

    `real_time_result: str | None`
    :   Real-time results.

    `real_time_result_rate: str | None`
    :   Real-time result rate.

    `result: str | None`
    :   Number of results.

    `result_rate: str | None`
    :   Rate of results.

    `secondary_goal_result: str | None`
    :   Results for secondary goals.

    `secondary_goal_result_rate: str | None`
    :   Rate of secondary goal results.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

`AdsReportsDailySearchQuery(*args, **kwargs)`
:   Search query for ads_reports_daily entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailyAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsReportsDailySortFilter]`
    :   The type of the None singleton.

`AdsReportsDailySortFilter(*args, **kwargs)`
:   Available fields for sorting ads_reports_daily search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: Literal['asc', 'desc']`
    :   The unique identifier for the ad.

    `ad_name: Literal['asc', 'desc']`
    :   The name of the ad.

    `ad_text: Literal['asc', 'desc']`
    :   The text content of the ad.

    `adgroup_id: Literal['asc', 'desc']`
    :   The unique identifier for the ad group.

    `adgroup_name: Literal['asc', 'desc']`
    :   The name of the ad group.

    `app_install: Literal['asc', 'desc']`
    :   Number of app installations.

    `average_video_play: Literal['asc', 'desc']`
    :   Average video play duration.

    `average_video_play_per_user: Literal['asc', 'desc']`
    :   Average video play duration per user.

    `campaign_id: Literal['asc', 'desc']`
    :   The unique identifier for the campaign.

    `campaign_name: Literal['asc', 'desc']`
    :   The name of the marketing campaign.

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Literal['asc', 'desc']`
    :   Number of clicks on the music disc.

    `comments: Literal['asc', 'desc']`
    :   Number of comments.

    `conversion: Literal['asc', 'desc']`
    :   Number of conversions.

    `conversion_rate: Literal['asc', 'desc']`
    :   Rate of conversions.

    `cost_per_1000_reached: Literal['asc', 'desc']`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: Literal['asc', 'desc']`
    :   Cost per conversion.

    `cost_per_result: Literal['asc', 'desc']`
    :   Cost per result.

    `cost_per_secondary_goal_result: Literal['asc', 'desc']`
    :   Cost per secondary goal result.

    `cpc: Literal['asc', 'desc']`
    :   Cost per click.

    `cpm: Literal['asc', 'desc']`
    :   Cost per thousand impressions.

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate.

    `follows: Literal['asc', 'desc']`
    :   Number of follows.

    `frequency: Literal['asc', 'desc']`
    :   Average number of times each person saw the ad.

    `impressions: Literal['asc', 'desc']`
    :   Number of times the ad was displayed.

    `likes: Literal['asc', 'desc']`
    :   Number of likes.

    `placement_type: Literal['asc', 'desc']`
    :   Type of ad placement.

    `profile_visits: Literal['asc', 'desc']`
    :   Number of profile visits.

    `reach: Literal['asc', 'desc']`
    :   Total number of unique users reached.

    `real_time_app_install: Literal['asc', 'desc']`
    :   Real-time app installations.

    `real_time_app_install_cost: Literal['asc', 'desc']`
    :   Cost of real-time app installations.

    `real_time_conversion: Literal['asc', 'desc']`
    :   Real-time conversions.

    `real_time_conversion_rate: Literal['asc', 'desc']`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: Literal['asc', 'desc']`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: Literal['asc', 'desc']`
    :   Real-time cost per result.

    `real_time_result: Literal['asc', 'desc']`
    :   Real-time results.

    `real_time_result_rate: Literal['asc', 'desc']`
    :   Real-time result rate.

    `result: Literal['asc', 'desc']`
    :   Number of results.

    `result_rate: Literal['asc', 'desc']`
    :   Rate of results.

    `secondary_goal_result: Literal['asc', 'desc']`
    :   Results for secondary goals.

    `secondary_goal_result_rate: Literal['asc', 'desc']`
    :   Rate of secondary goal results.

    `shares: Literal['asc', 'desc']`
    :   Number of shares.

    `spend: Literal['asc', 'desc']`
    :   Total amount of money spent.

    `stat_time_day: Literal['asc', 'desc']`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Literal['asc', 'desc']`
    :   Number of video play actions.

    `video_views_p100: Literal['asc', 'desc']`
    :   Number of times video was watched to 100%.

    `video_views_p25: Literal['asc', 'desc']`
    :   Number of times video was watched to 25%.

    `video_views_p50: Literal['asc', 'desc']`
    :   Number of times video was watched to 50%.

    `video_views_p75: Literal['asc', 'desc']`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 6 seconds.

`AdsReportsDailyStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_id: str`
    :   The unique identifier for the ad.

    `ad_name: str`
    :   The name of the ad.

    `ad_text: str`
    :   The text content of the ad.

    `adgroup_id: str`
    :   The unique identifier for the ad group.

    `adgroup_name: str`
    :   The name of the ad group.

    `app_install: str`
    :   Number of app installations.

    `average_video_play: str`
    :   Average video play duration.

    `average_video_play_per_user: str`
    :   Average video play duration per user.

    `campaign_id: str`
    :   The unique identifier for the campaign.

    `campaign_name: str`
    :   The name of the marketing campaign.

    `clicks: str`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: str`
    :   Number of clicks on the music disc.

    `comments: str`
    :   Number of comments.

    `conversion: str`
    :   Number of conversions.

    `conversion_rate: str`
    :   Rate of conversions.

    `cost_per_1000_reached: str`
    :   Cost per 1000 unique users reached.

    `cost_per_conversion: str`
    :   Cost per conversion.

    `cost_per_result: str`
    :   Cost per result.

    `cost_per_secondary_goal_result: str`
    :   Cost per secondary goal result.

    `cpc: str`
    :   Cost per click.

    `cpm: str`
    :   Cost per thousand impressions.

    `ctr: str`
    :   Click-through rate.

    `follows: str`
    :   Number of follows.

    `frequency: str`
    :   Average number of times each person saw the ad.

    `impressions: str`
    :   Number of times the ad was displayed.

    `likes: str`
    :   Number of likes.

    `placement_type: str`
    :   Type of ad placement.

    `profile_visits: str`
    :   Number of profile visits.

    `reach: str`
    :   Total number of unique users reached.

    `real_time_app_install: str`
    :   Real-time app installations.

    `real_time_app_install_cost: str`
    :   Cost of real-time app installations.

    `real_time_conversion: str`
    :   Real-time conversions.

    `real_time_conversion_rate: str`
    :   Real-time conversion rate.

    `real_time_cost_per_conversion: str`
    :   Real-time cost per conversion.

    `real_time_cost_per_result: str`
    :   Real-time cost per result.

    `real_time_result: str`
    :   Real-time results.

    `real_time_result_rate: str`
    :   Real-time result rate.

    `result: str`
    :   Number of results.

    `result_rate: str`
    :   Rate of results.

    `secondary_goal_result: str`
    :   Results for secondary goals.

    `secondary_goal_result_rate: str`
    :   Rate of secondary goal results.

    `shares: str`
    :   Number of shares.

    `spend: str`
    :   Total amount of money spent.

    `stat_time_day: str`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: str`
    :   Number of video play actions.

    `video_views_p100: str`
    :   Number of times video was watched to 100%.

    `video_views_p25: str`
    :   Number of times video was watched to 25%.

    `video_views_p50: str`
    :   Number of times video was watched to 50%.

    `video_views_p75: str`
    :   Number of times video was watched to 75%.

    `video_watched_2s: str`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: str`
    :   Number of times video was watched for at least 6 seconds.

`AdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_format: str | None`
    :   The format of the ad

    `ad_id: int | None`
    :   The unique identifier of the ad

    `ad_name: str | None`
    :   The name of the ad

    `ad_text: str | None`
    :   The text content of the ad

    `adgroup_id: int | None`
    :   The unique identifier of the ad group

    `adgroup_name: str | None`
    :   The name of the ad group

    `advertiser_id: int | None`
    :   The unique identifier of the advertiser

    `campaign_id: int | None`
    :   The unique identifier of the campaign

    `campaign_name: str | None`
    :   The name of the campaign

    `create_time: str | None`
    :   The timestamp when the ad was created

    `landing_page_url: str | None`
    :   The URL of the landing page for the ad

    `modify_time: str | None`
    :   The timestamp when the ad was last modified

    `operation_status: str | None`
    :   The operational status of the ad

    `secondary_status: str | None`
    :   The secondary status of the ad

    `video_id: str | None`
    :   The unique identifier of the video

`AdsSearchQuery(*args, **kwargs)`
:   Search query for ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdsSortFilter]`
    :   The type of the None singleton.

`AdsSortFilter(*args, **kwargs)`
:   Available fields for sorting ads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_format: Literal['asc', 'desc']`
    :   The format of the ad

    `ad_id: Literal['asc', 'desc']`
    :   The unique identifier of the ad

    `ad_name: Literal['asc', 'desc']`
    :   The name of the ad

    `ad_text: Literal['asc', 'desc']`
    :   The text content of the ad

    `adgroup_id: Literal['asc', 'desc']`
    :   The unique identifier of the ad group

    `adgroup_name: Literal['asc', 'desc']`
    :   The name of the ad group

    `advertiser_id: Literal['asc', 'desc']`
    :   The unique identifier of the advertiser

    `campaign_id: Literal['asc', 'desc']`
    :   The unique identifier of the campaign

    `campaign_name: Literal['asc', 'desc']`
    :   The name of the campaign

    `create_time: Literal['asc', 'desc']`
    :   The timestamp when the ad was created

    `landing_page_url: Literal['asc', 'desc']`
    :   The URL of the landing page for the ad

    `modify_time: Literal['asc', 'desc']`
    :   The timestamp when the ad was last modified

    `operation_status: Literal['asc', 'desc']`
    :   The operational status of the ad

    `secondary_status: Literal['asc', 'desc']`
    :   The secondary status of the ad

    `video_id: Literal['asc', 'desc']`
    :   The unique identifier of the video

`AdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_format: str`
    :   The format of the ad

    `ad_id: str`
    :   The unique identifier of the ad

    `ad_name: str`
    :   The name of the ad

    `ad_text: str`
    :   The text content of the ad

    `adgroup_id: str`
    :   The unique identifier of the ad group

    `adgroup_name: str`
    :   The name of the ad group

    `advertiser_id: str`
    :   The unique identifier of the advertiser

    `campaign_id: str`
    :   The unique identifier of the campaign

    `campaign_name: str`
    :   The name of the campaign

    `create_time: str`
    :   The timestamp when the ad was created

    `landing_page_url: str`
    :   The URL of the landing page for the ad

    `modify_time: str`
    :   The timestamp when the ad was last modified

    `operation_status: str`
    :   The operational status of the ad

    `secondary_status: str`
    :   The secondary status of the ad

    `video_id: str`
    :   The unique identifier of the video

`AdvertisersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAnyCondition]`
    :   The type of the None singleton.

`AdvertisersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAnyValueFilter`
    :   The type of the None singleton.

`AdvertisersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: Any`
    :   The physical address of the advertiser.

    `advertiser_account_type: Any`
    :   The type of advertiser's account (e.g., individual, business).

    `advertiser_id: Any`
    :   Unique identifier for the advertiser.

    `balance: Any`
    :   The current balance in the advertiser's account.

    `brand: Any`
    :   The brand name associated with the advertiser.

    `cellphone_number: Any`
    :   The cellphone number of the advertiser.

    `company: Any`
    :   The name of the company associated with the advertiser.

    `contacter: Any`
    :   The contact person for the advertiser.

    `country: Any`
    :   The country where the advertiser is located.

    `create_time: Any`
    :   The timestamp when the advertiser account was created.

    `currency: Any`
    :   The currency used for transactions in the account.

    `description: Any`
    :   A brief description or bio of the advertiser or company.

    `display_timezone: Any`
    :   The timezone for display purposes.

    `email: Any`
    :   The email address associated with the advertiser.

    `industry: Any`
    :   The industry or sector the advertiser operates in.

    `language: Any`
    :   The preferred language of communication for the advertiser.

    `license_city: Any`
    :   The city where the advertiser's license is registered.

    `license_no: Any`
    :   The license number of the advertiser.

    `license_province: Any`
    :   The province or state where the advertiser's license is registered.

    `license_url: Any`
    :   The URL link to the advertiser's license documentation.

    `name: Any`
    :   The name of the advertiser or company.

    `promotion_area: Any`
    :   The specific area or region where the advertiser focuses promotion.

    `promotion_center_city: Any`
    :   The city at the center of the advertiser's promotion activities.

    `promotion_center_province: Any`
    :   The province or state at the center of the advertiser's promotion activities.

    `rejection_reason: Any`
    :   Reason for any advertisement rejection by the platform.

    `role: Any`
    :   The role or position of the advertiser within the company.

    `status: Any`
    :   The current status of the advertiser's account.

    `telephone_number: Any`
    :   The telephone number of the advertiser.

    `timezone: Any`
    :   The timezone setting for the advertiser's activities.

`AdvertisersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAnyValueFilter`
    :   The type of the None singleton.

`AdvertisersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSearchFilter`
    :   The type of the None singleton.

`AdvertisersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersStringFilter`
    :   The type of the None singleton.

`AdvertisersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSearchFilter`
    :   The type of the None singleton.

`AdvertisersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSearchFilter`
    :   The type of the None singleton.

`AdvertisersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersInFilter`
    :   The type of the None singleton.

`AdvertisersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: list[str]`
    :   The physical address of the advertiser.

    `advertiser_account_type: list[str]`
    :   The type of advertiser's account (e.g., individual, business).

    `advertiser_id: list[int]`
    :   Unique identifier for the advertiser.

    `balance: list[float]`
    :   The current balance in the advertiser's account.

    `brand: list[str]`
    :   The brand name associated with the advertiser.

    `cellphone_number: list[str]`
    :   The cellphone number of the advertiser.

    `company: list[str]`
    :   The name of the company associated with the advertiser.

    `contacter: list[str]`
    :   The contact person for the advertiser.

    `country: list[str]`
    :   The country where the advertiser is located.

    `create_time: list[int]`
    :   The timestamp when the advertiser account was created.

    `currency: list[str]`
    :   The currency used for transactions in the account.

    `description: list[str]`
    :   A brief description or bio of the advertiser or company.

    `display_timezone: list[str]`
    :   The timezone for display purposes.

    `email: list[str]`
    :   The email address associated with the advertiser.

    `industry: list[str]`
    :   The industry or sector the advertiser operates in.

    `language: list[str]`
    :   The preferred language of communication for the advertiser.

    `license_city: list[str]`
    :   The city where the advertiser's license is registered.

    `license_no: list[str]`
    :   The license number of the advertiser.

    `license_province: list[str]`
    :   The province or state where the advertiser's license is registered.

    `license_url: list[str]`
    :   The URL link to the advertiser's license documentation.

    `name: list[str]`
    :   The name of the advertiser or company.

    `promotion_area: list[str]`
    :   The specific area or region where the advertiser focuses promotion.

    `promotion_center_city: list[str]`
    :   The city at the center of the advertiser's promotion activities.

    `promotion_center_province: list[str]`
    :   The province or state at the center of the advertiser's promotion activities.

    `rejection_reason: list[str]`
    :   Reason for any advertisement rejection by the platform.

    `role: list[str]`
    :   The role or position of the advertiser within the company.

    `status: list[str]`
    :   The current status of the advertiser's account.

    `telephone_number: list[str]`
    :   The telephone number of the advertiser.

    `timezone: list[str]`
    :   The timezone setting for the advertiser's activities.

`AdvertisersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersStringFilter`
    :   The type of the None singleton.

`AdvertisersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersStringFilter`
    :   The type of the None singleton.

`AdvertisersListParams(*args, **kwargs)`
:   Parameters for advertisers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_ids: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AdvertisersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSearchFilter`
    :   The type of the None singleton.

`AdvertisersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSearchFilter`
    :   The type of the None singleton.

`AdvertisersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSearchFilter`
    :   The type of the None singleton.

`AdvertisersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAnyCondition`
    :   The type of the None singleton.

`AdvertisersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAnyCondition]`
    :   The type of the None singleton.

`AdvertisersReportsDailyAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAnyCondition]`
    :   The type of the None singleton.

`AdvertisersReportsDailyAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: Any`
    :   The unique identifier for the advertiser.

    `app_install: Any`
    :   Number of app installations.

    `average_video_play: Any`
    :   Average video play duration.

    `average_video_play_per_user: Any`
    :   Average video play duration per user.

    `cash_spend: Any`
    :   The amount of money spent in cash.

    `clicks: Any`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Any`
    :   Number of clicks on the music disc.

    `comments: Any`
    :   Number of comments.

    `cost_per_1000_reached: Any`
    :   Cost per 1000 unique users reached.

    `cpc: Any`
    :   Cost per click.

    `cpm: Any`
    :   Cost per thousand impressions.

    `ctr: Any`
    :   Click-through rate.

    `follows: Any`
    :   Number of follows.

    `frequency: Any`
    :   Average number of times each person saw the ad.

    `impressions: Any`
    :   Number of times the ad was displayed.

    `likes: Any`
    :   Number of likes.

    `profile_visits: Any`
    :   Number of profile visits.

    `reach: Any`
    :   Total number of unique users reached.

    `real_time_app_install: Any`
    :   Real-time app installations.

    `real_time_app_install_cost: Any`
    :   Cost of real-time app installations.

    `shares: Any`
    :   Number of shares.

    `spend: Any`
    :   Total amount of money spent.

    `stat_time_day: Any`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Any`
    :   Number of video play actions.

    `video_views_p100: Any`
    :   Number of times video was watched to 100%.

    `video_views_p25: Any`
    :   Number of times video was watched to 25%.

    `video_views_p50: Any`
    :   Number of times video was watched to 50%.

    `video_views_p75: Any`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Any`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Any`
    :   Number of times video was watched for at least 6 seconds.

    `voucher_spend: Any`
    :   Amount spent using vouchers.

`AdvertisersReportsDailyContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySearchFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyStringFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySearchFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySearchFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyInFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: list[int]`
    :   The unique identifier for the advertiser.

    `app_install: list[float]`
    :   Number of app installations.

    `average_video_play: list[float]`
    :   Average video play duration.

    `average_video_play_per_user: list[float]`
    :   Average video play duration per user.

    `cash_spend: list[str]`
    :   The amount of money spent in cash.

    `clicks: list[str]`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: list[float]`
    :   Number of clicks on the music disc.

    `comments: list[float]`
    :   Number of comments.

    `cost_per_1000_reached: list[str]`
    :   Cost per 1000 unique users reached.

    `cpc: list[str]`
    :   Cost per click.

    `cpm: list[str]`
    :   Cost per thousand impressions.

    `ctr: list[str]`
    :   Click-through rate.

    `follows: list[float]`
    :   Number of follows.

    `frequency: list[str]`
    :   Average number of times each person saw the ad.

    `impressions: list[str]`
    :   Number of times the ad was displayed.

    `likes: list[float]`
    :   Number of likes.

    `profile_visits: list[float]`
    :   Number of profile visits.

    `reach: list[str]`
    :   Total number of unique users reached.

    `real_time_app_install: list[float]`
    :   Real-time app installations.

    `real_time_app_install_cost: list[float]`
    :   Cost of real-time app installations.

    `shares: list[float]`
    :   Number of shares.

    `spend: list[str]`
    :   Total amount of money spent.

    `stat_time_day: list[str]`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: list[float]`
    :   Number of video play actions.

    `video_views_p100: list[float]`
    :   Number of times video was watched to 100%.

    `video_views_p25: list[float]`
    :   Number of times video was watched to 25%.

    `video_views_p50: list[float]`
    :   Number of times video was watched to 50%.

    `video_views_p75: list[float]`
    :   Number of times video was watched to 75%.

    `video_watched_2s: list[float]`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: list[float]`
    :   Number of times video was watched for at least 6 seconds.

    `voucher_spend: list[str]`
    :   Amount spent using vouchers.

`AdvertisersReportsDailyKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyStringFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyStringFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyListParams(*args, **kwargs)`
:   Parameters for advertisers_reports_daily.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `data_level: str`
    :   The type of the None singleton.

    `dimensions: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `metrics: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `report_type: str`
    :   The type of the None singleton.

    `service_type: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

`AdvertisersReportsDailyLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySearchFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySearchFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySearchFilter`
    :   The type of the None singleton.

`AdvertisersReportsDailyNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAnyCondition`
    :   The type of the None singleton.

`AdvertisersReportsDailyOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAnyCondition]`
    :   The type of the None singleton.

`AdvertisersReportsDailySearchFilter(*args, **kwargs)`
:   Available fields for filtering advertisers_reports_daily search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: int | None`
    :   The unique identifier for the advertiser.

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `cash_spend: str | None`
    :   The amount of money spent in cash.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

    `voucher_spend: str | None`
    :   Amount spent using vouchers.

`AdvertisersReportsDailySearchQuery(*args, **kwargs)`
:   Search query for advertisers_reports_daily entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailyAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersReportsDailySortFilter]`
    :   The type of the None singleton.

`AdvertisersReportsDailySortFilter(*args, **kwargs)`
:   Available fields for sorting advertisers_reports_daily search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: Literal['asc', 'desc']`
    :   The unique identifier for the advertiser.

    `app_install: Literal['asc', 'desc']`
    :   Number of app installations.

    `average_video_play: Literal['asc', 'desc']`
    :   Average video play duration.

    `average_video_play_per_user: Literal['asc', 'desc']`
    :   Average video play duration per user.

    `cash_spend: Literal['asc', 'desc']`
    :   The amount of money spent in cash.

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Literal['asc', 'desc']`
    :   Number of clicks on the music disc.

    `comments: Literal['asc', 'desc']`
    :   Number of comments.

    `cost_per_1000_reached: Literal['asc', 'desc']`
    :   Cost per 1000 unique users reached.

    `cpc: Literal['asc', 'desc']`
    :   Cost per click.

    `cpm: Literal['asc', 'desc']`
    :   Cost per thousand impressions.

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate.

    `follows: Literal['asc', 'desc']`
    :   Number of follows.

    `frequency: Literal['asc', 'desc']`
    :   Average number of times each person saw the ad.

    `impressions: Literal['asc', 'desc']`
    :   Number of times the ad was displayed.

    `likes: Literal['asc', 'desc']`
    :   Number of likes.

    `profile_visits: Literal['asc', 'desc']`
    :   Number of profile visits.

    `reach: Literal['asc', 'desc']`
    :   Total number of unique users reached.

    `real_time_app_install: Literal['asc', 'desc']`
    :   Real-time app installations.

    `real_time_app_install_cost: Literal['asc', 'desc']`
    :   Cost of real-time app installations.

    `shares: Literal['asc', 'desc']`
    :   Number of shares.

    `spend: Literal['asc', 'desc']`
    :   Total amount of money spent.

    `stat_time_day: Literal['asc', 'desc']`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Literal['asc', 'desc']`
    :   Number of video play actions.

    `video_views_p100: Literal['asc', 'desc']`
    :   Number of times video was watched to 100%.

    `video_views_p25: Literal['asc', 'desc']`
    :   Number of times video was watched to 25%.

    `video_views_p50: Literal['asc', 'desc']`
    :   Number of times video was watched to 50%.

    `video_views_p75: Literal['asc', 'desc']`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 6 seconds.

    `voucher_spend: Literal['asc', 'desc']`
    :   Amount spent using vouchers.

`AdvertisersReportsDailyStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The unique identifier for the advertiser.

    `app_install: str`
    :   Number of app installations.

    `average_video_play: str`
    :   Average video play duration.

    `average_video_play_per_user: str`
    :   Average video play duration per user.

    `cash_spend: str`
    :   The amount of money spent in cash.

    `clicks: str`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: str`
    :   Number of clicks on the music disc.

    `comments: str`
    :   Number of comments.

    `cost_per_1000_reached: str`
    :   Cost per 1000 unique users reached.

    `cpc: str`
    :   Cost per click.

    `cpm: str`
    :   Cost per thousand impressions.

    `ctr: str`
    :   Click-through rate.

    `follows: str`
    :   Number of follows.

    `frequency: str`
    :   Average number of times each person saw the ad.

    `impressions: str`
    :   Number of times the ad was displayed.

    `likes: str`
    :   Number of likes.

    `profile_visits: str`
    :   Number of profile visits.

    `reach: str`
    :   Total number of unique users reached.

    `real_time_app_install: str`
    :   Real-time app installations.

    `real_time_app_install_cost: str`
    :   Cost of real-time app installations.

    `shares: str`
    :   Number of shares.

    `spend: str`
    :   Total amount of money spent.

    `stat_time_day: str`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: str`
    :   Number of video play actions.

    `video_views_p100: str`
    :   Number of times video was watched to 100%.

    `video_views_p25: str`
    :   Number of times video was watched to 25%.

    `video_views_p50: str`
    :   Number of times video was watched to 50%.

    `video_views_p75: str`
    :   Number of times video was watched to 75%.

    `video_watched_2s: str`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: str`
    :   Number of times video was watched for at least 6 seconds.

    `voucher_spend: str`
    :   Amount spent using vouchers.

`AdvertisersSearchFilter(*args, **kwargs)`
:   Available fields for filtering advertisers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: str | None`
    :   The physical address of the advertiser.

    `advertiser_account_type: str | None`
    :   The type of advertiser's account (e.g., individual, business).

    `advertiser_id: int | None`
    :   Unique identifier for the advertiser.

    `balance: float | None`
    :   The current balance in the advertiser's account.

    `brand: str | None`
    :   The brand name associated with the advertiser.

    `cellphone_number: str | None`
    :   The cellphone number of the advertiser.

    `company: str | None`
    :   The name of the company associated with the advertiser.

    `contacter: str | None`
    :   The contact person for the advertiser.

    `country: str | None`
    :   The country where the advertiser is located.

    `create_time: int | None`
    :   The timestamp when the advertiser account was created.

    `currency: str | None`
    :   The currency used for transactions in the account.

    `description: str | None`
    :   A brief description or bio of the advertiser or company.

    `display_timezone: str | None`
    :   The timezone for display purposes.

    `email: str | None`
    :   The email address associated with the advertiser.

    `industry: str | None`
    :   The industry or sector the advertiser operates in.

    `language: str | None`
    :   The preferred language of communication for the advertiser.

    `license_city: str | None`
    :   The city where the advertiser's license is registered.

    `license_no: str | None`
    :   The license number of the advertiser.

    `license_province: str | None`
    :   The province or state where the advertiser's license is registered.

    `license_url: str | None`
    :   The URL link to the advertiser's license documentation.

    `name: str | None`
    :   The name of the advertiser or company.

    `promotion_area: str | None`
    :   The specific area or region where the advertiser focuses promotion.

    `promotion_center_city: str | None`
    :   The city at the center of the advertiser's promotion activities.

    `promotion_center_province: str | None`
    :   The province or state at the center of the advertiser's promotion activities.

    `rejection_reason: str | None`
    :   Reason for any advertisement rejection by the platform.

    `role: str | None`
    :   The role or position of the advertiser within the company.

    `status: str | None`
    :   The current status of the advertiser's account.

    `telephone_number: str | None`
    :   The telephone number of the advertiser.

    `timezone: str | None`
    :   The timezone setting for the advertiser's activities.

`AdvertisersSearchQuery(*args, **kwargs)`
:   Search query for advertisers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AdvertisersSortFilter]`
    :   The type of the None singleton.

`AdvertisersSortFilter(*args, **kwargs)`
:   Available fields for sorting advertisers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: Literal['asc', 'desc']`
    :   The physical address of the advertiser.

    `advertiser_account_type: Literal['asc', 'desc']`
    :   The type of advertiser's account (e.g., individual, business).

    `advertiser_id: Literal['asc', 'desc']`
    :   Unique identifier for the advertiser.

    `balance: Literal['asc', 'desc']`
    :   The current balance in the advertiser's account.

    `brand: Literal['asc', 'desc']`
    :   The brand name associated with the advertiser.

    `cellphone_number: Literal['asc', 'desc']`
    :   The cellphone number of the advertiser.

    `company: Literal['asc', 'desc']`
    :   The name of the company associated with the advertiser.

    `contacter: Literal['asc', 'desc']`
    :   The contact person for the advertiser.

    `country: Literal['asc', 'desc']`
    :   The country where the advertiser is located.

    `create_time: Literal['asc', 'desc']`
    :   The timestamp when the advertiser account was created.

    `currency: Literal['asc', 'desc']`
    :   The currency used for transactions in the account.

    `description: Literal['asc', 'desc']`
    :   A brief description or bio of the advertiser or company.

    `display_timezone: Literal['asc', 'desc']`
    :   The timezone for display purposes.

    `email: Literal['asc', 'desc']`
    :   The email address associated with the advertiser.

    `industry: Literal['asc', 'desc']`
    :   The industry or sector the advertiser operates in.

    `language: Literal['asc', 'desc']`
    :   The preferred language of communication for the advertiser.

    `license_city: Literal['asc', 'desc']`
    :   The city where the advertiser's license is registered.

    `license_no: Literal['asc', 'desc']`
    :   The license number of the advertiser.

    `license_province: Literal['asc', 'desc']`
    :   The province or state where the advertiser's license is registered.

    `license_url: Literal['asc', 'desc']`
    :   The URL link to the advertiser's license documentation.

    `name: Literal['asc', 'desc']`
    :   The name of the advertiser or company.

    `promotion_area: Literal['asc', 'desc']`
    :   The specific area or region where the advertiser focuses promotion.

    `promotion_center_city: Literal['asc', 'desc']`
    :   The city at the center of the advertiser's promotion activities.

    `promotion_center_province: Literal['asc', 'desc']`
    :   The province or state at the center of the advertiser's promotion activities.

    `rejection_reason: Literal['asc', 'desc']`
    :   Reason for any advertisement rejection by the platform.

    `role: Literal['asc', 'desc']`
    :   The role or position of the advertiser within the company.

    `status: Literal['asc', 'desc']`
    :   The current status of the advertiser's account.

    `telephone_number: Literal['asc', 'desc']`
    :   The telephone number of the advertiser.

    `timezone: Literal['asc', 'desc']`
    :   The timezone setting for the advertiser's activities.

`AdvertisersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: str`
    :   The physical address of the advertiser.

    `advertiser_account_type: str`
    :   The type of advertiser's account (e.g., individual, business).

    `advertiser_id: str`
    :   Unique identifier for the advertiser.

    `balance: str`
    :   The current balance in the advertiser's account.

    `brand: str`
    :   The brand name associated with the advertiser.

    `cellphone_number: str`
    :   The cellphone number of the advertiser.

    `company: str`
    :   The name of the company associated with the advertiser.

    `contacter: str`
    :   The contact person for the advertiser.

    `country: str`
    :   The country where the advertiser is located.

    `create_time: str`
    :   The timestamp when the advertiser account was created.

    `currency: str`
    :   The currency used for transactions in the account.

    `description: str`
    :   A brief description or bio of the advertiser or company.

    `display_timezone: str`
    :   The timezone for display purposes.

    `email: str`
    :   The email address associated with the advertiser.

    `industry: str`
    :   The industry or sector the advertiser operates in.

    `language: str`
    :   The preferred language of communication for the advertiser.

    `license_city: str`
    :   The city where the advertiser's license is registered.

    `license_no: str`
    :   The license number of the advertiser.

    `license_province: str`
    :   The province or state where the advertiser's license is registered.

    `license_url: str`
    :   The URL link to the advertiser's license documentation.

    `name: str`
    :   The name of the advertiser or company.

    `promotion_area: str`
    :   The specific area or region where the advertiser focuses promotion.

    `promotion_center_city: str`
    :   The city at the center of the advertiser's promotion activities.

    `promotion_center_province: str`
    :   The province or state at the center of the advertiser's promotion activities.

    `rejection_reason: str`
    :   Reason for any advertisement rejection by the platform.

    `role: str`
    :   The role or position of the advertiser within the company.

    `status: str`
    :   The current status of the advertiser's account.

    `telephone_number: str`
    :   The telephone number of the advertiser.

    `timezone: str`
    :   The timezone setting for the advertiser's activities.

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

`AudiencesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAnyCondition]`
    :   The type of the None singleton.

`AudiencesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAnyValueFilter`
    :   The type of the None singleton.

`AudiencesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `audience_id: Any`
    :   Unique identifier for the audience

    `audience_type: Any`
    :   Type of audience

    `cover_num: Any`
    :   Number of audience members covered

    `create_time: Any`
    :   Timestamp indicating when the audience was created

    `is_valid: Any`
    :   Flag indicating if the audience data is valid

    `name: Any`
    :   Name of the audience

    `shared: Any`
    :   Flag indicating if the audience is shared

`AudiencesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAnyValueFilter`
    :   The type of the None singleton.

`AudiencesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesStringFilter`
    :   The type of the None singleton.

`AudiencesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesInFilter`
    :   The type of the None singleton.

`AudiencesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `audience_id: list[str]`
    :   Unique identifier for the audience

    `audience_type: list[str]`
    :   Type of audience

    `cover_num: list[int]`
    :   Number of audience members covered

    `create_time: list[str]`
    :   Timestamp indicating when the audience was created

    `is_valid: list[bool]`
    :   Flag indicating if the audience data is valid

    `name: list[str]`
    :   Name of the audience

    `shared: list[bool]`
    :   Flag indicating if the audience is shared

`AudiencesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesStringFilter`
    :   The type of the None singleton.

`AudiencesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesStringFilter`
    :   The type of the None singleton.

`AudiencesListParams(*args, **kwargs)`
:   Parameters for audiences.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`AudiencesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSearchFilter`
    :   The type of the None singleton.

`AudiencesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAnyCondition`
    :   The type of the None singleton.

`AudiencesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAnyCondition]`
    :   The type of the None singleton.

`AudiencesSearchFilter(*args, **kwargs)`
:   Available fields for filtering audiences search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `audience_id: str | None`
    :   Unique identifier for the audience

    `audience_type: str | None`
    :   Type of audience

    `cover_num: int | None`
    :   Number of audience members covered

    `create_time: str | None`
    :   Timestamp indicating when the audience was created

    `is_valid: bool | None`
    :   Flag indicating if the audience data is valid

    `name: str | None`
    :   Name of the audience

    `shared: bool | None`
    :   Flag indicating if the audience is shared

`AudiencesSearchQuery(*args, **kwargs)`
:   Search query for audiences entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.AudiencesSortFilter]`
    :   The type of the None singleton.

`AudiencesSortFilter(*args, **kwargs)`
:   Available fields for sorting audiences search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `audience_id: Literal['asc', 'desc']`
    :   Unique identifier for the audience

    `audience_type: Literal['asc', 'desc']`
    :   Type of audience

    `cover_num: Literal['asc', 'desc']`
    :   Number of audience members covered

    `create_time: Literal['asc', 'desc']`
    :   Timestamp indicating when the audience was created

    `is_valid: Literal['asc', 'desc']`
    :   Flag indicating if the audience data is valid

    `name: Literal['asc', 'desc']`
    :   Name of the audience

    `shared: Literal['asc', 'desc']`
    :   Flag indicating if the audience is shared

`AudiencesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `audience_id: str`
    :   Unique identifier for the audience

    `audience_type: str`
    :   Type of audience

    `cover_num: str`
    :   Number of audience members covered

    `create_time: str`
    :   Timestamp indicating when the audience was created

    `is_valid: str`
    :   Flag indicating if the audience data is valid

    `name: str`
    :   Name of the audience

    `shared: str`
    :   Flag indicating if the audience is shared

`CampaignsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: Any`
    :   The unique identifier of the advertiser associated with the campaign

    `app_promotion_type: Any`
    :   Type of app promotion being used in the campaign

    `bid_type: Any`
    :   Type of bid strategy being used in the campaign

    `budget: Any`
    :   Total budget allocated for the campaign

    `budget_mode: Any`
    :   Mode in which the budget is being managed (e.g., daily, lifetime)

    `budget_optimize_on: Any`
    :   The metric or event that the budget optimization is based on

    `campaign_id: Any`
    :   The unique identifier of the campaign

    `campaign_name: Any`
    :   Name of the campaign for easy identification

    `campaign_type: Any`
    :   Type of campaign (e.g., awareness, conversion)

    `create_time: Any`
    :   Timestamp when the campaign was created

    `deep_bid_type: Any`
    :   Advanced bid type used for campaign optimization

    `is_new_structure: Any`
    :   Flag indicating if the campaign utilizes a new campaign structure

    `is_search_campaign: Any`
    :   Flag indicating if the campaign is a search campaign

    `is_smart_performance_campaign: Any`
    :   Flag indicating if the campaign uses smart performance optimization

    `modify_time: Any`
    :   Timestamp when the campaign was last modified

    `objective: Any`
    :   The objective or goal of the campaign

    `objective_type: Any`
    :   Type of objective selected for the campaign

    `operation_status: Any`
    :   Current operational status of the campaign

    `optimization_goal: Any`
    :   Specific goal to be optimized for in the campaign

    `rf_campaign_type: Any`
    :   Type of RF (reach and frequency) campaign being run

    `roas_bid: Any`
    :   Return on ad spend goal set for the campaign

    `secondary_status: Any`
    :   Additional status information of the campaign

    `split_test_variable: Any`
    :   Variable being tested in a split test campaign

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsInFilter`
    :   The type of the None singleton.

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: list[int]`
    :   The unique identifier of the advertiser associated with the campaign

    `app_promotion_type: list[str]`
    :   Type of app promotion being used in the campaign

    `bid_type: list[str]`
    :   Type of bid strategy being used in the campaign

    `budget: list[float]`
    :   Total budget allocated for the campaign

    `budget_mode: list[str]`
    :   Mode in which the budget is being managed (e.g., daily, lifetime)

    `budget_optimize_on: list[bool]`
    :   The metric or event that the budget optimization is based on

    `campaign_id: list[int]`
    :   The unique identifier of the campaign

    `campaign_name: list[str]`
    :   Name of the campaign for easy identification

    `campaign_type: list[str]`
    :   Type of campaign (e.g., awareness, conversion)

    `create_time: list[str]`
    :   Timestamp when the campaign was created

    `deep_bid_type: list[str]`
    :   Advanced bid type used for campaign optimization

    `is_new_structure: list[bool]`
    :   Flag indicating if the campaign utilizes a new campaign structure

    `is_search_campaign: list[bool]`
    :   Flag indicating if the campaign is a search campaign

    `is_smart_performance_campaign: list[bool]`
    :   Flag indicating if the campaign uses smart performance optimization

    `modify_time: list[str]`
    :   Timestamp when the campaign was last modified

    `objective: list[str]`
    :   The objective or goal of the campaign

    `objective_type: list[str]`
    :   Type of objective selected for the campaign

    `operation_status: list[str]`
    :   Current operational status of the campaign

    `optimization_goal: list[str]`
    :   Specific goal to be optimized for in the campaign

    `rf_campaign_type: list[str]`
    :   Type of RF (reach and frequency) campaign being run

    `roas_bid: list[float]`
    :   Return on ad spend goal set for the campaign

    `secondary_status: list[str]`
    :   Additional status information of the campaign

    `split_test_variable: list[str]`
    :   Variable being tested in a split test campaign

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAnyCondition`
    :   The type of the None singleton.

`CampaignsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

`CampaignsReportsDailyAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAnyCondition]`
    :   The type of the None singleton.

`CampaignsReportsDailyAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_install: Any`
    :   Number of app installations.

    `average_video_play: Any`
    :   Average video play duration.

    `average_video_play_per_user: Any`
    :   Average video play duration per user.

    `campaign_id: Any`
    :   The unique identifier for the campaign.

    `campaign_name: Any`
    :   The name of the marketing campaign.

    `clicks: Any`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Any`
    :   Number of clicks on the music disc.

    `comments: Any`
    :   Number of comments.

    `cost_per_1000_reached: Any`
    :   Cost per 1000 unique users reached.

    `cpc: Any`
    :   Cost per click.

    `cpm: Any`
    :   Cost per thousand impressions.

    `ctr: Any`
    :   Click-through rate.

    `follows: Any`
    :   Number of follows.

    `frequency: Any`
    :   Average number of times each person saw the ad.

    `impressions: Any`
    :   Number of times the ad was displayed.

    `likes: Any`
    :   Number of likes.

    `profile_visits: Any`
    :   Number of profile visits.

    `reach: Any`
    :   Total number of unique users reached.

    `real_time_app_install: Any`
    :   Real-time app installations.

    `real_time_app_install_cost: Any`
    :   Cost of real-time app installations.

    `shares: Any`
    :   Number of shares.

    `spend: Any`
    :   Total amount of money spent.

    `stat_time_day: Any`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Any`
    :   Number of video play actions.

    `video_views_p100: Any`
    :   Number of times video was watched to 100%.

    `video_views_p25: Any`
    :   Number of times video was watched to 25%.

    `video_views_p50: Any`
    :   Number of times video was watched to 50%.

    `video_views_p75: Any`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Any`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Any`
    :   Number of times video was watched for at least 6 seconds.

`CampaignsReportsDailyContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAnyValueFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySearchFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyStringFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySearchFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySearchFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyInFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_install: list[float]`
    :   Number of app installations.

    `average_video_play: list[float]`
    :   Average video play duration.

    `average_video_play_per_user: list[float]`
    :   Average video play duration per user.

    `campaign_id: list[int]`
    :   The unique identifier for the campaign.

    `campaign_name: list[str]`
    :   The name of the marketing campaign.

    `clicks: list[str]`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: list[float]`
    :   Number of clicks on the music disc.

    `comments: list[float]`
    :   Number of comments.

    `cost_per_1000_reached: list[str]`
    :   Cost per 1000 unique users reached.

    `cpc: list[str]`
    :   Cost per click.

    `cpm: list[str]`
    :   Cost per thousand impressions.

    `ctr: list[str]`
    :   Click-through rate.

    `follows: list[float]`
    :   Number of follows.

    `frequency: list[str]`
    :   Average number of times each person saw the ad.

    `impressions: list[str]`
    :   Number of times the ad was displayed.

    `likes: list[float]`
    :   Number of likes.

    `profile_visits: list[float]`
    :   Number of profile visits.

    `reach: list[str]`
    :   Total number of unique users reached.

    `real_time_app_install: list[float]`
    :   Real-time app installations.

    `real_time_app_install_cost: list[float]`
    :   Cost of real-time app installations.

    `shares: list[float]`
    :   Number of shares.

    `spend: list[str]`
    :   Total amount of money spent.

    `stat_time_day: list[str]`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: list[float]`
    :   Number of video play actions.

    `video_views_p100: list[float]`
    :   Number of times video was watched to 100%.

    `video_views_p25: list[float]`
    :   Number of times video was watched to 25%.

    `video_views_p50: list[float]`
    :   Number of times video was watched to 50%.

    `video_views_p75: list[float]`
    :   Number of times video was watched to 75%.

    `video_watched_2s: list[float]`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: list[float]`
    :   Number of times video was watched for at least 6 seconds.

`CampaignsReportsDailyKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyStringFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyStringFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyListParams(*args, **kwargs)`
:   Parameters for campaigns_reports_daily.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `data_level: str`
    :   The type of the None singleton.

    `dimensions: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `metrics: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `report_type: str`
    :   The type of the None singleton.

    `service_type: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

`CampaignsReportsDailyLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySearchFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySearchFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySearchFilter`
    :   The type of the None singleton.

`CampaignsReportsDailyNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAnyCondition`
    :   The type of the None singleton.

`CampaignsReportsDailyOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAnyCondition]`
    :   The type of the None singleton.

`CampaignsReportsDailySearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns_reports_daily search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_install: float | None`
    :   Number of app installations.

    `average_video_play: float | None`
    :   Average video play duration.

    `average_video_play_per_user: float | None`
    :   Average video play duration per user.

    `campaign_id: int | None`
    :   The unique identifier for the campaign.

    `campaign_name: str | None`
    :   The name of the marketing campaign.

    `clicks: str | None`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: float | None`
    :   Number of clicks on the music disc.

    `comments: float | None`
    :   Number of comments.

    `cost_per_1000_reached: str | None`
    :   Cost per 1000 unique users reached.

    `cpc: str | None`
    :   Cost per click.

    `cpm: str | None`
    :   Cost per thousand impressions.

    `ctr: str | None`
    :   Click-through rate.

    `follows: float | None`
    :   Number of follows.

    `frequency: str | None`
    :   Average number of times each person saw the ad.

    `impressions: str | None`
    :   Number of times the ad was displayed.

    `likes: float | None`
    :   Number of likes.

    `profile_visits: float | None`
    :   Number of profile visits.

    `reach: str | None`
    :   Total number of unique users reached.

    `real_time_app_install: float | None`
    :   Real-time app installations.

    `real_time_app_install_cost: float | None`
    :   Cost of real-time app installations.

    `shares: float | None`
    :   Number of shares.

    `spend: str | None`
    :   Total amount of money spent.

    `stat_time_day: str | None`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: float | None`
    :   Number of video play actions.

    `video_views_p100: float | None`
    :   Number of times video was watched to 100%.

    `video_views_p25: float | None`
    :   Number of times video was watched to 25%.

    `video_views_p50: float | None`
    :   Number of times video was watched to 50%.

    `video_views_p75: float | None`
    :   Number of times video was watched to 75%.

    `video_watched_2s: float | None`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: float | None`
    :   Number of times video was watched for at least 6 seconds.

`CampaignsReportsDailySearchQuery(*args, **kwargs)`
:   Search query for campaigns_reports_daily entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailyAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsReportsDailySortFilter]`
    :   The type of the None singleton.

`CampaignsReportsDailySortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns_reports_daily search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_install: Literal['asc', 'desc']`
    :   Number of app installations.

    `average_video_play: Literal['asc', 'desc']`
    :   Average video play duration.

    `average_video_play_per_user: Literal['asc', 'desc']`
    :   Average video play duration per user.

    `campaign_id: Literal['asc', 'desc']`
    :   The unique identifier for the campaign.

    `campaign_name: Literal['asc', 'desc']`
    :   The name of the marketing campaign.

    `clicks: Literal['asc', 'desc']`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: Literal['asc', 'desc']`
    :   Number of clicks on the music disc.

    `comments: Literal['asc', 'desc']`
    :   Number of comments.

    `cost_per_1000_reached: Literal['asc', 'desc']`
    :   Cost per 1000 unique users reached.

    `cpc: Literal['asc', 'desc']`
    :   Cost per click.

    `cpm: Literal['asc', 'desc']`
    :   Cost per thousand impressions.

    `ctr: Literal['asc', 'desc']`
    :   Click-through rate.

    `follows: Literal['asc', 'desc']`
    :   Number of follows.

    `frequency: Literal['asc', 'desc']`
    :   Average number of times each person saw the ad.

    `impressions: Literal['asc', 'desc']`
    :   Number of times the ad was displayed.

    `likes: Literal['asc', 'desc']`
    :   Number of likes.

    `profile_visits: Literal['asc', 'desc']`
    :   Number of profile visits.

    `reach: Literal['asc', 'desc']`
    :   Total number of unique users reached.

    `real_time_app_install: Literal['asc', 'desc']`
    :   Real-time app installations.

    `real_time_app_install_cost: Literal['asc', 'desc']`
    :   Cost of real-time app installations.

    `shares: Literal['asc', 'desc']`
    :   Number of shares.

    `spend: Literal['asc', 'desc']`
    :   Total amount of money spent.

    `stat_time_day: Literal['asc', 'desc']`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: Literal['asc', 'desc']`
    :   Number of video play actions.

    `video_views_p100: Literal['asc', 'desc']`
    :   Number of times video was watched to 100%.

    `video_views_p25: Literal['asc', 'desc']`
    :   Number of times video was watched to 25%.

    `video_views_p50: Literal['asc', 'desc']`
    :   Number of times video was watched to 50%.

    `video_views_p75: Literal['asc', 'desc']`
    :   Number of times video was watched to 75%.

    `video_watched_2s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: Literal['asc', 'desc']`
    :   Number of times video was watched for at least 6 seconds.

`CampaignsReportsDailyStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_install: str`
    :   Number of app installations.

    `average_video_play: str`
    :   Average video play duration.

    `average_video_play_per_user: str`
    :   Average video play duration per user.

    `campaign_id: str`
    :   The unique identifier for the campaign.

    `campaign_name: str`
    :   The name of the marketing campaign.

    `clicks: str`
    :   Number of clicks on the ad.

    `clicks_on_music_disc: str`
    :   Number of clicks on the music disc.

    `comments: str`
    :   Number of comments.

    `cost_per_1000_reached: str`
    :   Cost per 1000 unique users reached.

    `cpc: str`
    :   Cost per click.

    `cpm: str`
    :   Cost per thousand impressions.

    `ctr: str`
    :   Click-through rate.

    `follows: str`
    :   Number of follows.

    `frequency: str`
    :   Average number of times each person saw the ad.

    `impressions: str`
    :   Number of times the ad was displayed.

    `likes: str`
    :   Number of likes.

    `profile_visits: str`
    :   Number of profile visits.

    `reach: str`
    :   Total number of unique users reached.

    `real_time_app_install: str`
    :   Real-time app installations.

    `real_time_app_install_cost: str`
    :   Cost of real-time app installations.

    `shares: str`
    :   Number of shares.

    `spend: str`
    :   Total amount of money spent.

    `stat_time_day: str`
    :   The date for which the statistical data is recorded (YYYY-MM-DD HH:MM:SS format).

    `video_play_actions: str`
    :   Number of video play actions.

    `video_views_p100: str`
    :   Number of times video was watched to 100%.

    `video_views_p25: str`
    :   Number of times video was watched to 25%.

    `video_views_p50: str`
    :   Number of times video was watched to 50%.

    `video_views_p75: str`
    :   Number of times video was watched to 75%.

    `video_watched_2s: str`
    :   Number of times video was watched for at least 2 seconds.

    `video_watched_6s: str`
    :   Number of times video was watched for at least 6 seconds.

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: int | None`
    :   The unique identifier of the advertiser associated with the campaign

    `app_promotion_type: str | None`
    :   Type of app promotion being used in the campaign

    `bid_type: str | None`
    :   Type of bid strategy being used in the campaign

    `budget: float | None`
    :   Total budget allocated for the campaign

    `budget_mode: str | None`
    :   Mode in which the budget is being managed (e.g., daily, lifetime)

    `budget_optimize_on: bool | None`
    :   The metric or event that the budget optimization is based on

    `campaign_id: int | None`
    :   The unique identifier of the campaign

    `campaign_name: str | None`
    :   Name of the campaign for easy identification

    `campaign_type: str | None`
    :   Type of campaign (e.g., awareness, conversion)

    `create_time: str | None`
    :   Timestamp when the campaign was created

    `deep_bid_type: str | None`
    :   Advanced bid type used for campaign optimization

    `is_new_structure: bool | None`
    :   Flag indicating if the campaign utilizes a new campaign structure

    `is_search_campaign: bool | None`
    :   Flag indicating if the campaign is a search campaign

    `is_smart_performance_campaign: bool | None`
    :   Flag indicating if the campaign uses smart performance optimization

    `modify_time: str | None`
    :   Timestamp when the campaign was last modified

    `objective: str | None`
    :   The objective or goal of the campaign

    `objective_type: str | None`
    :   Type of objective selected for the campaign

    `operation_status: str | None`
    :   Current operational status of the campaign

    `optimization_goal: str | None`
    :   Specific goal to be optimized for in the campaign

    `rf_campaign_type: str | None`
    :   Type of RF (reach and frequency) campaign being run

    `roas_bid: float | None`
    :   Return on ad spend goal set for the campaign

    `secondary_status: str | None`
    :   Additional status information of the campaign

    `split_test_variable: str | None`
    :   Variable being tested in a split test campaign

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CampaignsSortFilter]`
    :   The type of the None singleton.

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: Literal['asc', 'desc']`
    :   The unique identifier of the advertiser associated with the campaign

    `app_promotion_type: Literal['asc', 'desc']`
    :   Type of app promotion being used in the campaign

    `bid_type: Literal['asc', 'desc']`
    :   Type of bid strategy being used in the campaign

    `budget: Literal['asc', 'desc']`
    :   Total budget allocated for the campaign

    `budget_mode: Literal['asc', 'desc']`
    :   Mode in which the budget is being managed (e.g., daily, lifetime)

    `budget_optimize_on: Literal['asc', 'desc']`
    :   The metric or event that the budget optimization is based on

    `campaign_id: Literal['asc', 'desc']`
    :   The unique identifier of the campaign

    `campaign_name: Literal['asc', 'desc']`
    :   Name of the campaign for easy identification

    `campaign_type: Literal['asc', 'desc']`
    :   Type of campaign (e.g., awareness, conversion)

    `create_time: Literal['asc', 'desc']`
    :   Timestamp when the campaign was created

    `deep_bid_type: Literal['asc', 'desc']`
    :   Advanced bid type used for campaign optimization

    `is_new_structure: Literal['asc', 'desc']`
    :   Flag indicating if the campaign utilizes a new campaign structure

    `is_search_campaign: Literal['asc', 'desc']`
    :   Flag indicating if the campaign is a search campaign

    `is_smart_performance_campaign: Literal['asc', 'desc']`
    :   Flag indicating if the campaign uses smart performance optimization

    `modify_time: Literal['asc', 'desc']`
    :   Timestamp when the campaign was last modified

    `objective: Literal['asc', 'desc']`
    :   The objective or goal of the campaign

    `objective_type: Literal['asc', 'desc']`
    :   Type of objective selected for the campaign

    `operation_status: Literal['asc', 'desc']`
    :   Current operational status of the campaign

    `optimization_goal: Literal['asc', 'desc']`
    :   Specific goal to be optimized for in the campaign

    `rf_campaign_type: Literal['asc', 'desc']`
    :   Type of RF (reach and frequency) campaign being run

    `roas_bid: Literal['asc', 'desc']`
    :   Return on ad spend goal set for the campaign

    `secondary_status: Literal['asc', 'desc']`
    :   Additional status information of the campaign

    `split_test_variable: Literal['asc', 'desc']`
    :   Variable being tested in a split test campaign

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The unique identifier of the advertiser associated with the campaign

    `app_promotion_type: str`
    :   Type of app promotion being used in the campaign

    `bid_type: str`
    :   Type of bid strategy being used in the campaign

    `budget: str`
    :   Total budget allocated for the campaign

    `budget_mode: str`
    :   Mode in which the budget is being managed (e.g., daily, lifetime)

    `budget_optimize_on: str`
    :   The metric or event that the budget optimization is based on

    `campaign_id: str`
    :   The unique identifier of the campaign

    `campaign_name: str`
    :   Name of the campaign for easy identification

    `campaign_type: str`
    :   Type of campaign (e.g., awareness, conversion)

    `create_time: str`
    :   Timestamp when the campaign was created

    `deep_bid_type: str`
    :   Advanced bid type used for campaign optimization

    `is_new_structure: str`
    :   Flag indicating if the campaign utilizes a new campaign structure

    `is_search_campaign: str`
    :   Flag indicating if the campaign is a search campaign

    `is_smart_performance_campaign: str`
    :   Flag indicating if the campaign uses smart performance optimization

    `modify_time: str`
    :   Timestamp when the campaign was last modified

    `objective: str`
    :   The objective or goal of the campaign

    `objective_type: str`
    :   Type of objective selected for the campaign

    `operation_status: str`
    :   Current operational status of the campaign

    `optimization_goal: str`
    :   Specific goal to be optimized for in the campaign

    `rf_campaign_type: str`
    :   Type of RF (reach and frequency) campaign being run

    `roas_bid: str`
    :   Return on ad spend goal set for the campaign

    `secondary_status: str`
    :   Additional status information of the campaign

    `split_test_variable: str`
    :   Variable being tested in a split test campaign

`CreativeAssetsImagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAnyCondition]`
    :   The type of the None singleton.

`CreativeAssetsImagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAnyValueFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Any`
    :   The timestamp when the image was created.

    `file_name: Any`
    :   The name of the image file.

    `format: Any`
    :   The format type of the image file.

    `height: Any`
    :   The height dimension of the image.

    `image_id: Any`
    :   The unique identifier for the image.

    `image_url: Any`
    :   The URL to access the image.

    `modify_time: Any`
    :   The timestamp when the image was last modified.

    `size: Any`
    :   The size of the image file.

    `width: Any`
    :   The width dimension of the image.

`CreativeAssetsImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAnyValueFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesStringFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesInFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: list[str]`
    :   The timestamp when the image was created.

    `file_name: list[str]`
    :   The name of the image file.

    `format: list[str]`
    :   The format type of the image file.

    `height: list[int]`
    :   The height dimension of the image.

    `image_id: list[str]`
    :   The unique identifier for the image.

    `image_url: list[str]`
    :   The URL to access the image.

    `modify_time: list[str]`
    :   The timestamp when the image was last modified.

    `size: list[int]`
    :   The size of the image file.

    `width: list[int]`
    :   The width dimension of the image.

`CreativeAssetsImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesStringFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesStringFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesListParams(*args, **kwargs)`
:   Parameters for creative_assets_images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CreativeAssetsImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsImagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAnyCondition`
    :   The type of the None singleton.

`CreativeAssetsImagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAnyCondition]`
    :   The type of the None singleton.

`CreativeAssetsImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering creative_assets_images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str | None`
    :   The timestamp when the image was created.

    `file_name: str | None`
    :   The name of the image file.

    `format: str | None`
    :   The format type of the image file.

    `height: int | None`
    :   The height dimension of the image.

    `image_id: str | None`
    :   The unique identifier for the image.

    `image_url: str | None`
    :   The URL to access the image.

    `modify_time: str | None`
    :   The timestamp when the image was last modified.

    `size: int | None`
    :   The size of the image file.

    `width: int | None`
    :   The width dimension of the image.

`CreativeAssetsImagesSearchQuery(*args, **kwargs)`
:   Search query for creative_assets_images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsImagesSortFilter]`
    :   The type of the None singleton.

`CreativeAssetsImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting creative_assets_images search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Literal['asc', 'desc']`
    :   The timestamp when the image was created.

    `file_name: Literal['asc', 'desc']`
    :   The name of the image file.

    `format: Literal['asc', 'desc']`
    :   The format type of the image file.

    `height: Literal['asc', 'desc']`
    :   The height dimension of the image.

    `image_id: Literal['asc', 'desc']`
    :   The unique identifier for the image.

    `image_url: Literal['asc', 'desc']`
    :   The URL to access the image.

    `modify_time: Literal['asc', 'desc']`
    :   The timestamp when the image was last modified.

    `size: Literal['asc', 'desc']`
    :   The size of the image file.

    `width: Literal['asc', 'desc']`
    :   The width dimension of the image.

`CreativeAssetsImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str`
    :   The timestamp when the image was created.

    `file_name: str`
    :   The name of the image file.

    `format: str`
    :   The format type of the image file.

    `height: str`
    :   The height dimension of the image.

    `image_id: str`
    :   The unique identifier for the image.

    `image_url: str`
    :   The URL to access the image.

    `modify_time: str`
    :   The timestamp when the image was last modified.

    `size: str`
    :   The size of the image file.

    `width: str`
    :   The width dimension of the image.

`CreativeAssetsVideosAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAnyCondition]`
    :   The type of the None singleton.

`CreativeAssetsVideosAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAnyValueFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Any`
    :   Timestamp when the video was created.

    `duration: Any`
    :   Duration of the video in seconds.

    `file_name: Any`
    :   Name of the video file.

    `format: Any`
    :   Format of the video file.

    `height: Any`
    :   Height of the video in pixels.

    `modify_time: Any`
    :   Timestamp when the video was last modified.

    `size: Any`
    :   Size of the video file in bytes.

    `video_cover_url: Any`
    :   URL for the cover image of the video.

    `video_id: Any`
    :   ID of the video.

    `width: Any`
    :   Width of the video in pixels.

`CreativeAssetsVideosContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAnyValueFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosStringFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosInFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: list[str]`
    :   Timestamp when the video was created.

    `duration: list[float]`
    :   Duration of the video in seconds.

    `file_name: list[str]`
    :   Name of the video file.

    `format: list[str]`
    :   Format of the video file.

    `height: list[int]`
    :   Height of the video in pixels.

    `modify_time: list[str]`
    :   Timestamp when the video was last modified.

    `size: list[int]`
    :   Size of the video file in bytes.

    `video_cover_url: list[str]`
    :   URL for the cover image of the video.

    `video_id: list[str]`
    :   ID of the video.

    `width: list[int]`
    :   Width of the video in pixels.

`CreativeAssetsVideosKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosStringFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosStringFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosListParams(*args, **kwargs)`
:   Parameters for creative_assets_videos.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`CreativeAssetsVideosLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSearchFilter`
    :   The type of the None singleton.

`CreativeAssetsVideosNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAnyCondition`
    :   The type of the None singleton.

`CreativeAssetsVideosOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAnyCondition]`
    :   The type of the None singleton.

`CreativeAssetsVideosSearchFilter(*args, **kwargs)`
:   Available fields for filtering creative_assets_videos search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str | None`
    :   Timestamp when the video was created.

    `duration: float | None`
    :   Duration of the video in seconds.

    `file_name: str | None`
    :   Name of the video file.

    `format: str | None`
    :   Format of the video file.

    `height: int | None`
    :   Height of the video in pixels.

    `modify_time: str | None`
    :   Timestamp when the video was last modified.

    `size: int | None`
    :   Size of the video file in bytes.

    `video_cover_url: str | None`
    :   URL for the cover image of the video.

    `video_id: str | None`
    :   ID of the video.

    `width: int | None`
    :   Width of the video in pixels.

`CreativeAssetsVideosSearchQuery(*args, **kwargs)`
:   Search query for creative_assets_videos entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosEqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNeqCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosGteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLtCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLteCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosInCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosLikeCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosFuzzyCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosKeywordCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosContainsCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosNotCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAndCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosOrCondition | airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.tiktok_marketing.types.CreativeAssetsVideosSortFilter]`
    :   The type of the None singleton.

`CreativeAssetsVideosSortFilter(*args, **kwargs)`
:   Available fields for sorting creative_assets_videos search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Literal['asc', 'desc']`
    :   Timestamp when the video was created.

    `duration: Literal['asc', 'desc']`
    :   Duration of the video in seconds.

    `file_name: Literal['asc', 'desc']`
    :   Name of the video file.

    `format: Literal['asc', 'desc']`
    :   Format of the video file.

    `height: Literal['asc', 'desc']`
    :   Height of the video in pixels.

    `modify_time: Literal['asc', 'desc']`
    :   Timestamp when the video was last modified.

    `size: Literal['asc', 'desc']`
    :   Size of the video file in bytes.

    `video_cover_url: Literal['asc', 'desc']`
    :   URL for the cover image of the video.

    `video_id: Literal['asc', 'desc']`
    :   ID of the video.

    `width: Literal['asc', 'desc']`
    :   Width of the video in pixels.

`CreativeAssetsVideosStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str`
    :   Timestamp when the video was created.

    `duration: str`
    :   Duration of the video in seconds.

    `file_name: str`
    :   Name of the video file.

    `format: str`
    :   Format of the video file.

    `height: str`
    :   Height of the video in pixels.

    `modify_time: str`
    :   Timestamp when the video was last modified.

    `size: str`
    :   Size of the video file in bytes.

    `video_cover_url: str`
    :   URL for the cover image of the video.

    `video_id: str`
    :   ID of the video.

    `width: str`
    :   Width of the video in pixels.