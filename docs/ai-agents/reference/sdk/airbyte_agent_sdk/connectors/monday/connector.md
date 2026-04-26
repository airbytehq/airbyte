---
id: airbyte_agent_sdk-connectors-monday-connector
title: airbyte_agent_sdk.connectors.monday.connector
---

Module airbyte_agent_sdk.connectors.monday.connector
====================================================
Monday connector.

Classes
-------

<a id="ActivityLogsQuery"></a>

`ActivityLogsQuery(connector: MondayConnector)`
:   Query class for ActivityLogs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ActivityLogsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[ActivityLogsSearchData]`
    :   Search activity_logs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ActivityLogsSearchFilter):
        - board_id: Board ID the activity belongs to
        - created_at: When the activity occurred
        - created_at_int: When the activity occurred (Unix timestamp)
        - data: Event data (JSON string)
        - entity: Entity type that was affected
        - event: Event type
        - id: Unique activity log identifier
        - pulse_id: Item (pulse) ID the activity belongs to
        - user_id: ID of the user who performed the action
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ActivityLogsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, board_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[ActivityLog]]`
    :   Returns activity logs from boards. Requires a board_id parameter.
        
        Args:
            board_id: Board ID to fetch activity logs from
            **kwargs: Additional parameters
        
        Returns:
            ActivityLogsListResult

<a id="BoardsQuery"></a>

`BoardsQuery(connector: MondayConnector)`
:   Query class for Boards entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BoardsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[BoardsSearchData]`
    :   Search boards records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BoardsSearchFilter):
        - board_kind: Board kind (public, private, share)
        - columns: Board columns
        - communication: Board communication value
        - creator: Board creator
        - description: Board description
        - groups: Board groups
        - id: Unique board identifier
        - name: Board name
        - owners: Board owners
        - permissions: Board permissions
        - state: Board state (active, archived, deleted)
        - subscribers: Board subscribers
        - tags: Board tags
        - top_group: Top group on the board
        - type_: Board type
        - updated_at: When the board was last updated
        - updated_at_int: When the board was last updated (Unix timestamp)
        - updates: Board updates
        - views: Board views
        - workspace: Workspace the board belongs to
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BoardsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns a single board by ID
        
        Args:
            id: Board ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Board]]`
    :   Returns all boards in the Monday.com account
        
        Returns:
            BoardsListResult

<a id="ItemsQuery"></a>

`ItemsQuery(connector: MondayConnector)`
:   Query class for Items entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ItemsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[ItemsSearchData]`
    :   Search items records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ItemsSearchFilter):
        - assets: Files attached to the item
        - board: Board the item belongs to
        - column_values: Item column values
        - created_at: When the item was created
        - creator_id: ID of the user who created the item
        - group: Group the item belongs to
        - id: Unique item identifier
        - name: Item name
        - parent_item: Parent item (for subitems)
        - state: Item state (active, archived, deleted)
        - subscribers: Item subscribers
        - updated_at: When the item was last updated
        - updated_at_int: When the item was last updated (Unix timestamp)
        - updates: Item updates
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ItemsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns a single item by ID
        
        Args:
            id: Item ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, board_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Item]]`
    :   Returns items from boards. Queries items through the boards endpoint using items_page for pagination.
        
        Args:
            board_id: Board ID to fetch items from
            **kwargs: Additional parameters
        
        Returns:
            ItemsListResult

<a id="MondayConnector"></a>

`MondayConnector(auth_config: MondayAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Monday API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new monday connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., MondayAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = MondayConnector(auth_config=MondayAuthConfig(access_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = MondayConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = MondayConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'MondayAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            A MondayConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await MondayConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=MondayAuthConfig(access_token="...", client_id="...", client_secret="..."),
            )
        
            # With server-side OAuth:
            connector = await MondayConnector.create(
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
            consent_url = await MondayConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Monday Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @MondayConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @MondayConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await MondayConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.monday.models.MondayCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            MondayCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="TagsQuery"></a>

`TagsQuery(connector: MondayConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[TagsSearchData]`
    :   Search tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TagsSearchFilter):
        - color: Tag color
        - id: Unique tag identifier
        - name: Tag name
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TagsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Tag]]`
    :   Returns all tags in the Monday.com account
        
        Returns:
            TagsListResult

<a id="TeamsQuery"></a>

`TeamsQuery(connector: MondayConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - id: Unique team identifier
        - name: Team name
        - picture_url: Team picture URL
        - users: Team members
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TeamsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns a single team by ID
        
        Args:
            id: Team ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Team]]`
    :   Returns all teams in the Monday.com account
        
        Returns:
            TeamsListResult

<a id="UpdatesQuery"></a>

`UpdatesQuery(connector: MondayConnector)`
:   Query class for Updates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UpdatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[UpdatesSearchData]`
    :   Search updates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UpdatesSearchFilter):
        - assets: Files attached to this update
        - body: Update body (HTML)
        - created_at: When the update was created
        - creator_id: ID of the user who created the update
        - id: Unique update identifier
        - item_id: ID of the item this update belongs to
        - replies: Replies to this update
        - text_body: Update body (plain text)
        - updated_at: When the update was last modified
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UpdatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns a single update by ID
        
        Args:
            id: Update ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, page: int | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Update]]`
    :   Returns all updates (comments/posts) in the Monday.com account
        
        Args:
            page: Page number for pagination
            limit: Number of updates to return per page
            **kwargs: Additional parameters
        
        Returns:
            UpdatesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: MondayConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - birthday: User's birthday
        - country_code: User's country code
        - created_at: When the user was created
        - email: User's email address
        - enabled: Whether the user account is enabled
        - id: Unique user identifier
        - is_admin: Whether the user is an admin
        - is_guest: Whether the user is a guest
        - is_pending: Whether the user is pending
        - is_view_only: Whether the user is view-only
        - is_verified: Whether the user is verified
        - join_date: When the user joined
        - location: User's location
        - mobile_phone: User's mobile phone number
        - name: User's display name
        - phone: User's phone number
        - photo_original: URL to original size photo
        - photo_small: URL to small photo
        - photo_thumb: URL to thumbnail photo
        - photo_thumb_small: URL to small thumbnail photo
        - photo_tiny: URL to tiny photo
        - time_zone_identifier: User's timezone identifier
        - title: User's job title
        - url: User's Monday.com profile URL
        - utc_hours_diff: UTC hours difference for the user's timezone
        
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

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns a single user by ID
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[User]]`
    :   Returns all users in the Monday.com account
        
        Returns:
            UsersListResult

<a id="WorkspacesQuery"></a>

`WorkspacesQuery(connector: MondayConnector)`
:   Query class for Workspaces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WorkspacesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.monday.models.AirbyteSearchResult[WorkspacesSearchData]`
    :   Search workspaces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WorkspacesSearchFilter):
        - account_product: Account product info
        - created_at: When the workspace was created
        - description: Workspace description
        - id: Unique workspace identifier
        - kind: Workspace kind (open, closed)
        - name: Workspace name
        - owners_subscribers: Owner subscribers
        - settings: Workspace settings
        - state: Workspace state
        - team_owners_subscribers: Team owner subscribers
        - teams_subscribers: Team subscribers
        - users_subscribers: User subscribers
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            WorkspacesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns a single workspace by ID
        
        Args:
            id: Workspace ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.monday.models.MondayExecuteResult[list[Workspace]]`
    :   Returns all workspaces in the Monday.com account
        
        Returns:
            WorkspacesListResult