---
id: airbyte_agent_sdk-connectors-google_search_console-index
title: airbyte_agent_sdk.connectors.google_search_console.index
---

Module airbyte_agent_sdk.connectors.google_search_console
=========================================================
Google-Search-Console connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.google_search_console.connector
* airbyte_agent_sdk.connectors.google_search_console.connector_model
* airbyte_agent_sdk.connectors.google_search_console.models
* airbyte_agent_sdk.connectors.google_search_console.types

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

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsAllFieldsSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByCountrySearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByDateSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByDeviceSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByPageSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByQuerySearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SitemapsSearchData]
    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SitesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="SearchAnalyticsAllFieldsSearchResult"></a>

`SearchAnalyticsAllFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchAnalyticsByCountrySearchResult"></a>

`SearchAnalyticsByCountrySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchAnalyticsByDateSearchResult"></a>

`SearchAnalyticsByDateSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchAnalyticsByDeviceSearchResult"></a>

`SearchAnalyticsByDeviceSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchAnalyticsByPageSearchResult"></a>

`SearchAnalyticsByPageSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchAnalyticsByQuerySearchResult"></a>

`SearchAnalyticsByQuerySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SitemapsSearchResult"></a>

`SitemapsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SitesSearchResult"></a>

`SitesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoogleSearchConsoleAuthConfig"></a>

`GoogleSearchConsoleAuthConfig(**data: Any)`
:   OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   The client ID of your Google Search Console developer application.

    `client_secret: str`
    :   The client secret of your Google Search Console developer application.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The refresh token for obtaining new access tokens.

<a id="GoogleSearchConsoleConnector"></a>

`GoogleSearchConsoleConnector(auth_config: GoogleSearchConsoleAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Google-Search-Console API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new google-search-console connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GoogleSearchConsoleAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GoogleSearchConsoleConnector(auth_config=GoogleSearchConsoleAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GoogleSearchConsoleConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GoogleSearchConsoleConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GoogleSearchConsoleAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GoogleSearchConsoleReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A GoogleSearchConsoleConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GoogleSearchConsoleConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleSearchConsoleAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GoogleSearchConsoleConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleSearchConsoleAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
                replication_config=GoogleSearchConsoleReplicationConfig(site_urls="...", start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await GoogleSearchConsoleConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GoogleSearchConsoleReplicationConfig(site_urls="...", start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GoogleSearchConsoleReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await GoogleSearchConsoleConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Google-Search-Console Source",
                replication_config=GoogleSearchConsoleReplicationConfig(site_urls="...", start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GoogleSearchConsoleConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GoogleSearchConsoleConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GoogleSearchConsoleConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GoogleSearchConsoleCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="GoogleSearchConsoleReplicationConfig"></a>

`GoogleSearchConsoleReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Google Search Console.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `site_urls: str`
    :   The URLs of the website property attached to your GSC account. Examples: https://example.com/ or sc-domain:example.com

    `start_date: str | None`
    :   UTC date in the format YYYY-MM-DD. Any data before this date will not be replicated.

<a id="SearchAnalyticsAllFieldsSearchData"></a>

`SearchAnalyticsAllFieldsSearchData(**data: Any)`
:   Search result data for search_analytics_all_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The number of times users clicked on the search result for a specific query

    `country: str | None`
    :   The country from which the search query originated

    `ctr: float | None`
    :   Click-through rate, calculated as clicks divided by impressions

    `date: str | None`
    :   The date when the search query occurred

    `device: str | None`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: int | None`
    :   The number of times a search result appeared in response to a query

    `model_config`
    :   The type of the None singleton.

    `page: str | None`
    :   The page URL that appeared in the search results

    `position: float | None`
    :   The average position of the search result on the search engine results page

    `query: str | None`
    :   The search query entered by the user

    `search_type: str | None`
    :   The type of search (e.g., web, image, video) that triggered the search result

    `site_url: str | None`
    :   The URL of the site from which the data originates

<a id="SearchAnalyticsByCountrySearchData"></a>

`SearchAnalyticsByCountrySearchData(**data: Any)`
:   Search result data for search_analytics_by_country entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The number of times users clicked on the search result for a specific country

    `country: str | None`
    :   The country for which the search analytics data is being reported

    `ctr: float | None`
    :   The click-through rate for a specific country

    `date: str | None`
    :   The date for which the search analytics data is being reported

    `impressions: int | None`
    :   The total number of times a search result was shown for a specific country

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position at which the site's search result appeared for a specific country

    `search_type: str | None`
    :   The type of search for which the data is being reported

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDateSearchData"></a>

`SearchAnalyticsByDateSearchData(**data: Any)`
:   Search result data for search_analytics_by_date entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The total number of clicks on the specific date

    `ctr: float | None`
    :   The click-through rate for the specific date

    `date: str | None`
    :   The date for which the search analytics data is being reported

    `impressions: int | None`
    :   The number of impressions on the specific date

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position in search results for the specific date

    `search_type: str | None`
    :   The type of search query that generated the data

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByDeviceSearchData"></a>

`SearchAnalyticsByDeviceSearchData(**data: Any)`
:   Search result data for search_analytics_by_device entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The total number of clicks by device type

    `ctr: float | None`
    :   Click-through rate by device type

    `date: str | None`
    :   The date for which the search analytics data is provided

    `device: str | None`
    :   The type of device used by the user (e.g., desktop, mobile)

    `impressions: int | None`
    :   The total number of impressions by device type

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position in search results by device type

    `search_type: str | None`
    :   The type of search performed

    `site_url: str | None`
    :   The URL of the site for which search analytics data is being provided

<a id="SearchAnalyticsByPageSearchData"></a>

`SearchAnalyticsByPageSearchData(**data: Any)`
:   Search result data for search_analytics_by_page entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The number of clicks for a specific page

    `ctr: float | None`
    :   Click-through rate for the page

    `date: str | None`
    :   The date for which the search analytics data is reported

    `impressions: int | None`
    :   The number of impressions for the page

    `model_config`
    :   The type of the None singleton.

    `page: str | None`
    :   The URL of the specific page being analyzed

    `position: float | None`
    :   The average position at which the page appeared in search results

    `search_type: str | None`
    :   The type of search query that led to the page being displayed

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is being reported

<a id="SearchAnalyticsByQuerySearchData"></a>

`SearchAnalyticsByQuerySearchData(**data: Any)`
:   Search result data for search_analytics_by_query entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicks: int | None`
    :   The number of clicks for the specific query

    `ctr: float | None`
    :   The click-through rate for the specific query

    `date: str | None`
    :   The date for which the search analytics data is recorded

    `impressions: int | None`
    :   The number of impressions for the specific query

    `model_config`
    :   The type of the None singleton.

    `position: float | None`
    :   The average position for the specific query

    `query: str | None`
    :   The search query for which the data is recorded

    `search_type: str | None`
    :   The type of search result for the specific query

    `site_url: str | None`
    :   The URL of the site for which the search analytics data is captured

<a id="SitemapsSearchData"></a>

`SitemapsSearchData(**data: Any)`
:   Search result data for sitemaps entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contents: list[typing.Any] | None`
    :   Data related to the sitemap contents

    `errors: str | None`
    :   Errors encountered while processing the sitemaps

    `is_pending: bool | None`
    :   Flag indicating if the sitemap is pending for processing

    `is_sitemaps_index: bool | None`
    :   Flag indicating if the data represents a sitemap index

    `last_downloaded: str | None`
    :   Timestamp when the sitemap was last downloaded

    `last_submitted: str | None`
    :   Timestamp when the sitemap was last submitted

    `model_config`
    :   The type of the None singleton.

    `path: str | None`
    :   Path to the sitemap file

    `type_: str | None`
    :   Type of the sitemap

    `warnings: str | None`
    :   Warnings encountered while processing the sitemaps

<a id="SitesSearchData"></a>

`SitesSearchData(**data: Any)`
:   Search result data for sites entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `permission_level: str | None`
    :   The user's permission level for the site (owner, full, restricted, etc.)

    `site_url: str | None`
    :   The URL of the site data being fetched