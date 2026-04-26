---
id: airbyte_agent_sdk-connectors-gitlab-connector
title: airbyte_agent_sdk.connectors.gitlab.connector
---

Module airbyte_agent_sdk.connectors.gitlab.connector
====================================================
Gitlab connector.

Classes
-------

<a id="BranchesQuery"></a>

`BranchesQuery(connector: GitlabConnector)`
:   Query class for Branches entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BranchesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[BranchesSearchData]`
    :   Search branches records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BranchesSearchFilter):
        - project_id: ID of the project the branch belongs to
        - name: Name of the branch
        - merged: Whether the branch is merged
        - protected: Whether the branch is protected
        - developers_can_push: Whether developers can push to the branch
        - developers_can_merge: Whether developers can merge into the branch
        - can_push: Whether the current user can push
        - default: Whether this is the default branch
        - web_url: Web URL of the branch
        - commit_id: SHA of the head commit
        - commit: Head commit details
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BranchesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, branch: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Branch`
    :   Get a single project repository branch.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            branch: The name of the branch (URL-encoded if it contains special characters)
            **kwargs: Additional parameters
        
        Returns:
            Branch

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, search: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Branch], BranchesListResultMeta]`
    :   Get a list of repository branches from a project.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            search: Return list of branches containing the search string
            **kwargs: Additional parameters
        
        Returns:
            BranchesListResult

<a id="CommitsQuery"></a>

`CommitsQuery(connector: GitlabConnector)`
:   Query class for Commits entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CommitsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[CommitsSearchData]`
    :   Search commits records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CommitsSearchFilter):
        - project_id: ID of the project the commit belongs to
        - id: SHA of the commit
        - short_id: Short SHA of the commit
        - created_at: Timestamp when the commit was created
        - parent_ids: SHAs of parent commits
        - title: Title of the commit
        - message: Full commit message
        - author_name: Name of the commit author
        - author_email: Email of the commit author
        - authored_date: Date the commit was authored
        - committer_name: Name of the committer
        - committer_email: Email of the committer
        - committed_date: Date the commit was committed
        - trailers: Git trailers for the commit
        - web_url: Web URL of the commit
        - stats: Commit statistics
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CommitsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, sha: str, stats: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Commit`
    :   Get a specific commit identified by the commit hash or name of a branch or tag.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            sha: The commit hash or name of a repository branch or tag
            stats: Include commit stats
            **kwargs: Additional parameters
        
        Returns:
            Commit

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, ref_name: str | None = None, since: str | None = None, until: str | None = None, with_stats: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Commit], CommitsListResultMeta]`
    :   Get a list of repository commits in a project.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            ref_name: The name of a repository branch, tag, or revision range
            since: Only commits after or on this date (ISO 8601)
            until: Only commits before or on this date (ISO 8601)
            with_stats: Include stats about each commit
            **kwargs: Additional parameters
        
        Returns:
            CommitsListResult

<a id="GitlabConnector"></a>

`GitlabConnector(auth_config: GitlabAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, api_url: str | None = None)`
:   Type-safe Gitlab API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new gitlab connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GitlabAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            api_url: GitLab instance hostname
    Examples:
        # Local mode (direct API calls)
        connector = GitlabConnector(auth_config=GitlabAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GitlabConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GitlabConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GitlabAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GitlabReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A GitlabConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GitlabConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GitlabAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GitlabConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GitlabAuthConfig(access_token="..."),
                replication_config=GitlabReplicationConfig(start_date="..."),
            )
        
            # With server-side OAuth:
            connector = await GitlabConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GitlabReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GitlabReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            replication_config: Typed replication settings. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await GitlabConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Gitlab Source",
                replication_config=GitlabReplicationConfig(start_date="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GitlabConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GitlabConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GitlabConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GitlabCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="GroupMembersQuery"></a>

`GroupMembersQuery(connector: GitlabConnector)`
:   Query class for GroupMembers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GroupMembersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupMembersSearchData]`
    :   Search group_members records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GroupMembersSearchFilter):
        - group_id: ID of the group
        - id: ID of the member
        - name: Full name of the member
        - username: Username of the member
        - state: State of the member account
        - membership_state: State of the membership
        - avatar_url: URL of the member avatar
        - web_url: Web URL of the member profile
        - access_level: Access level of the member
        - created_at: Timestamp when the member was added
        - expires_at: Expiration date of the membership
        - created_by: User who added the member
        - locked: Whether the member account is locked
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GroupMembersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, group_id: str, user_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Member`
    :   Get a member of a group.
        
        Args:
            group_id: The ID or URL-encoded path of the group
            user_id: The user ID of the member
            **kwargs: Additional parameters
        
        Returns:
            Member

    `list(self, group_id: str, page: int | None = None, per_page: int | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Member], GroupMembersListResultMeta]`
    :   Gets a list of group members viewable by the authenticated user.
        
        Args:
            group_id: The ID or URL-encoded path of the group
            page: Page number
            per_page: Number of items per page
            query: Filter members by name or username
            **kwargs: Additional parameters
        
        Returns:
            GroupMembersListResult

<a id="GroupMilestonesQuery"></a>

`GroupMilestonesQuery(connector: GitlabConnector)`
:   Query class for GroupMilestones entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GroupMilestonesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupMilestonesSearchData]`
    :   Search group_milestones records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GroupMilestonesSearchFilter):
        - id: ID of the milestone
        - iid: Internal ID of the milestone within the group
        - group_id: ID of the group
        - title: Title of the milestone
        - description: Description of the milestone
        - state: State of the milestone
        - created_at: Timestamp when the milestone was created
        - updated_at: Timestamp when the milestone was last updated
        - due_date: Due date of the milestone
        - start_date: Start date of the milestone
        - expired: Whether the milestone is expired
        - web_url: Web URL of the milestone
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GroupMilestonesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, group_id: str, milestone_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Milestone`
    :   Get a single group milestone.
        
        Args:
            group_id: The ID or URL-encoded path of the group
            milestone_id: The ID of the milestone
            **kwargs: Additional parameters
        
        Returns:
            Milestone

    `list(self, group_id: str, page: int | None = None, per_page: int | None = None, state: str | None = None, search: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Milestone], GroupMilestonesListResultMeta]`
    :   Returns a list of group milestones.
        
        Args:
            group_id: The ID or URL-encoded path of the group
            page: Page number
            per_page: Number of items per page
            state: Filter milestones by state
            search: Search for milestones by title or description
            **kwargs: Additional parameters
        
        Returns:
            GroupMilestonesListResult

<a id="GroupsQuery"></a>

`GroupsQuery(connector: GitlabConnector)`
:   Query class for Groups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupsSearchData]`
    :   Search groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GroupsSearchFilter):
        - id: ID of the group
        - web_url: Web URL of the group
        - name: Name of the group
        - path: URL path of the group
        - description: Description of the group
        - visibility: Visibility level of the group
        - share_with_group_lock: Whether sharing with other groups is locked
        - require_two_factor_authentication: Whether two-factor authentication is required
        - two_factor_grace_period: Grace period for two-factor authentication
        - project_creation_level: Level required to create projects
        - auto_devops_enabled: Whether Auto DevOps is enabled
        - subgroup_creation_level: Level required to create subgroups
        - emails_disabled: Whether emails are disabled
        - emails_enabled: Whether emails are enabled
        - mentions_disabled: Whether mentions are disabled
        - lfs_enabled: Whether Git LFS is enabled
        - default_branch_protection: Default branch protection level
        - avatar_url: URL of the group avatar
        - request_access_enabled: Whether access requests are enabled
        - full_name: Full name of the group
        - full_path: Full path of the group
        - created_at: Timestamp when the group was created
        - parent_id: ID of the parent group
        - shared_with_groups: Groups this group is shared with
        - projects: Projects in the group
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Group`
    :   Get all details of a group.
        
        Args:
            id: The ID or URL-encoded path of the group
            **kwargs: Additional parameters
        
        Returns:
            Group

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, owned: bool | None = None, order_by: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Group], GroupsListResultMeta]`
    :   Get a list of visible groups for the authenticated user.
        
        Args:
            page: Page number
            per_page: Number of items per page
            search: Search for groups by name or path
            owned: Limit to groups explicitly owned by the current user
            order_by: Order groups by field
            sort: Sort order
            **kwargs: Additional parameters
        
        Returns:
            GroupsListResult

<a id="IssuesQuery"></a>

`IssuesQuery(connector: GitlabConnector)`
:   Query class for Issues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: IssuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[IssuesSearchData]`
    :   Search issues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssuesSearchFilter):
        - id: ID of the issue
        - iid: Internal ID of the issue within the project
        - project_id: ID of the project the issue belongs to
        - title: Title of the issue
        - description: Description of the issue
        - state: State of the issue
        - created_at: Timestamp when the issue was created
        - updated_at: Timestamp when the issue was last updated
        - closed_at: Timestamp when the issue was closed
        - labels: Labels assigned to the issue
        - assignees: Users assigned to the issue
        - type_: Type of the issue
        - user_notes_count: Number of user notes on the issue
        - merge_requests_count: Number of related merge requests
        - upvotes: Number of upvotes
        - downvotes: Number of downvotes
        - due_date: Due date for the issue
        - confidential: Whether the issue is confidential
        - discussion_locked: Whether discussion is locked
        - issue_type: Type classification of the issue
        - web_url: Web URL of the issue
        - time_stats: Time tracking statistics
        - task_completion_status: Task completion status
        - blocking_issues_count: Number of blocking issues
        - has_tasks: Whether the issue has tasks
        - links: Related resource links
        - references: Issue references
        - author: Author of the issue
        - author_id: ID of the author
        - assignee: Primary assignee of the issue
        - assignee_id: ID of the primary assignee
        - closed_by: User who closed the issue
        - closed_by_id: ID of the user who closed the issue
        - milestone: Milestone the issue belongs to
        - milestone_id: ID of the milestone
        - weight: Weight of the issue
        - severity: Severity level of the issue
        
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

    `get(self, project_id: str, issue_iid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Issue`
    :   Get a single project issue.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            issue_iid: The internal ID of a project's issue
            **kwargs: Additional parameters
        
        Returns:
            Issue

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, state: str | None = None, scope: str | None = None, order_by: str | None = None, sort: str | None = None, created_after: str | None = None, created_before: str | None = None, updated_after: str | None = None, updated_before: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Issue], IssuesListResultMeta]`
    :   Get a list of a project's issues.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            state: Filter issues by state
            scope: Filter issues by scope
            order_by: Return issues ordered by field
            sort: Return issues sorted in asc or desc order
            created_after: Return issues created on or after the given time (ISO 8601 format)
            created_before: Return issues created on or before the given time (ISO 8601 format)
            updated_after: Return issues updated on or after the given time (ISO 8601 format)
            updated_before: Return issues updated on or before the given time (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            IssuesListResult

<a id="MergeRequestsQuery"></a>

`MergeRequestsQuery(connector: GitlabConnector)`
:   Query class for MergeRequests entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MergeRequestsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[MergeRequestsSearchData]`
    :   Search merge_requests records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MergeRequestsSearchFilter):
        - id: ID of the merge request
        - iid: Internal ID of the merge request within the project
        - project_id: ID of the project
        - title: Title of the merge request
        - description: Description of the merge request
        - state: State of the merge request
        - created_at: Timestamp when the merge request was created
        - updated_at: Timestamp when the merge request was last updated
        - merged_at: Timestamp when the merge request was merged
        - closed_at: Timestamp when the merge request was closed
        - target_branch: Target branch for the merge request
        - source_branch: Source branch for the merge request
        - user_notes_count: Number of user notes
        - upvotes: Number of upvotes
        - downvotes: Number of downvotes
        - assignees: Users assigned to the merge request
        - reviewers: Users assigned as reviewers
        - source_project_id: ID of the source project
        - target_project_id: ID of the target project
        - labels: Labels assigned to the merge request
        - work_in_progress: Whether the merge request is a work in progress
        - merge_when_pipeline_succeeds: Whether to merge when pipeline succeeds
        - merge_status: Merge status of the merge request
        - sha: SHA of the head commit
        - merge_commit_sha: SHA of the merge commit
        - squash_commit_sha: SHA of the squash commit
        - discussion_locked: Whether discussion is locked
        - should_remove_source_branch: Whether source branch should be removed
        - force_remove_source_branch: Whether to force remove source branch
        - reference: Short reference for the merge request
        - references: Merge request references
        - web_url: Web URL of the merge request
        - time_stats: Time tracking statistics
        - squash: Whether to squash commits on merge
        - task_completion_status: Task completion status
        - has_conflicts: Whether the merge request has conflicts
        - blocking_discussions_resolved: Whether blocking discussions are resolved
        - author: Author of the merge request
        - author_id: ID of the author
        - assignee: Primary assignee of the merge request
        - assignee_id: ID of the primary assignee
        - closed_by: User who closed the merge request
        - closed_by_id: ID of the user who closed it
        - milestone: Milestone the merge request belongs to
        - milestone_id: ID of the milestone
        - merged_by: User who merged the merge request
        - merged_by_id: ID of the user who merged it
        - draft: Whether the merge request is a draft
        - detailed_merge_status: Detailed merge status
        - merge_user: User who performed the merge
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MergeRequestsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, merge_request_iid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.MergeRequest`
    :   Get information about a single merge request.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            merge_request_iid: The internal ID of the merge request
            **kwargs: Additional parameters
        
        Returns:
            MergeRequest

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, state: str | None = None, scope: str | None = None, order_by: str | None = None, sort: str | None = None, created_after: str | None = None, created_before: str | None = None, updated_after: str | None = None, updated_before: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[MergeRequest], MergeRequestsListResultMeta]`
    :   Get all merge requests for a project.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            state: Filter merge requests by state
            scope: Filter merge requests by scope
            order_by: Return merge requests ordered by field
            sort: Return merge requests sorted in asc or desc order
            created_after: Return merge requests created on or after the given time (ISO 8601 format)
            created_before: Return merge requests created on or before the given time (ISO 8601 format)
            updated_after: Return merge requests updated on or after the given time (ISO 8601 format)
            updated_before: Return merge requests updated on or before the given time (ISO 8601 format)
            **kwargs: Additional parameters
        
        Returns:
            MergeRequestsListResult

<a id="PipelinesQuery"></a>

`PipelinesQuery(connector: GitlabConnector)`
:   Query class for Pipelines entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PipelinesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[PipelinesSearchData]`
    :   Search pipelines records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PipelinesSearchFilter):
        - id: ID of the pipeline
        - iid: Internal ID of the pipeline within the project
        - project_id: ID of the project
        - sha: SHA of the commit that triggered the pipeline
        - source: Source that triggered the pipeline
        - ref: Branch or tag that triggered the pipeline
        - status: Status of the pipeline
        - created_at: Timestamp when the pipeline was created
        - updated_at: Timestamp when the pipeline was last updated
        - web_url: Web URL of the pipeline
        - name: Name of the pipeline
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PipelinesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, pipeline_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Pipeline`
    :   Get one pipeline of a project.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            pipeline_id: The ID of the pipeline
            **kwargs: Additional parameters
        
        Returns:
            Pipeline

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, status: str | None = None, ref: str | None = None, order_by: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Pipeline], PipelinesListResultMeta]`
    :   List pipelines in a project.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            status: Filter pipelines by status
            ref: Filter pipelines by ref
            order_by: Order pipelines by field
            sort: Sort order
            **kwargs: Additional parameters
        
        Returns:
            PipelinesListResult

<a id="ProjectMembersQuery"></a>

`ProjectMembersQuery(connector: GitlabConnector)`
:   Query class for ProjectMembers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectMembersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectMembersSearchData]`
    :   Search project_members records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectMembersSearchFilter):
        - project_id: ID of the project
        - id: ID of the member
        - name: Full name of the member
        - username: Username of the member
        - state: State of the member account
        - membership_state: State of the membership
        - avatar_url: URL of the member avatar
        - web_url: Web URL of the member profile
        - access_level: Access level of the member
        - created_at: Timestamp when the member was added
        - expires_at: Expiration date of the membership
        - created_by: User who added the member
        - locked: Whether the member account is locked
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectMembersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, user_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Member`
    :   Get a member of a project.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            user_id: The user ID of the member
            **kwargs: Additional parameters
        
        Returns:
            Member

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Member], ProjectMembersListResultMeta]`
    :   Gets a list of project members viewable by the authenticated user.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            query: Filter members by name or username
            **kwargs: Additional parameters
        
        Returns:
            ProjectMembersListResult

<a id="ProjectMilestonesQuery"></a>

`ProjectMilestonesQuery(connector: GitlabConnector)`
:   Query class for ProjectMilestones entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectMilestonesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectMilestonesSearchData]`
    :   Search project_milestones records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectMilestonesSearchFilter):
        - id: ID of the milestone
        - iid: Internal ID of the milestone within the project
        - project_id: ID of the project
        - title: Title of the milestone
        - description: Description of the milestone
        - state: State of the milestone
        - created_at: Timestamp when the milestone was created
        - updated_at: Timestamp when the milestone was last updated
        - due_date: Due date of the milestone
        - start_date: Start date of the milestone
        - expired: Whether the milestone is expired
        - web_url: Web URL of the milestone
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectMilestonesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, milestone_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Milestone`
    :   Get a single project milestone.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            milestone_id: The ID of the milestone
            **kwargs: Additional parameters
        
        Returns:
            Milestone

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, state: str | None = None, search: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Milestone], ProjectMilestonesListResultMeta]`
    :   Returns a list of project milestones.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            state: Filter milestones by state
            search: Search for milestones by title or description
            **kwargs: Additional parameters
        
        Returns:
            ProjectMilestonesListResult

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: GitlabConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - id: ID of the project
        - description: Description of the project
        - description_html: HTML-rendered description of the project
        - name: Name of the project
        - name_with_namespace: Full name including namespace
        - path: URL path of the project
        - path_with_namespace: Full path including namespace
        - created_at: Timestamp when the project was created
        - updated_at: Timestamp when the project was last updated
        - default_branch: Default branch of the project
        - tag_list: List of tags for the project
        - topics: List of topics for the project
        - ssh_url_to_repo: SSH URL to the repository
        - http_url_to_repo: HTTP URL to the repository
        - web_url: Web URL of the project
        - readme_url: URL to the project README
        - avatar_url: URL of the project avatar
        - forks_count: Number of forks
        - star_count: Number of stars
        - last_activity_at: Timestamp of last activity
        - namespace: Namespace the project belongs to
        - container_registry_image_prefix: Prefix for container registry images
        - links: Related resource links
        - packages_enabled: Whether packages are enabled
        - empty_repo: Whether the repository is empty
        - archived: Whether the project is archived
        - visibility: Visibility level of the project
        - resolve_outdated_diff_discussions: Whether outdated diff discussions are auto-resolved
        - container_registry_enabled: Whether container registry is enabled
        - container_expiration_policy: Container expiration policy settings
        - issues_enabled: Whether issues are enabled
        - merge_requests_enabled: Whether merge requests are enabled
        - wiki_enabled: Whether wiki is enabled
        - jobs_enabled: Whether jobs are enabled
        - snippets_enabled: Whether snippets are enabled
        - service_desk_enabled: Whether service desk is enabled
        - service_desk_address: Email address for the service desk
        - can_create_merge_request_in: Whether user can create merge requests
        - issues_access_level: Access level for issues
        - repository_access_level: Access level for the repository
        - merge_requests_access_level: Access level for merge requests
        - forking_access_level: Access level for forking
        - wiki_access_level: Access level for the wiki
        - builds_access_level: Access level for builds
        - snippets_access_level: Access level for snippets
        - pages_access_level: Access level for pages
        - operations_access_level: Access level for operations
        - analytics_access_level: Access level for analytics
        - emails_disabled: Whether emails are disabled
        - shared_runners_enabled: Whether shared runners are enabled
        - lfs_enabled: Whether Git LFS is enabled
        - creator_id: ID of the project creator
        - import_status: Import status of the project
        - open_issues_count: Number of open issues
        - ci_default_git_depth: Default git depth for CI pipelines
        - ci_forward_deployment_enabled: Whether CI forward deployment is enabled
        - public_jobs: Whether jobs are public
        - build_timeout: Build timeout in seconds
        - auto_cancel_pending_pipelines: Auto-cancel pending pipelines setting
        - ci_config_path: Path to the CI configuration file
        - shared_with_groups: Groups the project is shared with
        - only_allow_merge_if_pipeline_succeeds: Whether merge requires pipeline success
        - allow_merge_on_skipped_pipeline: Whether merge is allowed on skipped pipeline
        - restrict_user_defined_variables: Whether user-defined variables are restricted
        - request_access_enabled: Whether access requests are enabled
        - only_allow_merge_if_all_discussions_are_resolved: Whether merge requires all discussions resolved
        - remove_source_branch_after_merge: Whether source branch is removed after merge
        - printing_merge_request_link_enabled: Whether MR link printing is enabled
        - merge_method: Merge method used for the project
        - statistics: Project statistics
        - auto_devops_enabled: Whether Auto DevOps is enabled
        - auto_devops_deploy_strategy: Auto DevOps deployment strategy
        - autoclose_referenced_issues: Whether referenced issues are auto-closed
        - external_authorization_classification_label: External authorization classification label
        - requirements_enabled: Whether requirements are enabled
        - security_and_compliance_enabled: Whether security and compliance is enabled
        - compliance_frameworks: Compliance frameworks for the project
        - permissions: User permissions for the project
        - keep_latest_artifact: Whether the latest artifact is kept
        
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

    `get(self, id: str | None = None, statistics: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Project`
    :   Get a specific project by ID.
        
        Args:
            id: The ID or URL-encoded path of the project
            statistics: Include project statistics
            **kwargs: Additional parameters
        
        Returns:
            Project

    `list(self, page: int | None = None, per_page: int | None = None, membership: bool | None = None, owned: bool | None = None, search: str | None = None, order_by: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Project], ProjectsListResultMeta]`
    :   Get a list of all visible projects across GitLab for the authenticated user.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page (max 100)
            membership: Limit by projects that the current user is a member of
            owned: Limit by projects explicitly owned by the current user
            search: Return list of projects matching the search criteria
            order_by: Return projects ordered by field
            sort: Return projects sorted in asc or desc order
            **kwargs: Additional parameters
        
        Returns:
            ProjectsListResult

<a id="ReleasesQuery"></a>

`ReleasesQuery(connector: GitlabConnector)`
:   Query class for Releases entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ReleasesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ReleasesSearchData]`
    :   Search releases records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ReleasesSearchFilter):
        - name: Name of the release
        - tag_name: Tag name associated with the release
        - description: Description of the release
        - created_at: Timestamp when the release was created
        - released_at: Timestamp when the release was published
        - upcoming_release: Whether this is an upcoming release
        - milestones: Milestones associated with the release
        - commit_path: Path to the release commit
        - tag_path: Path to the release tag
        - assets: Assets attached to the release
        - evidences: Evidences collected for the release
        - links: Related resource links
        - author: Author of the release
        - author_id: ID of the author
        - commit: Commit associated with the release
        - commit_id: SHA of the associated commit
        - project_id: ID of the project
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ReleasesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, project_id: str, tag_name: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Release`
    :   Get a release for the given tag.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            tag_name: The Git tag the release is associated with
            **kwargs: Additional parameters
        
        Returns:
            Release

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, order_by: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Release], ReleasesListResultMeta]`
    :   Paginated list of releases for a given project, sorted by released_at.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            order_by: Order by field
            sort: Sort order
            **kwargs: Additional parameters
        
        Returns:
            ReleasesListResult

<a id="TagsQuery"></a>

`TagsQuery(connector: GitlabConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[TagsSearchData]`
    :   Search tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TagsSearchFilter):
        - name: Name of the tag
        - message: Annotation message of the tag
        - target: SHA the tag points to
        - release: Release associated with the tag
        - protected: Whether the tag is protected
        - commit: Commit the tag points to
        - commit_id: SHA of the tagged commit
        - project_id: ID of the project
        
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

    `get(self, project_id: str, tag_name: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.Tag`
    :   Get a specific repository tag determined by its name.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            tag_name: The name of the tag
            **kwargs: Additional parameters
        
        Returns:
            Tag

    `list(self, project_id: str, page: int | None = None, per_page: int | None = None, search: str | None = None, order_by: str | None = None, sort: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Tag], TagsListResultMeta]`
    :   Get a list of repository tags from a project, sorted by update date and time in descending order.
        
        Args:
            project_id: The ID or URL-encoded path of the project
            page: Page number
            per_page: Number of items per page
            search: Return list of tags matching the search criteria
            order_by: Return tags ordered by field
            sort: Sort order
            **kwargs: Additional parameters
        
        Returns:
            TagsListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: GitlabConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - id: ID of the user
        - name: Full name of the user
        - username: Username of the user
        - state: State of the user account
        - avatar_url: URL of the user avatar
        - web_url: Web URL of the user profile
        - locked: Whether the user account is locked
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.User`
    :   Get a single user by ID.
        
        Args:
            id: The ID of the user
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, page: int | None = None, per_page: int | None = None, search: str | None = None, active: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Get a list of users.
        
        Args:
            page: Page number
            per_page: Number of items per page
            search: Search for users by name, username, or email
            active: Filter users by active state
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult