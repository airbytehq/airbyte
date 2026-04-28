---
id: airbyte_agent_sdk-connectors-google_analytics_data_api-connector
title: airbyte_agent_sdk.connectors.google_analytics_data_api.connector
---

Module airbyte_agent_sdk.connectors.google_analytics_data_api.connector
=======================================================================
Google-Analytics-Data-Api connector.

Classes
-------

<a id="DailyActiveUsersQuery"></a>

`DailyActiveUsersQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for DailyActiveUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DailyActiveUsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[DailyActiveUsersSearchData]`
    :   Search daily_active_users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DailyActiveUsersSearchFilter):
        - active1_day_users: Number of distinct users active in the last 1 day
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - property_id: GA4 property ID
        - start_date: Start date of the reporting period
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DailyActiveUsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[DailyActiveUsersListParamsDaterangesItem] | None = None, dimensions: list[DailyActiveUsersListParamsDimensionsItem] | None = None, metrics: list[DailyActiveUsersListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], DailyActiveUsersListResultMeta]`
    :   Returns daily active user counts (1-day active users) by date.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            DailyActiveUsersListResult

<a id="DevicesQuery"></a>

`DevicesQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for Devices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DevicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[DevicesSearchData]`
    :   Search devices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DevicesSearchFilter):
        - average_session_duration: Average duration of sessions in seconds
        - bounce_rate: Percentage of sessions that were single-page with no interaction
        - browser: The web browser used (e.g., Chrome, Safari, Firefox)
        - date: Date of the report row in YYYYMMDD format
        - device_category: The device category (desktop, mobile, tablet)
        - end_date: End date of the reporting period
        - new_users: Number of first-time users
        - operating_system: The operating system used (e.g., Windows, iOS, Android)
        - property_id: GA4 property ID
        - screen_page_views: Total number of screen or page views
        - screen_page_views_per_session: Average page views per session
        - sessions: Total number of sessions
        - sessions_per_user: Average number of sessions per user
        - start_date: Start date of the reporting period
        - total_users: Total number of unique users
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DevicesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[DevicesListParamsDaterangesItem] | None = None, dimensions: list[DevicesListParamsDimensionsItem] | None = None, metrics: list[DevicesListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], DevicesListResultMeta]`
    :   Returns device-related metrics broken down by device category, operating system, browser, and date, including users, sessions, and page views.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            DevicesListResult

<a id="FourWeeklyActiveUsersQuery"></a>

`FourWeeklyActiveUsersQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for FourWeeklyActiveUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FourWeeklyActiveUsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[FourWeeklyActiveUsersSearchData]`
    :   Search four_weekly_active_users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FourWeeklyActiveUsersSearchFilter):
        - active28_day_users: Number of distinct users active in the last 28 days
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - property_id: GA4 property ID
        - start_date: Start date of the reporting period
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FourWeeklyActiveUsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[FourWeeklyActiveUsersListParamsDaterangesItem] | None = None, dimensions: list[FourWeeklyActiveUsersListParamsDimensionsItem] | None = None, metrics: list[FourWeeklyActiveUsersListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], FourWeeklyActiveUsersListResultMeta]`
    :   Returns 28-day active user counts by date.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            FourWeeklyActiveUsersListResult

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

<a id="LocationsQuery"></a>

`LocationsQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for Locations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: LocationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[LocationsSearchData]`
    :   Search locations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (LocationsSearchFilter):
        - average_session_duration: Average duration of sessions in seconds
        - bounce_rate: Percentage of sessions that were single-page with no interaction
        - city: The city of the user
        - country: The country of the user
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - new_users: Number of first-time users
        - property_id: GA4 property ID
        - region: The region (state/province) of the user
        - screen_page_views: Total number of screen or page views
        - screen_page_views_per_session: Average page views per session
        - sessions: Total number of sessions
        - sessions_per_user: Average number of sessions per user
        - start_date: Start date of the reporting period
        - total_users: Total number of unique users
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            LocationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[LocationsListParamsDaterangesItem] | None = None, dimensions: list[LocationsListParamsDimensionsItem] | None = None, metrics: list[LocationsListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], LocationsListResultMeta]`
    :   Returns geographic metrics broken down by region, country, city, and date, including users, sessions, bounce rate, and page views.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            LocationsListResult

<a id="PagesQuery"></a>

`PagesQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for Pages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[PagesSearchData]`
    :   Search pages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PagesSearchFilter):
        - bounce_rate: Percentage of sessions that were single-page with no interaction
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - host_name: The hostname of the page
        - page_path_plus_query_string: The page path and query string
        - property_id: GA4 property ID
        - screen_page_views: Total number of screen or page views
        - start_date: Start date of the reporting period
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[PagesListParamsDaterangesItem] | None = None, dimensions: list[PagesListParamsDimensionsItem] | None = None, metrics: list[PagesListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], PagesListResultMeta]`
    :   Returns page-level metrics including page views and bounce rate, broken down by host name, page path, and date.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            PagesListResult

<a id="TrafficSourcesQuery"></a>

`TrafficSourcesQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for TrafficSources entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TrafficSourcesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[TrafficSourcesSearchData]`
    :   Search traffic_sources records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TrafficSourcesSearchFilter):
        - average_session_duration: Average duration of sessions in seconds
        - bounce_rate: Percentage of sessions that were single-page with no interaction
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - new_users: Number of first-time users
        - property_id: GA4 property ID
        - screen_page_views: Total number of screen or page views
        - screen_page_views_per_session: Average page views per session
        - session_medium: The medium of the traffic source (e.g., organic, cpc, referral)
        - session_source: The source of the traffic (e.g., google, direct)
        - sessions: Total number of sessions
        - sessions_per_user: Average number of sessions per user
        - start_date: Start date of the reporting period
        - total_users: Total number of unique users
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TrafficSourcesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[TrafficSourcesListParamsDaterangesItem] | None = None, dimensions: list[TrafficSourcesListParamsDimensionsItem] | None = None, metrics: list[TrafficSourcesListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], TrafficSourcesListResultMeta]`
    :   Returns traffic source metrics broken down by session source, session medium, and date, including users, sessions, bounce rate, and page views.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            TrafficSourcesListResult

<a id="WebsiteOverviewQuery"></a>

`WebsiteOverviewQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for WebsiteOverview entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WebsiteOverviewSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[WebsiteOverviewSearchData]`
    :   Search website_overview records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WebsiteOverviewSearchFilter):
        - average_session_duration: Average duration of sessions in seconds
        - bounce_rate: Percentage of sessions that were single-page with no interaction
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - new_users: Number of first-time users
        - property_id: GA4 property ID
        - screen_page_views: Total number of screen or page views
        - screen_page_views_per_session: Average page views per session
        - sessions: Total number of sessions
        - sessions_per_user: Average number of sessions per user
        - start_date: Start date of the reporting period
        - total_users: Total number of unique users
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            WebsiteOverviewSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[WebsiteOverviewListParamsDaterangesItem] | None = None, dimensions: list[WebsiteOverviewListParamsDimensionsItem] | None = None, metrics: list[WebsiteOverviewListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], WebsiteOverviewListResultMeta]`
    :   Returns website overview metrics including total users, new users, sessions, bounce rate, page views, and average session duration by date.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            WebsiteOverviewListResult

<a id="WeeklyActiveUsersQuery"></a>

`WeeklyActiveUsersQuery(connector: GoogleAnalyticsDataApiConnector)`
:   Query class for WeeklyActiveUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WeeklyActiveUsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.AirbyteSearchResult[WeeklyActiveUsersSearchData]`
    :   Search weekly_active_users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WeeklyActiveUsersSearchFilter):
        - active7_day_users: Number of distinct users active in the last 7 days
        - date: Date of the report row in YYYYMMDD format
        - end_date: End date of the reporting period
        - property_id: GA4 property ID
        - start_date: Start date of the reporting period
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            WeeklyActiveUsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, property_id: str, date_ranges: list[WeeklyActiveUsersListParamsDaterangesItem] | None = None, dimensions: list[WeeklyActiveUsersListParamsDimensionsItem] | None = None, metrics: list[WeeklyActiveUsersListParamsMetricsItem] | None = None, keep_empty_rows: bool | None = None, return_property_quota: bool | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_analytics_data_api.models.GoogleAnalyticsDataApiExecuteResultWithMeta[list[Row], WeeklyActiveUsersListResultMeta]`
    :   Returns weekly active user counts (7-day active users) by date.
        
        Args:
            date_ranges: Parameter dateRanges
            dimensions: Parameter dimensions
            metrics: Parameter metrics
            keep_empty_rows: Parameter keepEmptyRows
            return_property_quota: Parameter returnPropertyQuota
            limit: Parameter limit
            property_id: GA4 property ID
            **kwargs: Additional parameters
        
        Returns:
            WeeklyActiveUsersListResult