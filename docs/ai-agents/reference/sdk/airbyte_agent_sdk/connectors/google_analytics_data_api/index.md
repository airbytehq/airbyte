---
id: airbyte_agent_sdk-connectors-google_analytics_data_api-index
title: airbyte_agent_sdk.connectors.google_analytics_data_api.index
---

Module airbyte_agent_sdk.connectors.google_analytics_data_api
=============================================================
Google-Analytics-Data-Api connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.google_analytics_data_api.connector
* airbyte_agent_sdk.connectors.google_analytics_data_api.connector_model
* airbyte_agent_sdk.connectors.google_analytics_data_api.models
* airbyte_agent_sdk.connectors.google_analytics_data_api.types

Classes
-------

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

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[DailyActiveUsersSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[DevicesSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[FourWeeklyActiveUsersSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[LocationsSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[TrafficSourcesSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[WebsiteOverviewSearchData]
    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[WeeklyActiveUsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="DailyActiveUsersSearchResult"></a>

`DailyActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DevicesSearchResult"></a>

`DevicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FourWeeklyActiveUsersSearchResult"></a>

`FourWeeklyActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="LocationsSearchResult"></a>

`LocationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PagesSearchResult"></a>

`PagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TrafficSourcesSearchResult"></a>

`TrafficSourcesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="WebsiteOverviewSearchResult"></a>

`WebsiteOverviewSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="WeeklyActiveUsersSearchResult"></a>

`WeeklyActiveUsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DailyActiveUsersSearchData"></a>

`DailyActiveUsersSearchData(**data: Any)`
:   Search result data for daily_active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active1_day_users: int | None`
    :   Number of distinct users active in the last 1 day

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="DevicesSearchData"></a>

`DevicesSearchData(**data: Any)`
:   Search result data for devices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `browser: str | None`
    :   The web browser used (e.g., Chrome, Safari, Firefox)

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `device_category: str | None`
    :   The device category (desktop, mobile, tablet)

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `operating_system: str | None`
    :   The operating system used (e.g., Windows, iOS, Android)

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="FourWeeklyActiveUsersSearchData"></a>

`FourWeeklyActiveUsersSearchData(**data: Any)`
:   Search result data for four_weekly_active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active28_day_users: int | None`
    :   Number of distinct users active in the last 28 days

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period

<a id="GoogleAnalyticsDataApiAuthConfig"></a>

`GoogleAnalyticsDataApiAuthConfig(**data: Any)`
:   OAuth 2.0 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   OAuth 2.0 Client ID from Google Cloud Console

    `client_secret: str`
    :   OAuth 2.0 Client Secret from Google Cloud Console

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth 2.0 Refresh Token for obtaining new access tokens

<a id="GoogleAnalyticsDataApiConnector"></a>

`GoogleAnalyticsDataApiConnector(auth_config: GoogleAnalyticsDataApiAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Google-Analytics-Data-Api API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new google-analytics-data-api connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GoogleAnalyticsDataApiAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GoogleAnalyticsDataApiConnector(auth_config=GoogleAnalyticsDataApiAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GoogleAnalyticsDataApiConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GoogleAnalyticsDataApiConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GoogleAnalyticsDataApiAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GoogleAnalyticsDataApiReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A GoogleAnalyticsDataApiConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GoogleAnalyticsDataApiConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleAnalyticsDataApiAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GoogleAnalyticsDataApiConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleAnalyticsDataApiAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
                replication_config=GoogleAnalyticsDataApiReplicationConfig(property_ids="..."),
            )
        
            # With server-side OAuth:
            connector = await GoogleAnalyticsDataApiConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GoogleAnalyticsDataApiReplicationConfig(property_ids="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GoogleAnalyticsDataApiReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await GoogleAnalyticsDataApiConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Google-Analytics-Data-Api Source",
                replication_config=GoogleAnalyticsDataApiReplicationConfig(property_ids="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GoogleAnalyticsDataApiConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GoogleAnalyticsDataApiConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GoogleAnalyticsDataApiConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GoogleAnalyticsDataApiCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="GoogleAnalyticsDataApiReplicationConfig"></a>

`GoogleAnalyticsDataApiReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Google Analytics.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `property_ids: str`
    :   A list of GA4 Property IDs to replicate data from.

<a id="LocationsSearchData"></a>

`LocationsSearchData(**data: Any)`
:   Search result data for locations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `city: str | None`
    :   The city of the user

    `country: str | None`
    :   The country of the user

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `region: str | None`
    :   The region (state/province) of the user

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="PagesSearchData"></a>

`PagesSearchData(**data: Any)`
:   Search result data for pages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `host_name: str | None`
    :   The hostname of the page

    `model_config`
    :   The type of the None singleton.

    `page_path_plus_query_string: str | None`
    :   The page path and query string

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `start_date: str | None`
    :   Start date of the reporting period

<a id="TrafficSourcesSearchData"></a>

`TrafficSourcesSearchData(**data: Any)`
:   Search result data for traffic_sources entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `session_medium: str | None`
    :   The medium of the traffic source (e.g., organic, cpc, referral)

    `session_source: str | None`
    :   The source of the traffic (e.g., google, direct)

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="WebsiteOverviewSearchData"></a>

`WebsiteOverviewSearchData(**data: Any)`
:   Search result data for website_overview entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `average_session_duration: float | None`
    :   Average duration of sessions in seconds

    `bounce_rate: float | None`
    :   Percentage of sessions that were single-page with no interaction

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `new_users: int | None`
    :   Number of first-time users

    `property_id: str`
    :   GA4 property ID

    `screen_page_views: int | None`
    :   Total number of screen or page views

    `screen_page_views_per_session: float | None`
    :   Average page views per session

    `sessions: int | None`
    :   Total number of sessions

    `sessions_per_user: float | None`
    :   Average number of sessions per user

    `start_date: str | None`
    :   Start date of the reporting period

    `total_users: int | None`
    :   Total number of unique users

<a id="WeeklyActiveUsersSearchData"></a>

`WeeklyActiveUsersSearchData(**data: Any)`
:   Search result data for weekly_active_users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active7_day_users: int | None`
    :   Number of distinct users active in the last 7 days

    `date: str | None`
    :   Date of the report row in YYYYMMDD format

    `end_date: str | None`
    :   End date of the reporting period

    `model_config`
    :   The type of the None singleton.

    `property_id: str`
    :   GA4 property ID

    `start_date: str | None`
    :   Start date of the reporting period