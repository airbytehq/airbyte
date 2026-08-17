---
id: airbyte_agent_sdk-connectors-linear-connector
title: airbyte_agent_sdk.connectors.linear.connector
---

Module airbyte_agent_sdk.connectors.linear.connector
====================================================
Linear connector.

Classes
-------

<a id="CommentsQuery"></a>

`CommentsQuery(connector: LinearConnector)`
:   Query class for Comments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CommentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[CommentsSearchData]`
    :   Search comments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CommentsSearchFilter):
        - body: 
        - body_data: 
        - created_at: 
        - edited_at: 
        - id: 
        - issue: 
        - issue_id: 
        - parent: 
        - parent_comment_id: 
        - resolving_comment_id: 
        - resolving_user_id: 
        - updated_at: 
        - url: 
        - user: 
        - user_id: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CommentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, issue_id: str, body: str, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.CommentMutationPayload`
    :   Create a new comment on an issue via GraphQL mutation
        
        Args:
            issue_id: The ID of the issue to add the comment to
            body: The comment content in markdown
            **kwargs: Additional parameters
        
        Returns:
            CommentMutationPayload

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.Comment`
    :   Get a single comment by ID via GraphQL
        
        Args:
            id: Comment ID
            **kwargs: Additional parameters
        
        Returns:
            Comment

    `list(self, issue_id: str, first: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Comment], CommentsListResultMeta]`
    :   Returns a paginated list of comments for an issue via GraphQL
        
        Args:
            issue_id: Issue ID to get comments for
            first: Number of items to return (max 250)
            after: Cursor to start after (for pagination)
            **kwargs: Additional parameters
        
        Returns:
            CommentsListResult

    `update(self, body: str, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.CommentMutationPayload`
    :   Update an existing comment via GraphQL mutation
        
        Args:
            id: The ID of the comment to update
            body: The new comment content in markdown
            **kwargs: Additional parameters
        
        Returns:
            CommentMutationPayload

<a id="IssuesQuery"></a>

`IssuesQuery(connector: LinearConnector)`
:   Query class for Issues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IssuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[IssuesSearchData]`
    :   Search issues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssuesSearchFilter):
        - added_to_cycle_at: 
        - added_to_project_at: 
        - added_to_team_at: 
        - assignee: 
        - assignee_id: 
        - attachment_ids: 
        - attachments: 
        - branch_name: 
        - canceled_at: 
        - completed_at: 
        - created_at: 
        - creator: 
        - creator_id: 
        - customer_ticket_count: 
        - cycle: 
        - cycle_id: 
        - description: 
        - description_state: 
        - due_date: 
        - estimate: 
        - id: 
        - identifier: 
        - integration_source_type: 
        - label_ids: 
        - labels: 
        - milestone_id: 
        - number: 
        - parent: 
        - parent_id: 
        - previous_identifiers: 
        - priority: 
        - priority_label: 
        - priority_sort_order: 
        - project: 
        - project_id: 
        - project_milestone: 
        - reaction_data: 
        - relation_ids: 
        - relations: 
        - sla_type: 
        - sort_order: 
        - source_comment_id: 
        - started_at: 
        - state: 
        - state_id: 
        - sub_issue_sort_order: 
        - subscriber_ids: 
        - subscribers: 
        - team: 
        - team_id: 
        - title: 
        - updated_at: 
        - url: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            IssuesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, team_id: str, title: str, description: str | None = None, state_id: str | None = None, priority: int | None = None, project_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.IssueMutationPayload`
    :   Create a new issue via GraphQL mutation
        
        Args:
            team_id: The ID of the team to create the issue in
            title: The title of the issue
            description: The description of the issue (supports markdown)
            state_id: The ID of the workflow state for the issue
            priority: The priority of the issue (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low)
            project_id: The ID of the project to add the issue to. Get project IDs from the projects list.
            **kwargs: Additional parameters
        
        Returns:
            IssueMutationPayload

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.Issue`
    :   Get a single issue by ID via GraphQL
        
        Args:
            id: Issue ID
            **kwargs: Additional parameters
        
        Returns:
            Issue

    `list(self, first: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Issue], IssuesListResultMeta]`
    :   Returns a paginated list of issues via GraphQL with pagination support
        
        Args:
            first: Number of items to return (max 250)
            after: Cursor to start after (for pagination)
            **kwargs: Additional parameters
        
        Returns:
            IssuesListResult

    `update(self, id: str | None = None, title: str | None = None, description: str | None = None, state_id: str | None = None, priority: int | None = None, assignee_id: str | None = None, project_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.IssueMutationPayload`
    :   Update an existing issue via GraphQL mutation. All fields except id are optional for partial updates.
        To assign a user, provide assigneeId with the user's ID (get user IDs from the users list).
        Omit assigneeId to leave the current assignee unchanged.
        
        
                Args:
                    id: The ID of the issue to update
                    title: The new title of the issue
                    description: The new description of the issue (supports markdown)
                    state_id: The ID of the new workflow state for the issue
                    priority: The new priority of the issue (0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low)
                    assignee_id: The ID of the user to assign to this issue. Get user IDs from the users list.
                    project_id: The ID of the project to add this issue to. Get project IDs from the projects list.
                    **kwargs: Additional parameters
        
                Returns:
                    IssueMutationPayload

<a id="LinearConnector"></a>

`LinearConnector(auth_config: LinearAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Linear API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new linear connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., LinearAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = LinearConnector(auth_config=LinearAuthConfig(client_id="...", client_secret="...", refresh_token="...", access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = LinearConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = LinearConnector(
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
            connector = LinearConnector(...)
        
            @LinearConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @LinearConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @LinearConnector.agent_tool()
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
        
        connector = LinearConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @LinearConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @LinearConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @LinearConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.linear.models.LinearCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            LinearCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: LinearConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - canceled_at: 
        - color: 
        - completed_at: 
        - completed_issue_count_history: 
        - completed_scope_history: 
        - content: 
        - content_state: 
        - converted_from_issue: 
        - converted_from_issue_id: 
        - created_at: 
        - creator: 
        - creator_id: 
        - description: 
        - health: 
        - health_updated_at: 
        - icon: 
        - id: 
        - in_progress_scope_history: 
        - issue_count_history: 
        - lead: 
        - lead_id: 
        - name: 
        - priority: 
        - priority_sort_order: 
        - progress: 
        - scope: 
        - scope_history: 
        - slug_id: 
        - sort_order: 
        - start_date: 
        - started_at: 
        - status: 
        - status_id: 
        - target_date: 
        - team_ids: 
        - teams: 
        - update_reminders_day: 
        - update_reminders_hour: 
        - updated_at: 
        - url: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, name: str, team_ids: list[str], description: str | None = None, state: str | None = None, start_date: str | None = None, target_date: str | None = None, lead_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.ProjectMutationPayload`
    :   Create a new project via GraphQL mutation
        
        Args:
            name: The name of the project
            team_ids: The IDs of the teams to associate with this project. Get team IDs from the teams list.
            description: The description of the project (supports markdown)
            state: The state of the project (backlog, planned, started, paused, completed, canceled)
            start_date: The planned start date of the project (YYYY-MM-DD format)
            target_date: The target completion date of the project (YYYY-MM-DD format)
            lead_id: The ID of the user to set as project lead. Get user IDs from the users list.
            **kwargs: Additional parameters
        
        Returns:
            ProjectMutationPayload

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.Project`
    :   Get a single project by ID via GraphQL
        
        Args:
            id: Project ID
            **kwargs: Additional parameters
        
        Returns:
            Project

    `list(self, first: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Project], ProjectsListResultMeta]`
    :   Returns a paginated list of projects via GraphQL with pagination support
        
        Args:
            first: Number of items to return (max 250)
            after: Cursor to start after (for pagination)
            **kwargs: Additional parameters
        
        Returns:
            ProjectsListResult

    `update(self, id: str | None = None, name: str | None = None, description: str | None = None, state: str | None = None, start_date: str | None = None, target_date: str | None = None, lead_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.ProjectMutationPayload`
    :   Update an existing project via GraphQL mutation. All fields except id are optional for partial updates.
        Use this to rename projects, change descriptions, update dates, or change the project state.
        
        
                Args:
                    id: The ID of the project to update
                    name: The new name of the project
                    description: The new description of the project (supports markdown)
                    state: The new state of the project (backlog, planned, started, paused, completed, canceled)
                    start_date: The new planned start date of the project (YYYY-MM-DD format)
                    target_date: The new target completion date of the project (YYYY-MM-DD format)
                    lead_id: The ID of the user to set as project lead. Get user IDs from the users list.
                    **kwargs: Additional parameters
        
                Returns:
                    ProjectMutationPayload

<a id="TeamsQuery"></a>

`TeamsQuery(connector: LinearConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - active_cycle: 
        - active_cycle_id: 
        - auto_archive_period: 
        - auto_close_period: 
        - auto_close_state_id: 
        - color: 
        - created_at: 
        - cycle_calender_url: 
        - cycle_cooldown_time: 
        - cycle_duration: 
        - cycle_issue_auto_assign_completed: 
        - cycle_issue_auto_assign_started: 
        - cycle_lock_to_active: 
        - cycle_start_day: 
        - cycles_enabled: 
        - default_issue_estimate: 
        - default_issue_state: 
        - default_issue_state_id: 
        - group_issue_history: 
        - icon: 
        - id: 
        - invite_hash: 
        - issue_count: 
        - issue_estimation_allow_zero: 
        - issue_estimation_extended: 
        - issue_estimation_type: 
        - key: 
        - marked_as_duplicate_workflow_state: 
        - marked_as_duplicate_workflow_state_id: 
        - name: 
        - parent_team_id: 
        - private: 
        - require_priority_to_leave_triage: 
        - scim_managed: 
        - set_issue_sort_order_on_state_change: 
        - timezone: 
        - triage_enabled: 
        - triage_issue_state_id: 
        - upcoming_cycle_count: 
        - updated_at: 
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.Team`
    :   Get a single team by ID via GraphQL
        
        Args:
            id: Team ID
            **kwargs: Additional parameters
        
        Returns:
            Team

    `list(self, first: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Team], TeamsListResultMeta]`
    :   Returns a list of teams via GraphQL with pagination support
        
        Args:
            first: Number of items to return (max 250)
            after: Cursor to start after (for pagination)
            **kwargs: Additional parameters
        
        Returns:
            TeamsListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: LinearConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - active: 
        - admin: 
        - avatar_background_color: 
        - avatar_url: 
        - created_at: 
        - created_issue_count: 
        - display_name: 
        - email: 
        - guest: 
        - id: 
        - initials: 
        - invite_hash: 
        - is_me: 
        - last_seen: 
        - name: 
        - team_ids: 
        - teams: 
        - timezone: 
        - updated_at: 
        - url: 
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.User`
    :   Get a single user by ID via GraphQL
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, first: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a paginated list of users in the organization via GraphQL
        
        Args:
            first: Number of items to return (max 250)
            after: Cursor to start after (for pagination)
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult

<a id="WorkflowStatesQuery"></a>

`WorkflowStatesQuery(connector: LinearConnector)`
:   Query class for WorkflowStates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WorkflowStatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[WorkflowStatesSearchData]`
    :   Search workflow_states records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WorkflowStatesSearchFilter):
        - color: 
        - created_at: 
        - description: 
        - id: 
        - inherited_from_id: 
        - name: 
        - position: 
        - team: 
        - team_id: 
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
            WorkflowStatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, first: int | None = None, after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[WorkflowState], WorkflowStatesListResultMeta]`
    :   Returns workflow states for a team via GraphQL, including name and UUID for status transitions
        
        Args:
            first: Number of items to return (max 250)
            after: Cursor to start after (for pagination)
            **kwargs: Additional parameters
        
        Returns:
            WorkflowStatesListResult