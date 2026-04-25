---
id: airbyte_agent_sdk-connectors-pinterest-index
title: airbyte_agent_sdk.connectors.pinterest.index
---

Module airbyte_agent_sdk.connectors.pinterest
=============================================
Pinterest connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.pinterest.connector
* airbyte_agent_sdk.connectors.pinterest.connector_model
* airbyte_agent_sdk.connectors.pinterest.models
* airbyte_agent_sdk.connectors.pinterest.types

Classes
-------

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

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

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

<a id="PinterestConnector"></a>

`PinterestConnector(auth_config: PinterestAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Pinterest API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new pinterest connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., PinterestAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = PinterestConnector(auth_config=PinterestAuthConfig(refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = PinterestConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = PinterestConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'PinterestAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'PinterestReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Supports two authentication modes:
        1. Direct credentials: Provide `auth_config` with typed credentials
        2. Server-side OAuth: Provide `server_side_oauth_secret_id` from OAuth flow
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config. Required unless using server_side_oauth_secret_id.
            server_side_oauth_secret_id: OAuth secret ID from get_consent_url redirect.
                When provided, auth_config is not required.
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A PinterestConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await PinterestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PinterestAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await PinterestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=PinterestAuthConfig(refresh_token="...", client_id="...", client_secret="..."),
                replication_config=PinterestReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await PinterestConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=PinterestReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'PinterestReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Initiate server-side OAuth flow with auto-source creation.
        
        Returns a consent URL where the end user should be redirected to grant access.
        After completing consent, the source is automatically created and the user is
        redirected to your redirect_url with a `connector_id` query parameter.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            redirect_url: URL where users will be redirected after OAuth consent.
                After consent, user arrives at: redirect_url?connector_id=...
            name: Optional name for the source. Defaults to connector name + workspace_name.
            replication_config: Typed replication settings. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await PinterestConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Pinterest Source",
                replication_config=PinterestReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @PinterestConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @PinterestConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await PinterestConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.pinterest.models.PinterestCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            PinterestCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

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