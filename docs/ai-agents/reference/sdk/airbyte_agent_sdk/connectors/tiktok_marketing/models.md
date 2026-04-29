---
id: airbyte_agent_sdk-connectors-tiktok_marketing-models
title: airbyte_agent_sdk.connectors.tiktok_marketing.models
---

Module airbyte_agent_sdk.connectors.tiktok_marketing.models
===========================================================
Pydantic models for tiktok-marketing connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Ad"></a>

`Ad(**data: Any)`
:   TikTok ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_format: str | Any | None`
    :   The type of the None singleton.

    `ad_id: str | Any`
    :   The type of the None singleton.

    `ad_name: str | Any`
    :   The type of the None singleton.

    `ad_text: str | Any | None`
    :   The type of the None singleton.

    `ad_texts: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `adgroup_id: str | Any`
    :   The type of the None singleton.

    `adgroup_name: str | Any`
    :   The type of the None singleton.

    `advertiser_id: str | Any`
    :   The type of the None singleton.

    `app_name: str | Any | None`
    :   The type of the None singleton.

    `avatar_icon_web_uri: str | Any | None`
    :   The type of the None singleton.

    `brand_safety_postbid_partner: str | Any | None`
    :   The type of the None singleton.

    `brand_safety_vast_url: str | Any | None`
    :   The type of the None singleton.

    `call_to_action: str | Any | None`
    :   The type of the None singleton.

    `call_to_action_id: str | Any | None`
    :   The type of the None singleton.

    `campaign_automation_type: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any`
    :   The type of the None singleton.

    `campaign_name: str | Any`
    :   The type of the None singleton.

    `card_id: str | Any | None`
    :   The type of the None singleton.

    `carousel_image_labels: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `click_tracking_url: str | Any | None`
    :   The type of the None singleton.

    `create_time: str | Any`
    :   The type of the None singleton.

    `creative_authorized: bool | Any | None`
    :   The type of the None singleton.

    `creative_type: str | Any | None`
    :   The type of the None singleton.

    `deeplink: str | Any | None`
    :   The type of the None singleton.

    `deeplink_type: str | Any | None`
    :   The type of the None singleton.

    `display_name: str | Any | None`
    :   The type of the None singleton.

    `fallback_type: str | Any | None`
    :   The type of the None singleton.

    `identity_id: str | Any | None`
    :   The type of the None singleton.

    `identity_type: str | Any | None`
    :   The type of the None singleton.

    `image_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `image_mode: str | Any | None`
    :   The type of the None singleton.

    `impression_tracking_url: str | Any | None`
    :   The type of the None singleton.

    `is_aco: bool | Any | None`
    :   The type of the None singleton.

    `is_new_structure: bool | Any | None`
    :   The type of the None singleton.

    `landing_page_url: str | Any | None`
    :   The type of the None singleton.

    `landing_page_urls: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | Any`
    :   The type of the None singleton.

    `music_id: str | Any | None`
    :   The type of the None singleton.

    `operation_status: str | Any | None`
    :   The type of the None singleton.

    `optimization_event: str | Any | None`
    :   The type of the None singleton.

    `page_id: str | Any | None`
    :   The type of the None singleton.

    `playable_url: str | Any | None`
    :   The type of the None singleton.

    `profile_image_url: str | Any | None`
    :   The type of the None singleton.

    `secondary_status: str | Any`
    :   The type of the None singleton.

    `tracking_pixel_id: int | Any | None`
    :   The type of the None singleton.

    `vast_moat_enabled: bool | Any | None`
    :   The type of the None singleton.

    `video_id: str | Any | None`
    :   The type of the None singleton.

    `viewability_postbid_partner: str | Any | None`
    :   The type of the None singleton.

    `viewability_vast_url: str | Any | None`
    :   The type of the None singleton.

<a id="AdGroup"></a>

`AdGroup(**data: Any)`
:   TikTok ad group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `adgroup_app_profile_page_state: str | Any | None`
    :   The type of the None singleton.

    `adgroup_id: str | Any`
    :   The type of the None singleton.

    `adgroup_name: str | Any`
    :   The type of the None singleton.

    `advertiser_id: str | Any`
    :   The type of the None singleton.

    `age_groups: list[str] | Any | None`
    :   The type of the None singleton.

    `app_config: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `app_download_url: str | Any | None`
    :   The type of the None singleton.

    `app_id: str | Any | None`
    :   The type of the None singleton.

    `app_type: str | Any | None`
    :   The type of the None singleton.

    `audience_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `auto_targeting_enabled: bool | Any | None`
    :   The type of the None singleton.

    `automated_keywords_enabled: bool | Any | None`
    :   The type of the None singleton.

    `bid_display_mode: str | Any | None`
    :   The type of the None singleton.

    `bid_price: float | Any`
    :   The type of the None singleton.

    `bid_type: str | Any | None`
    :   The type of the None singleton.

    `billing_event: str | Any | None`
    :   The type of the None singleton.

    `brand_safety_partner: str | Any | None`
    :   The type of the None singleton.

    `brand_safety_type: str | Any | None`
    :   The type of the None singleton.

    `budget: float | Any`
    :   The type of the None singleton.

    `budget_mode: str | Any`
    :   The type of the None singleton.

    `campaign_automation_type: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any`
    :   The type of the None singleton.

    `campaign_name: str | Any | None`
    :   The type of the None singleton.

    `category_exclusion_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `category_id: str | Any | None`
    :   The type of the None singleton.

    `comment_disabled: bool | Any | None`
    :   The type of the None singleton.

    `contextual_tag_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `conversion_bid_price: float | Any`
    :   The type of the None singleton.

    `conversion_window: str | Any | None`
    :   The type of the None singleton.

    `create_time: str | Any`
    :   The type of the None singleton.

    `creative_material_mode: str | Any`
    :   The type of the None singleton.

    `custom_conversion_id: str | Any | None`
    :   The type of the None singleton.

    `dayparting: str | Any | None`
    :   The type of the None singleton.

    `deep_bid_type: str | Any | None`
    :   The type of the None singleton.

    `deep_cpa_bid: float | Any`
    :   The type of the None singleton.

    `deep_funnel_event_source: str | Any | None`
    :   The type of the None singleton.

    `deep_funnel_event_source_id: str | Any | None`
    :   The type of the None singleton.

    `deep_funnel_optimization_event: str | Any | None`
    :   The type of the None singleton.

    `deep_funnel_optimization_status: str | Any | None`
    :   The type of the None singleton.

    `delivery_mode: str | Any | None`
    :   The type of the None singleton.

    `device_model_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `device_price_ranges: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `excluded_audience_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `excluded_custom_actions: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `feed_type: str | Any | None`
    :   The type of the None singleton.

    `frequency: int | Any | None`
    :   The type of the None singleton.

    `frequency_schedule: int | Any | None`
    :   The type of the None singleton.

    `gender: str | Any | None`
    :   The type of the None singleton.

    `household_income: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `included_custom_actions: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `interest_category_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `interest_keyword_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `inventory_filter_enabled: bool | Any | None`
    :   The type of the None singleton.

    `ios14_quota_type: str | Any | None`
    :   The type of the None singleton.

    `is_hfss: bool | Any | None`
    :   The type of the None singleton.

    `is_new_structure: bool | Any`
    :   The type of the None singleton.

    `is_smart_performance_campaign: bool | Any | None`
    :   The type of the None singleton.

    `isp_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `keywords: str | Any | None`
    :   The type of the None singleton.

    `languages: list[str] | Any | None`
    :   The type of the None singleton.

    `location_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | Any`
    :   The type of the None singleton.

    `network_types: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `next_day_retention: float | Any | None`
    :   The type of the None singleton.

    `operating_systems: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `operation_status: str | Any`
    :   The type of the None singleton.

    `optimization_event: str | Any | None`
    :   The type of the None singleton.

    `optimization_goal: str | Any`
    :   The type of the None singleton.

    `pacing: str | Any | None`
    :   The type of the None singleton.

    `pixel_id: str | Any | None`
    :   The type of the None singleton.

    `placement_type: str | Any`
    :   The type of the None singleton.

    `placements: list[str] | Any | None`
    :   The type of the None singleton.

    `promotion_type: str | Any`
    :   The type of the None singleton.

    `purchased_impression: float | Any | None`
    :   The type of the None singleton.

    `purchased_reach: float | Any | None`
    :   The type of the None singleton.

    `rf_estimated_cpr: float | Any | None`
    :   The type of the None singleton.

    `rf_estimated_frequency: float | Any | None`
    :   The type of the None singleton.

    `rf_purchased_type: str | Any | None`
    :   The type of the None singleton.

    `schedule_end_time: str | Any`
    :   The type of the None singleton.

    `schedule_infos: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `schedule_start_time: str | Any`
    :   The type of the None singleton.

    `schedule_type: str | Any`
    :   The type of the None singleton.

    `scheduled_budget: float | Any | None`
    :   The type of the None singleton.

    `search_result_enabled: bool | Any | None`
    :   The type of the None singleton.

    `secondary_optimization_event: str | Any | None`
    :   The type of the None singleton.

    `secondary_status: str | Any`
    :   The type of the None singleton.

    `share_disabled: bool | Any | None`
    :   The type of the None singleton.

    `skip_learning_phase: bool | Any | None`
    :   The type of the None singleton.

    `smart_audience_enabled: bool | Any | None`
    :   The type of the None singleton.

    `smart_interest_behavior_enabled: bool | Any | None`
    :   The type of the None singleton.

    `spending_power: str | Any | None`
    :   The type of the None singleton.

    `statistic_type: str | Any | None`
    :   The type of the None singleton.

    `vbo_window: str | Any | None`
    :   The type of the None singleton.

    `video_download_disabled: bool | Any | None`
    :   The type of the None singleton.

    `zipcode_ids: list[typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="AdGroupsListResultMeta"></a>

`AdGroupsListResultMeta(**data: Any)`
:   Metadata for ad_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AdGroupsReportDaily"></a>

`AdGroupsReportDaily(**data: Any)`
:   Daily performance report at the ad group level
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adgroup_id: int | Any | None`
    :   The type of the None singleton.

    `adgroup_name: str | Any | None`
    :   The type of the None singleton.

    `app_install: float | Any | None`
    :   The type of the None singleton.

    `average_video_play: float | Any | None`
    :   The type of the None singleton.

    `average_video_play_per_user: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: int | Any | None`
    :   The type of the None singleton.

    `campaign_name: str | Any | None`
    :   The type of the None singleton.

    `clicks: str | Any | None`
    :   The type of the None singleton.

    `clicks_on_music_disc: float | Any | None`
    :   The type of the None singleton.

    `comments: float | Any | None`
    :   The type of the None singleton.

    `conversion: str | Any | None`
    :   The type of the None singleton.

    `conversion_rate: str | Any | None`
    :   The type of the None singleton.

    `cost_per_1000_reached: str | Any | None`
    :   The type of the None singleton.

    `cost_per_conversion: str | Any | None`
    :   The type of the None singleton.

    `cost_per_result: str | Any | None`
    :   The type of the None singleton.

    `cost_per_secondary_goal_result: str | Any | None`
    :   The type of the None singleton.

    `cpc: str | Any | None`
    :   The type of the None singleton.

    `cpm: str | Any | None`
    :   The type of the None singleton.

    `ctr: str | Any | None`
    :   The type of the None singleton.

    `follows: float | Any | None`
    :   The type of the None singleton.

    `frequency: str | Any | None`
    :   The type of the None singleton.

    `impressions: str | Any | None`
    :   The type of the None singleton.

    `likes: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `placement_type: str | Any | None`
    :   The type of the None singleton.

    `profile_visits: float | Any | None`
    :   The type of the None singleton.

    `reach: str | Any | None`
    :   The type of the None singleton.

    `real_time_app_install: float | Any | None`
    :   The type of the None singleton.

    `real_time_app_install_cost: float | Any | None`
    :   The type of the None singleton.

    `real_time_conversion: str | Any | None`
    :   The type of the None singleton.

    `real_time_conversion_rate: str | Any | None`
    :   The type of the None singleton.

    `real_time_cost_per_conversion: str | Any | None`
    :   The type of the None singleton.

    `real_time_cost_per_result: str | Any | None`
    :   The type of the None singleton.

    `real_time_result: str | Any | None`
    :   The type of the None singleton.

    `real_time_result_rate: str | Any | None`
    :   The type of the None singleton.

    `result: str | Any | None`
    :   The type of the None singleton.

    `result_rate: str | Any | None`
    :   The type of the None singleton.

    `secondary_goal_result: str | Any | None`
    :   The type of the None singleton.

    `secondary_goal_result_rate: str | Any | None`
    :   The type of the None singleton.

    `shares: float | Any | None`
    :   The type of the None singleton.

    `spend: str | Any | None`
    :   The type of the None singleton.

    `stat_time_day: str | Any | None`
    :   The type of the None singleton.

    `video_play_actions: float | Any | None`
    :   The type of the None singleton.

    `video_views_p100: float | Any | None`
    :   The type of the None singleton.

    `video_views_p25: float | Any | None`
    :   The type of the None singleton.

    `video_views_p50: float | Any | None`
    :   The type of the None singleton.

    `video_views_p75: float | Any | None`
    :   The type of the None singleton.

    `video_watched_2s: float | Any | None`
    :   The type of the None singleton.

    `video_watched_6s: float | Any | None`
    :   The type of the None singleton.

<a id="AdGroupsReportsDailyListResultMeta"></a>

`AdGroupsReportsDailyListResultMeta(**data: Any)`
:   Metadata for ad_groups_reports_daily.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AdGroupsReportsDailySearchData"></a>

`AdGroupsReportsDailySearchData(**data: Any)`
:   Search result data for ad_groups_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdGroupsSearchData"></a>

`AdGroupsSearchData(**data: Any)`
:   Search result data for ad_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdsListResultMeta"></a>

`AdsListResultMeta(**data: Any)`
:   Metadata for ads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AdsReportDaily"></a>

`AdsReportDaily(**data: Any)`
:   Daily performance report at the ad level
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_id: int | Any | None`
    :   The type of the None singleton.

    `ad_name: str | Any | None`
    :   The type of the None singleton.

    `ad_text: str | Any | None`
    :   The type of the None singleton.

    `adgroup_id: int | Any | None`
    :   The type of the None singleton.

    `adgroup_name: str | Any | None`
    :   The type of the None singleton.

    `app_install: float | Any | None`
    :   The type of the None singleton.

    `average_video_play: float | Any | None`
    :   The type of the None singleton.

    `average_video_play_per_user: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: int | Any | None`
    :   The type of the None singleton.

    `campaign_name: str | Any | None`
    :   The type of the None singleton.

    `clicks: str | Any | None`
    :   The type of the None singleton.

    `clicks_on_music_disc: float | Any | None`
    :   The type of the None singleton.

    `comments: float | Any | None`
    :   The type of the None singleton.

    `conversion: str | Any | None`
    :   The type of the None singleton.

    `conversion_rate: str | Any | None`
    :   The type of the None singleton.

    `cost_per_1000_reached: str | Any | None`
    :   The type of the None singleton.

    `cost_per_conversion: str | Any | None`
    :   The type of the None singleton.

    `cost_per_result: str | Any | None`
    :   The type of the None singleton.

    `cost_per_secondary_goal_result: str | Any | None`
    :   The type of the None singleton.

    `cpc: str | Any | None`
    :   The type of the None singleton.

    `cpm: str | Any | None`
    :   The type of the None singleton.

    `ctr: str | Any | None`
    :   The type of the None singleton.

    `follows: float | Any | None`
    :   The type of the None singleton.

    `frequency: str | Any | None`
    :   The type of the None singleton.

    `impressions: str | Any | None`
    :   The type of the None singleton.

    `likes: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `placement_type: str | Any | None`
    :   The type of the None singleton.

    `profile_visits: float | Any | None`
    :   The type of the None singleton.

    `reach: str | Any | None`
    :   The type of the None singleton.

    `real_time_app_install: float | Any | None`
    :   The type of the None singleton.

    `real_time_app_install_cost: float | Any | None`
    :   The type of the None singleton.

    `real_time_conversion: str | Any | None`
    :   The type of the None singleton.

    `real_time_conversion_rate: str | Any | None`
    :   The type of the None singleton.

    `real_time_cost_per_conversion: str | Any | None`
    :   The type of the None singleton.

    `real_time_cost_per_result: str | Any | None`
    :   The type of the None singleton.

    `real_time_result: str | Any | None`
    :   The type of the None singleton.

    `real_time_result_rate: str | Any | None`
    :   The type of the None singleton.

    `result: str | Any | None`
    :   The type of the None singleton.

    `result_rate: str | Any | None`
    :   The type of the None singleton.

    `secondary_goal_result: str | Any | None`
    :   The type of the None singleton.

    `secondary_goal_result_rate: str | Any | None`
    :   The type of the None singleton.

    `shares: float | Any | None`
    :   The type of the None singleton.

    `spend: str | Any | None`
    :   The type of the None singleton.

    `stat_time_day: str | Any | None`
    :   The type of the None singleton.

    `video_play_actions: float | Any | None`
    :   The type of the None singleton.

    `video_views_p100: float | Any | None`
    :   The type of the None singleton.

    `video_views_p25: float | Any | None`
    :   The type of the None singleton.

    `video_views_p50: float | Any | None`
    :   The type of the None singleton.

    `video_views_p75: float | Any | None`
    :   The type of the None singleton.

    `video_watched_2s: float | Any | None`
    :   The type of the None singleton.

    `video_watched_6s: float | Any | None`
    :   The type of the None singleton.

<a id="AdsReportsDailyListResultMeta"></a>

`AdsReportsDailyListResultMeta(**data: Any)`
:   Metadata for ads_reports_daily.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AdsReportsDailySearchData"></a>

`AdsReportsDailySearchData(**data: Any)`
:   Search result data for ads_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdsSearchData"></a>

`AdsSearchData(**data: Any)`
:   Search result data for ads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   The timestamp when the ad was last modified

    `operation_status: str | None`
    :   The operational status of the ad

    `secondary_status: str | None`
    :   The secondary status of the ad

    `video_id: str | None`
    :   The unique identifier of the video

<a id="Advertiser"></a>

`Advertiser(**data: Any)`
:   TikTok advertiser account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: str | Any | None`
    :   The type of the None singleton.

    `advertiser_account_type: str | Any | None`
    :   The type of the None singleton.

    `advertiser_id: str | Any`
    :   The type of the None singleton.

    `balance: float | Any`
    :   The type of the None singleton.

    `brand: str | Any | None`
    :   The type of the None singleton.

    `cellphone_number: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `contacter: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `create_time: int | Any`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `display_timezone: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `industry: str | Any | None`
    :   The type of the None singleton.

    `language: str | Any | None`
    :   The type of the None singleton.

    `license_city: str | Any | None`
    :   The type of the None singleton.

    `license_no: str | Any | None`
    :   The type of the None singleton.

    `license_province: str | Any | None`
    :   The type of the None singleton.

    `license_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `promotion_area: str | Any | None`
    :   The type of the None singleton.

    `promotion_center_city: str | Any | None`
    :   The type of the None singleton.

    `promotion_center_province: str | Any | None`
    :   The type of the None singleton.

    `rejection_reason: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `telephone_number: str | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

<a id="AdvertisersListResultMeta"></a>

`AdvertisersListResultMeta(**data: Any)`
:   Metadata for advertisers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AdvertisersReportDaily"></a>

`AdvertisersReportDaily(**data: Any)`
:   Daily performance report at the advertiser level
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advertiser_id: int | Any | None`
    :   The type of the None singleton.

    `app_install: float | Any | None`
    :   The type of the None singleton.

    `average_video_play: float | Any | None`
    :   The type of the None singleton.

    `average_video_play_per_user: float | Any | None`
    :   The type of the None singleton.

    `cash_spend: str | Any | None`
    :   The type of the None singleton.

    `clicks: str | Any | None`
    :   The type of the None singleton.

    `clicks_on_music_disc: float | Any | None`
    :   The type of the None singleton.

    `comments: float | Any | None`
    :   The type of the None singleton.

    `cost_per_1000_reached: str | Any | None`
    :   The type of the None singleton.

    `cpc: str | Any | None`
    :   The type of the None singleton.

    `cpm: str | Any | None`
    :   The type of the None singleton.

    `ctr: str | Any | None`
    :   The type of the None singleton.

    `follows: float | Any | None`
    :   The type of the None singleton.

    `frequency: str | Any | None`
    :   The type of the None singleton.

    `impressions: str | Any | None`
    :   The type of the None singleton.

    `likes: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_visits: float | Any | None`
    :   The type of the None singleton.

    `reach: str | Any | None`
    :   The type of the None singleton.

    `real_time_app_install: float | Any | None`
    :   The type of the None singleton.

    `real_time_app_install_cost: float | Any | None`
    :   The type of the None singleton.

    `shares: float | Any | None`
    :   The type of the None singleton.

    `spend: str | Any | None`
    :   The type of the None singleton.

    `stat_time_day: str | Any | None`
    :   The type of the None singleton.

    `video_play_actions: float | Any | None`
    :   The type of the None singleton.

    `video_views_p100: float | Any | None`
    :   The type of the None singleton.

    `video_views_p25: float | Any | None`
    :   The type of the None singleton.

    `video_views_p50: float | Any | None`
    :   The type of the None singleton.

    `video_views_p75: float | Any | None`
    :   The type of the None singleton.

    `video_watched_2s: float | Any | None`
    :   The type of the None singleton.

    `video_watched_6s: float | Any | None`
    :   The type of the None singleton.

    `voucher_spend: str | Any | None`
    :   The type of the None singleton.

<a id="AdvertisersReportsDailyListResultMeta"></a>

`AdvertisersReportsDailyListResultMeta(**data: Any)`
:   Metadata for advertisers_reports_daily.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AdvertisersReportsDailySearchData"></a>

`AdvertisersReportsDailySearchData(**data: Any)`
:   Search result data for advertisers_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AdvertisersSearchData"></a>

`AdvertisersSearchData(**data: Any)`
:   Search result data for advertisers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdGroupsReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdGroupsSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdsReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdsSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdvertisersReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AdvertisersSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[AudiencesSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CampaignsReportsDailySearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CreativeAssetsImagesSearchData]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult[CreativeAssetsVideosSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AdGroupsReportsDailySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsReportsDailySearchResult"></a>

`AdGroupsReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsSearchResult"></a>

`AdGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsReportsDailySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsReportsDailySearchResult"></a>

`AdsReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsSearchResult"></a>

`AdsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdvertisersReportsDailySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdvertisersReportsDailySearchResult"></a>

`AdvertisersReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdvertisersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdvertisersSearchResult"></a>

`AdvertisersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AudiencesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AudiencesSearchResult"></a>

`AudiencesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsReportsDailySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsReportsDailySearchResult"></a>

`CampaignsReportsDailySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsSearchResult"></a>

`CampaignsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CreativeAssetsImagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativeAssetsImagesSearchResult"></a>

`CreativeAssetsImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CreativeAssetsVideosSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativeAssetsVideosSearchResult"></a>

`CreativeAssetsVideosSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Audience"></a>

`Audience(**data: Any)`
:   TikTok custom audience
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audience_id: str | Any | None`
    :   The type of the None singleton.

    `audience_type: str | Any | None`
    :   The type of the None singleton.

    `calculate_type: str | Any | None`
    :   The type of the None singleton.

    `cover_num: int | Any | None`
    :   The type of the None singleton.

    `create_time: str | Any | None`
    :   The type of the None singleton.

    `expired_time: str | Any | None`
    :   The type of the None singleton.

    `is_creator: bool | Any | None`
    :   The type of the None singleton.

    `is_expiring: bool | Any | None`
    :   The type of the None singleton.

    `is_valid: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `shared: bool | Any | None`
    :   The type of the None singleton.

<a id="AudiencesListResultMeta"></a>

`AudiencesListResultMeta(**data: Any)`
:   Metadata for audiences.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="AudiencesSearchData"></a>

`AudiencesSearchData(**data: Any)`
:   Search result data for audiences entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the audience

    `shared: bool | None`
    :   Flag indicating if the audience is shared

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   TikTok marketing campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advertiser_id: str | Any`
    :   The type of the None singleton.

    `app_promotion_type: str | Any | None`
    :   The type of the None singleton.

    `bid_type: str | Any | None`
    :   The type of the None singleton.

    `budget: float | Any`
    :   The type of the None singleton.

    `budget_mode: str | Any`
    :   The type of the None singleton.

    `budget_optimize_on: bool | Any | None`
    :   The type of the None singleton.

    `campaign_automation_type: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any`
    :   The type of the None singleton.

    `campaign_name: str | Any`
    :   The type of the None singleton.

    `campaign_type: str | Any`
    :   The type of the None singleton.

    `create_time: str | Any`
    :   The type of the None singleton.

    `deep_bid_type: str | Any | None`
    :   The type of the None singleton.

    `disable_skan_campaign: bool | Any | None`
    :   The type of the None singleton.

    `is_advanced_dedicated_campaign: bool | Any | None`
    :   The type of the None singleton.

    `is_new_structure: bool | Any`
    :   The type of the None singleton.

    `is_search_campaign: bool | Any | None`
    :   The type of the None singleton.

    `is_smart_performance_campaign: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | Any`
    :   The type of the None singleton.

    `objective: str | Any | None`
    :   The type of the None singleton.

    `objective_type: str | Any | None`
    :   The type of the None singleton.

    `operation_status: str | Any | None`
    :   The type of the None singleton.

    `optimization_goal: str | Any | None`
    :   The type of the None singleton.

    `rf_campaign_type: str | Any | None`
    :   The type of the None singleton.

    `roas_bid: float | Any | None`
    :   The type of the None singleton.

    `rta_bid_enabled: bool | Any | None`
    :   The type of the None singleton.

    `rta_id: str | Any | None`
    :   The type of the None singleton.

    `rta_product_selection_enabled: bool | Any | None`
    :   The type of the None singleton.

    `secondary_status: str | Any`
    :   The type of the None singleton.

    `split_test_variable: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignsListResultMeta"></a>

`CampaignsListResultMeta(**data: Any)`
:   Metadata for campaigns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="CampaignsReportDaily"></a>

`CampaignsReportDaily(**data: Any)`
:   Daily performance report at the campaign level
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_install: float | Any | None`
    :   The type of the None singleton.

    `average_video_play: float | Any | None`
    :   The type of the None singleton.

    `average_video_play_per_user: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: int | Any | None`
    :   The type of the None singleton.

    `campaign_name: str | Any | None`
    :   The type of the None singleton.

    `clicks: str | Any | None`
    :   The type of the None singleton.

    `clicks_on_music_disc: float | Any | None`
    :   The type of the None singleton.

    `comments: float | Any | None`
    :   The type of the None singleton.

    `cost_per_1000_reached: str | Any | None`
    :   The type of the None singleton.

    `cpc: str | Any | None`
    :   The type of the None singleton.

    `cpm: str | Any | None`
    :   The type of the None singleton.

    `ctr: str | Any | None`
    :   The type of the None singleton.

    `follows: float | Any | None`
    :   The type of the None singleton.

    `frequency: str | Any | None`
    :   The type of the None singleton.

    `impressions: str | Any | None`
    :   The type of the None singleton.

    `likes: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_visits: float | Any | None`
    :   The type of the None singleton.

    `reach: str | Any | None`
    :   The type of the None singleton.

    `real_time_app_install: float | Any | None`
    :   The type of the None singleton.

    `real_time_app_install_cost: float | Any | None`
    :   The type of the None singleton.

    `shares: float | Any | None`
    :   The type of the None singleton.

    `spend: str | Any | None`
    :   The type of the None singleton.

    `stat_time_day: str | Any | None`
    :   The type of the None singleton.

    `video_play_actions: float | Any | None`
    :   The type of the None singleton.

    `video_views_p100: float | Any | None`
    :   The type of the None singleton.

    `video_views_p25: float | Any | None`
    :   The type of the None singleton.

    `video_views_p50: float | Any | None`
    :   The type of the None singleton.

    `video_views_p75: float | Any | None`
    :   The type of the None singleton.

    `video_watched_2s: float | Any | None`
    :   The type of the None singleton.

    `video_watched_6s: float | Any | None`
    :   The type of the None singleton.

<a id="CampaignsReportsDailyListResultMeta"></a>

`CampaignsReportsDailyListResultMeta(**data: Any)`
:   Metadata for campaigns_reports_daily.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="CampaignsReportsDailySearchData"></a>

`CampaignsReportsDailySearchData(**data: Any)`
:   Search result data for campaigns_reports_daily entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="CampaignsSearchData"></a>

`CampaignsSearchData(**data: Any)`
:   Search result data for campaigns entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="CreativeAssetImage"></a>

`CreativeAssetImage(**data: Any)`
:   TikTok creative asset image
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | Any | None`
    :   The type of the None singleton.

    `displayable: bool | Any | None`
    :   The type of the None singleton.

    `file_name: str | Any | None`
    :   The type of the None singleton.

    `format: str | Any | None`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `image_id: str | Any | None`
    :   The type of the None singleton.

    `image_url: str | Any | None`
    :   The type of the None singleton.

    `is_carousel_usable: bool | Any | None`
    :   The type of the None singleton.

    `material_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | Any | None`
    :   The type of the None singleton.

    `signature: str | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

<a id="CreativeAssetVideo"></a>

`CreativeAssetVideo(**data: Any)`
:   TikTok creative asset video
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_download: bool | Any | None`
    :   The type of the None singleton.

    `allowed_placements: list[str | None] | Any | None`
    :   The type of the None singleton.

    `bit_rate: float | Any | None`
    :   The type of the None singleton.

    `create_time: str | Any | None`
    :   The type of the None singleton.

    `displayable: bool | Any | None`
    :   The type of the None singleton.

    `duration: float | Any | None`
    :   The type of the None singleton.

    `file_name: str | Any | None`
    :   The type of the None singleton.

    `fix_task_id: str | Any | None`
    :   The type of the None singleton.

    `flaw_types: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `format: str | Any | None`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `material_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | Any | None`
    :   The type of the None singleton.

    `preview_url: str | Any | None`
    :   The type of the None singleton.

    `preview_url_expire_time: str | Any | None`
    :   The type of the None singleton.

    `signature: str | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `video_cover_url: str | Any | None`
    :   The type of the None singleton.

    `video_id: str | Any | None`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

<a id="CreativeAssetsImagesListResultMeta"></a>

`CreativeAssetsImagesListResultMeta(**data: Any)`
:   Metadata for creative_assets_images.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="CreativeAssetsImagesSearchData"></a>

`CreativeAssetsImagesSearchData(**data: Any)`
:   Search result data for creative_assets_images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `modify_time: str | None`
    :   The timestamp when the image was last modified.

    `size: int | None`
    :   The size of the image file.

    `width: int | None`
    :   The width dimension of the image.

<a id="CreativeAssetsVideosListResultMeta"></a>

`CreativeAssetsVideosListResultMeta(**data: Any)`
:   Metadata for creative_assets_videos.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_info: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="CreativeAssetsVideosSearchData"></a>

`CreativeAssetsVideosSearchData(**data: Any)`
:   Search result data for creative_assets_videos entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="TiktokMarketingAuthConfig"></a>

`TiktokMarketingAuthConfig(**data: Any)`
:   OAuth Access Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your TikTok Marketing API access token

    `model_config`
    :   The type of the None singleton.

<a id="TiktokMarketingCheckResult"></a>

`TiktokMarketingCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="TiktokMarketingExecuteResult"></a>

`TiktokMarketingExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="TiktokMarketingExecuteResultWithMeta"></a>

`TiktokMarketingExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdGroupsReportDaily], AdGroupsReportsDailyListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdsReportDaily], AdsReportsDailyListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Advertiser], AdvertisersListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[AdvertisersReportDaily], AdvertisersReportsDailyListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Audience], AudiencesListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[CampaignsReportDaily], CampaignsReportsDailyListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[CreativeAssetImage], CreativeAssetsImagesListResultMeta]
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta[list[CreativeAssetVideo], CreativeAssetsVideosListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`TiktokMarketingExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsListResult"></a>

`AdGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[AdGroupsReportDaily], AdGroupsReportsDailyListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsReportsDailyListResult"></a>

`AdGroupsReportsDailyListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsListResult"></a>

`AdsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[AdsReportDaily], AdsReportsDailyListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsReportsDailyListResult"></a>

`AdsReportsDailyListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[Advertiser], AdvertisersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdvertisersListResult"></a>

`AdvertisersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[AdvertisersReportDaily], AdvertisersReportsDailyListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdvertisersReportsDailyListResult"></a>

`AdvertisersReportsDailyListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[Audience], AudiencesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AudiencesListResult"></a>

`AudiencesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResult"></a>

`CampaignsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[CampaignsReportDaily], CampaignsReportsDailyListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsReportsDailyListResult"></a>

`CampaignsReportsDailyListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[CreativeAssetImage], CreativeAssetsImagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativeAssetsImagesListResult"></a>

`CreativeAssetsImagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`TiktokMarketingExecuteResultWithMeta[list[CreativeAssetVideo], CreativeAssetsVideosListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativeAssetsVideosListResult"></a>

`CreativeAssetsVideosListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.tiktok_marketing.models.TiktokMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TiktokMarketingReplicationConfig"></a>

`TiktokMarketingReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from TikTok Marketing.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   The start date in YYYY-MM-DD format. Any data before this date will not be replicated. If not set, defaults to 2016-09-01.