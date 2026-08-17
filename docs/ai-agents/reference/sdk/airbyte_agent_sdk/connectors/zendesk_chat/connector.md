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

    `agent_tool(role: AgentToolRole | None = None, *, inspect_tool: str | None = None, docs_tool: str | None = None, max_output_chars: int | None | Unset = UNSET, framework: FrameworkName = 'none', internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Callable[[~_F], ~_F]`
    :   Framework-agnostic decorator for user-written connector tool functions.
        
        The progressive-docs sibling of tool_utils: instead of baking the full
        entity/action reference into the docstring, it instructs the agent to
        call this connector's inspect and docs tools before executing. Tool
        failures raise :class:`airbyte_agent_sdk.AirbyteToolError` by default
        (``framework="none"``, no auto-detection) — pass ``framework=...`` to
        translate to a supported framework's signal instead.
        
        Decorate three functions per connector — execute, inspect and docs.
        The role is inferred from each function's signature (extra parameters
        are allowed); a signature matching more than one role, a generic
        ``(*args, **kwargs)`` wrapper, or a callable whose signature cannot
        be read must pass the role explicitly:
        
        - ``(entity, action, ...)`` -> ``"execute"``
        - ``(section, ...)``        -> ``"read_skill_docs"``
        - ``()``                    -> ``"inspect_connector"``
        
        Usage:
            connector = ZendeskChatConnector(...)
        
            @ZendeskChatConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @ZendeskChatConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @ZendeskChatConnector.agent_tool()
            async def read_skill_docs(section: str | None = None):
                return await connector.read_skill_docs(section)
        
        Args:
            role: ``"execute" | "inspect_connector" | "read_skill_docs"``.
                None (default) infers the role from the decorated function's
                signature; an explicit role validates the canonical
                parameters are present (functions accepting ``**kwargs``, or
                callables whose signature cannot be read, pass validation).
            inspect_tool: Exact registered name of the sibling inspect tool,
                woven into the execute docstring for tighter steering.
                Defaults to generic phrasing.
            docs_tool: Exact registered name of the sibling docs tool (see
                inspect_tool).
            max_output_chars: Max serialized output size before failing.
                Defaults per role: execute -> DEFAULT_MAX_OUTPUT_CHARS, docs
                tools -> None.
            framework: Translation target for tool failures. Defaults to
                ``"none"`` (raise AirbyteToolError); never auto-detects.
            internal_retries: How many transient runtime failures (429/5xx,
                network, timeout) to retry silently before surfacing.
                Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs)
                -> bool`` further restricting which retryable errors are safe
                for this specific tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback ``(error,
                args, kwargs) -> str | None`` invoked after internal retries
                are exhausted or skipped. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Add connector-specific documentation and runtime safeguards to one tool.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = ZendeskChatConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @ZendeskChatConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @ZendeskChatConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @ZendeskChatConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                `airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate `(error, args, kwargs) -> bool`
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                `(error, args, kwargs) -> str | None`. Invoked after internal retries
                are exhausted or were skipped because `should_internal_retry` returned
                `False`. Forwarded to `airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

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

    `execute(self, entity: str, action: "Literal['get', 'list', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
            select_fields: Optional allowlist of dot-notation fields to include
            exclude_fields: Optional blocklist of dot-notation fields to remove
            skip_truncation: Disable long-text truncation for collection actions
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `inspect_connector(self) ‑> dict[str, typing.Any]`
    :   Inspect this connector's hosted metadata/readiness and resolve its docs skill id.
        
        Call this before read_skill_docs in the normal hosted flow. For
        local/offline connectors this returns a local-mode payload with a
        warning instead of a hosted inspection.
        
        Example:
            info = await connector.inspect_connector()
            print(info["docs_skill_id"])

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

    `read_skill_docs(self, section: str | None = None) ‑> str`
    :   Read this connector's usage docs, rendered to text.
        
        Omit section for the outline and general guidance; pass an exact
        section id from the outline for full details. For local/offline
        connectors the full generated docs are returned and section is
        ignored.
        
        Example:
            outline = await connector.read_skill_docs()
            details = await connector.read_skill_docs(section="entity:contacts")