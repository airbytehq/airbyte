---
id: airbyte_agent_sdk-connectors-google_search_console-connector
title: airbyte_agent_sdk.connectors.google_search_console.connector
---

Module airbyte_agent_sdk.connectors.google_search_console.connector
===================================================================
Google-Search-Console connector.

Classes
-------

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

<a id="SearchAnalyticsAllFieldsQuery"></a>

`SearchAnalyticsAllFieldsQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for SearchAnalyticsAllFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchAnalyticsAllFieldsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsAllFieldsSearchData]`
    :   Search search_analytics_all_fields records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchAnalyticsAllFieldsSearchFilter):
        - clicks: The number of times users clicked on the search result for a specific query
        - country: The country from which the search query originated
        - ctr: Click-through rate, calculated as clicks divided by impressions
        - date: The date when the search query occurred
        - device: The type of device used by the user (e.g., desktop, mobile)
        - impressions: The number of times a search result appeared in response to a query
        - page: The page URL that appeared in the search results
        - position: The average position of the search result on the search engine results page
        - query: The search query entered by the user
        - search_type: The type of search (e.g., web, image, video) that triggered the search result
        - site_url: The URL of the site from which the data originates
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchAnalyticsAllFieldsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, site_url: str, dimensions: list[str] | None = None, row_limit: int | None = None, start_row: int | None = None, type: str | None = None, aggregation_type: str | None = None, data_state: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsAllFieldsListResultMeta]`
    :   Query search analytics data grouped by all dimensions (date, country, device, page, query). Returns the most granular breakdown of search data.
        
        
        Args:
            start_date: Start date of the requested date range, in YYYY-MM-DD format.
            end_date: End date of the requested date range, in YYYY-MM-DD format.
            dimensions: Dimensions to group results by.
            row_limit: The maximum number of rows to return.
            start_row: Zero-based index of the first row in the response.
            type: Filter results by type: web, discover, googleNews, news, image, video.
        
            aggregation_type: How data is aggregated: auto, byPage, byProperty.
        
            data_state: Data freshness: final (stable data only) or all (includes fresh data).
        
            site_url: The URL of the property as defined in Search Console.
            **kwargs: Additional parameters
        
        Returns:
            SearchAnalyticsAllFieldsListResult

<a id="SearchAnalyticsByCountryQuery"></a>

`SearchAnalyticsByCountryQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for SearchAnalyticsByCountry entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchAnalyticsByCountrySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByCountrySearchData]`
    :   Search search_analytics_by_country records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchAnalyticsByCountrySearchFilter):
        - clicks: The number of times users clicked on the search result for a specific country
        - country: The country for which the search analytics data is being reported
        - ctr: The click-through rate for a specific country
        - date: The date for which the search analytics data is being reported
        - impressions: The total number of times a search result was shown for a specific country
        - position: The average position at which the site's search result appeared for a specific country
        - search_type: The type of search for which the data is being reported
        - site_url: The URL of the site for which the search analytics data is being reported
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchAnalyticsByCountrySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, site_url: str, dimensions: list[str] | None = None, row_limit: int | None = None, start_row: int | None = None, type: str | None = None, aggregation_type: str | None = None, data_state: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByCountryListResultMeta]`
    :   Query search analytics data grouped by date and country. Returns clicks, impressions, CTR, and average position for each country.
        
        
        Args:
            start_date: Start date of the requested date range, in YYYY-MM-DD format.
            end_date: End date of the requested date range, in YYYY-MM-DD format.
            dimensions: Dimensions to group results by.
            row_limit: The maximum number of rows to return.
            start_row: Zero-based index of the first row in the response.
            type: Filter results by type: web, discover, googleNews, news, image, video.
        
            aggregation_type: How data is aggregated: auto, byPage, byProperty.
        
            data_state: Data freshness: final (stable data only) or all (includes fresh data).
        
            site_url: The URL of the property as defined in Search Console.
            **kwargs: Additional parameters
        
        Returns:
            SearchAnalyticsByCountryListResult

<a id="SearchAnalyticsByDateQuery"></a>

`SearchAnalyticsByDateQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for SearchAnalyticsByDate entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchAnalyticsByDateSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByDateSearchData]`
    :   Search search_analytics_by_date records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchAnalyticsByDateSearchFilter):
        - clicks: The total number of clicks on the specific date
        - ctr: The click-through rate for the specific date
        - date: The date for which the search analytics data is being reported
        - impressions: The number of impressions on the specific date
        - position: The average position in search results for the specific date
        - search_type: The type of search query that generated the data
        - site_url: The URL of the site for which the search analytics data is being reported
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchAnalyticsByDateSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, site_url: str, dimensions: list[str] | None = None, row_limit: int | None = None, start_row: int | None = None, type: str | None = None, aggregation_type: str | None = None, data_state: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByDateListResultMeta]`
    :   Query search analytics data grouped by date. Returns clicks, impressions, CTR, and average position for each date in the specified range.
        
        
        Args:
            start_date: Start date of the requested date range, in YYYY-MM-DD format.
            end_date: End date of the requested date range, in YYYY-MM-DD format.
            dimensions: Dimensions to group results by.
            row_limit: The maximum number of rows to return.
            start_row: Zero-based index of the first row in the response.
            type: Filter results by type: web, discover, googleNews, news, image, video.
        
            aggregation_type: How data is aggregated: auto, byPage, byProperty, byNewsShowcasePanel.
        
            data_state: Data freshness: final (stable data only) or all (includes fresh data).
        
            site_url: The URL of the property as defined in Search Console.
            **kwargs: Additional parameters
        
        Returns:
            SearchAnalyticsByDateListResult

<a id="SearchAnalyticsByDeviceQuery"></a>

`SearchAnalyticsByDeviceQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for SearchAnalyticsByDevice entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchAnalyticsByDeviceSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByDeviceSearchData]`
    :   Search search_analytics_by_device records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchAnalyticsByDeviceSearchFilter):
        - clicks: The total number of clicks by device type
        - ctr: Click-through rate by device type
        - date: The date for which the search analytics data is provided
        - device: The type of device used by the user (e.g., desktop, mobile)
        - impressions: The total number of impressions by device type
        - position: The average position in search results by device type
        - search_type: The type of search performed
        - site_url: The URL of the site for which search analytics data is being provided
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchAnalyticsByDeviceSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, site_url: str, dimensions: list[str] | None = None, row_limit: int | None = None, start_row: int | None = None, type: str | None = None, aggregation_type: str | None = None, data_state: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByDeviceListResultMeta]`
    :   Query search analytics data grouped by date and device. Returns clicks, impressions, CTR, and average position for each device type.
        
        
        Args:
            start_date: Start date of the requested date range, in YYYY-MM-DD format.
            end_date: End date of the requested date range, in YYYY-MM-DD format.
            dimensions: Dimensions to group results by.
            row_limit: The maximum number of rows to return.
            start_row: Zero-based index of the first row in the response.
            type: Filter results by type: web, discover, googleNews, news, image, video.
        
            aggregation_type: How data is aggregated: auto, byPage, byProperty.
        
            data_state: Data freshness: final (stable data only) or all (includes fresh data).
        
            site_url: The URL of the property as defined in Search Console.
            **kwargs: Additional parameters
        
        Returns:
            SearchAnalyticsByDeviceListResult

<a id="SearchAnalyticsByPageQuery"></a>

`SearchAnalyticsByPageQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for SearchAnalyticsByPage entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchAnalyticsByPageSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByPageSearchData]`
    :   Search search_analytics_by_page records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchAnalyticsByPageSearchFilter):
        - clicks: The number of clicks for a specific page
        - ctr: Click-through rate for the page
        - date: The date for which the search analytics data is reported
        - impressions: The number of impressions for the page
        - page: The URL of the specific page being analyzed
        - position: The average position at which the page appeared in search results
        - search_type: The type of search query that led to the page being displayed
        - site_url: The URL of the site for which the search analytics data is being reported
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchAnalyticsByPageSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, site_url: str, dimensions: list[str] | None = None, row_limit: int | None = None, start_row: int | None = None, type: str | None = None, aggregation_type: str | None = None, data_state: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByPageListResultMeta]`
    :   Query search analytics data grouped by date and page. Returns clicks, impressions, CTR, and average position for each page URL.
        
        
        Args:
            start_date: Start date of the requested date range, in YYYY-MM-DD format.
            end_date: End date of the requested date range, in YYYY-MM-DD format.
            dimensions: Dimensions to group results by.
            row_limit: The maximum number of rows to return.
            start_row: Zero-based index of the first row in the response.
            type: Filter results by type: web, discover, googleNews, news, image, video.
        
            aggregation_type: How data is aggregated: auto, byPage, byProperty.
        
            data_state: Data freshness: final (stable data only) or all (includes fresh data).
        
            site_url: The URL of the property as defined in Search Console.
            **kwargs: Additional parameters
        
        Returns:
            SearchAnalyticsByPageListResult

<a id="SearchAnalyticsByQueryQuery"></a>

`SearchAnalyticsByQueryQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for SearchAnalyticsByQuery entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SearchAnalyticsByQuerySearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SearchAnalyticsByQuerySearchData]`
    :   Search search_analytics_by_query records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SearchAnalyticsByQuerySearchFilter):
        - clicks: The number of clicks for the specific query
        - ctr: The click-through rate for the specific query
        - date: The date for which the search analytics data is recorded
        - impressions: The number of impressions for the specific query
        - position: The average position for the specific query
        - query: The search query for which the data is recorded
        - search_type: The type of search result for the specific query
        - site_url: The URL of the site for which the search analytics data is captured
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SearchAnalyticsByQuerySearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start_date: str, end_date: str, site_url: str, dimensions: list[str] | None = None, row_limit: int | None = None, start_row: int | None = None, type: str | None = None, aggregation_type: str | None = None, data_state: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResultWithMeta[list[SearchAnalyticsRow], SearchAnalyticsByQueryListResultMeta]`
    :   Query search analytics data grouped by date and query. Returns clicks, impressions, CTR, and average position for each search query.
        
        
        Args:
            start_date: Start date of the requested date range, in YYYY-MM-DD format.
            end_date: End date of the requested date range, in YYYY-MM-DD format.
            dimensions: Dimensions to group results by.
            row_limit: The maximum number of rows to return.
            start_row: Zero-based index of the first row in the response.
            type: Filter results by type: web, discover, googleNews, news, image, video.
        
            aggregation_type: How data is aggregated: auto, byPage, byProperty.
        
            data_state: Data freshness: final (stable data only) or all (includes fresh data).
        
            site_url: The URL of the property as defined in Search Console.
            **kwargs: Additional parameters
        
        Returns:
            SearchAnalyticsByQueryListResult

<a id="SitemapsQuery"></a>

`SitemapsQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for Sitemaps entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SitemapsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SitemapsSearchData]`
    :   Search sitemaps records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SitemapsSearchFilter):
        - contents: Data related to the sitemap contents
        - errors: Errors encountered while processing the sitemaps
        - is_pending: Flag indicating if the sitemap is pending for processing
        - is_sitemaps_index: Flag indicating if the data represents a sitemap index
        - last_downloaded: Timestamp when the sitemap was last downloaded
        - last_submitted: Timestamp when the sitemap was last submitted
        - path: Path to the sitemap file
        - type_: Type of the sitemap
        - warnings: Warnings encountered while processing the sitemaps
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SitemapsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, site_url: str, feedpath: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.Sitemap`
    :   Retrieves information about a specific sitemap.
        
        Args:
            site_url: The URL of the property as defined in Search Console.
        
            feedpath: The URL of the sitemap.
            **kwargs: Additional parameters
        
        Returns:
            Sitemap

    `list(self, site_url: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult[list[Sitemap]]`
    :   Lists the sitemaps submitted for a site.
        
        Args:
            site_url: The URL of the property as defined in Search Console.
        
            **kwargs: Additional parameters
        
        Returns:
            SitemapsListResult

<a id="SitesQuery"></a>

`SitesQuery(connector: GoogleSearchConsoleConnector)`
:   Query class for Sites entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SitesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_search_console.models.AirbyteSearchResult[SitesSearchData]`
    :   Search sites records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SitesSearchFilter):
        - permission_level: The user's permission level for the site (owner, full, restricted, etc.)
        - site_url: The URL of the site data being fetched
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SitesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, site_url: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.Site`
    :   Retrieves information about a specific site.
        
        Args:
            site_url: The URL of the property as defined in Search Console. Examples: http://www.example.com/ (for a URL-prefix property) or sc-domain:example.com (for a Domain property)
        
            **kwargs: Additional parameters
        
        Returns:
            Site

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.google_search_console.models.GoogleSearchConsoleExecuteResult[list[Site]]`
    :   Lists the user's Search Console sites.
        
        Returns:
            SitesListResult