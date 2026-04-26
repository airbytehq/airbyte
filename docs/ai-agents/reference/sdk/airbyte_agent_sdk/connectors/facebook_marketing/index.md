---
id: airbyte_agent_sdk-connectors-facebook_marketing-index
title: airbyte_agent_sdk.connectors.facebook_marketing.index
---

Module airbyte_agent_sdk.connectors.facebook_marketing
======================================================
Facebook-Marketing connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.facebook_marketing.connector
* airbyte_agent_sdk.connectors.facebook_marketing.connector_model
* airbyte_agent_sdk.connectors.facebook_marketing.models
* airbyte_agent_sdk.connectors.facebook_marketing.types

Classes
-------

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

<a id="FacebookMarketingConnector"></a>

`FacebookMarketingConnector(auth_config: FacebookMarketingAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Facebook-Marketing API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new facebook-marketing connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., FacebookMarketingAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = FacebookMarketingConnector(auth_config=FacebookMarketingAuthConfig(access_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = FacebookMarketingConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = FacebookMarketingConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'FacebookMarketingAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'FacebookMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A FacebookMarketingConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await FacebookMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=FacebookMarketingAuthConfig(access_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await FacebookMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=FacebookMarketingAuthConfig(access_token="...", client_id="...", client_secret="..."),
                replication_config=FacebookMarketingReplicationConfig(account_ids="..."),
            )
        
            # With server-side OAuth:
            connector = await FacebookMarketingConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=FacebookMarketingReplicationConfig(account_ids="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'FacebookMarketingReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await FacebookMarketingConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Facebook-Marketing Source",
                replication_config=FacebookMarketingReplicationConfig(account_ids="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @FacebookMarketingConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @FacebookMarketingConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await FacebookMarketingConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.facebook_marketing.models.FacebookMarketingCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            FacebookMarketingCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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