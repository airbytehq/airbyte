---
id: airbyte_agent_sdk-connectors-reddit_ads-connector
title: airbyte_agent_sdk.connectors.reddit_ads.connector
---

Module airbyte_agent_sdk.connectors.reddit_ads.connector
========================================================
Reddit-Ads connector.

Classes
-------

<a id="AdAccountsQuery"></a>

`AdAccountsQuery(connector: RedditAdsConnector)`
:   Query class for AdAccounts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, ad_account_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.AdAccount`
    :   Retrieve ad account by ID.
        
        Args:
            ad_account_id: The ad account ID
            **kwargs: Additional parameters
        
        Returns:
            AdAccount

    `list(self, business_id: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[AdAccount], AdAccountsListResultMeta]`
    :   Retrieve the ad accounts in a business.
        
        Args:
            business_id: The business ID
            page_size: Number of items per page (max 1000)
            page_token: Pagination token for next page
            **kwargs: Additional parameters
        
        Returns:
            AdAccountsListResult

<a id="AdGroupsQuery"></a>

`AdGroupsQuery(connector: RedditAdsConnector)`
:   Query class for AdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, ad_group_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.AdGroup`
    :   Retrieve an ad group by ID.
        
        Args:
            ad_group_id: The ad group ID
            **kwargs: Additional parameters
        
        Returns:
            AdGroup

    `list(self, ad_account_id: str, campaign_id: str | None = None, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[AdGroup], AdGroupsListResultMeta]`
    :   Retrieve ad groups by ad account.
        
        Args:
            ad_account_id: The ad account ID
            campaign_id: Filter by campaign ID
            page_size: Number of items per page (max 1000)
            page_token: Pagination token for next page
            **kwargs: Additional parameters
        
        Returns:
            AdGroupsListResult

<a id="AdsQuery"></a>

`AdsQuery(connector: RedditAdsConnector)`
:   Query class for Ads entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AdsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[AdsSearchData]`
    :   Search ads records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AdsSearchFilter):
        - ad_account_id: The ad account this ad belongs to
        - ad_group_id: The ad group this ad belongs to
        - campaign_id: The campaign this ad belongs to
        - click_url: Click destination URL
        - configured_status: User-configured status
        - created_at: Creation timestamp
        - effective_status: Effective delivery status
        - id: Unique ad identifier
        - modified_at: Last modification timestamp
        - name: Ad name
        - post_id: Reddit post ID (t3_ prefix)
        - post_url: Reddit post URL
        - preview_url: Ad preview URL
        - rejection_reason: Reason the ad was rejected
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AdsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against ads records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, ad_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.Ad`
    :   Retrieve an ad by ID.
        
        Args:
            ad_id: The ad ID
            **kwargs: Additional parameters
        
        Returns:
            Ad

    `list(self, ad_account_id: str, campaign_id: list[str] | None = None, ad_group_id: list[str] | None = None, configured_status: list[str] | None = None, effective_status: list[str] | None = None, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[Ad], AdsListResultMeta]`
    :   Retrieve ads by ad account. Filters combine with logical AND across different query parameters.
        
        
        Args:
            ad_account_id: The ad account ID
            campaign_id: Filter by campaign IDs (comma-separated)
            ad_group_id: Filter by ad group IDs (comma-separated)
            configured_status: Filter by configured status
            effective_status: Filter by effective status
            page_size: Number of items per page (max 1000)
            page_token: Pagination token for next page
            **kwargs: Additional parameters
        
        Returns:
            AdsListResult

<a id="BusinessesQuery"></a>

`BusinessesQuery(connector: RedditAdsConnector)`
:   Query class for Businesses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[Business], BusinessesListResultMeta]`
    :   Retrieve all businesses associated with the authenticated user.
        
        Args:
            page_size: Number of items per page (max 1000)
            page_token: Pagination token for next page
            **kwargs: Additional parameters
        
        Returns:
            BusinessesListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: RedditAdsConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - ad_account_id: The ad account this campaign belongs to
        - app_id: App Store or Play Store ID
        - configured_status: User-configured status (ACTIVE, ARCHIVED, DELETED, PAUSED)
        - created_at: Creation timestamp in ISO 8601 format
        - effective_status: Effective delivery status
        - funding_instrument_id: Funding instrument ID
        - goal_type: Goal type (LIFETIME_SPEND, DAILY_SPEND)
        - goal_value: Goal value in microcurrency
        - id: Unique campaign identifier
        - is_campaign_budget_optimization: Whether campaign budget optimization is enabled
        - modified_at: Last modification timestamp
        - name: Campaign name
        - objective: Campaign objective
        - spend_cap: Spend cap in microcurrency
        
        Args:
            query: Filter and sort conditions. Supports operators such as eq, neq, gt, gte, lt, lte,
                   in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or.
                   Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `context_store_sql_query(self, sql: str, limit: int | None = None) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.AirbyteSearchResult[dict[str, Any]]`
    :   Run a SQL query against campaigns records in the Airbyte Context Store.
        
        Only available in hosted execution mode.
        
        Args:
            sql: SQL query to execute.
            limit: Maximum results to return.
        
        Returns:
            AirbyteSearchResult containing the projected rows and query metadata.
        
        Raises:
            NotImplementedError: If called in local execution mode.

    `get(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.Campaign`
    :   Retrieve a campaign by ID.
        
        Args:
            campaign_id: The campaign ID
            **kwargs: Additional parameters
        
        Returns:
            Campaign

    `list(self, ad_account_id: str, id: list[str] | None = None, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Retrieve campaigns by ad account.
        
        Args:
            ad_account_id: The ad account ID
            id: Filter by campaign IDs (comma-separated)
            page_size: Number of items per page (max 1000)
            page_token: Pagination token for next page
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="RedditAdsConnector"></a>

`RedditAdsConnector(auth_config: RedditAdsAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Reddit-Ads API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new reddit-ads connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., RedditAdsAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = RedditAdsConnector(auth_config=RedditAdsAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = RedditAdsConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = RedditAdsConnector(
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
    :   Decorator for new user-written connector tool functions.
        
        Use this when a tool needs a custom body or the framework lacks a
        native strategy. Instead of baking the full entity/action reference
        into the docstring, it instructs the agent to call this connector's
        inspect and docs tools before executing. Tool failures raise
        :class:`airbyte_agent_sdk.AirbyteToolError` by default
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
            connector = RedditAdsConnector(...)
        
            @RedditAdsConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @RedditAdsConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @RedditAdsConnector.agent_tool()
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
    :   Deprecated. Add connector-specific documentation and runtime safeguards to one tool.
        
        Kept for backwards compatibility with existing single-tool
        integrations; it is not removed and does not warn at runtime, but new
        code should use `build_connector_tools` or `agent_tool` below.
        
        For new agents, prefer `build_connector_tools`. It returns progressive
        `inspect_connector`, `read_skill_docs`, and `execute` tools so the agent
        can load only the connector guidance it needs:
        
        ```python
        from airbyte_agent_sdk import build_connector_tools
        from pydantic_ai import Agent
        
        tools = build_connector_tools(connector, framework="pydantic_ai")
        agent = Agent("openai:gpt-4o", tools=tools.as_list())
        ```
        
        When a new integration needs custom tool bodies or a framework
        without native support, use `agent_tool` instead.
        
        ### Legacy: one generated-description tool
        
        Existing integrations can keep using `tool_utils` for one broad
        `execute` tool with the connector's full generated catalog in its
        description:
        
        ```python
        from fastmcp import FastMCP
        
        connector = RedditAdsConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @RedditAdsConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @RedditAdsConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @RedditAdsConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        This decorator composes `translate_exceptions` for runtime wrapping,
        output-size checks, framework signal translation, and optional internal
        retries, then adds connector-specific docstring augmentation.
        
        Args:
            update_docstring: When True, append connector capabilities to `__doc__`.
            max_output_chars: Max serialized output size before raising. Use `None` to disable.
            framework: One of `"pydantic_ai" | "langchain" | "openai_agents" | "mcp" | "none"`.
                Defaults to `None`, which auto-detects each framework's canonical
                import in order and falls back to `"none"` with a warning when no
                supported framework is installed. Explicit always wins, and an
                explicit framework whose package is missing raises `RuntimeError`.
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

    `check(self) ‑> airbyte_agent_sdk.connectors.reddit_ads.models.RedditAdsCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            RedditAdsCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search', 'context_store_sql_query']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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