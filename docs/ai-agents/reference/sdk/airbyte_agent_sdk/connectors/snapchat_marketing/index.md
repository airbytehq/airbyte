---
id: airbyte_agent_sdk-connectors-snapchat_marketing-index
title: airbyte_agent_sdk.connectors.snapchat_marketing.index
---

Module airbyte_agent_sdk.connectors.snapchat_marketing
======================================================
Snapchat-Marketing connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.snapchat_marketing.connector
* airbyte_agent_sdk.connectors.snapchat_marketing.connector_model
* airbyte_agent_sdk.connectors.snapchat_marketing.models
* airbyte_agent_sdk.connectors.snapchat_marketing.types

Classes
-------

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

<a id="SnapchatMarketingConnector"></a>

`SnapchatMarketingConnector(auth_config: SnapchatMarketingAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Snapchat-Marketing API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new snapchat-marketing connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SnapchatMarketingAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = SnapchatMarketingConnector(auth_config=SnapchatMarketingAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SnapchatMarketingConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SnapchatMarketingConnector(
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

    `agent_tool(role: AgentToolRole | None = None, *, inspect_tool: str | None = None, docs_tool: str | None = None, max_output_chars: int | None | Unset = UNSET, framework: FrameworkName = 'none', internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Callable[[~_F], ~_F]`
    :   Framework-agnostic decorator for user-written connector tool functions.
        
        The progressive-docs sibling of tool_utils: instead of baking the full
        entity/action reference into the docstring, it instructs the agent to
        call this connector's inspect and docs tools before executing. Tool
        failures raise :class:`airbyte_agent_sdk.AirbyteToolError` by default
        (``framework="none"``, no auto-detection) — pass ``framework=...`` to
        translate to a supported framework's signal instead.
        
        Decorate three functions per connector — execute, inspect and docs.
        The role is inferred from each function's signature (extra parameters
        are allowed); a signature matching more than one role, a generic
        ``(*args, **kwargs)`` wrapper, or a callable whose signature cannot
        be read must pass the role explicitly:
        
        - ``(entity, action, ...)`` -> ``"execute"``
        - ``(section, ...)``        -> ``"read_skill_docs"``
        - ``()``                    -> ``"inspect_connector"``
        
        Usage:
            connector = SnapchatMarketingConnector(...)
        
            @SnapchatMarketingConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @SnapchatMarketingConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @SnapchatMarketingConnector.agent_tool()
            async def read_skill_docs(section: str | None = None):
                return await connector.read_skill_docs(section)
        
        Args:
            role: ``"execute" | "inspect_connector" | "read_skill_docs"``.
                None (default) infers the role from the decorated function's
                signature; an explicit role validates the canonical
                parameters are present (functions accepting ``**kwargs``, or
                callables whose signature cannot be read, pass validation).
            inspect_tool: Exact registered name of the sibling inspect tool,
                woven into the execute docstring for tighter steering.
                Defaults to generic phrasing.
            docs_tool: Exact registered name of the sibling docs tool (see
                inspect_tool).
            max_output_chars: Max serialized output size before failing.
                Defaults per role: execute -> DEFAULT_MAX_OUTPUT_CHARS, docs
                tools -> None.
            framework: Translation target for tool failures. Defaults to
                ``"none"`` (raise AirbyteToolError); never auto-detects.
            internal_retries: How many transient runtime failures (429/5xx,
                network, timeout) to retry silently before surfacing.
                Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs)
                -> bool`` further restricting which retryable errors are safe
                for this specific tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback ``(error,
                args, kwargs) -> str | None`` invoked after internal retries
                are exhausted or skipped. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Add connector-specific documentation and runtime safeguards to one tool.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = SnapchatMarketingConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @SnapchatMarketingConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @SnapchatMarketingConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @SnapchatMarketingConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                `airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate `(error, args, kwargs) -> bool`
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                `(error, args, kwargs) -> str | None`. Invoked after internal retries
                are exhausted or were skipped because `should_internal_retry` returned
                `False`. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.snapchat_marketing.models.SnapchatMarketingCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SnapchatMarketingCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
            select_fields: Optional allowlist of dot-notation fields to include
            exclude_fields: Optional blocklist of dot-notation fields to remove
            skip_truncation: Disable long-text truncation for collection actions
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `inspect_connector(self) ‑> dict[str, typing.Any]`
    :   Inspect this connector's hosted metadata/readiness and resolve its docs skill id.
        
        Call this before read_skill_docs in the normal hosted flow. For
        local/offline connectors this returns a local-mode payload with a
        warning instead of a hosted inspection.
        
        Example:
            info = await connector.inspect_connector()
            print(info["docs_skill_id"])

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

    `read_skill_docs(self, section: str | None = None) ‑> str`
    :   Read this connector's usage docs, rendered to text.
        
        Omit section for the outline and general guidance; pass an exact
        section id from the outline for full details. For local/offline
        connectors the full generated docs are returned and section is
        ignored.
        
        Example:
            outline = await connector.read_skill_docs()
            details = await connector.read_skill_docs(section="entity:contacts")

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