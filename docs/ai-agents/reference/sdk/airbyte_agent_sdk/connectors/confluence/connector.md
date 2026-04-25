---
id: airbyte_agent_sdk-connectors-confluence-connector
title: airbyte_agent_sdk.connectors.confluence.connector
---

Module airbyte_agent_sdk.connectors.confluence.connector
========================================================
Confluence connector.

Classes
-------

<a id="AuditQuery"></a>

`AuditQuery(connector: ConfluenceConnector)`
:   Query class for Audit entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AuditSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[AuditSearchData]`
    :   Search audit records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AuditSearchFilter):
        - affected_object: The object that was affected by the audit event.
        - associated_objects: Any associated objects related to the audit event.
        - author: The user who triggered the audit event.
        - category: The category under which the audit event falls.
        - changed_values: Details of the values that were changed during the audit event.
        - creation_date: The date and time when the audit event was created.
        - description: A detailed description of the audit event.
        - remote_address: The IP address from which the audit event originated.
        - summary: A brief summary or title describing the audit event.
        - super_admin: Indicates if the user triggering the audit event is a super admin.
        - sys_admin: Indicates if the user triggering the audit event is a system admin.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AuditSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start: int | None = None, limit: int | None = None, start_date: str | None = None, end_date: str | None = None, search_string: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[AuditRecord], AuditListResultMeta]`
    :   Returns audit log records.
        
        Args:
            start: Starting index for pagination
            limit: Maximum number of audit records to return
            start_date: Start date for filtering audit records (ISO 8601)
            end_date: End date for filtering audit records (ISO 8601)
            search_string: Search string to filter audit records
            **kwargs: Additional parameters
        
        Returns:
            AuditListResult

<a id="BlogPostsQuery"></a>

`BlogPostsQuery(connector: ConfluenceConnector)`
:   Query class for BlogPosts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BlogPostsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[BlogPostsSearchData]`
    :   Search blog_posts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BlogPostsSearchFilter):
        - links: Links related to the blog post
        - author_id: ID of the user who created the blog post
        - body: Blog post body content
        - created_at: Timestamp when the blog post was created
        - id: Unique blog post identifier
        - space_id: ID of the space containing this blog post
        - status: Blog post status (current, draft, trashed)
        - title: Blog post title
        - version: Version information
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BlogPostsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, body_format: str | None = None, version: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.BlogPost`
    :   Returns a specific blog post.
        
        Args:
            id: The ID of the blog post
            body_format: The format of the blog post body in the response
            version: Specific version number to retrieve
            **kwargs: Additional parameters
        
        Returns:
            BlogPost

    `list(self, cursor: str | None = None, limit: int | None = None, space_id: list[int] | None = None, title: str | None = None, status: list[str] | None = None, sort: str | None = None, body_format: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[BlogPost], BlogPostsListResultMeta]`
    :   Returns all blog posts. Only blog posts that the user has permission to view will be returned.
        
        Args:
            cursor: Cursor for pagination
            limit: Maximum number of blog posts to return
            space_id: Filter blog posts by space ID(s)
            title: Filter blog posts by title (exact match)
            status: Filter blog posts by status
            sort: Sort order for results
            body_format: The format of the blog post body in the response
            **kwargs: Additional parameters
        
        Returns:
            BlogPostsListResult

<a id="ConfluenceConnector"></a>

`ConfluenceConnector(auth_config: ConfluenceAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Confluence API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new confluence connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ConfluenceAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Confluence Cloud subdomain (e.g., mycompany for mycompany.atlassian.net)
    Examples:
        # Local mode (direct API calls)
        connector = ConfluenceConnector(auth_config=ConfluenceAuthConfig(username="...", password="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ConfluenceConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ConfluenceConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ConfluenceAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.confluence.connector.ConfluenceConnector`
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
            A ConfluenceConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ConfluenceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ConfluenceAuthConfig(username="...", password="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ConfluenceConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ConfluenceConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ConfluenceConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ConfluenceCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="GroupsQuery"></a>

`GroupsQuery(connector: ConfluenceConnector)`
:   Query class for Groups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[GroupsSearchData]`
    :   Search groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GroupsSearchFilter):
        - links: Links related to the group
        - id: The unique identifier of the group
        - name: The name of the group
        - type_: The type of group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start: int | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[Group], GroupsListResultMeta]`
    :   Returns all user groups.
        
        Args:
            start: Starting index for pagination
            limit: Maximum number of groups to return
            **kwargs: Additional parameters
        
        Returns:
            GroupsListResult

<a id="PagesQuery"></a>

`PagesQuery(connector: ConfluenceConnector)`
:   Query class for Pages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[PagesSearchData]`
    :   Search pages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PagesSearchFilter):
        - links: Links related to the page
        - author_id: ID of the user who created the page
        - body: Page body content
        - created_at: Timestamp when the page was created
        - id: Unique page identifier
        - last_owner_id: ID of the previous page owner
        - owner_id: ID of the current page owner
        - parent_id: ID of the parent page
        - parent_type: Type of the parent (page or space)
        - position: Position of the page among siblings
        - space_id: ID of the space containing this page
        - status: Page status (current, archived, trashed, draft)
        - title: Page title
        - version: Version information
        
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

    `get(self, id: str | None = None, body_format: str | None = None, version: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.Page`
    :   Returns a specific page.
        
        Args:
            id: The ID of the page
            body_format: The format of the page body in the response
            version: Specific version number to retrieve
            **kwargs: Additional parameters
        
        Returns:
            Page

    `list(self, cursor: str | None = None, limit: int | None = None, space_id: list[int] | None = None, title: str | None = None, status: list[str] | None = None, sort: str | None = None, body_format: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[Page], PagesListResultMeta]`
    :   Returns all pages. Only pages that the user has permission to view will be returned.
        
        Args:
            cursor: Cursor for pagination
            limit: Maximum number of pages to return
            space_id: Filter pages by space ID(s)
            title: Filter pages by title (exact match)
            status: Filter pages by status
            sort: Sort order for results
            body_format: The format of the page body in the response
            **kwargs: Additional parameters
        
        Returns:
            PagesListResult

<a id="SpacesQuery"></a>

`SpacesQuery(connector: ConfluenceConnector)`
:   Query class for Spaces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SpacesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[SpacesSearchData]`
    :   Search spaces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SpacesSearchFilter):
        - links: Links related to the space
        - author_id: ID of the user who created the space
        - created_at: Timestamp when the space was created
        - description: Space description in various formats
        - homepage_id: ID of the space homepage
        - icon: Space icon information
        - id: Unique space identifier
        - key: Space key
        - name: Space name
        - status: Space status (current or archived)
        - type_: Space type (global or personal)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SpacesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, description_format: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.Space`
    :   Returns a specific space.
        
        Args:
            id: The ID of the space
            description_format: The format of the space description in the response
            **kwargs: Additional parameters
        
        Returns:
            Space

    `list(self, cursor: str | None = None, limit: int | None = None, type: str | None = None, status: str | None = None, keys: list[str] | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[Space], SpacesListResultMeta]`
    :   Returns all spaces. Only spaces that the user has permission to view will be returned.
        
        Args:
            cursor: Cursor for pagination
            limit: Maximum number of spaces to return
            type: Filter by space type (global or personal)
            status: Filter by space status (current or archived)
            keys: Filter by space keys
            sort: Sort order for results
            **kwargs: Additional parameters
        
        Returns:
            SpacesListResult