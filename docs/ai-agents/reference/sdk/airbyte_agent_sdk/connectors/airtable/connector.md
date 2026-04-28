---
id: airbyte_agent_sdk-connectors-airtable-connector
title: airbyte_agent_sdk.connectors.airtable.connector
---

Module airbyte_agent_sdk.connectors.airtable.connector
======================================================
Airtable connector.

Classes
-------

<a id="AirtableConnector"></a>

`AirtableConnector(auth_config: AirtableAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Airtable API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new airtable connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., AirtableAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = AirtableConnector(auth_config=AirtableAuthConfig(personal_access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = AirtableConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = AirtableConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AirtableAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.airtable.connector.AirtableConnector`
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
            A AirtableConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AirtableConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AirtableAuthConfig(personal_access_token="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AirtableConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AirtableConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AirtableConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.airtable.models.AirtableCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AirtableCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="BasesQuery"></a>

`BasesQuery(connector: AirtableConnector)`
:   Query class for Bases entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BasesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.airtable.models.AirbyteSearchResult[BasesSearchData]`
    :   Search bases records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BasesSearchFilter):
        - id: Unique identifier for the base
        - name: Name of the base
        - permission_level: Permission level for the base
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BasesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.airtable.models.AirtableExecuteResultWithMeta[list[Base], BasesListResultMeta]`
    :   Returns a list of all bases the user has access to
        
        Args:
            offset: Pagination offset from previous response
            **kwargs: Additional parameters
        
        Returns:
            BasesListResult

<a id="RecordsQuery"></a>

`RecordsQuery(connector: AirtableConnector)`
:   Query class for Records entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, base_id: str, table_id_or_name: str, record_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.airtable.models.Record`
    :   Returns a single record by ID from the specified table
        
        Args:
            base_id: The ID of the base
            table_id_or_name: The ID or name of the table
            record_id: The ID of the record
            **kwargs: Additional parameters
        
        Returns:
            Record

    `list(self, base_id: str, table_id_or_name: str, offset: str | None = None, page_size: int | None = None, view: str | None = None, filter_by_formula: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.airtable.models.AirtableExecuteResultWithMeta[list[Record], RecordsListResultMeta]`
    :   Returns a paginated list of records from the specified table
        
        Args:
            base_id: The ID of the base
            table_id_or_name: The ID or name of the table
            offset: Pagination offset from previous response
            page_size: Number of records per page (max 100)
            view: Name or ID of a view to filter records
            filter_by_formula: Airtable formula to filter records
            sort: Sort configuration as JSON array
            **kwargs: Additional parameters
        
        Returns:
            RecordsListResult

<a id="TablesQuery"></a>

`TablesQuery(connector: AirtableConnector)`
:   Query class for Tables entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TablesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.airtable.models.AirbyteSearchResult[TablesSearchData]`
    :   Search tables records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TablesSearchFilter):
        - id: Unique identifier for the table
        - name: Name of the table
        - primary_field_id: ID of the primary field
        - fields: List of fields in the table
        - views: List of views in the table
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TablesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, base_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.airtable.models.AirtableExecuteResult[list[Table]]`
    :   Returns a list of all tables in the specified base with their schema information
        
        Args:
            base_id: The ID of the base
            **kwargs: Additional parameters
        
        Returns:
            TablesListResult