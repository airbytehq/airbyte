---
id: airbyte_agent_sdk-connectors-clickup_api-connector
title: airbyte_agent_sdk.connectors.clickup_api.connector
---

Module airbyte_agent_sdk.connectors.clickup_api.connector
=========================================================
Clickup-Api connector.

Classes
-------

<a id="ClickupApiConnector"></a>

`ClickupApiConnector(auth_config: ClickupApiAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Clickup-Api API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new clickup-api connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ClickupApiAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = ClickupApiConnector(auth_config=ClickupApiAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ClickupApiConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ClickupApiConnector(
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

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @ClickupApiConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ClickupApiConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ClickupApiConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.
            framework: One of ``"pydantic_ai" | "langchain" | "openai_agents" | "mcp"``.
                Defaults to None → auto-detect by attempting each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs) -> bool``
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                ``(error, args, kwargs) -> str | None``. Invoked after internal retries
                are exhausted OR were skipped via ``should_internal_retry`` returning
                False. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ClickupApiCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'api_search', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="CommentsQuery"></a>

`CommentsQuery(connector: ClickupApiConnector)`
:   Query class for Comments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CommentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[CommentsSearchData]`
    :   Search comments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CommentsSearchFilter):
        - id: Unique identifier for the comment
        - comment_text: Plain-text content of the comment
        - date: Timestamp when the comment was posted, in ClickUp timestamp format
        - reply_count: Number of replies on the comment
        
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

    `create(self, comment_text: str, task_id: str, assignee: int | None = None, notify_all: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.CommentCreateResponse`
    :   Create a comment on a task
        
        Args:
            comment_text: The comment text
            assignee: User ID to assign
            notify_all: Notify all assignees and watchers
            task_id: The ID of the task
            **kwargs: Additional parameters
        
        Returns:
            CommentCreateResponse

    `get(self, comment_id: str, **kwargs) ‑> list[airbyte_agent_sdk.connectors.clickup_api.models.Comment]`
    :   Get threaded replies on a comment
        
        Args:
            comment_id: The ID of the comment
            **kwargs: Additional parameters
        
        Returns:
            list[Comment]

    `list(self, task_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Comment]]`
    :   Get the comments on a task
        
        Args:
            task_id: The ID of the task
            **kwargs: Additional parameters
        
        Returns:
            CommentsListResult

    `update(self, comment_id: str, comment_text: str | None = None, assignee: int | None = None, resolved: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.CommentUpdateResponse`
    :   Update an existing comment
        
        Args:
            comment_text: Updated comment text
            assignee: User ID to assign
            resolved: Whether the comment is resolved
            comment_id: The ID of the comment
            **kwargs: Additional parameters
        
        Returns:
            CommentUpdateResponse

<a id="DocsQuery"></a>

`DocsQuery(connector: ClickupApiConnector)`
:   Query class for Docs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, workspace_id: str, doc_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.Doc`
    :   Fetch a single doc by ID
        
        Args:
            workspace_id: The ID of the workspace
            doc_id: The ID of the doc
            **kwargs: Additional parameters
        
        Returns:
            Doc

    `list(self, workspace_id: str, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Doc], DocsListResultMeta]`
    :   Search for docs in a workspace
        
        Args:
            workspace_id: The ID of the workspace
            cursor: Cursor for pagination to the next page of results
            **kwargs: Additional parameters
        
        Returns:
            DocsListResult

<a id="FoldersQuery"></a>

`FoldersQuery(connector: ClickupApiConnector)`
:   Query class for Folders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FoldersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[FoldersSearchData]`
    :   Search folders records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FoldersSearchFilter):
        - id: Unique identifier for the folder
        - name: Name of the folder
        - hidden: Whether the folder is hidden from the sidebar
        - task_count: Number of tasks contained in the folder
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FoldersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, folder_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.Folder`
    :   Get a single folder by ID
        
        Args:
            folder_id: The ID of the folder
            **kwargs: Additional parameters
        
        Returns:
            Folder

    `list(self, space_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Folder]]`
    :   Get the folders in a space
        
        Args:
            space_id: The ID of the space
            **kwargs: Additional parameters
        
        Returns:
            FoldersListResult

<a id="GoalsQuery"></a>

`GoalsQuery(connector: ClickupApiConnector)`
:   Query class for Goals entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GoalsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[GoalsSearchData]`
    :   Search goals records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GoalsSearchFilter):
        - id: Unique identifier for the goal
        - name: Name of the goal
        - description: Description of the goal
        - archived: Whether the goal has been archived
        - pinned: Whether the goal is pinned to the top of the list
        - private: Whether the goal is private to its owners
        - date_created: Creation timestamp of the goal, in ClickUp timestamp format
        - due_date: Due date for the goal, in ClickUp timestamp format
        - percent_completed: Completion percentage of the goal, between 0 and 100
        - team_id: Identifier of the team that owns the goal
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GoalsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, goal_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.Goal`
    :   Get a single goal by ID
        
        Args:
            goal_id: The ID of the goal
            **kwargs: Additional parameters
        
        Returns:
            Goal

    `list(self, team_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Goal]]`
    :   Get the goals in a workspace
        
        Args:
            team_id: The ID of the workspace
            **kwargs: Additional parameters
        
        Returns:
            GoalsListResult

<a id="ListsQuery"></a>

`ListsQuery(connector: ClickupApiConnector)`
:   Query class for Lists entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[ListsSearchData]`
    :   Search lists records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListsSearchFilter):
        - id: Unique identifier for the list
        - name: Name of the list
        - archived: Whether the list has been archived
        - due_date: Due date for the list, in ClickUp timestamp format
        - start_date: Start date for the list, in ClickUp timestamp format
        - priority: Priority assigned to the list
        - task_count: Number of tasks contained in the list
        
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

    `get(self, list_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.List`
    :   Get a single list by ID
        
        Args:
            list_id: The ID of the list
            **kwargs: Additional parameters
        
        Returns:
            List

    `list(self, folder_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[List]]`
    :   Get the lists in a folder
        
        Args:
            folder_id: The ID of the folder
            **kwargs: Additional parameters
        
        Returns:
            ListsListResult

<a id="MembersQuery"></a>

`MembersQuery(connector: ClickupApiConnector)`
:   Query class for Members entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, task_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Member]]`
    :   Get the members assigned to a task
        
        Args:
            task_id: The ID of the task
            **kwargs: Additional parameters
        
        Returns:
            MembersListResult

<a id="SpacesQuery"></a>

`SpacesQuery(connector: ClickupApiConnector)`
:   Query class for Spaces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SpacesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[SpacesSearchData]`
    :   Search spaces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SpacesSearchFilter):
        - id: Unique identifier for the space
        - name: Name of the space
        - private: Whether the space is private
        
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

    `get(self, space_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.Space`
    :   Get a single space by ID
        
        Args:
            space_id: The ID of the space
            **kwargs: Additional parameters
        
        Returns:
            Space

    `list(self, team_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Space]]`
    :   Get the spaces available in a workspace
        
        Args:
            team_id: The ID of the workspace
            **kwargs: Additional parameters
        
        Returns:
            SpacesListResult

<a id="TasksQuery"></a>

`TasksQuery(connector: ClickupApiConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, team_id: str, search: str | None = None, statuses: list[str] | None = None, assignees: list[str] | None = None, tags: list[str] | None = None, priority: int | None = None, due_date_gt: int | None = None, due_date_lt: int | None = None, date_created_gt: int | None = None, date_created_lt: int | None = None, date_updated_gt: int | None = None, date_updated_lt: int | None = None, custom_fields: list[dict[str, Any]] | None = None, include_closed: bool | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Task], TasksApiSearchResultMeta]`
    :   View the tasks that meet specific criteria from a workspace. Supports free-text search
        and structured filters including status, assignee, tags, priority, and date ranges.
        Responses are limited to 100 tasks per page.
        
        
                Args:
                    team_id: The workspace ID to search within
                    search: Free-text search across task name, description, and custom field text
                    statuses: Filter by status names (e.g. "in progress", "done")
                    assignees: Filter by user IDs
                    tags: Filter by tag names
                    priority: Filter by priority: 1=Urgent, 2=High, 3=Normal, 4=Low
                    due_date_gt: Due date after (Unix ms)
                    due_date_lt: Due date before (Unix ms)
                    date_created_gt: Created after (Unix ms)
                    date_created_lt: Created before (Unix ms)
                    date_updated_gt: Updated after (Unix ms)
                    date_updated_lt: Updated before (Unix ms)
                    custom_fields: JSON array of custom field filters. Each object: \{"field_id": "&lt;UUID&gt;", "operator": "&lt;OP&gt;", "value": "&lt;DATA&gt;"\}.
        Operators: = (contains), == (exact), &lt;, &lt;=, &gt;, >=, !=, !==, IS NULL, IS NOT NULL, RANGE, ANY, ALL, NOT ANY, NOT ALL
        
                    include_closed: Include closed tasks (excluded by default)
                    page: Page number (0-indexed), results capped at 100/page
                    **kwargs: Additional parameters
        
                Returns:
                    TasksApiSearchResult

    `context_store_search(self, query: TasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TasksSearchData]`
    :   Search tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TasksSearchFilter):
        - id: Unique identifier for the task
        - name: Name of the task
        - date_created: Creation timestamp of the task, in ClickUp timestamp format
        - date_updated: Last update timestamp of the task, in ClickUp timestamp format
        - date_closed: Timestamp when the task was closed, in ClickUp timestamp format
        - due_date: Due date for the task, in ClickUp timestamp format
        - start_date: Start date for the task, in ClickUp timestamp format
        - parent: ID of the parent task, if this task is a subtask
        - url: Permalink URL to view the task in ClickUp
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TasksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, task_id: str, custom_task_ids: bool | None = None, include_subtasks: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.Task`
    :   Get a single task by ID
        
        Args:
            task_id: The ID of the task
            custom_task_ids: Set to true to use a custom task ID
            include_subtasks: Include subtasks
            **kwargs: Additional parameters
        
        Returns:
            Task

    `list(self, list_id: str, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Task], TasksListResultMeta]`
    :   Get the tasks in a list
        
        Args:
            list_id: The ID of the list
            page: Page number (0-indexed)
            **kwargs: Additional parameters
        
        Returns:
            TasksListResult

<a id="TeamsQuery"></a>

`TeamsQuery(connector: ClickupApiConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - id: Unique identifier for the team (workspace)
        - name: Name of the team
        
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

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Team]]`
    :   Get the workspaces (teams) available to the authenticated user
        
        Returns:
            TeamsListResult

<a id="TimeTrackingQuery"></a>

`TimeTrackingQuery(connector: ClickupApiConnector)`
:   Query class for TimeTracking entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TimeTrackingSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TimeTrackingSearchData]`
    :   Search time_tracking records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TimeTrackingSearchFilter):
        - time: Total tracked time in milliseconds
        - user: User who tracked the time
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TimeTrackingSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, team_id: str, time_entry_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.TimeEntry`
    :   Get a single time entry by ID
        
        Args:
            team_id: The ID of the workspace
            time_entry_id: The ID of the time entry
            **kwargs: Additional parameters
        
        Returns:
            TimeEntry

    `list(self, team_id: str, start_date: int | None = None, end_date: int | None = None, assignee: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[TimeEntry]]`
    :   Get time entries within a date range for a workspace
        
        Args:
            team_id: The ID of the workspace
            start_date: Start date (Unix ms)
            end_date: End date (Unix ms)
            assignee: Filter by user ID
            **kwargs: Additional parameters
        
        Returns:
            TimeTrackingListResult

<a id="UserQuery"></a>

`UserQuery(connector: ClickupApiConnector)`
:   Query class for User entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UserSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[UserSearchData]`
    :   Search user records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UserSearchFilter):
        - id: Unique identifier for the user
        - username: Display name of the user
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UserSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.User`
    :   View the details of the authenticated user's ClickUp account
        
        Returns:
            User

<a id="ViewTasksQuery"></a>

`ViewTasksQuery(connector: ClickupApiConnector)`
:   Query class for ViewTasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, view_id: str, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Task], ViewTasksListResultMeta]`
    :   Get tasks matching a view's pre-configured filters — useful as a secondary search mechanism
        
        Args:
            view_id: The ID of the view
            page: Page number (0-indexed)
            **kwargs: Additional parameters
        
        Returns:
            ViewTasksListResult

<a id="ViewsQuery"></a>

`ViewsQuery(connector: ClickupApiConnector)`
:   Query class for Views entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, view_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.View`
    :   Get a single view by ID
        
        Args:
            view_id: The ID of the view
            **kwargs: Additional parameters
        
        Returns:
            View

    `list(self, team_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[View]]`
    :   Get the workspace-level (Everything level) views
        
        Args:
            team_id: The ID of the workspace
            **kwargs: Additional parameters
        
        Returns:
            ViewsListResult