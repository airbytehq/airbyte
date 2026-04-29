---
id: airbyte_agent_sdk-connectors-facebook_marketing-models
title: airbyte_agent_sdk.connectors.facebook_marketing.models
---

Module airbyte_agent_sdk.connectors.facebook_marketing.models
=============================================================
Pydantic models for facebook-marketing connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Ad"></a>

`Ad(**data: Any)`
:   Facebook Ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `adlabels: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdLabel] | Any | None`
    :   The type of the None singleton.

    `adset_id: str | Any | None`
    :   The type of the None singleton.

    `bid_amount: int | Any | None`
    :   The type of the None singleton.

    `bid_info: Any`
    :   The type of the None singleton.

    `bid_type: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `configured_status: str | Any | None`
    :   The type of the None singleton.

    `conversion_specs: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `creative: Any`
    :   The type of the None singleton.

    `effective_status: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `last_updated_by_app_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `recommendations: list[airbyte_agent_sdk.connectors.facebook_marketing.models.Recommendation] | Any | None`
    :   The type of the None singleton.

    `source_ad_id: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tracking_specs: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `updated_time: str | Any | None`
    :   The type of the None singleton.

<a id="AdAccount"></a>

`AdAccount(**data: Any)`
:   Facebook Ad Account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `account_status: int | Any | None`
    :   The type of the None singleton.

    `age: float | Any | None`
    :   The type of the None singleton.

    `amount_spent: str | Any | None`
    :   The type of the None singleton.

    `balance: str | Any | None`
    :   The type of the None singleton.

    `business: Any`
    :   The type of the None singleton.

    `business_city: str | Any | None`
    :   The type of the None singleton.

    `business_country_code: str | Any | None`
    :   The type of the None singleton.

    `business_name: str | Any | None`
    :   The type of the None singleton.

    `business_state: str | Any | None`
    :   The type of the None singleton.

    `business_street: str | Any | None`
    :   The type of the None singleton.

    `business_street2: str | Any | None`
    :   The type of the None singleton.

    `business_zip: str | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `disable_reason: int | Any | None`
    :   The type of the None singleton.

    `end_advertiser: str | Any | None`
    :   The type of the None singleton.

    `end_advertiser_name: str | Any | None`
    :   The type of the None singleton.

    `funding_source: str | Any | None`
    :   The type of the None singleton.

    `funding_source_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `has_migrated_permissions: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_personal: int | Any | None`
    :   The type of the None singleton.

    `is_prepay_account: bool | Any | None`
    :   The type of the None singleton.

    `is_tax_id_required: bool | Any | None`
    :   The type of the None singleton.

    `min_campaign_group_spend_cap: str | Any | None`
    :   The type of the None singleton.

    `min_daily_budget: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owner: str | Any | None`
    :   The type of the None singleton.

    `spend_cap: str | Any | None`
    :   The type of the None singleton.

    `timezone_id: int | Any | None`
    :   The type of the None singleton.

    `timezone_name: str | Any | None`
    :   The type of the None singleton.

    `timezone_offset_hours_utc: float | Any | None`
    :   The type of the None singleton.

<a id="AdAccountListItem"></a>

`AdAccountListItem(**data: Any)`
:   Facebook Ad Account in list response
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `account_status: int | Any | None`
    :   The type of the None singleton.

    `age: float | Any | None`
    :   The type of the None singleton.

    `amount_spent: str | Any | None`
    :   The type of the None singleton.

    `balance: str | Any | None`
    :   The type of the None singleton.

    `business: Any`
    :   The type of the None singleton.

    `business_name: str | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `disable_reason: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `spend_cap: str | Any | None`
    :   The type of the None singleton.

    `timezone_id: int | Any | None`
    :   The type of the None singleton.

    `timezone_name: str | Any | None`
    :   The type of the None singleton.

<a id="AdAccountSearchData"></a>

`AdAccountSearchData(**data: Any)`
:   Search result data for ad_account entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID (numeric)

    `account_status: int | None`
    :   Account status

    `amount_spent: str | None`
    :   Total amount spent

    `balance: str | None`
    :   Current balance of the ad account

    `business_name: str | None`
    :   Business name

    `created_time: str | None`
    :   Account creation time

    `currency: str | None`
    :   Currency used by the ad account

    `id: str | None`
    :   Ad account ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad account name

    `spend_cap: str | None`
    :   Spend cap

    `timezone_name: str | None`
    :   Timezone name

<a id="AdAccountsList"></a>

`AdAccountsList(**data: Any)`
:   List of Facebook Ad Accounts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdAccountListItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
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

    `after: str | Any | None`
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

    `account_id: str | None`
    :   Ad account ID (numeric)

    `account_status: int | None`
    :   Account status

    `amount_spent: str | None`
    :   Total amount spent

    `balance: str | None`
    :   Current balance of the ad account

    `business_name: str | None`
    :   Business name

    `created_time: str | None`
    :   Account creation time

    `currency: str | None`
    :   Currency used by the ad account

    `id: str | None`
    :   Ad account ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad account name

    `spend_cap: str | None`
    :   Spend cap

    `timezone_name: str | None`
    :   Timezone name

<a id="AdCreateParams"></a>

`AdCreateParams(**data: Any)`
:   Parameters for creating a new ad. Note - requires a Facebook Page to be connected to the ad account.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adset_id: str | Any`
    :   The type of the None singleton.

    `bid_amount: str | Any | None`
    :   The type of the None singleton.

    `creative: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `tracking_specs: str | Any | None`
    :   The type of the None singleton.

<a id="AdCreateResponse"></a>

`AdCreateResponse(**data: Any)`
:   Response from creating an ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdCreative"></a>

`AdCreative(**data: Any)`
:   Facebook Ad Creative
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `actor_id: str | Any | None`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `call_to_action_type: str | Any | None`
    :   The type of the None singleton.

    `effective_object_story_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `image_hash: str | Any | None`
    :   The type of the None singleton.

    `image_url: str | Any | None`
    :   The type of the None singleton.

    `link_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `object_story_id: str | Any | None`
    :   The type of the None singleton.

    `object_story_spec: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `object_type: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `thumbnail_url: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `url_tags: str | Any | None`
    :   The type of the None singleton.

<a id="AdCreativeRef"></a>

`AdCreativeRef(**data: Any)`
:   AdCreativeRef type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `creative_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdCreativesList"></a>

`AdCreativesList(**data: Any)`
:   AdCreativesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdCreative] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="AdCreativesListResultMeta"></a>

`AdCreativesListResultMeta(**data: Any)`
:   Metadata for ad_creatives.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdCreativesSearchData"></a>

`AdCreativesSearchData(**data: Any)`
:   Search result data for ad_creatives entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `body: str | None`
    :   Ad body text

    `call_to_action_type: str | None`
    :   Call to action type

    `id: str | None`
    :   Ad Creative ID

    `image_url: str | None`
    :   Image URL

    `link_url: str | None`
    :   Link URL

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad Creative name

    `status: str | None`
    :   Creative status

    `thumbnail_url: str | None`
    :   Thumbnail URL

    `title: str | None`
    :   Ad title

<a id="AdLabel"></a>

`AdLabel(**data: Any)`
:   AdLabel type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_time: str | Any | None`
    :   The type of the None singleton.

<a id="AdLibraryAd"></a>

`AdLibraryAd(**data: Any)`
:   An archived ad from the Facebook Ad Library, containing ad creative content, delivery information, spend data, and demographic reach breakdowns.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_creation_time: str | Any | None`
    :   The type of the None singleton.

    `ad_creative_bodies: list[str] | Any | None`
    :   The type of the None singleton.

    `ad_creative_link_captions: list[str] | Any | None`
    :   The type of the None singleton.

    `ad_creative_link_descriptions: list[str] | Any | None`
    :   The type of the None singleton.

    `ad_creative_link_titles: list[str] | Any | None`
    :   The type of the None singleton.

    `ad_delivery_start_time: str | Any | None`
    :   The type of the None singleton.

    `ad_delivery_stop_time: str | Any | None`
    :   The type of the None singleton.

    `ad_snapshot_url: str | Any | None`
    :   The type of the None singleton.

    `age_country_gender_reach_breakdown: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `beneficiary_payers: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `br_total_reach: int | Any | None`
    :   The type of the None singleton.

    `bylines: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `delivery_by_region: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdLibraryAdDeliveryByRegionItem] | Any | None`
    :   The type of the None singleton.

    `demographic_distribution: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdLibraryAdDemographicDistributionItem] | Any | None`
    :   The type of the None singleton.

    `estimated_audience_size: airbyte_agent_sdk.connectors.facebook_marketing.models.AdLibraryAdEstimatedAudienceSize | Any | None`
    :   The type of the None singleton.

    `eu_total_reach: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `impressions: airbyte_agent_sdk.connectors.facebook_marketing.models.AdLibraryAdImpressions | Any | None`
    :   The type of the None singleton.

    `languages: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_id: str | Any | None`
    :   The type of the None singleton.

    `page_name: str | Any | None`
    :   The type of the None singleton.

    `publisher_platforms: list[str] | Any | None`
    :   The type of the None singleton.

    `spend: airbyte_agent_sdk.connectors.facebook_marketing.models.AdLibraryAdSpend | Any | None`
    :   The type of the None singleton.

    `target_ages: list[str] | Any | None`
    :   The type of the None singleton.

    `target_gender: str | Any | None`
    :   The type of the None singleton.

    `target_locations: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `total_reach_by_location: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

<a id="AdLibraryAdDeliveryByRegionItem"></a>

`AdLibraryAdDeliveryByRegionItem(**data: Any)`
:   Nested schema for AdLibraryAd.delivery_by_region_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `percentage: str | Any | None`
    :   Percentage of audience in this region

    `region: str | Any | None`
    :   Region name

<a id="AdLibraryAdDemographicDistributionItem"></a>

`AdLibraryAdDemographicDistributionItem(**data: Any)`
:   Nested schema for AdLibraryAd.demographic_distribution_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `age: str | Any | None`
    :   Age range

    `gender: str | Any | None`
    :   Gender category

    `model_config`
    :   The type of the None singleton.

    `percentage: str | Any | None`
    :   Percentage of audience in this demographic

<a id="AdLibraryAdEstimatedAudienceSize"></a>

`AdLibraryAdEstimatedAudienceSize(**data: Any)`
:   Estimated audience size range
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `lower_bound: int | Any | None`
    :   Lower bound of the estimated audience size

    `model_config`
    :   The type of the None singleton.

    `upper_bound: int | Any | None`
    :   Upper bound of the estimated audience size

<a id="AdLibraryAdImpressions"></a>

`AdLibraryAdImpressions(**data: Any)`
:   Number of impressions as a range
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `lower_bound: int | Any | None`
    :   Lower bound of impressions

    `model_config`
    :   The type of the None singleton.

    `upper_bound: int | Any | None`
    :   Upper bound of impressions

<a id="AdLibraryAdSpend"></a>

`AdLibraryAdSpend(**data: Any)`
:   Amount spent on the ad as a range
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `lower_bound: int | Any | None`
    :   Lower bound of spend

    `model_config`
    :   The type of the None singleton.

    `upper_bound: int | Any | None`
    :   Upper bound of spend

<a id="AdLibraryList"></a>

`AdLibraryList(**data: Any)`
:   AdLibraryList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdLibraryAd] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="AdLibraryListResultMeta"></a>

`AdLibraryListResultMeta(**data: Any)`
:   Metadata for ad_library.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdSet"></a>

`AdSet(**data: Any)`
:   Facebook Ad Set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `adlabels: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdLabel] | Any | None`
    :   The type of the None singleton.

    `bid_amount: float | Any | None`
    :   The type of the None singleton.

    `bid_constraints: Any`
    :   The type of the None singleton.

    `bid_info: Any`
    :   The type of the None singleton.

    `bid_strategy: str | Any | None`
    :   The type of the None singleton.

    `budget_remaining: float | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: float | Any | None`
    :   The type of the None singleton.

    `effective_status: str | Any | None`
    :   The type of the None singleton.

    `end_time: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `learning_stage_info: Any`
    :   The type of the None singleton.

    `lifetime_budget: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `promoted_object: Any`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `targeting: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_time: str | Any | None`
    :   The type of the None singleton.

<a id="AdSetCreateParams"></a>

`AdSetCreateParams(**data: Any)`
:   Parameters for creating a new ad set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bid_amount: str | Any | None`
    :   The type of the None singleton.

    `billing_event: str | Any`
    :   The type of the None singleton.

    `campaign_id: str | Any`
    :   The type of the None singleton.

    `daily_budget: str | Any | None`
    :   The type of the None singleton.

    `end_time: str | Any | None`
    :   The type of the None singleton.

    `lifetime_budget: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `optimization_goal: str | Any`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `targeting: str | Any`
    :   The type of the None singleton.

<a id="AdSetCreateResponse"></a>

`AdSetCreateResponse(**data: Any)`
:   Response from creating an ad set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdSetUpdateParams"></a>

`AdSetUpdateParams(**data: Any)`
:   Parameters for updating an ad set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bid_amount: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: str | Any | None`
    :   The type of the None singleton.

    `end_time: str | Any | None`
    :   The type of the None singleton.

    `lifetime_budget: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `targeting: str | Any | None`
    :   The type of the None singleton.

<a id="AdSetsList"></a>

`AdSetsList(**data: Any)`
:   AdSetsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdSet] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="AdSetsListResultMeta"></a>

`AdSetsListResultMeta(**data: Any)`
:   Metadata for ad_sets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdSetsSearchData"></a>

`AdSetsSearchData(**data: Any)`
:   Search result data for ad_sets entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `bid_amount: float | None`
    :   Bid amount

    `bid_strategy: str | None`
    :   Bid strategy

    `budget_remaining: float | None`
    :   Remaining budget

    `campaign_id: str | None`
    :   Parent campaign ID

    `created_time: str | None`
    :   Ad set creation time

    `daily_budget: float | None`
    :   Daily budget

    `effective_status: str | None`
    :   Effective status

    `end_time: str | None`
    :   Ad set end time

    `id: str | None`
    :   Ad Set ID

    `lifetime_budget: float | None`
    :   Lifetime budget

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad Set name

    `start_time: str | None`
    :   Ad set start time

    `updated_time: str | None`
    :   Last update time

<a id="AdUpdateParams"></a>

`AdUpdateParams(**data: Any)`
:   Parameters for updating an ad
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bid_amount: str | Any | None`
    :   The type of the None singleton.

    `creative: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tracking_specs: str | Any | None`
    :   The type of the None singleton.

<a id="AdsActionStats"></a>

`AdsActionStats(**data: Any)`
:   Action statistics for Facebook ads
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action_destination: str | Any | None`
    :   The type of the None singleton.

    `action_target_id: str | Any | None`
    :   The type of the None singleton.

    `action_type: str | Any | None`
    :   The type of the None singleton.

    `field_1d_click: float | Any | None`
    :   The type of the None singleton.

    `field_1d_view: float | Any | None`
    :   The type of the None singleton.

    `field_28d_click: float | Any | None`
    :   The type of the None singleton.

    `field_28d_view: float | Any | None`
    :   The type of the None singleton.

    `field_7d_click: float | Any | None`
    :   The type of the None singleton.

    `field_7d_view: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: float | Any | None`
    :   The type of the None singleton.

<a id="AdsInsight"></a>

`AdsInsight(**data: Any)`
:   Facebook Ads Insight
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `account_name: str | Any | None`
    :   The type of the None singleton.

    `action_values: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdsActionStats] | Any | None`
    :   The type of the None singleton.

    `actions: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdsActionStats] | Any | None`
    :   The type of the None singleton.

    `ad_id: str | Any | None`
    :   The type of the None singleton.

    `ad_name: str | Any | None`
    :   The type of the None singleton.

    `adset_id: str | Any | None`
    :   The type of the None singleton.

    `adset_name: str | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `campaign_name: str | Any | None`
    :   The type of the None singleton.

    `clicks: int | Any | None`
    :   The type of the None singleton.

    `cpc: float | Any | None`
    :   The type of the None singleton.

    `cpm: float | Any | None`
    :   The type of the None singleton.

    `ctr: float | Any | None`
    :   The type of the None singleton.

    `date_start: str | Any | None`
    :   The type of the None singleton.

    `date_stop: str | Any | None`
    :   The type of the None singleton.

    `impressions: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reach: int | Any | None`
    :   The type of the None singleton.

    `spend: float | Any | None`
    :   The type of the None singleton.

<a id="AdsInsightsList"></a>

`AdsInsightsList(**data: Any)`
:   AdsInsightsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdsInsight] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="AdsInsightsListResultMeta"></a>

`AdsInsightsListResultMeta(**data: Any)`
:   Metadata for ads_insights.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdsInsightsSearchData"></a>

`AdsInsightsSearchData(**data: Any)`
:   Search result data for ads_insights entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `account_name: str | None`
    :   Ad account name

    `action_values: list[typing.Any] | None`
    :   Action values taken on the ad

    `actions: list[typing.Any] | None`
    :   Total number of actions taken

    `ad_id: str | None`
    :   Ad ID

    `ad_name: str | None`
    :   Ad name

    `adset_id: str | None`
    :   Ad set ID

    `adset_name: str | None`
    :   Ad set name

    `campaign_id: str | None`
    :   Campaign ID

    `campaign_name: str | None`
    :   Campaign name

    `clicks: int | None`
    :   Number of clicks

    `cpc: float | None`
    :   Cost per click

    `cpm: float | None`
    :   Cost per 1000 impressions

    `ctr: float | None`
    :   Click-through rate

    `date_start: str | None`
    :   Start date of the reporting period

    `date_stop: str | None`
    :   End date of the reporting period

    `impressions: int | None`
    :   Number of impressions

    `model_config`
    :   The type of the None singleton.

    `reach: int | None`
    :   Number of unique people reached

    `spend: float | None`
    :   Amount spent

<a id="AdsList"></a>

`AdsList(**data: Any)`
:   AdsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.Ad] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
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

    `after: str | Any | None`
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

    `account_id: str | None`
    :   Ad account ID

    `adset_id: str | None`
    :   Parent ad set ID

    `campaign_id: str | None`
    :   Parent campaign ID

    `created_time: str | None`
    :   Ad creation time

    `effective_status: str | None`
    :   Effective status

    `id: str | None`
    :   Ad ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad name

    `status: str | None`
    :   Ad status

    `updated_time: str | None`
    :   Last update time

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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdAccountSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdAccountsSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdCreativesSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdSetsSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdsInsightsSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[AdsSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[CustomConversionsSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[ImagesSearchData]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult[VideosSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AdAccountSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdAccountSearchResult"></a>

`AdAccountSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdAccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdCreativesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdCreativesSearchResult"></a>

`AdCreativesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdSetsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdSetsSearchResult"></a>

`AdSetsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsInsightsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsInsightsSearchResult"></a>

`AdsInsightsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomConversionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomConversionsSearchResult"></a>

`CustomConversionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ImagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ImagesSearchResult"></a>

`ImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[VideosSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="VideosSearchResult"></a>

`VideosSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BidConstraints"></a>

`BidConstraints(**data: Any)`
:   BidConstraints type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `roas_average_floor: int | Any | None`
    :   The type of the None singleton.

<a id="BidInfo"></a>

`BidInfo(**data: Any)`
:   BidInfo type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: int | Any | None`
    :   The type of the None singleton.

    `clicks: int | Any | None`
    :   The type of the None singleton.

    `impressions: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reach: int | Any | None`
    :   The type of the None singleton.

    `social: int | Any | None`
    :   The type of the None singleton.

<a id="BusinessRef"></a>

`BusinessRef(**data: Any)`
:   Reference to a Facebook Business
    
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

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Facebook Ad Campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `adlabels: list[airbyte_agent_sdk.connectors.facebook_marketing.models.AdLabel] | Any | None`
    :   The type of the None singleton.

    `bid_strategy: str | Any | None`
    :   The type of the None singleton.

    `boosted_object_id: str | Any | None`
    :   The type of the None singleton.

    `budget_rebalance_flag: bool | Any | None`
    :   The type of the None singleton.

    `budget_remaining: float | Any | None`
    :   The type of the None singleton.

    `buying_type: str | Any | None`
    :   The type of the None singleton.

    `configured_status: str | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: float | Any | None`
    :   The type of the None singleton.

    `effective_status: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `issues_info: list[airbyte_agent_sdk.connectors.facebook_marketing.models.IssueInfo] | Any | None`
    :   The type of the None singleton.

    `lifetime_budget: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `objective: str | Any | None`
    :   The type of the None singleton.

    `smart_promotion_type: str | Any | None`
    :   The type of the None singleton.

    `source_campaign_id: str | Any | None`
    :   The type of the None singleton.

    `special_ad_category: str | Any | None`
    :   The type of the None singleton.

    `special_ad_category_country: list[str | None] | Any | None`
    :   The type of the None singleton.

    `spend_cap: float | Any | None`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `stop_time: str | Any | None`
    :   The type of the None singleton.

    `updated_time: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignCreateParams"></a>

`CampaignCreateParams(**data: Any)`
:   Parameters for creating a new campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bid_strategy: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: str | Any | None`
    :   The type of the None singleton.

    `is_adset_budget_sharing_enabled: bool | Any | None`
    :   The type of the None singleton.

    `lifetime_budget: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `objective: str | Any`
    :   The type of the None singleton.

    `special_ad_categories: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="CampaignCreateResponse"></a>

`CampaignCreateResponse(**data: Any)`
:   Response from creating a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignUpdateParams"></a>

`CampaignUpdateParams(**data: Any)`
:   Parameters for updating a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bid_strategy: str | Any | None`
    :   The type of the None singleton.

    `daily_budget: str | Any | None`
    :   The type of the None singleton.

    `lifetime_budget: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `spend_cap: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   CampaignsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.Campaign] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
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

    `after: str | Any | None`
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

    `account_id: str | None`
    :   Ad account ID

    `budget_remaining: float | None`
    :   Remaining budget

    `created_time: str | None`
    :   Campaign creation time

    `daily_budget: float | None`
    :   Daily budget in account currency

    `effective_status: str | None`
    :   Effective status

    `id: str | None`
    :   Campaign ID

    `lifetime_budget: float | None`
    :   Lifetime budget

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Campaign name

    `objective: str | None`
    :   Campaign objective

    `start_time: str | None`
    :   Campaign start time

    `status: str | None`
    :   Campaign status

    `stop_time: str | None`
    :   Campaign stop time

    `updated_time: str | None`
    :   Last update time

<a id="CurrentUser"></a>

`CurrentUser(**data: Any)`
:   Current Facebook user associated with the access token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="CustomConversion"></a>

`CustomConversion(**data: Any)`
:   Facebook Custom Conversion
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `business: str | Any | None`
    :   The type of the None singleton.

    `creation_time: str | Any | None`
    :   The type of the None singleton.

    `custom_event_type: str | Any | None`
    :   The type of the None singleton.

    `data_sources: list[airbyte_agent_sdk.connectors.facebook_marketing.models.DataSource] | Any | None`
    :   The type of the None singleton.

    `default_conversion_value: float | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `event_source_type: str | Any | None`
    :   The type of the None singleton.

    `first_fired_time: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_unavailable: bool | Any | None`
    :   The type of the None singleton.

    `last_fired_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `offline_conversion_data_set: str | Any | None`
    :   The type of the None singleton.

    `retention_days: float | Any | None`
    :   The type of the None singleton.

    `rule: str | Any | None`
    :   The type of the None singleton.

<a id="CustomConversionsList"></a>

`CustomConversionsList(**data: Any)`
:   CustomConversionsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.CustomConversion] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="CustomConversionsListResultMeta"></a>

`CustomConversionsListResultMeta(**data: Any)`
:   Metadata for custom_conversions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomConversionsSearchData"></a>

`CustomConversionsSearchData(**data: Any)`
:   Search result data for custom_conversions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `creation_time: str | None`
    :   Creation time

    `custom_event_type: str | None`
    :   Custom event type

    `description: str | None`
    :   Description

    `first_fired_time: str | None`
    :   First fired time

    `id: str | None`
    :   Custom Conversion ID

    `is_archived: bool | None`
    :   Whether the conversion is archived

    `last_fired_time: str | None`
    :   Last fired time

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Custom Conversion name

<a id="DataSource"></a>

`DataSource(**data: Any)`
:   DataSource type definition
    
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

    `source_type: str | Any | None`
    :   The type of the None singleton.

<a id="FacebookMarketingCheckResult"></a>

`FacebookMarketingCheckResult(**data: Any)`
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

<a id="FacebookMarketingExecuteResult"></a>

`FacebookMarketingExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult[list[PixelStat]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="FacebookMarketingExecuteResultWithMeta"></a>

`FacebookMarketingExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdAccountListItem], AdAccountsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdCreative], AdCreativesListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdLibraryAd], AdLibraryListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdSet], AdSetsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[AdsInsight], AdsInsightsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[CustomConversion], CustomConversionsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Image], ImagesListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Pixel], PixelsListResultMeta]
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta[list[Video], VideosListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`FacebookMarketingExecuteResultWithMeta[list[AdAccountListItem], AdAccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[AdCreative], AdCreativesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdCreativesListResult"></a>

`AdCreativesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[AdLibraryAd], AdLibraryListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdLibraryListResult"></a>

`AdLibraryListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[AdSet], AdSetsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdSetsListResult"></a>

`AdSetsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[AdsInsight], AdsInsightsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsInsightsListResult"></a>

`AdsInsightsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
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

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[CustomConversion], CustomConversionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomConversionsListResult"></a>

`CustomConversionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[Image], ImagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ImagesListResult"></a>

`ImagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[Pixel], PixelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PixelsListResult"></a>

`PixelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResultWithMeta[list[Video], VideosListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="VideosListResult"></a>

`VideosListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FacebookMarketingExecuteResult[list[PixelStat]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PixelStatsListResult"></a>

`PixelStatsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FacebookMarketingOauth20AuthenticationAuthConfig"></a>

`FacebookMarketingOauth20AuthenticationAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Facebook OAuth2 Access Token

    `client_id: str | None`
    :   Facebook App Client ID

    `client_secret: str | None`
    :   Facebook App Client Secret

    `model_config`
    :   The type of the None singleton.

<a id="FacebookMarketingReplicationConfig"></a>

`FacebookMarketingReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Facebook Marketing.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_ids: str`
    :   The Facebook Ad account ID(s) to pull data from. The Ad account ID number is in the account dropdown menu or in your browser's address bar of your Meta Ads Manager.

    `model_config`
    :   The type of the None singleton.

<a id="FacebookMarketingServiceAccountKeyAuthenticationAuthConfig"></a>

`FacebookMarketingServiceAccountKeyAuthenticationAuthConfig(**data: Any)`
:   Service Account Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_key: str`
    :   Facebook long-lived access token for Service Account authentication

    `model_config`
    :   The type of the None singleton.

<a id="Image"></a>

`Image(**data: Any)`
:   Image type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `creatives: list[str | None] | Any | None`
    :   The type of the None singleton.

    `filename: str | Any | None`
    :   The type of the None singleton.

    `hash: str | Any | None`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_associated_creatives_in_adgroups: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `original_height: int | Any | None`
    :   The type of the None singleton.

    `original_width: int | Any | None`
    :   The type of the None singleton.

    `permalink_url: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `updated_time: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

    `url_128: str | Any | None`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

<a id="ImagesList"></a>

`ImagesList(**data: Any)`
:   ImagesList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.Image] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="ImagesListResultMeta"></a>

`ImagesListResultMeta(**data: Any)`
:   Metadata for images.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ImagesSearchData"></a>

`ImagesSearchData(**data: Any)`
:   Search result data for images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `created_time: str | None`
    :   Creation time

    `hash: str | None`
    :   Image hash

    `height: int | None`
    :   Image height

    `id: str | None`
    :   Image ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Image name

    `permalink_url: str | None`
    :   Permalink URL

    `status: str | None`
    :   Image status

    `updated_time: str | None`
    :   Last update time

    `url: str | None`
    :   Image URL

    `width: int | None`
    :   Image width

<a id="IssueInfo"></a>

`IssueInfo(**data: Any)`
:   IssueInfo type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `error_code: str | Any | None`
    :   The type of the None singleton.

    `error_message: str | Any | None`
    :   The type of the None singleton.

    `error_summary: str | Any | None`
    :   The type of the None singleton.

    `error_type: str | Any | None`
    :   The type of the None singleton.

    `level: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="LearningStageInfo"></a>

`LearningStageInfo(**data: Any)`
:   LearningStageInfo type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attribution_windows: list[str | None] | Any | None`
    :   The type of the None singleton.

    `conversions: int | Any | None`
    :   The type of the None singleton.

    `last_sig_edit_ts: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

<a id="Paging"></a>

`Paging(**data: Any)`
:   Paging type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursors: airbyte_agent_sdk.connectors.facebook_marketing.models.PagingCursors | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

    `previous: str | Any | None`
    :   The type of the None singleton.

<a id="PagingCursors"></a>

`PagingCursors(**data: Any)`
:   Nested schema for Paging.cursors
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   Cursor for next page

    `before: str | Any | None`
    :   Cursor for previous page

    `model_config`
    :   The type of the None singleton.

<a id="Pixel"></a>

`Pixel(**data: Any)`
:   Facebook Ads Pixel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `creation_time: str | Any | None`
    :   The type of the None singleton.

    `creator: airbyte_agent_sdk.connectors.facebook_marketing.models.PixelCreator | Any | None`
    :   The type of the None singleton.

    `data_use_setting: str | Any | None`
    :   The type of the None singleton.

    `enable_automatic_matching: bool | Any | None`
    :   The type of the None singleton.

    `first_party_cookie_status: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_created_by_app: bool | Any | None`
    :   The type of the None singleton.

    `is_crm: bool | Any | None`
    :   The type of the None singleton.

    `is_unavailable: bool | Any | None`
    :   The type of the None singleton.

    `last_fired_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owner_ad_account: airbyte_agent_sdk.connectors.facebook_marketing.models.PixelOwnerAdAccount | Any | None`
    :   The type of the None singleton.

    `owner_business: airbyte_agent_sdk.connectors.facebook_marketing.models.PixelOwnerBusiness | Any | None`
    :   The type of the None singleton.

<a id="PixelCreator"></a>

`PixelCreator(**data: Any)`
:   User who created the pixel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   Creator user ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Creator user name

<a id="PixelOwnerAdAccount"></a>

`PixelOwnerAdAccount(**data: Any)`
:   Ad account that owns the pixel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   Owner ad account ID

    `id: str | Any | None`
    :   Owner ad account ID (with act_ prefix)

    `model_config`
    :   The type of the None singleton.

<a id="PixelOwnerBusiness"></a>

`PixelOwnerBusiness(**data: Any)`
:   Business that owns the pixel
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   Owner business ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Owner business name

<a id="PixelStat"></a>

`PixelStat(**data: Any)`
:   Facebook Pixel event stat entry showing event counts and quality metrics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.PixelStatDataItem] | Any | None`
    :   The type of the None singleton.

    `event: str | Any | None`
    :   The type of the None singleton.

    `event_source: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `test_events_count: int | Any | None`
    :   The type of the None singleton.

    `total_count: int | Any | None`
    :   The type of the None singleton.

    `total_deduped_count: int | Any | None`
    :   The type of the None singleton.

    `total_matched_count: int | Any | None`
    :   The type of the None singleton.

<a id="PixelStatDataItem"></a>

`PixelStatDataItem(**data: Any)`
:   Nested schema for PixelStat.data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   Timestamp for the data point

    `value: int | Any | None`
    :   Event count at the timestamp

<a id="PixelStatsList"></a>

`PixelStatsList(**data: Any)`
:   PixelStatsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.PixelStat] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PixelsList"></a>

`PixelsList(**data: Any)`
:   PixelsList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.Pixel] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="PixelsListResultMeta"></a>

`PixelsListResultMeta(**data: Any)`
:   Metadata for pixels.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PromotedObject"></a>

`PromotedObject(**data: Any)`
:   PromotedObject type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_id: str | Any | None`
    :   The type of the None singleton.

    `custom_event_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_store_url: str | Any | None`
    :   The type of the None singleton.

    `offer_id: str | Any | None`
    :   The type of the None singleton.

    `page_id: str | Any | None`
    :   The type of the None singleton.

    `pixel_id: str | Any | None`
    :   The type of the None singleton.

    `pixel_rule: str | Any | None`
    :   The type of the None singleton.

    `product_set_id: str | Any | None`
    :   The type of the None singleton.

<a id="Recommendation"></a>

`Recommendation(**data: Any)`
:   Recommendation type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blame_field: str | Any | None`
    :   The type of the None singleton.

    `code: int | Any | None`
    :   The type of the None singleton.

    `confidence: str | Any | None`
    :   The type of the None singleton.

    `importance: str | Any | None`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="UpdateResponse"></a>

`UpdateResponse(**data: Any)`
:   Generic response from update operations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `success: bool | Any`
    :   The type of the None singleton.

<a id="Video"></a>

`Video(**data: Any)`
:   Video type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `ad_breaks: list[int] | Any | None`
    :   The type of the None singleton.

    `backdated_time: str | Any | None`
    :   The type of the None singleton.

    `backdated_time_granularity: str | Any | None`
    :   The type of the None singleton.

    `content_category: str | Any | None`
    :   The type of the None singleton.

    `content_tags: list[str] | Any | None`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `custom_labels: list[str] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `embed_html: str | Any | None`
    :   The type of the None singleton.

    `embeddable: bool | Any | None`
    :   The type of the None singleton.

    `format: list[airbyte_agent_sdk.connectors.facebook_marketing.models.VideoFormat] | Any | None`
    :   The type of the None singleton.

    `icon: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_crosspost_video: bool | Any | None`
    :   The type of the None singleton.

    `is_crossposting_eligible: bool | Any | None`
    :   The type of the None singleton.

    `is_episode: bool | Any | None`
    :   The type of the None singleton.

    `is_instagram_eligible: bool | Any | None`
    :   The type of the None singleton.

    `length: float | Any | None`
    :   The type of the None singleton.

    `live_status: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `permalink_url: str | Any | None`
    :   The type of the None singleton.

    `post_views: int | Any | None`
    :   The type of the None singleton.

    `premiere_living_room_status: bool | Any | None`
    :   The type of the None singleton.

    `published: bool | Any | None`
    :   The type of the None singleton.

    `scheduled_publish_time: str | Any | None`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `universal_video_id: str | Any | None`
    :   The type of the None singleton.

    `updated_time: str | Any | None`
    :   The type of the None singleton.

    `views: int | Any | None`
    :   The type of the None singleton.

<a id="VideoFormat"></a>

`VideoFormat(**data: Any)`
:   VideoFormat type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `embed_html: str | Any | None`
    :   The type of the None singleton.

    `filter: str | Any | None`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `picture: str | Any | None`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

<a id="VideosList"></a>

`VideosList(**data: Any)`
:   VideosList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.facebook_marketing.models.Video] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.facebook_marketing.models.Paging | Any`
    :   The type of the None singleton.

<a id="VideosListResultMeta"></a>

`VideosListResultMeta(**data: Any)`
:   Metadata for videos.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="VideosSearchData"></a>

`VideosSearchData(**data: Any)`
:   Search result data for videos entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Ad account ID

    `created_time: str | None`
    :   Creation time

    `description: str | None`
    :   Video description

    `id: str | None`
    :   Video ID

    `length: float | None`
    :   Video length in seconds

    `model_config`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   Permalink URL

    `source: str | None`
    :   Video source URL

    `title: str | None`
    :   Video title

    `updated_time: str | None`
    :   Last update time

    `views: int | None`
    :   Number of views