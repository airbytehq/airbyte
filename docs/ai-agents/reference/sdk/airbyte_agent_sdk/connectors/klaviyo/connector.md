---
id: airbyte_agent_sdk-connectors-klaviyo-connector
title: airbyte_agent_sdk.connectors.klaviyo.connector
---

Module airbyte_agent_sdk.connectors.klaviyo.connector
=====================================================
Klaviyo connector.

Classes
-------

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: KlaviyoConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - attributes: 
        - id: 
        - links: 
        - relationships: 
        - type_: 
        - updated_at: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.Campaign`
    :   Get a single campaign by ID
        
        Args:
            id: Campaign ID
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, filter: str, page_size: int | None = None, page_cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns a paginated list of campaigns. A channel filter is required.
        
        Args:
            filter: Filter by channel (email or sms)
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="EmailTemplatesQuery"></a>

`EmailTemplatesQuery(connector: KlaviyoConnector)`
:   Query class for EmailTemplates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EmailTemplatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[EmailTemplatesSearchData]`
    :   Search email_templates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EmailTemplatesSearchFilter):
        - attributes: 
        - id: 
        - links: 
        - type_: 
        - updated: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EmailTemplatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.Template`
    :   Get a single email template by ID
        
        Args:
            id: Template ID
            **kwargs: Additional parameters
        
        Returns:
            Template

    `list(self, page_size: int | None = None, page_cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Template], EmailTemplatesListResultMeta]`
    :   Returns a paginated list of email templates
        
        Args:
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            EmailTemplatesListResult

<a id="EventsQuery"></a>

`EventsQuery(connector: KlaviyoConnector)`
:   Query class for Events entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EventsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[EventsSearchData]`
    :   Search events records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EventsSearchFilter):
        - attributes: 
        - datetime: 
        - id: 
        - links: 
        - relationships: 
        - type_: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EventsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, page_cursor: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Event], EventsListResultMeta]`
    :   Returns a paginated list of events (actions taken by profiles)
        
        Args:
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            sort: Sort order for events
            **kwargs: Additional parameters
        
        Returns:
            EventsListResult

<a id="FlowsQuery"></a>

`FlowsQuery(connector: KlaviyoConnector)`
:   Query class for Flows entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FlowsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[FlowsSearchData]`
    :   Search flows records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FlowsSearchFilter):
        - attributes: 
        - id: 
        - links: 
        - relationships: 
        - type_: 
        - updated: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FlowsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.Flow`
    :   Get a single flow by ID
        
        Args:
            id: Flow ID
            **kwargs: Additional parameters
        
        Returns:
            Flow

    `list(self, page_size: int | None = None, page_cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Flow], FlowsListResultMeta]`
    :   Returns a paginated list of flows (automated sequences)
        
        Args:
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            FlowsListResult

<a id="KlaviyoConnector"></a>

`KlaviyoConnector(auth_config: KlaviyoAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Klaviyo API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new klaviyo connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., KlaviyoAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = KlaviyoConnector(auth_config=KlaviyoAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = KlaviyoConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = KlaviyoConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'KlaviyoAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.connector.KlaviyoConnector`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A KlaviyoConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await KlaviyoConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=KlaviyoAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @KlaviyoConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @KlaviyoConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await KlaviyoConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            KlaviyoCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="ListsQuery"></a>

`ListsQuery(connector: KlaviyoConnector)`
:   Query class for Lists entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[ListsSearchData]`
    :   Search lists records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListsSearchFilter):
        - attributes: 
        - id: 
        - links: 
        - relationships: 
        - type_: 
        - updated: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ListsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.List`
    :   Get a single list by ID
        
        Args:
            id: List ID
            **kwargs: Additional parameters
        
        Returns:
            List

    `list(self, page_size: int | None = None, page_cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[List], ListsListResultMeta]`
    :   Returns a paginated list of all lists in your Klaviyo account
        
        Args:
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            ListsListResult

<a id="MetricsQuery"></a>

`MetricsQuery(connector: KlaviyoConnector)`
:   Query class for Metrics entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MetricsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[MetricsSearchData]`
    :   Search metrics records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MetricsSearchFilter):
        - attributes: 
        - id: 
        - links: 
        - relationships: 
        - type_: 
        - updated: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MetricsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.Metric`
    :   Get a single metric by ID
        
        Args:
            id: Metric ID
            **kwargs: Additional parameters
        
        Returns:
            Metric

    `list(self, page_size: int | None = None, page_cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Metric], MetricsListResultMeta]`
    :   Returns a paginated list of metrics (event types)
        
        Args:
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            MetricsListResult

<a id="ProfilesQuery"></a>

`ProfilesQuery(connector: KlaviyoConnector)`
:   Query class for Profiles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProfilesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[ProfilesSearchData]`
    :   Search profiles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProfilesSearchFilter):
        - attributes: 
        - id: 
        - links: 
        - relationships: 
        - segments: 
        - type_: 
        - updated: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProfilesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.Profile`
    :   Get a single profile by ID
        
        Args:
            id: Profile ID
            **kwargs: Additional parameters
        
        Returns:
            Profile

    `list(self, page_size: int | None = None, page_cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Profile], ProfilesListResultMeta]`
    :   Returns a paginated list of profiles (contacts) in your Klaviyo account
        
        Args:
            page_size: Number of results per page (max 100)
            page_cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            ProfilesListResult