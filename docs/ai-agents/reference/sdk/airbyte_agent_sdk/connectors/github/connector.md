---
id: airbyte_agent_sdk-connectors-github-connector
title: airbyte_agent_sdk.connectors.github.connector
---

Module airbyte_agent_sdk.connectors.github.connector
====================================================
Github connector.

Classes
-------

<a id="BranchesQuery"></a>

`BranchesQuery(connector: GithubConnector)`
:   Query class for Branches entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BranchesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[BranchesSearchData]`
    :   Search branches records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BranchesSearchFilter):
        - name: Branch name (e.g. `main`, `feature/foo`)
        - prefix: Git ref prefix for the branch (typically `refs/heads/`)
        
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

    `get(self, owner: str, repo: str, branch: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific branch using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            branch: The branch name
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], BranchesListResultMeta]`
    :   Returns a list of branches for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            BranchesListResult

<a id="CommentsQuery"></a>

`CommentsQuery(connector: GithubConnector)`
:   Query class for Comments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CommentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[CommentsSearchData]`
    :   Search comments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CommentsSearchFilter):
        - id: GraphQL node ID of the comment
        - database_id: REST API numeric identifier for the comment
        - body: Markdown body of the comment
        - created_at: ISO 8601 timestamp when the comment was created
        - updated_at: ISO 8601 timestamp when the comment was last updated
        - url: Permalink to the comment on GitHub
        - is_minimized: Whether the comment has been hidden/collapsed
        
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

    `create(self, body: str, owner: str, repo: str, issue_number: str, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.CommentResponse`
    :   Creates a comment on the specified issue.
        This endpoint works for both issues and pull requests, since pull requests are issues.
        Any user with read access can create a comment.
        
        
                Args:
                    body: The contents of the comment (supports Markdown)
                    owner: The account owner of the repository (username or organization)
                    repo: The name of the repository
                    issue_number: The number that identifies the issue or pull request
                    **kwargs: Additional parameters
        
                Returns:
                    CommentResponse

    `get(self, id: str | None = None, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific issue comment by its GraphQL node ID.
        
        Note: This endpoint requires a GraphQL node ID (e.g., 'IC_kwDOBZtLds6YWTMj'),
        not a numeric database ID. You can obtain node IDs from the Comments_List response,
        where each comment includes both 'id' (node ID) and 'databaseId' (numeric ID).
        
        
                Args:
                    id: The GraphQL node ID of the comment
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `list(self, owner: str, repo: str, number: int, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], CommentsListResultMeta]`
    :   Returns a list of comments for the specified issue using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The issue number
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            CommentsListResult

<a id="CommitsQuery"></a>

`CommitsQuery(connector: GithubConnector)`
:   Query class for Commits entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CommitsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[CommitsSearchData]`
    :   Search commits records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CommitsSearchFilter):
        - oid: Full Git commit SHA
        - abbreviated_oid: Abbreviated Git commit SHA (typically 7 characters)
        - message_headline: First line of the commit message
        - message: Full commit message
        - committed_date: ISO 8601 timestamp when the commit was applied to its tree
        - authored_date: ISO 8601 timestamp when the commit was originally authored
        - additions: Number of lines added across all files in the commit
        - deletions: Number of lines deleted across all files in the commit
        - changed_files: Number of files changed in the commit
        - url: Permalink to the commit on GitHub
        
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

    `get(self, owner: str, repo: str, sha: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific commit by SHA using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            sha: The commit SHA
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, per_page: int | None = None, after: str | None = None, path: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], CommitsListResultMeta]`
    :   Returns a list of commits for the default branch using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            per_page: The number of results per page
            after: Cursor for pagination
            path: Only include commits that modified this file path (e.g. "airbyte-integrations/connectors/source-stripe/")
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            CommitsListResult

<a id="DirectoryContentQuery"></a>

`DirectoryContentQuery(connector: GithubConnector)`
:   Query class for DirectoryContent entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DirectoryContentSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[DirectoryContentSearchData]`
    :   Search directory_content records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DirectoryContentSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DirectoryContentSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, owner: str, repo: str, path: str, ref: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResult[list[dict[str, Any]]]`
    :   Returns a list of files and subdirectories at a specific path in the repository.
        Each entry includes the name, type (blob for files, tree for directories), and object ID.
        Use this to explore repository structure before reading specific files.
        
        
                Args:
                    owner: The account owner of the repository
                    repo: The name of the repository
                    path: The directory path within the repository (e.g. 'src' or 'airbyte-integrations/connectors/source-stripe')
                    ref: The git ref — branch name, tag, or commit SHA. Defaults to 'HEAD' (default branch)
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    DirectoryContentListResult

<a id="DiscussionsQuery"></a>

`DiscussionsQuery(connector: GithubConnector)`
:   Query class for Discussions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], DiscussionsApiSearchResultMeta]`
    :   Search for discussions using GitHub's search syntax
        
        Args:
            query: GitHub discussion search query using GitHub's search syntax
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            DiscussionsApiSearchResult

    `context_store_search(self, query: DiscussionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[DiscussionsSearchData]`
    :   Search discussions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DiscussionsSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DiscussionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, owner: str, repo: str, number: int, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific discussion by number using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The discussion number
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, states: list[str] | None = None, answered: bool | None = None, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], DiscussionsListResultMeta]`
    :   Returns a list of discussions for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            states: Filter by discussion state
            answered: Filter by answered/unanswered status
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            DiscussionsListResult

<a id="FileContentQuery"></a>

`FileContentQuery(connector: GithubConnector)`
:   Query class for FileContent entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FileContentSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[FileContentSearchData]`
    :   Search file_content records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FileContentSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FileContentSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, owner: str, repo: str, path: str, ref: str | None = None, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Returns the text content of a file at a specific path and git ref (branch, tag, or commit SHA).
        Only works for text files. Binary files will have text as null and isBinary as true.
        
        
                Args:
                    owner: The account owner of the repository
                    repo: The name of the repository
                    path: The file path within the repository (e.g. 'README.md' or 'src/main.py')
                    ref: The git ref to read from — branch name, tag, or commit SHA. Defaults to 'HEAD' (default branch)
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

<a id="GithubConnector"></a>

`GithubConnector(auth_config: GithubAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Github API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new github connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GithubAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GithubConnector(auth_config=GithubAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GithubConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GithubConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GithubAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GithubReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A GithubConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GithubConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GithubAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GithubConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GithubAuthConfig(access_token="..."),
                replication_config=GithubReplicationConfig(repositories="..."),
            )
        
            # With server-side OAuth:
            connector = await GithubConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GithubReplicationConfig(repositories="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GithubReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            consent_url = await GithubConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Github Source",
                replication_config=GithubReplicationConfig(repositories="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @GithubConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GithubConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GithubConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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
        
        Example:
            connector = await GithubConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.github.models.GithubCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GithubCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="IssuesQuery"></a>

`IssuesQuery(connector: GithubConnector)`
:   Query class for Issues entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], IssuesApiSearchResultMeta]`
    :   Search for issues using GitHub's search syntax
        
        Args:
            query: GitHub issue search query using GitHub's search syntax
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            IssuesApiSearchResult

    `context_store_search(self, query: IssuesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[IssuesSearchData]`
    :   Search issues records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (IssuesSearchFilter):
        - id: GraphQL node ID of the issue
        - database_id: REST API numeric identifier for the issue
        - number: Repository-scoped issue number
        - title: Issue title
        - state: Issue state: `OPEN` or `CLOSED`
        - state_reason: Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)
        - created_at: ISO 8601 timestamp when the issue was created
        - updated_at: ISO 8601 timestamp when the issue was last updated
        - closed_at: ISO 8601 timestamp when the issue was closed, if applicable
        - locked: Whether the conversation on the issue is locked
        - url: Permalink to the issue on GitHub
        
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

    `create(self, title: str, owner: str, repo: str, body: str | None = None, labels: list[str] | None = None, assignees: list[str] | None = None, milestone: int | None | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.IssueResponse`
    :   Creates a new issue in the specified repository.
        Any user with pull access to a repository can create an issue.
        Labels and assignees are silently dropped if the authenticated user does not have push access.
        
        
                Args:
                    title: The title of the issue
                    body: The contents of the issue (supports Markdown)
                    labels: Labels to associate with this issue (requires push access)
                    assignees: Logins for users to assign to this issue (requires push access)
                    milestone: The number of the milestone to associate this issue with (requires push access)
                    owner: The account owner of the repository (username or organization)
                    repo: The name of the repository
                    **kwargs: Additional parameters
        
                Returns:
                    IssueResponse

    `get(self, owner: str, repo: str, number: int, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific issue using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The issue number
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, states: list[str] | None = None, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], IssuesListResultMeta]`
    :   Returns a list of issues for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            states: Filter by issue state
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            IssuesListResult

    `update(self, owner: str, repo: str, issue_number: str, title: str | None = None, body: str | None = None, state: str | None = None, state_reason: str | None | None = None, labels: list[str] | None = None, assignees: list[str] | None = None, milestone: int | None | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.IssueResponse`
    :   Updates an existing issue in the specified repository.
        Use this to close/reopen issues, change title/body, add/remove labels, assign users, or set milestones.
        Any user with push access can update an issue.
        
        
                Args:
                    title: The title of the issue
                    body: The contents of the issue (supports Markdown)
                    state: State of the issue: open or closed
                    state_reason: Reason for the state change: completed, not_planned, reopened, or null
                    labels: Labels to set on this issue (replaces all existing labels; requires push access)
                    assignees: Logins for users to assign to this issue (replaces all existing assignees; requires push access)
                    milestone: The number of the milestone to associate this issue with, or null to remove the milestone (requires push access)
                    owner: The account owner of the repository (username or organization)
                    repo: The name of the repository
                    issue_number: The number that identifies the issue
                    **kwargs: Additional parameters
        
                Returns:
                    IssueResponse

<a id="LabelsQuery"></a>

`LabelsQuery(connector: GithubConnector)`
:   Query class for Labels entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: LabelsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[LabelsSearchData]`
    :   Search labels records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (LabelsSearchFilter):
        - id: GraphQL node ID of the label
        - name: Label name
        - color: Label color as a 6-character hex string without a leading `#`
        - description: Short description of what the label is used for
        - created_at: ISO 8601 timestamp when the label was created
        - url: Permalink to the label on GitHub
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            LabelsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, owner: str, repo: str, name: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific label by name using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            name: The label name
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], LabelsListResultMeta]`
    :   Returns a list of labels for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            LabelsListResult

<a id="MilestonesQuery"></a>

`MilestonesQuery(connector: GithubConnector)`
:   Query class for Milestones entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: MilestonesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[MilestonesSearchData]`
    :   Search milestones records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (MilestonesSearchFilter):
        - id: GraphQL node ID of the milestone
        - number: Repository-scoped milestone number
        - title: Milestone title
        - description: Milestone description
        - state: Milestone state: `OPEN` or `CLOSED`
        - due_on: ISO 8601 timestamp for the milestone's due date, if set
        - closed_at: ISO 8601 timestamp when the milestone was closed, if applicable
        - created_at: ISO 8601 timestamp when the milestone was created
        - updated_at: ISO 8601 timestamp when the milestone was last updated
        - progress_percentage: Percentage of associated issues/PRs that are closed
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            MilestonesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, owner: str, repo: str, number: int, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific milestone by number using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The milestone number
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, states: list[str] | None = None, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], MilestonesListResultMeta]`
    :   Returns a list of milestones for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            states: Filter by milestone state
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            MilestonesListResult

<a id="OrgRepositoriesQuery"></a>

`OrgRepositoriesQuery(connector: GithubConnector)`
:   Query class for OrgRepositories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrgRepositoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[OrgRepositoriesSearchData]`
    :   Search org_repositories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrgRepositoriesSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrgRepositoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, org: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], OrgRepositoriesListResultMeta]`
    :   Returns a list of repositories for the specified organization using GraphQL
        
        Args:
            org: The organization login/username
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            OrgRepositoriesListResult

<a id="OrganizationsQuery"></a>

`OrganizationsQuery(connector: GithubConnector)`
:   Query class for Organizations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OrganizationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[OrganizationsSearchData]`
    :   Search organizations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OrganizationsSearchFilter):
        - id: GraphQL node ID of the organization
        - database_id: REST API numeric identifier for the organization
        - login: Organization login/handle (unique URL slug)
        - name: Display name of the organization
        - description: Short public description of the organization
        - email: Public contact email for the organization, if set
        - location: Public location of the organization, if set
        - is_verified: Whether the organization has a verified domain
        - created_at: ISO 8601 timestamp when the organization was created
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OrganizationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, org: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific organization using GraphQL
        
        Args:
            org: The organization login/username
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, username: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], OrganizationsListResultMeta]`
    :   Returns a list of organizations the user belongs to using GraphQL
        
        Args:
            username: The username of the user
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            OrganizationsListResult

<a id="PrCommentsQuery"></a>

`PrCommentsQuery(connector: GithubConnector)`
:   Query class for PrComments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PrCommentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[PrCommentsSearchData]`
    :   Search pr_comments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PrCommentsSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PrCommentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific pull request comment by its GraphQL node ID.
        
        Note: This endpoint requires a GraphQL node ID (e.g., 'IC_kwDOBZtLds6YWTMj'),
        not a numeric database ID. You can obtain node IDs from the PRComments_List response,
        where each comment includes both 'id' (node ID) and 'databaseId' (numeric ID).
        
        
                Args:
                    id: The GraphQL node ID of the comment
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `list(self, owner: str, repo: str, number: int, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], PrCommentsListResultMeta]`
    :   Returns a list of comments for the specified pull request using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The pull request number
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            PrCommentsListResult

<a id="ProjectItemsQuery"></a>

`ProjectItemsQuery(connector: GithubConnector)`
:   Query class for ProjectItems entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectItemsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ProjectItemsSearchData]`
    :   Search project_items records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectItemsSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectItemsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, org: str, project_number: int, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ProjectItemsListResultMeta]`
    :   Returns a list of items (issues, pull requests, draft issues) in a GitHub Project V2.
        Each item includes its field values like Status, Priority, etc.
        
        
                Args:
                    org: The organization login/username
                    project_number: The project number
                    per_page: The number of results per page
                    after: Cursor for pagination (from previous response's endCursor)
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    ProjectItemsListResult

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: GithubConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - id: GraphQL node ID of the project
        - number: Organization- or user-scoped project number
        - title: Project title
        - short_description: Short description displayed on the project summary
        - url: Permalink to the project on GitHub
        - closed: Whether the project has been closed
        - public: Whether the project is publicly visible
        - created_at: ISO 8601 timestamp when the project was created
        - updated_at: ISO 8601 timestamp when the project was last updated
        
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

    `get(self, org: str, project_number: int, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific GitHub Project V2 by number
        
        Args:
            org: The organization login/username
            project_number: The project number
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, org: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ProjectsListResultMeta]`
    :   Returns a list of GitHub Projects V2 for the specified organization.
        Projects V2 are the new project boards that replaced classic projects.
        
        
                Args:
                    org: The organization login/username
                    per_page: The number of results per page
                    after: Cursor for pagination (from previous response's endCursor)
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    ProjectsListResult

<a id="PullRequestsQuery"></a>

`PullRequestsQuery(connector: GithubConnector)`
:   Query class for PullRequests entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], PullRequestsApiSearchResultMeta]`
    :   Search for pull requests using GitHub's search syntax
        
        Args:
            query: GitHub pull request search query using GitHub's search syntax
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            PullRequestsApiSearchResult

    `context_store_search(self, query: PullRequestsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[PullRequestsSearchData]`
    :   Search pull_requests records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PullRequestsSearchFilter):
        - id: GraphQL node ID of the pull request
        - database_id: REST API numeric identifier for the pull request
        - number: Repository-scoped pull request number
        - title: Pull request title
        - state: Pull request state: `OPEN`, `CLOSED`, or `MERGED`
        - is_draft: Whether the pull request is still a draft
        - merged: Whether the pull request has been merged
        - created_at: ISO 8601 timestamp when the pull request was created
        - updated_at: ISO 8601 timestamp when the pull request was last updated
        - closed_at: ISO 8601 timestamp when the pull request was closed, if applicable
        - merged_at: ISO 8601 timestamp when the pull request was merged, if applicable
        - base_ref_name: Name of the branch being merged into
        - head_ref_name: Name of the branch with the proposed changes
        - url: Permalink to the pull request on GitHub
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PullRequestsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, title: str, head: str, base: str, owner: str, repo: str, body: str | None = None, draft: bool | None = None, maintainer_can_modify: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.PullRequestResponse`
    :   Creates a new pull request in the specified repository.
        To open or update a pull request in a public repository, you must have write access to the head or the source branch.
        
        
                Args:
                    title: The title of the new pull request
                    head: The name of the branch where your changes are implemented. For cross-repository pull requests in the same network, namespace head with a user like this: username:branch
                    base: The name of the branch you want the changes pulled into (e.g. main)
                    body: The contents of the pull request (supports Markdown)
                    draft: Indicates whether the pull request is a draft
                    maintainer_can_modify: Indicates whether maintainers can modify the pull request
                    owner: The account owner of the repository (username or organization)
                    repo: The name of the repository
                    **kwargs: Additional parameters
        
                Returns:
                    PullRequestResponse

    `get(self, owner: str, repo: str, number: int, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific pull request using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The pull request number
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, states: list[str] | None = None, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], PullRequestsListResultMeta]`
    :   Returns a list of pull requests for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            states: Filter by pull request state
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            PullRequestsListResult

<a id="ReleasesQuery"></a>

`ReleasesQuery(connector: GithubConnector)`
:   Query class for Releases entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ReleasesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ReleasesSearchData]`
    :   Search releases records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ReleasesSearchFilter):
        - id: GraphQL node ID of the release
        - database_id: REST API numeric identifier for the release
        - name: Display name of the release
        - tag_name: Git tag the release points at (e.g. `v1.2.3`)
        - description: Markdown body / release notes
        - published_at: ISO 8601 timestamp when the release was published
        - created_at: ISO 8601 timestamp when the release was created
        - is_prerelease: Whether the release is marked as a pre-release
        - is_draft: Whether the release is still a draft and not published
        - url: Permalink to the release on GitHub
        
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

    `get(self, owner: str, repo: str, tag: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific release by tag name using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            tag: The release tag name
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ReleasesListResultMeta]`
    :   Returns a list of releases for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            ReleasesListResult

<a id="RepositoriesQuery"></a>

`RepositoriesQuery(connector: GithubConnector)`
:   Query class for Repositories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], RepositoriesApiSearchResultMeta]`
    :   Search for GitHub repositories using GitHub's powerful search syntax.
        Examples: "language:python stars:>1000", "topic:machine-learning", "org:facebook is:public"
        
        
                Args:
                    query: GitHub repository search query using GitHub's search syntax
                    limit: Number of results to return
                    after: Cursor for pagination (from previous response's endCursor)
                    fields: Optional array of field names to select.
        If not provided, uses default fields.
        
                    **kwargs: Additional parameters
        
                Returns:
                    RepositoriesApiSearchResult

    `context_store_search(self, query: RepositoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[RepositoriesSearchData]`
    :   Search repositories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (RepositoriesSearchFilter):
        - id: GraphQL node ID of the repository
        - name: Short repository name (without owner)
        - name_with_owner: Fully-qualified `owner/name` identifier for the repository
        - description: Short description of the repository
        - url: Canonical GitHub URL for the repository
        - created_at: ISO 8601 timestamp when the repository was created
        - updated_at: ISO 8601 timestamp when the repository was last updated
        - pushed_at: ISO 8601 timestamp of the most recent push to the repository
        - fork_count: Number of forks of the repository
        - stargazer_count: Number of users who have starred the repository
        - is_private: Whether the repository is private
        - is_fork: Whether the repository is a fork of another repository
        - is_archived: Whether the repository has been archived
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            RepositoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, owner: str, repo: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific GitHub repository using GraphQL
        
                Args:
                    owner: The account owner of the repository (username or organization)
                    repo: The name of the repository
                    fields: Optional array of field names to select.
        If not provided, uses default fields.
        
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `list(self, username: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], RepositoriesListResultMeta]`
    :   Returns a list of repositories for the specified user using GraphQL
        
                Args:
                    username: The username of the user whose repositories to list
                    per_page: The number of results per page
                    after: Cursor for pagination (from previous response's endCursor)
                    fields: Optional array of field names to select.
        If not provided, uses default fields.
        
                    **kwargs: Additional parameters
        
                Returns:
                    RepositoriesListResult

<a id="ReviewsQuery"></a>

`ReviewsQuery(connector: GithubConnector)`
:   Query class for Reviews entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ReviewsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ReviewsSearchData]`
    :   Search reviews records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ReviewsSearchFilter):
        - id: GraphQL node ID of the review
        - database_id: REST API numeric identifier for the review
        - state: Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`
        - body: Review body text
        - submitted_at: ISO 8601 timestamp when the review was submitted
        - created_at: ISO 8601 timestamp when the review was created
        - updated_at: ISO 8601 timestamp when the review was last updated
        - url: Permalink to the review on GitHub
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ReviewsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, owner: str, repo: str, number: int, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ReviewsListResultMeta]`
    :   Returns a list of reviews for the specified pull request using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            number: The pull request number
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            ReviewsListResult

<a id="StargazersQuery"></a>

`StargazersQuery(connector: GithubConnector)`
:   Query class for Stargazers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: StargazersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[StargazersSearchData]`
    :   Search stargazers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (StargazersSearchFilter):
        - starred_at: ISO 8601 timestamp when the user starred the repository
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            StargazersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, owner: str, repo: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], StargazersListResultMeta]`
    :   Returns a list of users who have starred the repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            StargazersListResult

<a id="TagsQuery"></a>

`TagsQuery(connector: GithubConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[TagsSearchData]`
    :   Search tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TagsSearchFilter):
        - name: Tag name (e.g. `v1.2.3`)
        - prefix: Git ref prefix for the tag (typically `refs/tags/`)
        
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

    `get(self, owner: str, repo: str, tag: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific tag by name using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            tag: The tag name
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, owner: str, repo: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], TagsListResultMeta]`
    :   Returns a list of tags for the specified repository using GraphQL
        
        Args:
            owner: The account owner of the repository
            repo: The name of the repository
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            TagsListResult

<a id="TeamsQuery"></a>

`TeamsQuery(connector: GithubConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - id: GraphQL node ID of the team
        - database_id: REST API numeric identifier for the team
        - slug: URL-friendly slug for the team within its organization
        - name: Display name of the team
        - description: Short description of the team
        - privacy: Team visibility: `SECRET` or `VISIBLE`
        - url: Permalink to the team on GitHub
        - created_at: ISO 8601 timestamp when the team was created
        - updated_at: ISO 8601 timestamp when the team was last updated
        
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

    `get(self, org: str, team_slug: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific team using GraphQL
        
        Args:
            org: The organization login/username
            team_slug: The team slug
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, org: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], TeamsListResultMeta]`
    :   Returns a list of teams for the specified organization using GraphQL
        
        Args:
            org: The organization login/username
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            TeamsListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: GithubConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], UsersApiSearchResultMeta]`
    :   Search for GitHub users using search syntax
        
        Args:
            query: GitHub user search query using GitHub's search syntax
            limit: Number of results to return
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            UsersApiSearchResult

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - id: GraphQL node ID of the user
        - database_id: REST API numeric identifier for the user
        - login: User login/handle
        - name: Public display name of the user, if set
        - email: Public email address of the user, if set
        - company: Public company affiliation of the user, if set
        - location: Public location of the user, if set
        - twitter_username: Public Twitter/X username of the user, if set
        - url: Permalink to the user's profile on GitHub
        - created_at: ISO 8601 timestamp when the user account was created
        - is_hireable: Whether the user has marked themselves as available for hire
        
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

    `get(self, username: str, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about a specific user using GraphQL
        
        Args:
            username: The username of the user
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, org: str, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], UsersListResultMeta]`
    :   Returns a list of members for the specified organization using GraphQL
        
        Args:
            org: The organization login/username
            per_page: The number of results per page
            after: Cursor for pagination
            fields: Optional array of field names to select
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult

<a id="ViewerQuery"></a>

`ViewerQuery(connector: GithubConnector)`
:   Query class for Viewer entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ViewerSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ViewerSearchData]`
    :   Search viewer records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ViewerSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ViewerSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, fields: list[str] | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Gets information about the currently authenticated user.
        This is useful when you don't know the username but need to access
        the current user's profile, permissions, or associated resources.
        
        
                Args:
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

<a id="ViewerRepositoriesQuery"></a>

`ViewerRepositoriesQuery(connector: GithubConnector)`
:   Query class for ViewerRepositories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ViewerRepositoriesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ViewerRepositoriesSearchData]`
    :   Search viewer_repositories records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ViewerRepositoriesSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ViewerRepositoriesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, per_page: int | None = None, after: str | None = None, fields: list[str] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ViewerRepositoriesListResultMeta]`
    :   Returns a list of repositories owned by the authenticated user.
        Unlike Repositories_List which requires a username, this endpoint
        automatically lists repositories for the current authenticated user.
        
        
                Args:
                    per_page: The number of results per page
                    after: Cursor for pagination (from previous response's endCursor)
                    fields: Optional array of field names to select
                    **kwargs: Additional parameters
        
                Returns:
                    ViewerRepositoriesListResult