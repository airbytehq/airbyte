---
id: airbyte_agent_sdk-connectors-exa-connector
title: airbyte_agent_sdk.connectors.exa.connector
---

Module airbyte_agent_sdk.connectors.exa.connector
=================================================
Exa connector.

Classes
-------

<a id="ContentsQuery"></a>

`ContentsQuery(connector: ExaConnector)`
:   Query class for Contents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, urls: list[str], text: Any | None = None, highlights: Any | None = None, summary: ContentsListParamsSummary | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult[list[SearchResult]]`
    :   Get the full page contents, summaries, and metadata for a list of URLs.
        Returns instant results from Exa's cache, with automatic live crawling
        as fallback for uncached pages. Use this to retrieve text, highlights,
        and summaries for specific URLs.
        
        
                Args:
                    urls: Array of URLs to retrieve contents for.
                    text: Text extraction options. Pass true for defaults or an object for advanced options.
                    highlights: Highlight extraction options. Pass true for defaults or an object for advanced options.
                    summary: Summary generation options.
                    **kwargs: Additional parameters
        
                Returns:
                    ContentsListResult

<a id="ExaConnector"></a>

`ExaConnector(auth_config: ExaAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Exa API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new exa connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ExaAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = ExaConnector(auth_config=ExaAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ExaConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ExaConnector(
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
        
        connector = ExaConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @ExaConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @ExaConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @ExaConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.exa.models.ExaCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ExaCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="SearchResultsQuery"></a>

`SearchResultsQuery(connector: ExaConnector)`
:   Query class for SearchResults entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, query: str, type: str | None = None, category: str | None = None, num_results: int | None = None, include_domains: list[str] | None = None, exclude_domains: list[str] | None = None, start_published_date: str | None = None, end_published_date: str | None = None, start_crawl_date: str | None = None, end_crawl_date: str | None = None, contents: SearchResultsListParamsContents | None = None, moderation: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult[list[SearchResult]]`
    :   Perform a search with an Exa prompt-engineered query and retrieve a list
        of relevant results. Optionally request contents (text, highlights, summary)
        inline with the search results. Supports filtering by domain, date, category,
        and number of results.
        
        
                Args:
                    query: The search query string.
                    type: The type of search. auto intelligently selects the best mode, instant provides lowest latency, fast uses lower-latency models, deep-lite provides lightweight synthesis, deep performs in-depth research with synthesis, and deep-reasoning adds more reasoning for complex searches.
                    category: A data category to focus on for improved result quality.
                    num_results: Number of results to return (max 100).
                    include_domains: List of domains to include. If specified, results will only come from these domains.
                    exclude_domains: List of domains to exclude. If specified, no results will be returned from these domains.
                    start_published_date: Only return links published after this date. ISO 8601 format.
                    end_published_date: Only return links published before this date. ISO 8601 format.
                    start_crawl_date: Only return links crawled by Exa after this date. ISO 8601 format.
                    end_crawl_date: Only return links crawled by Exa before this date. ISO 8601 format.
                    contents: Options for requesting page contents inline with search results.
                    moderation: Enable content moderation to filter unsafe content.
                    **kwargs: Additional parameters
        
                Returns:
                    SearchResultsListResult

<a id="SimilarResultsQuery"></a>

`SimilarResultsQuery(connector: ExaConnector)`
:   Query class for SimilarResults entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, url: str, num_results: int | None = None, include_domains: list[str] | None = None, exclude_domains: list[str] | None = None, start_published_date: str | None = None, end_published_date: str | None = None, start_crawl_date: str | None = None, end_crawl_date: str | None = None, contents: SimilarResultsListParamsContents | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.exa.models.ExaExecuteResult[list[SearchResult]]`
    :   Find web pages similar to a given URL. Uses Exa's embeddings to find
        semantically similar content. Supports filtering by domains and dates.
        
        
                Args:
                    url: The URL to find similar pages for.
                    num_results: Number of similar results to return (max 100).
                    include_domains: List of domains to include. If specified, results will only come from these domains.
                    exclude_domains: List of domains to exclude. If specified, no results will be returned from these domains.
                    start_published_date: Only return links published after this date. ISO 8601 format.
                    end_published_date: Only return links published before this date. ISO 8601 format.
                    start_crawl_date: Only return links crawled by Exa after this date. ISO 8601 format.
                    end_crawl_date: Only return links crawled by Exa before this date. ISO 8601 format.
                    contents: Options for requesting page contents inline with similar page results.
                    **kwargs: Additional parameters
        
                Returns:
                    SimilarResultsListResult