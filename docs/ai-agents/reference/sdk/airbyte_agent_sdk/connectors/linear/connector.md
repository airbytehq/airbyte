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
        connector = LinearConnector(auth_config=LinearAuthConfig(api_key="..."))
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'LinearAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.linear.connector.LinearConnector`
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
            A LinearConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await LinearConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=LinearAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @LinearConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @LinearConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await LinearConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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