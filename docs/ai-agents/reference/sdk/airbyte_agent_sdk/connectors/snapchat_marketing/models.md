---
id: airbyte_agent_sdk-connectors-snapchat_marketing-models
title: airbyte_agent_sdk.connectors.snapchat_marketing.models
---

Module airbyte_agent_sdk.connectors.snapchat_marketing.models
=============================================================
Pydantic models for snapchat-marketing connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Ad"></a>

`Ad(**data: Any)`
:   Snapchat ad object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_squad_id: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `creative_id: str | Any`
    :   The type of the None singleton.

    `delivery_status: list[str] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `render_type: str | Any`
    :   The type of the None singleton.

    `review_status: str | Any`
    :   The type of the None singleton.

    `review_status_reasons: list[str] | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="AdAccount"></a>

`AdAccount(**data: Any)`
:   Snapchat ad account object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advertiser_organization_id: str | Any`
    :   The type of the None singleton.

    `agency_representing_client: bool | Any`
    :   The type of the None singleton.

    `billing_center_id: str | Any`
    :   The type of the None singleton.

    `billing_type: str | Any`
    :   The type of the None singleton.

    `client_paying_invoices: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `funding_source_ids: list[str] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `organization_id: str | Any`
    :   The type of the None singleton.

    `regulations: airbyte_agent_sdk.connectors.snapchat_marketing.models.AdAccountRegulations | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `timezone: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="AdAccountRegulations"></a>

`AdAccountRegulations(**data: Any)`
:   Regulatory settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `restricted_delivery_signals: bool | Any`
    :   Whether restricted delivery signals are enabled

<a id="AdSquad"></a>

`AdSquad(**data: Any)`
:   Snapchat ad squad object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_bid: bool | Any`
    :   The type of the None singleton.

    `bid_strategy: str | Any`
    :   The type of the None singleton.

    `billing_event: str | Any`
    :   The type of the None singleton.

    `campaign_id: str | Any`
    :   The type of the None singleton.

    `child_ad_type: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `creation_state: str | Any`
    :   The type of the None singleton.

    `daily_budget_micro: int | Any`
    :   The type of the None singleton.

    `delivery_constraint: str | Any`
    :   The type of the None singleton.

    `delivery_properties_version: int | Any`
    :   The type of the None singleton.

    `delivery_status: list[str] | Any`
    :   The type of the None singleton.

    `end_time: str | Any`
    :   The type of the None singleton.

    `event_sources: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `forced_view_setting: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `lifetime_budget_micro: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `optimization_goal: str | Any`
    :   The type of the None singleton.

    `pacing_type: str | Any`
    :   The type of the None singleton.

    `placement: str | Any`
    :   The type of the None singleton.

    `skadnetwork_properties: airbyte_agent_sdk.connectors.snapchat_marketing.models.AdSquadSkadnetworkProperties | Any`
    :   The type of the None singleton.

    `start_time: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `target_bid: bool | Any`
    :   The type of the None singleton.

    `targeting: airbyte_agent_sdk.connectors.snapchat_marketing.models.AdSquadTargeting | Any`
    :   The type of the None singleton.

    `targeting_reach_status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="AdSquadSkadnetworkProperties"></a>

`AdSquadSkadnetworkProperties(**data: Any)`
:   SKAdNetwork properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ecid_enrollment_status: str | Any`
    :   The type of the None singleton.

    `enable_skoverlay: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="AdSquadTargeting"></a>

`AdSquadTargeting(**data: Any)`
:   Targeting specification
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_expansion_options: airbyte_agent_sdk.connectors.snapchat_marketing.models.AdSquadTargetingAutoExpansionOptions | Any`
    :   The type of the None singleton.

    `demographics: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `enable_targeting_expansion: bool | Any`
    :   The type of the None singleton.

    `geos: list[airbyte_agent_sdk.connectors.snapchat_marketing.models.AdSquadTargetingGeosItem] | Any`
    :   The type of the None singleton.

    `interests: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `locations: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `regulated_content: bool | Any`
    :   The type of the None singleton.

<a id="AdSquadTargetingAutoExpansionOptions"></a>

`AdSquadTargetingAutoExpansionOptions(**data: Any)`
:   Nested schema for AdSquadTargeting.auto_expansion_options
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `interest_expansion_option: airbyte_agent_sdk.connectors.snapchat_marketing.models.AdSquadTargetingAutoExpansionOptionsInterestExpansionOption | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdSquadTargetingAutoExpansionOptionsInterestExpansionOption"></a>

`AdSquadTargetingAutoExpansionOptionsInterestExpansionOption(**data: Any)`
:   Nested schema for AdSquadTargetingAutoExpansionOptions.interest_expansion_option
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AdSquadTargetingGeosItem"></a>

`AdSquadTargetingGeosItem(**data: Any)`
:   Nested schema for AdSquadTargeting.geos_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country_code: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `operation: str | Any`
    :   The type of the None singleton.

<a id="AdaccountsListResultMeta"></a>

`AdaccountsListResultMeta(**data: Any)`
:   Metadata for adaccounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="AdaccountsSearchData"></a>

`AdaccountsSearchData(**data: Any)`
:   Search result data for adaccounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advertiser_organization_id: str | None`
    :   Advertiser organization ID

    `agency_representing_client: bool | None`
    :   Whether the account is managed by an agency

    `billing_center_id: str | None`
    :   Billing center ID

    `billing_type: str | None`
    :   Billing type

    `client_paying_invoices: bool | None`
    :   Whether the client pays invoices directly

    `created_at: str | None`
    :   Creation timestamp

    `currency: str | None`
    :   Account currency code

    `funding_source_ids: list[typing.Any] | None`
    :   Associated funding source IDs

    `id: str | None`
    :   Unique ad account identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad account name

    `organization_id: str | None`
    :   Parent organization ID

    `regulations: dict[str, typing.Any] | None`
    :   Regulatory settings

    `status: str | None`
    :   Ad account status

    `timezone: str | None`
    :   Account timezone

    `type_: str | None`
    :   Ad account type

    `updated_at: str | None`
    :   Last update timestamp

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

    `next_link: str | Any`
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

    `ad_squad_id: str | None`
    :   Parent ad squad ID

    `created_at: str | None`
    :   Creation timestamp

    `creative_id: str | None`
    :   Associated creative ID

    `delivery_status: list[typing.Any] | None`
    :   Delivery status messages

    `id: str | None`
    :   Unique ad identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad name

    `render_type: str | None`
    :   Render type

    `review_status: str | None`
    :   Review status

    `review_status_reasons: list[typing.Any] | None`
    :   Reasons for review status

    `status: str | None`
    :   Ad status

    `type_: str | None`
    :   Ad type

    `updated_at: str | None`
    :   Last update timestamp

<a id="AdsquadsListResultMeta"></a>

`AdsquadsListResultMeta(**data: Any)`
:   Metadata for adsquads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="AdsquadsSearchData"></a>

`AdsquadsSearchData(**data: Any)`
:   Search result data for adsquads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_bid: bool | None`
    :   Whether auto bidding is enabled

    `bid_strategy: str | None`
    :   Bid strategy

    `billing_event: str | None`
    :   Billing event type

    `campaign_id: str | None`
    :   Parent campaign ID

    `child_ad_type: str | None`
    :   Child ad type

    `created_at: str | None`
    :   Creation timestamp

    `creation_state: str | None`
    :   Creation state

    `daily_budget_micro: int | None`
    :   Daily budget in micro-currency

    `delivery_constraint: str | None`
    :   Delivery constraint

    `delivery_properties_version: int | None`
    :   Delivery properties version

    `delivery_status: list[typing.Any] | None`
    :   Delivery status messages

    `end_time: str | None`
    :   Ad squad end time

    `event_sources: dict[str, typing.Any] | None`
    :   Event sources configuration

    `forced_view_setting: str | None`
    :   Forced view setting

    `id: str | None`
    :   Unique ad squad identifier

    `lifetime_budget_micro: int | None`
    :   Lifetime budget in micro-currency

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Ad squad name

    `optimization_goal: str | None`
    :   Optimization goal

    `pacing_type: str | None`
    :   Pacing type

    `placement: str | None`
    :   Placement type

    `skadnetwork_properties: dict[str, typing.Any] | None`
    :   SKAdNetwork properties

    `start_time: str | None`
    :   Ad squad start time

    `status: str | None`
    :   Ad squad status

    `target_bid: bool | None`
    :   Whether target bid is enabled

    `targeting: dict[str, typing.Any] | None`
    :   Targeting specification

    `targeting_reach_status: str | None`
    :   Targeting reach status

    `type_: str | None`
    :   Ad squad type

    `updated_at: str | None`
    :   Last update timestamp

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

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[AdaccountsSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[AdsSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[AdsquadsSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[CreativesSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[MediaSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[OrganizationsSearchData]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult[SegmentsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AdaccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdaccountsSearchResult"></a>

`AdaccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[AdsquadsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsquadsSearchResult"></a>

`AdsquadsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CreativesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativesSearchResult"></a>

`CreativesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MediaSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MediaSearchResult"></a>

`MediaSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrganizationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationsSearchResult"></a>

`OrganizationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SegmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SegmentsSearchResult"></a>

`SegmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Snapchat campaign object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any`
    :   The type of the None singleton.

    `buy_model: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `creation_state: str | Any`
    :   The type of the None singleton.

    `delivery_status: list[str] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `objective: str | Any`
    :   The type of the None singleton.

    `objective_v2_properties: airbyte_agent_sdk.connectors.snapchat_marketing.models.CampaignObjectiveV2Properties | Any`
    :   The type of the None singleton.

    `pacing_properties_version: int | Any`
    :   The type of the None singleton.

    `start_time: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="CampaignObjectiveV2Properties"></a>

`CampaignObjectiveV2Properties(**data: Any)`
:   Objective V2 properties for the campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_auto_generated: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `objective_v2_type: str | Any`
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

    `next_link: str | Any`
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
    :   Parent ad account ID

    `buy_model: str | None`
    :   Buy model type

    `created_at: str | None`
    :   Creation timestamp

    `creation_state: str | None`
    :   Creation state

    `delivery_status: list[typing.Any] | None`
    :   Delivery status messages

    `id: str | None`
    :   Unique campaign identifier

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

    `updated_at: str | None`
    :   Last update timestamp

<a id="Creative"></a>

`Creative(**data: Any)`
:   Snapchat creative object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any`
    :   The type of the None singleton.

    `ad_product: str | Any`
    :   The type of the None singleton.

    `ad_to_place_properties: airbyte_agent_sdk.connectors.snapchat_marketing.models.CreativeAdToPlaceProperties | Any`
    :   The type of the None singleton.

    `brand_name: str | Any`
    :   The type of the None singleton.

    `call_to_action: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `forced_view_eligibility: str | Any`
    :   The type of the None singleton.

    `headline: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `packaging_status: str | Any`
    :   The type of the None singleton.

    `render_type: str | Any`
    :   The type of the None singleton.

    `review_status: str | Any`
    :   The type of the None singleton.

    `review_status_details: str | Any`
    :   The type of the None singleton.

    `shareable: bool | Any`
    :   The type of the None singleton.

    `top_snap_crop_position: str | Any`
    :   The type of the None singleton.

    `top_snap_media_id: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `web_view_properties: airbyte_agent_sdk.connectors.snapchat_marketing.models.CreativeWebViewProperties | Any`
    :   The type of the None singleton.

<a id="CreativeAdToPlaceProperties"></a>

`CreativeAdToPlaceProperties(**data: Any)`
:   Ad-to-place properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `place_id: str | Any`
    :   The type of the None singleton.

<a id="CreativeWebViewProperties"></a>

`CreativeWebViewProperties(**data: Any)`
:   Web view properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_snap_javascript_sdk: bool | Any`
    :   The type of the None singleton.

    `block_preload: bool | Any`
    :   The type of the None singleton.

    `deep_link_urls: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `use_immersive_mode: bool | Any`
    :   The type of the None singleton.

<a id="CreativesListResultMeta"></a>

`CreativesListResultMeta(**data: Any)`
:   Metadata for creatives.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="CreativesSearchData"></a>

`CreativesSearchData(**data: Any)`
:   Search result data for creatives entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `ad_product: str | None`
    :   Ad product type

    `ad_to_place_properties: dict[str, typing.Any] | None`
    :   Ad-to-place properties

    `brand_name: str | None`
    :   Brand name displayed in the creative

    `call_to_action: str | None`
    :   Call to action text

    `created_at: str | None`
    :   Creation timestamp

    `forced_view_eligibility: str | None`
    :   Forced view eligibility status

    `headline: str | None`
    :   Creative headline

    `id: str | None`
    :   Unique creative identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Creative name

    `packaging_status: str | None`
    :   Packaging status

    `render_type: str | None`
    :   Render type

    `review_status: str | None`
    :   Review status

    `review_status_details: str | None`
    :   Details about the review status

    `shareable: bool | None`
    :   Whether the creative is shareable

    `top_snap_crop_position: str | None`
    :   Top snap crop position

    `top_snap_media_id: str | None`
    :   Top snap media ID

    `type_: str | None`
    :   Creative type

    `updated_at: str | None`
    :   Last update timestamp

    `web_view_properties: dict[str, typing.Any] | None`
    :   Web view properties

<a id="Media"></a>

`Media(**data: Any)`
:   Snapchat media object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `download_link: str | Any`
    :   The type of the None singleton.

    `duration_in_seconds: float | Any`
    :   The type of the None singleton.

    `file_name: str | Any`
    :   The type of the None singleton.

    `file_size_in_bytes: int | Any`
    :   The type of the None singleton.

    `hash: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `image_metadata: airbyte_agent_sdk.connectors.snapchat_marketing.models.MediaImageMetadata | Any`
    :   The type of the None singleton.

    `is_demo_media: bool | Any`
    :   The type of the None singleton.

    `media_status: str | Any`
    :   The type of the None singleton.

    `media_usages: list[str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `video_metadata: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `visibility: str | Any`
    :   The type of the None singleton.

<a id="MediaImageMetadata"></a>

`MediaImageMetadata(**data: Any)`
:   Image-specific metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `height_px: int | Any`
    :   The type of the None singleton.

    `image_format: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `width_px: int | Any`
    :   The type of the None singleton.

<a id="MediaListResultMeta"></a>

`MediaListResultMeta(**data: Any)`
:   Metadata for media.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="MediaSearchData"></a>

`MediaSearchData(**data: Any)`
:   Search result data for media entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `created_at: str | None`
    :   Creation timestamp

    `download_link: str | None`
    :   Download URL for the media

    `duration_in_seconds: float | None`
    :   Duration in seconds for video media

    `file_name: str | None`
    :   Original file name

    `file_size_in_bytes: int | None`
    :   File size in bytes

    `hash: str | None`
    :   Media file hash

    `id: str | None`
    :   Unique media identifier

    `image_metadata: dict[str, typing.Any] | None`
    :   Image-specific metadata

    `is_demo_media: bool | None`
    :   Whether this is demo media

    `media_status: str | None`
    :   Media processing status

    `media_usages: list[typing.Any] | None`
    :   Where the media is used

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Media name

    `type_: str | None`
    :   Media type

    `updated_at: str | None`
    :   Last update timestamp

    `video_metadata: dict[str, typing.Any] | None`
    :   Video-specific metadata

    `visibility: str | None`
    :   Media visibility setting

<a id="Organization"></a>

`Organization(**data: Any)`
:   Snapchat organization object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted_term_version: str | Any`
    :   The type of the None singleton.

    `address_line_1: str | Any`
    :   The type of the None singleton.

    `administrative_district_level_1: str | Any`
    :   The type of the None singleton.

    `configuration_settings: airbyte_agent_sdk.connectors.snapchat_marketing.models.OrganizationConfigurationSettings | Any`
    :   The type of the None singleton.

    `contact_email: str | Any`
    :   The type of the None singleton.

    `contact_name: str | Any`
    :   The type of the None singleton.

    `contact_phone: str | Any`
    :   The type of the None singleton.

    `contact_phone_optin: bool | Any`
    :   The type of the None singleton.

    `country: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `created_by_caller: bool | Any`
    :   The type of the None singleton.

    `demand_source: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_agency: bool | Any`
    :   The type of the None singleton.

    `locality: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `my_display_name: str | Any`
    :   The type of the None singleton.

    `my_invited_email: str | Any`
    :   The type of the None singleton.

    `my_member_id: str | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `postal_code: str | Any`
    :   The type of the None singleton.

    `roles: list[str] | Any`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `verification_request_id: str | Any`
    :   The type of the None singleton.

<a id="OrganizationConfigurationSettings"></a>

`OrganizationConfigurationSettings(**data: Any)`
:   Organization configuration settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `notifications_enabled: bool | Any`
    :   Whether notifications are enabled

<a id="OrganizationsListResultMeta"></a>

`OrganizationsListResultMeta(**data: Any)`
:   Metadata for organizations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="OrganizationsSearchData"></a>

`OrganizationsSearchData(**data: Any)`
:   Search result data for organizations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted_term_version: str | None`
    :   Version of accepted terms

    `address_line_1: str | None`
    :   Street address

    `administrative_district_level_1: str | None`
    :   State or province

    `configuration_settings: dict[str, typing.Any] | None`
    :   Organization configuration settings

    `contact_email: str | None`
    :   Contact email address

    `contact_name: str | None`
    :   Contact person name

    `contact_phone: str | None`
    :   Contact phone number

    `contact_phone_optin: bool | None`
    :   Whether the contact opted in for phone communications

    `country: str | None`
    :   Country code

    `created_at: str | None`
    :   Creation timestamp

    `created_by_caller: bool | None`
    :   Whether the organization was created by the caller

    `id: str | None`
    :   Unique organization identifier

    `locality: str | None`
    :   City or locality

    `model_config`
    :   The type of the None singleton.

    `my_display_name: str | None`
    :   Display name of the authenticated user in the organization

    `my_invited_email: str | None`
    :   Email used to invite the authenticated user

    `my_member_id: str | None`
    :   Member ID of the authenticated user

    `name: str | None`
    :   Organization name

    `postal_code: str | None`
    :   Postal code

    `roles: list[typing.Any] | None`
    :   Roles of the authenticated user in this organization

    `state: str | None`
    :   Organization state

    `type_: str | None`
    :   Organization type

    `updated_at: str | None`
    :   Last update timestamp

<a id="Segment"></a>

`Segment(**data: Any)`
:   Snapchat audience segment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | Any`
    :   The type of the None singleton.

    `approximate_number_users: int | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `organization_id: str | Any`
    :   The type of the None singleton.

    `retention_in_days: int | Any`
    :   The type of the None singleton.

    `source_ad_account_id: str | Any`
    :   The type of the None singleton.

    `source_type: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `targetable_status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `upload_status: str | Any`
    :   The type of the None singleton.

    `visible_to: list[str] | Any`
    :   The type of the None singleton.

<a id="SegmentsListResultMeta"></a>

`SegmentsListResultMeta(**data: Any)`
:   Metadata for segments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="SegmentsSearchData"></a>

`SegmentsSearchData(**data: Any)`
:   Search result data for segments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `approximate_number_users: int | None`
    :   Approximate number of users in the segment

    `created_at: str | None`
    :   Creation timestamp

    `description: str | None`
    :   Segment description

    `id: str | None`
    :   Unique segment identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Segment name

    `organization_id: str | None`
    :   Parent organization ID

    `retention_in_days: int | None`
    :   Data retention period in days

    `source_type: str | None`
    :   Segment source type

    `status: str | None`
    :   Segment status

    `targetable_status: str | None`
    :   Whether the segment is targetable

    `updated_at: str | None`
    :   Last update timestamp

    `upload_status: str | None`
    :   Upload processing status

    `visible_to: list[typing.Any] | None`
    :   Visibility settings

<a id="SnapchatMarketingAuthConfig"></a>

`SnapchatMarketingAuthConfig(**data: Any)`
:   Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   The Client ID of your Snapchat developer application

    `client_secret: str`
    :   The Client Secret of your Snapchat developer application

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Refresh Token to renew the expired Access Token

<a id="SnapchatMarketingCheckResult"></a>

`SnapchatMarketingCheckResult(**data: Any)`
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

<a id="SnapchatMarketingExecuteResult"></a>

`SnapchatMarketingExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="SnapchatMarketingExecuteResultWithMeta"></a>

`SnapchatMarketingExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[AdAccount], AdaccountsListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[AdSquad], AdsquadsListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Creative], CreativesListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Media], MediaListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Organization], OrganizationsListResultMeta]
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta[list[Segment], SegmentsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`SnapchatMarketingExecuteResultWithMeta[list[AdAccount], AdaccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdaccountsListResult"></a>

`AdaccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[AdSquad], AdsquadsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdsquadsListResult"></a>

`AdsquadsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[Ad], AdsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
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

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
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

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[Creative], CreativesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CreativesListResult"></a>

`CreativesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[Media], MediaListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MediaListResult"></a>

`MediaListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[Organization], OrganizationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationsListResult"></a>

`OrganizationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SnapchatMarketingExecuteResultWithMeta[list[Segment], SegmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SegmentsListResult"></a>

`SegmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SnapchatMarketingReplicationConfig"></a>

`SnapchatMarketingReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Snapchat Marketing.
    
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
    :   Date in YYYY-MM-DD format. Data before this date will not be replicated.