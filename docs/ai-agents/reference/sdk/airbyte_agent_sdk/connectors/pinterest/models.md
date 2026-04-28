---
id: airbyte_agent_sdk-connectors-pinterest-models
title: airbyte_agent_sdk.connectors.pinterest.models
---

Module airbyte_agent_sdk.connectors.pinterest.models
====================================================
Pydantic models for pinterest connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Ad"></a>

`Ad(**data: Any)`
:   Pinterest ad object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any | None`
    :   The type of the None singleton.

    `ad_group_id: str | Any | None`
    :   The type of the None singleton.

    `android_deep_link: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `carousel_android_deep_links: list[str] | Any | None`
    :   The type of the None singleton.

    `carousel_destination_urls: list[str] | Any | None`
    :   The type of the None singleton.

    `carousel_ios_deep_links: list[str] | Any | None`
    :   The type of the None singleton.

    `click_tracking_url: str | Any | None`
    :   The type of the None singleton.

    `collection_items_destination_url_template: str | Any | None`
    :   The type of the None singleton.

    `created_time: int | Any | None`
    :   The type of the None singleton.

    `creative_type: str | Any | None`
    :   The type of the None singleton.

    `customizable_cta_type: str | Any | None`
    :   The type of the None singleton.

    `destination_url: str | Any | None`
    :   The type of the None singleton.

    `disclosure_type: str | Any | None`
    :   The type of the None singleton.

    `disclosure_url: str | Any | None`
    :   The type of the None singleton.

    `grid_click_type: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `ios_deep_link: str | Any | None`
    :   The type of the None singleton.

    `is_pin_deleted: bool | Any | None`
    :   The type of the None singleton.

    `is_removable: bool | Any | None`
    :   The type of the None singleton.

    `lead_form_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `pin_id: str | Any | None`
    :   The type of the None singleton.

    `quiz_pin_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `rejected_reasons: list[str] | Any | None`
    :   The type of the None singleton.

    `rejection_labels: list[str] | Any | None`
    :   The type of the None singleton.

    `review_status: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `summary_status: str | Any | None`
    :   The type of the None singleton.

    `tracking_urls: airbyte_agent_sdk.connectors.pinterest.models.AdTrackingUrls | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_time: int | Any | None`
    :   The type of the None singleton.

    `view_tracking_url: str | Any | None`
    :   The type of the None singleton.

<a id="AdAccount"></a>

`AdAccount(**data: Any)`
:   Pinterest ad account object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country: str | Any | None`
    :   The type of the None singleton.

    `created_time: int | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owner: airbyte_agent_sdk.connectors.pinterest.models.AdAccountOwner | Any | None`
    :   The type of the None singleton.

    `permissions: list[str | None] | Any | None`
    :   The type of the None singleton.

    `updated_time: int | Any | None`
    :   The type of the None singleton.

<a id="AdAccountOwner"></a>

`AdAccountOwner(**data: Any)`
:   Owner details of the ad account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   Unique identifier of the owner

    `model_config`
    :   The type of the None singleton.

    `username: str | Any | None`
    :   Username of the owner

<a id="AdAccountsList"></a>

`AdAccountsList(**data: Any)`
:   Paginated list of ad accounts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.AdAccount] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdAccountsSearchData"></a>

`AdAccountsSearchData(**data: Any)`
:   Search result data for ad_accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country: str | None`
    :   Country associated with the ad account

    `created_time: int | None`
    :   Timestamp when the ad account was created (Unix seconds)

    `currency: str | None`
    :   Currency used for billing

    `id: str | None`
    :   Unique identifier for the ad account

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the ad account

    `owner: dict[str, typing.Any] | None`
    :   Owner details of the ad account

    `permissions: list[typing.Any] | None`
    :   Permissions assigned to the ad account

    `updated_time: int | None`
    :   Timestamp when the ad account was last updated (Unix seconds)

<a id="AdGroup"></a>

`AdGroup(**data: Any)`
:   Pinterest ad group object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any | None`
    :   The type of the None singleton.

    `auto_targeting_enabled: bool | Any | None`
    :   The type of the None singleton.

    `bid_in_micro_currency: float | Any | None`
    :   The type of the None singleton.

    `bid_multiplier: float | Any | None`
    :   The type of the None singleton.

    `bid_strategy_type: str | Any | None`
    :   The type of the None singleton.

    `billable_event: str | Any | None`
    :   The type of the None singleton.

    `budget_in_micro_currency: float | Any | None`
    :   The type of the None singleton.

    `budget_type: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `conversion_learning_mode_type: str | Any | None`
    :   The type of the None singleton.

    `created_time: float | Any | None`
    :   The type of the None singleton.

    `end_time: float | Any | None`
    :   The type of the None singleton.

    `feed_profile_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_creative_optimization: bool | Any | None`
    :   The type of the None singleton.

    `lifetime_frequency_cap: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `optimization_goal_metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `pacing_delivery_type: str | Any | None`
    :   The type of the None singleton.

    `placement_group: str | Any | None`
    :   The type of the None singleton.

    `placement_traffic_type: str | Any | None`
    :   The type of the None singleton.

    `promotion_application_level: str | Any | None`
    :   The type of the None singleton.

    `promotion_id: str | Any | None`
    :   The type of the None singleton.

    `promotion_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `start_time: float | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `summary_status: str | Any | None`
    :   The type of the None singleton.

    `targeting_spec: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `targeting_template_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `tracking_urls: airbyte_agent_sdk.connectors.pinterest.models.AdGroupTrackingUrls | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_time: float | Any | None`
    :   The type of the None singleton.

<a id="AdGroupTrackingUrls"></a>

`AdGroupTrackingUrls(**data: Any)`
:   Third-party tracking URLs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audience_verification: list[str] | Any | None`
    :   Audience verification tracking URLs

    `buyable_button: list[str] | Any | None`
    :   Buyable button tracking URLs

    `click: list[str] | Any | None`
    :   Click tracking URLs

    `engagement: list[str] | Any | None`
    :   Engagement tracking URLs

    `impression: list[str] | Any | None`
    :   Impression tracking URLs

    `model_config`
    :   The type of the None singleton.

<a id="AdGroupsList"></a>

`AdGroupsList(**data: Any)`
:   Paginated list of ad groups
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.AdGroup] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `ad_account_id: str | None`
    :   Ad account ID

    `auto_targeting_enabled: bool | None`
    :   Whether auto targeting is enabled

    `bid_in_micro_currency: float | None`
    :   Bid in microcurrency

    `bid_strategy_type: str | None`
    :   Bid strategy type

    `billable_event: str | None`
    :   Billable event type

    `budget_in_micro_currency: float | None`
    :   Budget in microcurrency

    `budget_type: str | None`
    :   Budget type

    `campaign_id: str | None`
    :   Parent campaign ID

    `conversion_learning_mode_type: str | None`
    :   oCPM learn mode type

    `created_time: float | None`
    :   Creation timestamp (Unix seconds)

    `end_time: float | None`
    :   End time (Unix seconds)

    `feed_profile_id: str | None`
    :   Feed profile ID

    `id: str | None`
    :   Ad group ID

    `lifetime_frequency_cap: float | None`
    :   Max impressions per user in 30 days

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad group name

    `optimization_goal_metadata: dict[str, typing.Any] | None`
    :   Optimization goal metadata

    `pacing_delivery_type: str | None`
    :   Pacing delivery type

    `placement_group: str | None`
    :   Placement group

    `start_time: float | None`
    :   Start time (Unix seconds)

    `status: str | None`
    :   Entity status

    `summary_status: str | None`
    :   Summary status

    `targeting_spec: dict[str, typing.Any] | None`
    :   Targeting specifications

    `tracking_urls: dict[str, typing.Any] | None`
    :   Third-party tracking URLs

    `type_: str | None`
    :   Always 'adgroup'

    `updated_time: float | None`
    :   Last update timestamp (Unix seconds)

<a id="AdTrackingUrls"></a>

`AdTrackingUrls(**data: Any)`
:   Third-party tracking URLs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audience_verification: list[str] | Any | None`
    :   Audience verification tracking URLs

    `buyable_button: list[str] | Any | None`
    :   Buyable button tracking URLs

    `click: list[str] | Any | None`
    :   Click tracking URLs

    `engagement: list[str] | Any | None`
    :   Engagement tracking URLs

    `impression: list[str] | Any | None`
    :   Impression tracking URLs

    `model_config`
    :   The type of the None singleton.

<a id="AdsList"></a>

`AdsList(**data: Any)`
:   Paginated list of ads
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.Ad] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
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
    :   Ad account ID

    `ad_group_id: str | None`
    :   Ad group ID

    `android_deep_link: str | None`
    :   Android deep link

    `campaign_id: str | None`
    :   Campaign ID

    `carousel_android_deep_links: list[typing.Any] | None`
    :   Carousel Android deep links

    `carousel_destination_urls: list[typing.Any] | None`
    :   Carousel destination URLs

    `carousel_ios_deep_links: list[typing.Any] | None`
    :   Carousel iOS deep links

    `click_tracking_url: str | None`
    :   Click tracking URL

    `collection_items_destination_url_template: str | None`
    :   Template URL for collection items

    `created_time: int | None`
    :   Creation timestamp (Unix seconds)

    `creative_type: str | None`
    :   Creative type

    `destination_url: str | None`
    :   Main destination URL

    `id: str | None`
    :   Unique ad ID

    `ios_deep_link: str | None`
    :   iOS deep link

    `is_pin_deleted: bool | None`
    :   Whether the original pin is deleted

    `is_removable: bool | None`
    :   Whether the ad is removable

    `lead_form_id: str | None`
    :   Lead form ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad name

    `pin_id: str | None`
    :   Associated pin ID

    `rejected_reasons: list[typing.Any] | None`
    :   Rejection reasons

    `rejection_labels: list[typing.Any] | None`
    :   Rejection text labels

    `review_status: str | None`
    :   Review status

    `status: str | None`
    :   Entity status

    `summary_status: str | None`
    :   Summary status

    `tracking_urls: dict[str, typing.Any] | None`
    :   Third-party tracking URLs

    `type_: str | None`
    :   Always 'pinpromotion'

    `updated_time: int | None`
    :   Last update timestamp (Unix seconds)

    `view_tracking_url: str | None`
    :   View tracking URL

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

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AdAccountsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AdGroupsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AdsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[AudiencesSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[BoardPinsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[BoardSectionsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[BoardsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CatalogsFeedsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CatalogsProductGroupsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CatalogsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[ConversionTagsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[CustomerListsSearchData]
    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult[KeywordsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AdAccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdAccountsSearchResult"></a>

`AdAccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AudiencesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BoardPinsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardPinsSearchResult"></a>

`BoardPinsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BoardSectionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardSectionsSearchResult"></a>

`BoardSectionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BoardsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardsSearchResult"></a>

`BoardsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CatalogsFeedsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsFeedsSearchResult"></a>

`CatalogsFeedsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CatalogsProductGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsProductGroupsSearchResult"></a>

`CatalogsProductGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CatalogsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsSearchResult"></a>

`CatalogsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ConversionTagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ConversionTagsSearchResult"></a>

`ConversionTagsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomerListsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomerListsSearchResult"></a>

`CustomerListsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[KeywordsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="KeywordsSearchResult"></a>

`KeywordsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Audience"></a>

`Audience(**data: Any)`
:   Pinterest audience object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any | None`
    :   The type of the None singleton.

    `audience_type: str | Any | None`
    :   The type of the None singleton.

    `created_by_company_name: str | Any | None`
    :   The type of the None singleton.

    `created_timestamp: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rule: airbyte_agent_sdk.connectors.pinterest.models.AudienceRule | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_timestamp: int | Any | None`
    :   The type of the None singleton.

<a id="AudienceRule"></a>

`AudienceRule(**data: Any)`
:   Audience targeting rules
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country: str | Any | None`
    :   Country criteria

    `customer_list_id: str | Any | None`
    :   Customer list ID

    `engagement_domain: list[str] | Any | None`
    :   Domains for engagement tracking

    `engagement_type: str | Any | None`
    :   Engagement type

    `event: str | Any | None`
    :   Pinterest tag event

    `model_config`
    :   The type of the None singleton.

    `retention_days: int | Any | None`
    :   Days to retain audience data

    `visitor_source_id: str | Any | None`
    :   Visitor source ID

<a id="AudiencesList"></a>

`AudiencesList(**data: Any)`
:   Paginated list of audiences
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.Audience] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
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

    `ad_account_id: str | None`
    :   Ad account ID

    `audience_type: str | None`
    :   Audience type

    `created_timestamp: int | None`
    :   Creation time (Unix seconds)

    `description: str | None`
    :   Audience description

    `id: str | None`
    :   Unique audience identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Audience name

    `rule: dict[str, typing.Any] | None`
    :   Audience targeting rules

    `size: int | None`
    :   Estimated audience size

    `status: str | None`
    :   Audience status

    `type_: str | None`
    :   Always 'audience'

    `updated_timestamp: int | None`
    :   Last update time (Unix seconds)

<a id="Board"></a>

`Board(**data: Any)`
:   Pinterest board object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `board_pins_modified_at: str | Any | None`
    :   The type of the None singleton.

    `collaborator_count: int | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `follower_count: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_ads_only: bool | Any | None`
    :   The type of the None singleton.

    `media: airbyte_agent_sdk.connectors.pinterest.models.BoardMedia | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owner: airbyte_agent_sdk.connectors.pinterest.models.BoardOwner | Any | None`
    :   The type of the None singleton.

    `pin_count: int | Any | None`
    :   The type of the None singleton.

    `privacy: str | Any | None`
    :   The type of the None singleton.

<a id="BoardMedia"></a>

`BoardMedia(**data: Any)`
:   Media content for the board
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `image_cover_url: str | Any | None`
    :   Cover image URL

    `model_config`
    :   The type of the None singleton.

    `pin_thumbnail_urls: list[str] | Any | None`
    :   Thumbnail URLs of pins

<a id="BoardOwner"></a>

`BoardOwner(**data: Any)`
:   Board owner details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `username: str | Any | None`
    :   Username of the board owner

<a id="BoardPin"></a>

`BoardPin(**data: Any)`
:   Pinterest pin on a board
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alt_text: str | Any | None`
    :   The type of the None singleton.

    `board_id: str | Any | None`
    :   The type of the None singleton.

    `board_owner: airbyte_agent_sdk.connectors.pinterest.models.BoardPinBoardOwner | Any | None`
    :   The type of the None singleton.

    `board_section_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `creative_type: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `dominant_color: str | Any | None`
    :   The type of the None singleton.

    `has_been_promoted: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_owner: bool | Any | None`
    :   The type of the None singleton.

    `is_removable: bool | Any | None`
    :   The type of the None singleton.

    `is_standard: bool | Any | None`
    :   The type of the None singleton.

    `link: str | Any | None`
    :   The type of the None singleton.

    `media: airbyte_agent_sdk.connectors.pinterest.models.BoardPinMedia | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent_pin_id: str | Any | None`
    :   The type of the None singleton.

    `pin_metrics: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `product_tags: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="BoardPinBoardOwner"></a>

`BoardPinBoardOwner(**data: Any)`
:   Board owner info
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `username: str | Any | None`
    :   Username of the board owner

<a id="BoardPinMedia"></a>

`BoardPinMedia(**data: Any)`
:   Media content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `media_type: str | Any | None`
    :   Type of media

    `model_config`
    :   The type of the None singleton.

<a id="BoardPinsList"></a>

`BoardPinsList(**data: Any)`
:   Paginated list of board pins
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.BoardPin] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BoardPinsListResultMeta"></a>

`BoardPinsListResultMeta(**data: Any)`
:   Metadata for board_pins.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BoardPinsSearchData"></a>

`BoardPinsSearchData(**data: Any)`
:   Search result data for board_pins entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alt_text: str | None`
    :   Alternate text for accessibility

    `board_id: str | None`
    :   Board the pin belongs to

    `board_owner: dict[str, typing.Any] | None`
    :   Board owner info

    `board_section_id: str | None`
    :   Section within the board

    `created_at: str | None`
    :   Timestamp when the pin was created

    `creative_type: str | None`
    :   Creative type

    `description: str | None`
    :   Pin description

    `dominant_color: str | None`
    :   Dominant color from the pin image

    `has_been_promoted: bool | None`
    :   Whether the pin has been promoted

    `id: str | None`
    :   Unique pin identifier

    `is_owner: bool | None`
    :   Whether the current user is the owner

    `is_standard: bool | None`
    :   Whether the pin is a standard pin

    `link: str | None`
    :   URL link associated with the pin

    `media: dict[str, typing.Any] | None`
    :   Media content

    `model_config`
    :   The type of the None singleton.

    `parent_pin_id: str | None`
    :   Parent pin ID if this is a repin

    `pin_metrics: dict[str, typing.Any] | None`
    :   Pin metrics data

    `title: str | None`
    :   Pin title

<a id="BoardSection"></a>

`BoardSection(**data: Any)`
:   Pinterest board section object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="BoardSectionsList"></a>

`BoardSectionsList(**data: Any)`
:   Paginated list of board sections
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.BoardSection] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BoardSectionsListResultMeta"></a>

`BoardSectionsListResultMeta(**data: Any)`
:   Metadata for board_sections.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BoardSectionsSearchData"></a>

`BoardSectionsSearchData(**data: Any)`
:   Search result data for board_sections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the board section

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the board section

<a id="BoardsList"></a>

`BoardsList(**data: Any)`
:   Paginated list of boards
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.Board] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BoardsListResultMeta"></a>

`BoardsListResultMeta(**data: Any)`
:   Metadata for boards.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BoardsSearchData"></a>

`BoardsSearchData(**data: Any)`
:   Search result data for boards entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `board_pins_modified_at: str | None`
    :   Timestamp when pins on the board were last modified

    `collaborator_count: int | None`
    :   Number of collaborators

    `created_at: str | None`
    :   Timestamp when the board was created

    `description: str | None`
    :   Board description

    `follower_count: int | None`
    :   Number of followers

    `id: str | None`
    :   Unique identifier for the board

    `media: dict[str, typing.Any] | None`
    :   Media content for the board

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Board name

    `owner: dict[str, typing.Any] | None`
    :   Board owner details

    `pin_count: int | None`
    :   Number of pins on the board

    `privacy: str | None`
    :   Board privacy setting

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Pinterest campaign object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any | None`
    :   The type of the None singleton.

    `bid_options: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_time: int | Any | None`
    :   The type of the None singleton.

    `daily_spend_cap: int | Any | None`
    :   The type of the None singleton.

    `end_time: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_automated_campaign: bool | Any | None`
    :   The type of the None singleton.

    `is_campaign_budget_optimization: bool | Any | None`
    :   The type of the None singleton.

    `is_flexible_daily_budgets: bool | Any | None`
    :   The type of the None singleton.

    `is_performance_plus: bool | Any | None`
    :   The type of the None singleton.

    `is_top_of_search: bool | Any | None`
    :   The type of the None singleton.

    `lifetime_spend_cap: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `objective_type: str | Any | None`
    :   The type of the None singleton.

    `order_line_id: str | Any | None`
    :   The type of the None singleton.

    `start_time: int | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `summary_status: str | Any | None`
    :   The type of the None singleton.

    `tracking_urls: airbyte_agent_sdk.connectors.pinterest.models.CampaignTrackingUrls | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_time: int | Any | None`
    :   The type of the None singleton.

<a id="CampaignTrackingUrls"></a>

`CampaignTrackingUrls(**data: Any)`
:   Third-party tracking URLs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `audience_verification: list[str] | Any | None`
    :   Audience verification tracking URLs

    `buyable_button: list[str] | Any | None`
    :   Buyable button tracking URLs

    `click: list[str] | Any | None`
    :   Click tracking URLs

    `engagement: list[str] | Any | None`
    :   Engagement tracking URLs

    `impression: list[str] | Any | None`
    :   Impression tracking URLs

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   Paginated list of campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.Campaign] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
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
    :   Ad account ID

    `created_time: int | None`
    :   Creation timestamp (Unix seconds)

    `daily_spend_cap: int | None`
    :   Maximum daily spend in microcurrency

    `end_time: int | None`
    :   End timestamp (Unix seconds)

    `id: str | None`
    :   Campaign ID

    `is_campaign_budget_optimization: bool | None`
    :   Whether CBO is enabled

    `is_flexible_daily_budgets: bool | None`
    :   Whether flexible daily budgets are enabled

    `lifetime_spend_cap: int | None`
    :   Maximum lifetime spend in microcurrency

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Campaign name

    `objective_type: str | None`
    :   Campaign objective type

    `order_line_id: str | None`
    :   Order line ID on invoice

    `start_time: int | None`
    :   Start timestamp (Unix seconds)

    `status: str | None`
    :   Entity status

    `summary_status: str | None`
    :   Summary status

    `tracking_urls: dict[str, typing.Any] | None`
    :   Third-party tracking URLs

    `type_: str | None`
    :   Always 'campaign'

    `updated_time: int | None`
    :   Last update timestamp (Unix seconds)

<a id="Catalog"></a>

`Catalog(**data: Any)`
:   Pinterest catalog object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_type: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="CatalogsFeed"></a>

`CatalogsFeed(**data: Any)`
:   Pinterest catalog feed object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_type: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `default_availability: str | Any | None`
    :   The type of the None singleton.

    `default_country: str | Any | None`
    :   The type of the None singleton.

    `default_currency: str | Any | None`
    :   The type of the None singleton.

    `default_locale: str | Any | None`
    :   The type of the None singleton.

    `format: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `location: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `preferred_processing_schedule: airbyte_agent_sdk.connectors.pinterest.models.CatalogsFeedPreferredProcessingSchedule | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="CatalogsFeedPreferredProcessingSchedule"></a>

`CatalogsFeedPreferredProcessingSchedule(**data: Any)`
:   Preferred processing schedule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `time: str | Any | None`
    :   Preferred processing time

    `timezone: str | Any | None`
    :   Timezone for processing

<a id="CatalogsFeedsList"></a>

`CatalogsFeedsList(**data: Any)`
:   Paginated list of catalog feeds
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.CatalogsFeed] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsFeedsListResultMeta"></a>

`CatalogsFeedsListResultMeta(**data: Any)`
:   Metadata for catalogs_feeds.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsFeedsSearchData"></a>

`CatalogsFeedsSearchData(**data: Any)`
:   Search result data for catalogs_feeds entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_type: str | None`
    :   Type of catalog

    `created_at: str | None`
    :   Timestamp when the feed was created

    `default_availability: str | None`
    :   Default availability status

    `default_country: str | None`
    :   Default country

    `default_currency: str | None`
    :   Default currency for pricing

    `default_locale: str | None`
    :   Default locale

    `format: str | None`
    :   Feed format

    `id: str | None`
    :   Unique feed identifier

    `location: str | None`
    :   URL where the feed is available

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Feed name

    `preferred_processing_schedule: dict[str, typing.Any] | None`
    :   Preferred processing schedule

    `status: str | None`
    :   Feed status

    `updated_at: str | None`
    :   Timestamp when the feed was last updated

<a id="CatalogsList"></a>

`CatalogsList(**data: Any)`
:   Paginated list of catalogs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.Catalog] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsListResultMeta"></a>

`CatalogsListResultMeta(**data: Any)`
:   Metadata for catalogs.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsProductGroup"></a>

`CatalogsProductGroup(**data: Any)`
:   Pinterest catalog product group object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `feed_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_featured: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

<a id="CatalogsProductGroupsList"></a>

`CatalogsProductGroupsList(**data: Any)`
:   Paginated list of catalog product groups
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.CatalogsProductGroup] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsProductGroupsListResultMeta"></a>

`CatalogsProductGroupsListResultMeta(**data: Any)`
:   Metadata for catalogs_product_groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsProductGroupsSearchData"></a>

`CatalogsProductGroupsSearchData(**data: Any)`
:   Search result data for catalogs_product_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | None`
    :   Creation timestamp (Unix seconds)

    `description: str | None`
    :   Product group description

    `feed_id: str | None`
    :   Associated feed ID

    `id: str | None`
    :   Unique product group identifier

    `is_featured: bool | None`
    :   Whether the product group is featured

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Product group name

    `status: str | None`
    :   Product group status

    `type_: str | None`
    :   Product group type

    `updated_at: int | None`
    :   Last update timestamp (Unix seconds)

<a id="CatalogsSearchData"></a>

`CatalogsSearchData(**data: Any)`
:   Search result data for catalogs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_type: str | None`
    :   Type of catalog

    `created_at: str | None`
    :   Timestamp when the catalog was created

    `id: str | None`
    :   Unique catalog identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Catalog name

    `updated_at: str | None`
    :   Timestamp when the catalog was last updated

<a id="ConversionTag"></a>

`ConversionTag(**data: Any)`
:   Pinterest conversion tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any | None`
    :   The type of the None singleton.

    `code_snippet: str | Any | None`
    :   The type of the None singleton.

    `configs: airbyte_agent_sdk.connectors.pinterest.models.ConversionTagConfigs | Any | None`
    :   The type of the None singleton.

    `enhanced_match_status: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `last_fired_time_ms: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `version: str | Any | None`
    :   The type of the None singleton.

<a id="ConversionTagConfigs"></a>

`ConversionTagConfigs(**data: Any)`
:   Tag configurations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `aem_db_enabled: bool | Any | None`
    :   AEM birthdate integration enabled

    `aem_enabled: bool | Any | None`
    :   AEM email integration enabled

    `aem_fnln_enabled: bool | Any | None`
    :   AEM name integration enabled

    `aem_ge_enabled: bool | Any | None`
    :   AEM gender integration enabled

    `aem_loc_enabled: bool | Any | None`
    :   AEM location integration enabled

    `aem_ph_enabled: bool | Any | None`
    :   AEM phone integration enabled

    `md_frequency: float | Any | None`
    :   Metadata ingestion frequency

    `model_config`
    :   The type of the None singleton.

<a id="ConversionTagsList"></a>

`ConversionTagsList(**data: Any)`
:   Paginated list of conversion tags
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.ConversionTag] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ConversionTagsListResultMeta"></a>

`ConversionTagsListResultMeta(**data: Any)`
:   Metadata for conversion_tags.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ConversionTagsSearchData"></a>

`ConversionTagsSearchData(**data: Any)`
:   Search result data for conversion_tags entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   Ad account ID

    `code_snippet: str | None`
    :   JavaScript code snippet for tracking

    `configs: dict[str, typing.Any] | None`
    :   Tag configurations

    `enhanced_match_status: str | None`
    :   Enhanced match status

    `id: str | None`
    :   Unique conversion tag identifier

    `last_fired_time_ms: int | None`
    :   Timestamp of last event fired (milliseconds)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Conversion tag name

    `status: str | None`
    :   Status

    `version: str | None`
    :   Version number

<a id="CustomerList"></a>

`CustomerList(**data: Any)`
:   Pinterest customer list object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any | None`
    :   The type of the None singleton.

    `created_time: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `num_batches: int | Any | None`
    :   The type of the None singleton.

    `num_removed_user_records: int | Any | None`
    :   The type of the None singleton.

    `num_uploaded_user_records: int | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_time: int | Any | None`
    :   The type of the None singleton.

<a id="CustomerListsList"></a>

`CustomerListsList(**data: Any)`
:   Paginated list of customer lists
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.CustomerList] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerListsListResultMeta"></a>

`CustomerListsListResultMeta(**data: Any)`
:   Metadata for customer_lists.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerListsSearchData"></a>

`CustomerListsSearchData(**data: Any)`
:   Search result data for customer_lists entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   Associated ad account ID

    `created_time: int | None`
    :   Creation time (Unix seconds)

    `id: str | None`
    :   Unique customer list identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Customer list name

    `num_batches: int | None`
    :   Total number of list updates

    `num_removed_user_records: int | None`
    :   Count of removed user records

    `num_uploaded_user_records: int | None`
    :   Count of uploaded user records

    `status: str | None`
    :   Status

    `type_: str | None`
    :   Always 'customerlist'

    `updated_time: int | None`
    :   Last update time (Unix seconds)

<a id="Keyword"></a>

`Keyword(**data: Any)`
:   Pinterest keyword object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   The type of the None singleton.

    `bid: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `match_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent_id: str | Any | None`
    :   The type of the None singleton.

    `parent_type: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

<a id="KeywordsList"></a>

`KeywordsList(**data: Any)`
:   Paginated list of keywords
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bookmark: str | Any | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.pinterest.models.Keyword] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="KeywordsListResultMeta"></a>

`KeywordsListResultMeta(**data: Any)`
:   Metadata for keywords.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="KeywordsSearchData"></a>

`KeywordsSearchData(**data: Any)`
:   Search result data for keywords entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Whether the keyword is archived

    `bid: int | None`
    :   Bid value in microcurrency

    `id: str | None`
    :   Unique keyword identifier

    `match_type: str | None`
    :   Match type

    `model_config`
    :   The type of the None singleton.

    `parent_id: str | None`
    :   Parent entity ID

    `parent_type: str | None`
    :   Parent entity type

    `type_: str | None`
    :   Always 'keyword'

    `value: str | None`
    :   Keyword text value

<a id="PinterestAuthConfig"></a>

`PinterestAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   Pinterest OAuth2 client ID.

    `client_secret: str`
    :   Pinterest OAuth2 client secret.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Pinterest OAuth2 refresh token.

<a id="PinterestCheckResult"></a>

`PinterestCheckResult(**data: Any)`
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

<a id="PinterestExecuteResult"></a>

`PinterestExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="PinterestExecuteResultWithMeta"></a>

`PinterestExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[AdAccount], AdAccountsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Ad], AdsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Audience], AudiencesListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[BoardPin], BoardPinsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[BoardSection], BoardSectionsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Board], BoardsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Catalog], CatalogsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[CatalogsFeed], CatalogsFeedsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[CatalogsProductGroup], CatalogsProductGroupsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[ConversionTag], ConversionTagsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[CustomerList], CustomerListsListResultMeta]
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta[list[Keyword], KeywordsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`PinterestExecuteResultWithMeta[list[AdAccount], AdAccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[Ad], AdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[Audience], AudiencesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[BoardPin], BoardPinsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardPinsListResult"></a>

`BoardPinsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[BoardSection], BoardSectionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardSectionsListResult"></a>

`BoardSectionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[Board], BoardsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BoardsListResult"></a>

`BoardsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
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

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[Catalog], CatalogsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsListResult"></a>

`CatalogsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[CatalogsFeed], CatalogsFeedsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsFeedsListResult"></a>

`CatalogsFeedsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[CatalogsProductGroup], CatalogsProductGroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CatalogsProductGroupsListResult"></a>

`CatalogsProductGroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[ConversionTag], ConversionTagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ConversionTagsListResult"></a>

`ConversionTagsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[CustomerList], CustomerListsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomerListsListResult"></a>

`CustomerListsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PinterestExecuteResultWithMeta[list[Keyword], KeywordsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="KeywordsListResult"></a>

`KeywordsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pinterest.models.PinterestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PinterestReplicationConfig"></a>

`PinterestReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Pinterest.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   A date in the format YYYY-MM-DD. If not set, defaults to 89 days ago.