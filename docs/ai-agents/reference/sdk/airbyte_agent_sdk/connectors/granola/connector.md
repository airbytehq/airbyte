---
id: airbyte_agent_sdk-connectors-granola-connector
title: airbyte_agent_sdk.connectors.granola.connector
---

Module airbyte_agent_sdk.connectors.granola.connector
=====================================================
Granola connector.

Classes
-------

<a id="GranolaConnector"></a>

`GranolaConnector(auth_config: GranolaAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Granola API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new granola connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GranolaAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GranolaConnector(auth_config=GranolaAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GranolaConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GranolaConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GranolaAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.granola.connector.GranolaConnector`
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
            A GranolaConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GranolaConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GranolaAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GranolaConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GranolaConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GranolaConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.granola.models.GranolaCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GranolaCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="NotesQuery"></a>

`NotesQuery(connector: GranolaConnector)`
:   Query class for Notes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: NotesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.granola.models.AirbyteSearchResult[NotesSearchData]`
    :   Search notes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (NotesSearchFilter):
        - id: The unique identifier of the note.
        - object_: The object type, always "note".
        - title: The title of the note.
        - owner: The owner of the note.
        - created_at: The creation time of the note in ISO 8601 format.
        - updated_at: The last update time of the note in ISO 8601 format.
        - summary_text: Plain text summary of the note.
        - summary_markdown: Markdown formatted summary of the note.
        - attendees: The attendees of the meeting.
        - calendar_event: Associated calendar event details.
        - folder_membership: The folder membership of the note.
        - transcript: Transcript of the meeting.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            NotesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, note_id: str, include: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.granola.models.Note`
    :   Get a single note by ID, including full details and optionally the transcript
        
        Args:
            note_id: The ID of the note
            include: Include the note transcript in the response
            **kwargs: Additional parameters
        
        Returns:
            Note

    `list(self, page_size: int | None = None, cursor: str | None = None, created_before: str | None = None, created_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.granola.models.GranolaExecuteResultWithMeta[list[Note], NotesListResultMeta]`
    :   Returns a paginated list of meeting notes
        
        Args:
            page_size: Maximum number of notes to return per page
            cursor: Pagination cursor for next page
            created_before: Return notes created before this date (YYYY-MM-DD)
            created_after: Return notes created after this date (YYYY-MM-DD)
            **kwargs: Additional parameters
        
        Returns:
            NotesListResult