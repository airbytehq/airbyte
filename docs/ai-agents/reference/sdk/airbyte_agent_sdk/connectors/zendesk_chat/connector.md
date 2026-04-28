---
id: airbyte_agent_sdk-connectors-zendesk_chat-connector
title: airbyte_agent_sdk.connectors.zendesk_chat.connector
---

Module airbyte_agent_sdk.connectors.zendesk_chat.connector
==========================================================
Zendesk-Chat connector.

Classes
-------

<a id="AccountsQuery"></a>

`AccountsQuery(connector: ZendeskChatConnector)`
:   Query class for Accounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Account`
    :   Returns the account information for the authenticated user
        
        Returns:
            Account

<a id="AgentTimelineQuery"></a>

`AgentTimelineQuery(connector: ZendeskChatConnector)`
:   Query class for AgentTimeline entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, start_time: int | None = None, limit: int | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta[list[AgentTimeline], AgentTimelineListResultMeta]`
    :   List agent timeline (incremental export)
        
        Args:
            start_time: Parameter start_time
            limit: Parameter limit
            fields: Parameter fields
            **kwargs: Additional parameters
        
        Returns:
            AgentTimelineListResult

<a id="AgentsQuery"></a>

`AgentsQuery(connector: ZendeskChatConnector)`
:   Query class for Agents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AgentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[AgentsSearchData]`
    :   Search agents records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AgentsSearchFilter):
        - id: Unique agent identifier
        - email: Agent email address
        - display_name: Agent display name
        - first_name: Agent first name
        - last_name: Agent last name
        - enabled: Whether agent is enabled
        - role_id: Agent role ID
        - departments: Department IDs agent belongs to
        - create_date: When agent was created
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AgentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, agent_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Agent`
    :   Get an agent
        
        Args:
            agent_id: Parameter agent_id
            **kwargs: Additional parameters
        
        Returns:
            Agent

    `list(self, limit: int | None = None, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Agent]]`
    :   List all agents
        
        Args:
            limit: Parameter limit
            since_id: Parameter since_id
            **kwargs: Additional parameters
        
        Returns:
            AgentsListResult

<a id="BansQuery"></a>

`BansQuery(connector: ZendeskChatConnector)`
:   Query class for Bans entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, ban_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Ban`
    :   Get a ban
        
        Args:
            ban_id: Parameter ban_id
            **kwargs: Additional parameters
        
        Returns:
            Ban

    `list(self, limit: int | None = None, since_id: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[dict[str, Any]]`
    :   List all bans
        
        Args:
            limit: Parameter limit
            since_id: Parameter since_id
            **kwargs: Additional parameters
        
        Returns:
            BansListResult

<a id="ChatsQuery"></a>

`ChatsQuery(connector: ZendeskChatConnector)`
:   Query class for Chats entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ChatsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[ChatsSearchData]`
    :   Search chats records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ChatsSearchFilter):
        - id: Unique chat identifier
        - timestamp: Chat start timestamp
        - update_timestamp: Last update timestamp
        - department_id: Department ID
        - department_name: Department name
        - duration: Chat duration in seconds
        - rating: Satisfaction rating
        - missed: Whether chat was missed
        - agent_ids: IDs of agents in chat
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ChatsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, chat_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Chat`
    :   Get a chat
        
        Args:
            chat_id: Parameter chat_id
            **kwargs: Additional parameters
        
        Returns:
            Chat

    `list(self, start_time: int | None = None, limit: int | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResultWithMeta[list[Chat], ChatsListResultMeta]`
    :   List chats (incremental export)
        
        Args:
            start_time: Parameter start_time
            limit: Parameter limit
            fields: Parameter fields
            **kwargs: Additional parameters
        
        Returns:
            ChatsListResult

<a id="DepartmentsQuery"></a>

`DepartmentsQuery(connector: ZendeskChatConnector)`
:   Query class for Departments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DepartmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[DepartmentsSearchData]`
    :   Search departments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DepartmentsSearchFilter):
        - id: Department ID
        - name: Department name
        - enabled: Whether department is enabled
        - members: Agent IDs in department
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DepartmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, department_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Department`
    :   Get a department
        
        Args:
            department_id: Parameter department_id
            **kwargs: Additional parameters
        
        Returns:
            Department

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Department]]`
    :   List all departments
        
        Returns:
            DepartmentsListResult

<a id="GoalsQuery"></a>

`GoalsQuery(connector: ZendeskChatConnector)`
:   Query class for Goals entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, goal_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Goal`
    :   Get a goal
        
        Args:
            goal_id: Parameter goal_id
            **kwargs: Additional parameters
        
        Returns:
            Goal

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Goal]]`
    :   List all goals
        
        Returns:
            GoalsListResult

<a id="RolesQuery"></a>

`RolesQuery(connector: ZendeskChatConnector)`
:   Query class for Roles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, role_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Role`
    :   Get a role
        
        Args:
            role_id: Parameter role_id
            **kwargs: Additional parameters
        
        Returns:
            Role

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Role]]`
    :   List all roles
        
        Returns:
            RolesListResult

<a id="RoutingSettingsQuery"></a>

`RoutingSettingsQuery(connector: ZendeskChatConnector)`
:   Query class for RoutingSettings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.RoutingSettings`
    :   Get routing settings
        
        Returns:
            RoutingSettings

<a id="ShortcutsQuery"></a>

`ShortcutsQuery(connector: ZendeskChatConnector)`
:   Query class for Shortcuts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ShortcutsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[ShortcutsSearchData]`
    :   Search shortcuts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ShortcutsSearchFilter):
        - id: Shortcut ID
        - name: Shortcut name/trigger
        - message: Shortcut message content
        - tags: Tags applied when shortcut is used
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ShortcutsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, shortcut_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Shortcut`
    :   Get a shortcut
        
        Args:
            shortcut_id: Parameter shortcut_id
            **kwargs: Additional parameters
        
        Returns:
            Shortcut

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Shortcut]]`
    :   List all shortcuts
        
        Returns:
            ShortcutsListResult

<a id="SkillsQuery"></a>

`SkillsQuery(connector: ZendeskChatConnector)`
:   Query class for Skills entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, skill_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.Skill`
    :   Get a skill
        
        Args:
            skill_id: Parameter skill_id
            **kwargs: Additional parameters
        
        Returns:
            Skill

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Skill]]`
    :   List all skills
        
        Returns:
            SkillsListResult

<a id="TriggersQuery"></a>

`TriggersQuery(connector: ZendeskChatConnector)`
:   Query class for Triggers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TriggersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[TriggersSearchData]`
    :   Search triggers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TriggersSearchFilter):
        - id: Trigger ID
        - name: Trigger name
        - enabled: Whether trigger is enabled
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TriggersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatExecuteResult[list[Trigger]]`
    :   List all triggers
        
        Returns:
            TriggersListResult

<a id="ZendeskChatConnector"></a>

`ZendeskChatConnector(auth_config: ZendeskChatAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Zendesk-Chat API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new zendesk-chat connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ZendeskChatAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)
    Examples:
        # Local mode (direct API calls)
        connector = ZendeskChatConnector(auth_config=ZendeskChatAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ZendeskChatConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ZendeskChatConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ZendeskChatAuthConfig'", name: str | None = None, replication_config: "'ZendeskChatReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A ZendeskChatConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ZendeskChatConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskChatAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await ZendeskChatConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskChatAuthConfig(access_token="..."),
                replication_config=ZendeskChatReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ZendeskChatConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ZendeskChatConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ZendeskChatConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ZendeskChatCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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