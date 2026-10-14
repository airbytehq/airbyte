---
id: airbyte_agent_sdk-connectors-reddit_ads-models
title: airbyte_agent_sdk.connectors.reddit_ads.models
---

Module airbyte_agent_sdk.connectors.reddit_ads.models
=====================================================
Pydantic models for reddit-ads connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Ad"></a>

`Ad(**data: Any)`
:   A Reddit ad with creative configuration, status, and tracking settings.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   The type of the None singleton.

    `ad_group_id: str | None`
    :   The type of the None singleton.

    `campaign_id: str | None`
    :   The type of the None singleton.

    `campaign_objective_type: str | None`
    :   The type of the None singleton.

    `click_url: str | None`
    :   The type of the None singleton.

    `click_url_query_parameters: list[airbyte_agent_sdk.connectors.reddit_ads.models.AdClickUrlQueryParametersItem] | None`
    :   The type of the None singleton.

    `configured_status: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `delivery_status: list[str] | None`
    :   The type of the None singleton.

    `effective_status: str | None`
    :   The type of the None singleton.

    `event_trackers: list[airbyte_agent_sdk.connectors.reddit_ads.models.AdEventTrackersItem] | None`
    :   The type of the None singleton.

    `extensions: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `post_id: str | None`
    :   The type of the None singleton.

    `post_url: str | None`
    :   The type of the None singleton.

    `preview_expiry: str | None`
    :   The type of the None singleton.

    `preview_url: str | None`
    :   The type of the None singleton.

    `products: list[typing.Any] | None`
    :   The type of the None singleton.

    `profile_id: str | None`
    :   The type of the None singleton.

    `rejection_reason: str | None`
    :   The type of the None singleton.

    `shopping_creative: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `skadnetwork_metadata: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="AdAccount"></a>

`AdAccount(**data: Any)`
:   A Reddit ad account with billing, attribution, and configuration settings.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_approval: str | None`
    :   The type of the None singleton.

    `app_attribution_type: str | None`
    :   The type of the None singleton.

    `app_click_attribution_window: str | None`
    :   The type of the None singleton.

    `app_view_attribution_window: str | None`
    :   The type of the None singleton.

    `attribution_type: str | None`
    :   The type of the None singleton.

    `business_id: str | None`
    :   The type of the None singleton.

    `click_attribution_window: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `excluded_communities: list[str] | None`
    :   The type of the None singleton.

    `excluded_keywords: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `pixel_partner_preferences: list[str] | None`
    :   The type of the None singleton.

    `primary_contact_member_id: str | None`
    :   The type of the None singleton.

    `suspension_reason: str | None`
    :   The type of the None singleton.

    `time_zone_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `view_attribution_window: str | None`
    :   The type of the None singleton.

<a id="AdAccountsListResultMeta"></a>

`AdAccountsListResultMeta(**data: Any)`
:   Metadata for ad_accounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

<a id="AdClickUrlQueryParametersItem"></a>

`AdClickUrlQueryParametersItem(**data: Any)`
:   Nested schema for Ad.click_url_query_parameters_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="AdEventTrackersItem"></a>

`AdEventTrackersItem(**data: Any)`
:   Nested schema for Ad.event_trackers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="AdGroup"></a>

`AdGroup(**data: Any)`
:   A Reddit ad group with targeting, bidding, and scheduling settings.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   The type of the None singleton.

    `app_id: str | None`
    :   The type of the None singleton.

    `bid_strategy: str | None`
    :   The type of the None singleton.

    `bid_type: str | None`
    :   The type of the None singleton.

    `bid_value: int | None`
    :   The type of the None singleton.

    `campaign_id: str | None`
    :   The type of the None singleton.

    `campaign_objective_type: str | None`
    :   The type of the None singleton.

    `configured_status: str | None`
    :   The type of the None singleton.

    `conversion_pixel_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `delivery_status: list[str] | None`
    :   The type of the None singleton.

    `effective_status: str | None`
    :   The type of the None singleton.

    `end_time: str | None`
    :   The type of the None singleton.

    `goal_type: str | None`
    :   The type of the None singleton.

    `goal_value: int | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_campaign_budget_optimization: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `optimization_goal: str | None`
    :   The type of the None singleton.

    `optimization_strategy_type: str | None`
    :   The type of the None singleton.

    `product_set_id: str | None`
    :   The type of the None singleton.

    `saved_audience_id: str | None`
    :   The type of the None singleton.

    `schedule: list[typing.Any] | None`
    :   The type of the None singleton.

    `shopping_type: str | None`
    :   The type of the None singleton.

    `skadnetwork_metadata: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `start_time: str | None`
    :   The type of the None singleton.

    `targeting: airbyte_agent_sdk.connectors.reddit_ads.models.AdGroupTargeting | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `view_through_conversion_type: str | None`
    :   The type of the None singleton.

<a id="AdGroupTargeting"></a>

`AdGroupTargeting(**data: Any)`
:   Targeting configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `age_targeting: dict[str, typing.Any] | None`
    :   Age range targeting configuration

    `carriers: list[str] | None`
    :   Mobile carrier targeting

    `communities: list[str] | None`
    :   Targeted community subreddit names

    `custom_audience_ids: list[str] | None`
    :   Custom audience IDs to target

    `devices: list[airbyte_agent_sdk.connectors.reddit_ads.models.AdGroupTargetingDevicesItem] | None`
    :   Targeted devices (type/OS/version constraints)

    `excluded_communities: list[str] | None`
    :   Excluded community subreddit names

    `excluded_custom_audience_ids: list[str] | None`
    :   Excluded custom audience IDs

    `excluded_geolocations: list[dict[str, typing.Any]] | None`
    :   Excluded geographic locations

    `excluded_keywords: list[str] | None`
    :   Excluded keywords for targeting

    `expand_targeting: bool | None`
    :   Whether to expand targeting beyond specified criteria

    `gender: str | None`
    :   Gender targeting filter

    `geolocations: list[dict[str, typing.Any]] | None`
    :   Targeted geographic locations

    `interests: list[str] | None`
    :   Interest category IDs for targeting

    `keywords: list[str] | None`
    :   Keyword targeting terms

    `languages: list[str] | None`
    :   Language targeting codes

    `locations: list[str] | None`
    :   Ad placement locations (e.g. FEED, COMMENTS_PAGE)

    `model_config`
    :   The type of the None singleton.

    `platforms: list[str] | None`
    :   Targeted platforms (e.g. ALL, IOS, ANDROID)

    `suppression_event_types: list[str] | None`
    :   Event types to suppress for retargeting

    `view_modes: list[str] | None`
    :   View mode targeting (e.g. ALL)

<a id="AdGroupTargetingDevicesItem"></a>

`AdGroupTargetingDevicesItem(**data: Any)`
:   Nested schema for AdGroupTargeting.devices_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `label_map: dict[str, typing.Any] | None`
    :   Device models to target, keyed by make

    `max_version: str | None`
    :   Maximum major OS version

    `min_version: str | None`
    :   Minimum major OS version

    `model_config`
    :   The type of the None singleton.

    `os: str | None`
    :   Device OS (ANDROID, IOS)

    `type_: str | None`
    :   Device type (DESKTOP, MOBILE)

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

    `next_link: str | None`
    :   The type of the None singleton.

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

    `next_link: str | None`
    :   The type of the None singleton.

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

    `ad_account_id: str | None`
    :   The ad account this ad belongs to

    `ad_group_id: str | None`
    :   The ad group this ad belongs to

    `campaign_id: str | None`
    :   The campaign this ad belongs to

    `click_url: str | None`
    :   Click destination URL

    `configured_status: str | None`
    :   User-configured status

    `created_at: str | None`
    :   Creation timestamp

    `effective_status: str | None`
    :   Effective delivery status

    `id: str | None`
    :   Unique ad identifier

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   Last modification timestamp

    `name: str | None`
    :   Ad name

    `post_id: str | None`
    :   Reddit post ID (t3_ prefix)

    `post_url: str | None`
    :   Reddit post URL

    `preview_url: str | None`
    :   Ad preview URL

    `rejection_reason: str | None`
    :   Reason the ad was rejected

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

    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[AdsSearchData]
    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[dict[str, Any]]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Business"></a>

`Business(**data: Any)`
:   A Reddit advertising business entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agency_affiliated: bool | None`
    :   The type of the None singleton.

    `country: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `industry: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `primary_contact_id: str | None`
    :   The type of the None singleton.

    `two_fa_enforcement: str | None`
    :   The type of the None singleton.

    `website_url: str | None`
    :   The type of the None singleton.

<a id="BusinessesListResultMeta"></a>

`BusinessesListResultMeta(**data: Any)`
:   Metadata for businesses.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   A Reddit advertising campaign with objective, budget, and scheduling settings.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   The type of the None singleton.

    `age_restriction: str | None`
    :   The type of the None singleton.

    `app_id: str | None`
    :   The type of the None singleton.

    `bid_strategy: str | None`
    :   The type of the None singleton.

    `bid_type: str | None`
    :   The type of the None singleton.

    `bid_value: int | None`
    :   The type of the None singleton.

    `configured_status: str | None`
    :   The type of the None singleton.

    `conversion_pixel_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `delivery_status: list[str] | None`
    :   The type of the None singleton.

    `effective_status: str | None`
    :   The type of the None singleton.

    `end_time: str | None`
    :   The type of the None singleton.

    `funding_instrument_id: str | None`
    :   The type of the None singleton.

    `goal_type: str | None`
    :   The type of the None singleton.

    `goal_value: int | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `invoice_label: str | None`
    :   The type of the None singleton.

    `is_campaign_budget_optimization: bool | None`
    :   The type of the None singleton.

    `is_max: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `objective: str | None`
    :   The type of the None singleton.

    `optimization_goal: str | None`
    :   The type of the None singleton.

    `schedule: list[typing.Any] | None`
    :   The type of the None singleton.

    `skadnetwork_metadata: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `special_ad_categories: list[str] | None`
    :   The type of the None singleton.

    `spend_cap: int | None`
    :   The type of the None singleton.

    `start_time: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `use_catalog: bool | None`
    :   The type of the None singleton.

    `view_through_conversion_type: str | None`
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

    `next_link: str | None`
    :   The type of the None singleton.

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

    `ad_account_id: str | None`
    :   The ad account this campaign belongs to

    `app_id: str | None`
    :   App Store or Play Store ID

    `configured_status: str | None`
    :   User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)

    `created_at: str | None`
    :   Creation timestamp in ISO 8601 format

    `effective_status: str | None`
    :   Effective delivery status

    `funding_instrument_id: str | None`
    :   Funding instrument ID

    `goal_type: str | None`
    :   Goal type (LIFETIME_SPEND, DAILY_SPEND)

    `goal_value: int | None`
    :   Goal value in microcurrency

    `id: str | None`
    :   Unique campaign identifier

    `is_campaign_budget_optimization: bool | None`
    :   Whether campaign budget optimization is enabled

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   Last modification timestamp

    `name: str | None`
    :   Campaign name

    `objective: str | None`
    :   Campaign objective

    `spend_cap: int | None`
    :   Spend cap in microcurrency

<a id="Pagination"></a>

`Pagination(**data: Any)`
:   Pagination metadata for list responses
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_url: str | None`
    :   The type of the None singleton.

    `previous_url: str | None`
    :   The type of the None singleton.

<a id="RedditAdsAuthConfig"></a>

`RedditAdsAuthConfig(**data: Any)`
:   Reddit OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   The OAuth2 client ID from your Reddit developer application.

    `client_secret: str`
    :   The OAuth2 client secret from your Reddit developer application.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The OAuth2 refresh token obtained through the authorization code flow.

<a id="RedditAdsCheckResult"></a>

`RedditAdsCheckResult(**data: Any)`
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

<a id="RedditAdsExecuteResult"></a>

`RedditAdsExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="RedditAdsExecuteResultWithMeta"></a>

`RedditAdsExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[AdAccount], AdAccountsListResultMeta]
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[Ad], AdsListResultMeta]
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[Business], BusinessesListResultMeta]
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`RedditAdsExecuteResultWithMeta[list[AdAccount], AdAccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdAccountsListResult"></a>

`AdAccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`RedditAdsExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
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

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`RedditAdsExecuteResultWithMeta[list[Ad], AdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
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

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`RedditAdsExecuteResultWithMeta[list[Business], BusinessesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BusinessesListResult"></a>

`BusinessesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`RedditAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
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

    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="RedditAdsReplicationConfig"></a>

`RedditAdsReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Reddit Ads.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str`
    :   The Reddit Ads account ID to replicate data from.

    `model_config`
    :   The type of the None singleton.

    `start_time: str | None`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ. Data will be replicated starting from this date. Defaults to 24 months ago.

    `user_agent: str | None`
    :   A unique user agent string identifying the client. Recommended format: platform:app_id:version (by /u/username).