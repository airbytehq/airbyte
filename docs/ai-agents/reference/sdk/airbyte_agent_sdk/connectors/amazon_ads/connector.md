---
id: airbyte_agent_sdk-connectors-amazon_ads-connector
title: airbyte_agent_sdk.connectors.amazon_ads.connector
---

Module airbyte_agent_sdk.connectors.amazon_ads.connector
========================================================
Amazon-Ads connector.

Classes
-------

<a id="AmazonAdsConnector"></a>

`AmazonAdsConnector(auth_config: AmazonAdsAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, region: str | None = None)`
:   Type-safe Amazon-Ads API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
            Initialize a new amazon-ads connector instance.
    
            Supports both local and hosted execution modes:
            - Local mode: Provide connector-specific auth config (e.g., AmazonAdsAuthConfig)
            - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
            Args:
                auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
                on_token_refresh: Optional callback for OAuth2 token refresh persistence.
                    Called with new_tokens dict when tokens are refreshed. Can be sync or async.
                    Example: lambda tokens: save_to_database(tokens)            region: The Amazon Ads API endpoint URL based on region:
    - NA (North America): https://advertising-api.amazon.com
    - EU (Europe): https://advertising-api-eu.amazon.com
    - FE (Far East): https://advertising-api-fe.amazon.com
    
            Examples:
                # Local mode (direct API calls)
                connector = AmazonAdsConnector(auth_config=AmazonAdsAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
                # Hosted mode with explicit connector_id (no lookup needed)
                connector = AmazonAdsConnector(
                    auth_config=AirbyteAuthConfig(
                        airbyte_client_id="client_abc123",
                        airbyte_client_secret="secret_xyz789",
                        connector_id="existing-source-uuid"
                    )
                )
    
                # Hosted mode with lookup by workspace_name
                connector = AmazonAdsConnector(
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
            connector = AmazonAdsConnector(...)
        
            @AmazonAdsConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @AmazonAdsConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @AmazonAdsConnector.agent_tool()
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
        
        connector = AmazonAdsConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @AmazonAdsConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @AmazonAdsConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @AmazonAdsConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AmazonAdsCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="PortfoliosQuery"></a>

`PortfoliosQuery(connector: AmazonAdsConnector)`
:   Query class for Portfolios entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, portfolio_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.Portfolio`
    :   Retrieves a single portfolio by its ID using the v2 API.
        
        
        Args:
            portfolio_id: The unique identifier of the portfolio
            **kwargs: Additional parameters
        
        Returns:
            Portfolio

    `list(self, include_extended_data_fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], PortfoliosListResultMeta]`
    :   Returns a list of portfolios for the specified profile. Portfolios are used to
        group campaigns together for organizational and budget management purposes.
        
        
                Args:
                    include_extended_data_fields: Whether to include extended data fields in the response
                    **kwargs: Additional parameters
        
                Returns:
                    PortfoliosListResult

<a id="ProfilesQuery"></a>

`ProfilesQuery(connector: AmazonAdsConnector)`
:   Query class for Profiles entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProfilesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AirbyteSearchResult[ProfilesSearchData]`
    :   Search profiles records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProfilesSearchFilter):
        - account_info: 
        - country_code: 
        - currency_code: 
        - daily_budget: 
        - profile_id: 
        - timezone: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProfilesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, profile_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.Profile`
    :   Retrieves a single advertising profile by its ID. The profile contains
        information about the advertiser's account in a specific marketplace.
        
        
                Args:
                    profile_id: The unique identifier of the profile
                    **kwargs: Additional parameters
        
                Returns:
                    Profile

    `list(self, profile_type_filter: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResult[list[Profile]]`
    :   Returns a list of advertising profiles associated with the authenticated user.
        Profiles represent an advertiser's account in a specific marketplace. Advertisers
        may have a single profile if they advertise in only one marketplace, or a separate
        profile for each marketplace if they advertise regionally or globally.
        
        
                Args:
                    profile_type_filter: Filter profiles by type. Comma-separated list of profile types.
        Valid values: seller, vendor, agency
        
                    **kwargs: Additional parameters
        
                Returns:
                    ProfilesListResult

<a id="SponsoredBrandsAdGroupsQuery"></a>

`SponsoredBrandsAdGroupsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredBrandsAdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredBrandsAdGroupsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsAdGroupsListResultMeta]`
    :   Returns a list of sponsored brands ad groups for the specified profile.
        Ad groups organize ads and targeting within a Sponsored Brands campaign.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredBrandsAdGroupsListResult

<a id="SponsoredBrandsCampaignsQuery"></a>

`SponsoredBrandsCampaignsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredBrandsCampaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredBrandsCampaignsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredBrandsCampaignsListResultMeta]`
    :   Returns a list of sponsored brands campaigns for the specified profile.
        Sponsored Brands campaigns help drive discovery and sales with creative ad experiences.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredBrandsCampaignsListResult

<a id="SponsoredProductAdGroupsQuery"></a>

`SponsoredProductAdGroupsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductAdGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductAdGroupsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductAdGroupsListResultMeta]`
    :   Returns a list of sponsored product ad groups for the specified profile.
        Ad groups are used to organize ads and targeting within a campaign.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductAdGroupsListResult

<a id="SponsoredProductCampaignsQuery"></a>

`SponsoredProductCampaignsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductCampaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, campaign_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.SponsoredProductCampaign`
    :   Retrieves a single sponsored product campaign by its ID using the v2 API.
        
        
        Args:
            campaign_id: The unique identifier of the campaign
            **kwargs: Additional parameters
        
        Returns:
            SponsoredProductCampaign

    `list(self, state_filter: SponsoredProductCampaignsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductCampaignsListResultMeta]`
    :   Returns a list of sponsored product campaigns for the specified profile.
        Sponsored Products campaigns promote individual product listings on Amazon.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductCampaignsListResult

<a id="SponsoredProductKeywordsQuery"></a>

`SponsoredProductKeywordsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductKeywords entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductKeywordsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductKeywordsListResultMeta]`
    :   Returns a list of sponsored product keywords for the specified profile.
        Keywords are used in manual targeting campaigns to match shopper search queries.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductKeywordsListResult

<a id="SponsoredProductNegativeKeywordsQuery"></a>

`SponsoredProductNegativeKeywordsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductNegativeKeywords entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductNegativeKeywordsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeKeywordsListResultMeta]`
    :   Returns a list of sponsored product negative keywords for the specified profile.
        Negative keywords prevent ads from showing for specific search terms.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductNegativeKeywordsListResult

<a id="SponsoredProductNegativeTargetsQuery"></a>

`SponsoredProductNegativeTargetsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductNegativeTargets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductNegativeTargetsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductNegativeTargetsListResultMeta]`
    :   Returns a list of sponsored product negative targeting clauses for the specified profile.
        Negative targeting clauses exclude specific products or categories from targeting.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductNegativeTargetsListResult

<a id="SponsoredProductProductAdsQuery"></a>

`SponsoredProductProductAdsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductProductAds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductProductAdsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductProductAdsListResultMeta]`
    :   Returns a list of sponsored product ads for the specified profile.
        Product ads associate an advertised product with an ad group.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductProductAdsListResult

<a id="SponsoredProductTargetsQuery"></a>

`SponsoredProductTargetsQuery(connector: AmazonAdsConnector)`
:   Query class for SponsoredProductTargets entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, state_filter: SponsoredProductTargetsListParamsStatefilter | None = None, max_results: int | None = None, next_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amazon_ads.models.AmazonAdsExecuteResultWithMeta[dict[str, Any], SponsoredProductTargetsListResultMeta]`
    :   Returns a list of sponsored product targeting clauses for the specified profile.
        Targeting clauses define product or category targeting for ad groups.
        
        
                Args:
                    state_filter: Parameter stateFilter
                    max_results: Maximum number of results to return
                    next_token: Token for pagination
                    **kwargs: Additional parameters
        
                Returns:
                    SponsoredProductTargetsListResult