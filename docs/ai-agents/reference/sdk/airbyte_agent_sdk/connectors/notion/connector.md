---
id: airbyte_agent_sdk-connectors-notion-connector
title: airbyte_agent_sdk.connectors.notion.connector
---

Module airbyte_agent_sdk.connectors.notion.connector
====================================================
Notion connector.

Classes
-------

<a id="BlocksQuery"></a>

`BlocksQuery(connector: NotionConnector)`
:   Query class for Blocks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BlocksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[BlocksSearchData]`
    :   Search blocks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BlocksSearchFilter):
        - archived: Indicates if the block is archived or not.
        - bookmark: Represents a bookmark within the block
        - breadcrumb: Represents a breadcrumb block.
        - bulleted_list_item: Represents an item in a bulleted list.
        - callout: Describes a callout message or content in the block
        - child_database: Represents a child database block.
        - child_page: Represents a child page block.
        - code: Contains code snippets or blocks in the block content
        - column: Represents a column block.
        - column_list: Represents a list of columns.
        - created_by: The user who created the block.
        - created_time: The timestamp when the block was created.
        - divider: Represents a divider block.
        - embed: Contains embedded content such as videos, tweets, etc.
        - equation: Represents an equation or mathematical formula in the block
        - file: Represents a file block.
        - has_children: Indicates if the block has children or not.
        - heading_1: Represents a level 1 heading.
        - heading_2: Represents a level 2 heading.
        - heading_3: Represents a level 3 heading.
        - id: The unique identifier of the block.
        - image: Represents an image block.
        - last_edited_by: The user who last edited the block.
        - last_edited_time: The timestamp when the block was last edited.
        - link_preview: Displays a preview of an external link within the block
        - link_to_page: Provides a link to another page within the block
        - numbered_list_item: Represents an item in a numbered list.
        - object_: Represents an object block.
        - paragraph: Represents a paragraph block.
        - parent: The parent block of the current block.
        - pdf: Represents a PDF document block.
        - quote: Represents a quote block.
        - synced_block: Represents a block synced from another source
        - table: Represents a table within the block
        - table_of_contents: Contains information regarding the table of contents
        - table_row: Represents a row in a table within the block
        - template: Specifies a template used within the block
        - to_do: Represents a to-do list or task content
        - toggle: Represents a toggle block.
        - type_: The type of the block.
        - unsupported: Represents an unsupported block.
        - video: Represents a video block.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BlocksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, block_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.Block`
    :   Retrieves a block object using the ID specified
        
        Args:
            block_id: Block ID
            **kwargs: Additional parameters
        
        Returns:
            Block

    `list(self, block_id: str, start_cursor: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[Block], BlocksListResultMeta]`
    :   Returns a paginated list of child blocks for the specified block
        
        Args:
            block_id: Block or page ID
            start_cursor: Pagination cursor for next page
            page_size: Number of items per page (max 100)
            **kwargs: Additional parameters
        
        Returns:
            BlocksListResult

<a id="CommentsQuery"></a>

`CommentsQuery(connector: NotionConnector)`
:   Query class for Comments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, block_id: str, start_cursor: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[Comment], CommentsListResultMeta]`
    :   Returns a list of comments for a specified block or page
        
        Args:
            block_id: Block or page ID to retrieve comments for
            start_cursor: Pagination cursor for next page
            page_size: Number of items per page (max 100)
            **kwargs: Additional parameters
        
        Returns:
            CommentsListResult

<a id="DataSourcesQuery"></a>

`DataSourcesQuery(connector: NotionConnector)`
:   Query class for DataSources entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DataSourcesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[DataSourcesSearchData]`
    :   Search data_sources records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DataSourcesSearchFilter):
        - archived: Indicates if the data source is archived or not.
        - cover: URL or reference to the cover image of the data source.
        - created_by: The user who created the data source.
        - created_time: The timestamp when the data source was created.
        - database_parent: The grandparent of the data source (parent of the database).
        - description: Description text associated with the data source.
        - icon: URL or reference to the icon of the data source.
        - id: Unique identifier of the data source.
        - is_inline: Indicates if the data source is displayed inline.
        - last_edited_by: The user who last edited the data source.
        - last_edited_time: The timestamp when the data source was last edited.
        - object_: The type of object (data_source).
        - parent: The parent database of the data source.
        - properties: Schema of properties for the data source.
        - public_url: Public URL to access the data source.
        - title: Title or name of the data source.
        - url: URL or reference to access the data source.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DataSourcesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, data_source_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.DataSource`
    :   Retrieves a data source object using the ID specified
        
        Args:
            data_source_id: Data Source ID
            **kwargs: Additional parameters
        
        Returns:
            DataSource

    `list(self, filter: DataSourcesListParamsFilter | None = None, sort: DataSourcesListParamsSort | None = None, start_cursor: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[DataSource], DataSourcesListResultMeta]`
    :   Returns data sources shared with the integration using the search endpoint
        
        Args:
            filter: Parameter filter
            sort: Parameter sort
            start_cursor: Pagination cursor
            page_size: Parameter page_size
            **kwargs: Additional parameters
        
        Returns:
            DataSourcesListResult

<a id="NotionConnector"></a>

`NotionConnector(auth_config: NotionAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Notion API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new notion connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., NotionAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = NotionConnector(auth_config=NotionAuthConfig(client_id="...", client_secret="...", access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = NotionConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = NotionConnector(
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

    `configure_oauth_app_parameters(*, airbyte_config: AirbyteAuthConfig, credentials: NotionOAuthCredentials | None) ‑> None`
    :   Configure or remove OAuth app credentials for your organization.
        
        When credentials are provided, replaces the default Airbyte-managed OAuth
        app credentials with your own. After calling this, all OAuth flows for
        this connector in your organization will use the provided credentials.
        
        When credentials are None, removes any existing override so the
        organization reverts to the default Airbyte-managed OAuth app.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials.
            credentials: Your OAuth app credentials (NotionOAuthCredentials), or None to remove the override.
        
        Example:
            await NotionConnector.configure_oauth_app_parameters(
                airbyte_config=AirbyteAuthConfig(
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                credentials=NotionOAuthCredentials(
                    client_id="...",
                    client_secret="...",
                ),
            )
        
            await NotionConnector.configure_oauth_app_parameters(
                airbyte_config=AirbyteAuthConfig(
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                credentials=None,
            )

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'NotionAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A NotionConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await NotionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=NotionAuthConfig(client_id="...", client_secret="...", access_token="..."),
            )
        
            # With server-side OAuth:
            connector = await NotionConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
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
            replication_config: Optional replication settings dict. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await NotionConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Notion Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @NotionConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @NotionConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await NotionConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.notion.models.NotionCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            NotionCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="PagesQuery"></a>

`PagesQuery(connector: NotionConnector)`
:   Query class for Pages entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[PagesSearchData]`
    :   Search pages records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PagesSearchFilter):
        - archived: Indicates whether the page is archived or not.
        - cover: URL or reference to the page cover image.
        - created_by: User ID or name of the creator of the page.
        - created_time: Date and time when the page was created.
        - icon: URL or reference to the page icon.
        - id: Unique identifier of the page.
        - in_trash: Indicates whether the page is in trash or not.
        - last_edited_by: User ID or name of the last editor of the page.
        - last_edited_time: Date and time when the page was last edited.
        - object_: Type or category of the page object.
        - parent: ID or reference to the parent page.
        - properties: Custom properties associated with the page.
        - public_url: Publicly accessible URL of the page.
        - url: URL of the page within the service.
        
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

    `get(self, page_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.Page`
    :   Retrieves a page object using the ID specified
        
        Args:
            page_id: Page ID
            **kwargs: Additional parameters
        
        Returns:
            Page

    `list(self, filter: PagesListParamsFilter | None = None, sort: PagesListParamsSort | None = None, start_cursor: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[Page], PagesListResultMeta]`
    :   Returns pages shared with the integration using the search endpoint
        
        Args:
            filter: Parameter filter
            sort: Parameter sort
            start_cursor: Pagination cursor
            page_size: Parameter page_size
            **kwargs: Additional parameters
        
        Returns:
            PagesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: NotionConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - avatar_url: URL of the user's avatar
        - bot: Bot-specific data
        - id: Unique identifier for the user
        - name: User's display name
        - object_: Always user
        - person: Person-specific data
        - type_: Type of user (person or bot)
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, user_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.User`
    :   Retrieves a single user by ID
        
        Args:
            user_id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, start_cursor: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.notion.models.NotionExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a paginated list of users for the workspace
        
        Args:
            start_cursor: Pagination cursor for next page
            page_size: Number of items per page (max 100)
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult