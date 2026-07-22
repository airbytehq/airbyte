---
id: airbyte_agent_sdk-connectors-sendgrid-connector
title: airbyte_agent_sdk.connectors.sendgrid.connector
---

Module airbyte_agent_sdk.connectors.sendgrid.connector
======================================================
Sendgrid connector.

Classes
-------

<a id="BlocksQuery"></a>

`BlocksQuery(connector: SendgridConnector)`
:   Query class for Blocks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BlocksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BlocksSearchData]`
    :   Search blocks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BlocksSearchFilter):
        - created: Unix timestamp when the block occurred
        - email: The blocked email address
        - reason: The reason for the block
        - status: The status code for the block
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BlocksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Block], BlocksListResultMeta]`
    :   Returns all blocked email records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            BlocksListResult

<a id="BouncesQuery"></a>

`BouncesQuery(connector: SendgridConnector)`
:   Query class for Bounces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: BouncesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BouncesSearchData]`
    :   Search bounces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (BouncesSearchFilter):
        - created: Unix timestamp when the bounce occurred
        - email: The email address that bounced
        - reason: The reason for the bounce
        - status: The enhanced status code for the bounce
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            BouncesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Bounce], BouncesListResultMeta]`
    :   Returns all bounced email records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            BouncesListResult

<a id="CampaignsQuery"></a>

`CampaignsQuery(connector: SendgridConnector)`
:   Query class for Campaigns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CampaignsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[CampaignsSearchData]`
    :   Search campaigns records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CampaignsSearchFilter):
        - channels: Channels for this campaign
        - created_at: When the campaign was created
        - id: Unique campaign identifier
        - is_abtest: Whether this campaign is an A/B test
        - name: Campaign name
        - status: Campaign status
        - updated_at: When the campaign was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CampaignsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]`
    :   Returns all marketing campaigns.
        
        Args:
            page_size: Maximum number of campaigns to return per page
            **kwargs: Additional parameters
        
        Returns:
            CampaignsListResult

<a id="ContactsQuery"></a>

`ContactsQuery(connector: SendgridConnector)`
:   Query class for Contacts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ContactsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ContactsSearchData]`
    :   Search contacts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ContactsSearchFilter):
        - address_line_1: Address line 1
        - address_line_2: Address line 2
        - alternate_emails: Alternate email addresses
        - city: City
        - contact_id: Unique contact identifier used by Airbyte
        - country: Country
        - created_at: When the contact was created
        - custom_fields: Custom field values
        - email: Contact email address
        - facebook: Facebook ID
        - first_name: Contact first name
        - last_name: Contact last name
        - line: LINE ID
        - list_ids: IDs of lists the contact belongs to
        - phone_number: Phone number
        - postal_code: Postal code
        - state_province_region: State, province, or region
        - unique_name: Unique name for the contact
        - updated_at: When the contact was last updated
        - whatsapp: WhatsApp number
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ContactsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.Contact`
    :   Returns the full details and all fields for the specified contact.
        
        Args:
            id: The ID of the contact
            **kwargs: Additional parameters
        
        Returns:
            Contact

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Contact], ContactsListResultMeta]`
    :   Returns a sample of contacts. Use the export endpoint for full lists.
        
        Returns:
            ContactsListResult

<a id="GlobalSuppressionsQuery"></a>

`GlobalSuppressionsQuery(connector: SendgridConnector)`
:   Query class for GlobalSuppressions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: GlobalSuppressionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[GlobalSuppressionsSearchData]`
    :   Search global_suppressions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (GlobalSuppressionsSearchFilter):
        - created: Unix timestamp when the global suppression was created
        - email: The globally suppressed email address
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            GlobalSuppressionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[GlobalSuppression], GlobalSuppressionsListResultMeta]`
    :   Returns all globally unsubscribed email addresses.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            GlobalSuppressionsListResult

<a id="InvalidEmailsQuery"></a>

`InvalidEmailsQuery(connector: SendgridConnector)`
:   Query class for InvalidEmails entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvalidEmailsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[InvalidEmailsSearchData]`
    :   Search invalid_emails records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvalidEmailsSearchFilter):
        - created: Unix timestamp when the invalid email was recorded
        - email: The invalid email address
        - reason: The reason the email is invalid
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvalidEmailsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[InvalidEmail], InvalidEmailsListResultMeta]`
    :   Returns all invalid email records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            InvalidEmailsListResult

<a id="ListsQuery"></a>

`ListsQuery(connector: SendgridConnector)`
:   Query class for Lists entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ListsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ListsSearchData]`
    :   Search lists records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ListsSearchFilter):
        - metadata: Metadata about the list resource
        - contact_count: Number of contacts in the list
        - id: Unique list identifier
        - name: Name of the list
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.List`
    :   Returns a specific marketing list by ID.
        
        Args:
            id: The ID of the list
            **kwargs: Additional parameters
        
        Returns:
            List

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[List], ListsListResultMeta]`
    :   Returns all marketing contact lists.
        
        Args:
            page_size: Maximum number of lists to return
            **kwargs: Additional parameters
        
        Returns:
            ListsListResult

<a id="SegmentsQuery"></a>

`SegmentsQuery(connector: SendgridConnector)`
:   Query class for Segments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SegmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SegmentsSearchData]`
    :   Search segments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SegmentsSearchFilter):
        - contacts_count: Number of contacts in the segment
        - created_at: When the segment was created
        - id: Unique segment identifier
        - name: Segment name
        - next_sample_update: When the next sample update will occur
        - parent_list_ids: IDs of parent lists
        - query_version: Query version used
        - sample_updated_at: When the sample was last updated
        - status: Segment status details
        - updated_at: When the segment was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SegmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, segment_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.Segment`
    :   Returns a specific segment by ID.
        
        Args:
            segment_id: The ID of the segment
            **kwargs: Additional parameters
        
        Returns:
            Segment

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult[list[Segment]]`
    :   Returns all segments (v2).
        
        Returns:
            SegmentsListResult

<a id="SendgridConnector"></a>

`SendgridConnector(auth_config: SendgridAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Sendgrid API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new sendgrid connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SendgridAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = SendgridConnector(auth_config=SendgridAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SendgridConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SendgridConnector(
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
            connector = SendgridConnector(...)
        
            @SendgridConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @SendgridConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @SendgridConnector.agent_tool()
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
        
        connector = SendgridConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @SendgridConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @SendgridConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @SendgridConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SendgridCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="SinglesendStatsQuery"></a>

`SinglesendStatsQuery(connector: SendgridConnector)`
:   Query class for SinglesendStats entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SinglesendStatsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendStatsSearchData]`
    :   Search singlesend_stats records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SinglesendStatsSearchFilter):
        - ab_phase: The A/B test phase
        - ab_variation: The A/B test variation
        - aggregation: The aggregation type
        - id: The single send ID
        - stats: Email statistics for the single send
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SinglesendStatsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SingleSendStats], SinglesendStatsListResultMeta]`
    :   Returns stats for all single sends.
        
        Args:
            page_size: Maximum number of stats to return per page
            **kwargs: Additional parameters
        
        Returns:
            SinglesendStatsListResult

<a id="SinglesendsQuery"></a>

`SinglesendsQuery(connector: SendgridConnector)`
:   Query class for Singlesends entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SinglesendsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendsSearchData]`
    :   Search singlesends records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SinglesendsSearchFilter):
        - categories: Categories associated with this single send
        - created_at: When the single send was created
        - id: Unique single send identifier
        - is_abtest: Whether this is an A/B test
        - name: Single send name
        - send_at: Scheduled send time
        - status: Current status: draft, scheduled, or triggered
        - updated_at: When the single send was last updated
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SinglesendsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SingleSend`
    :   Returns details about one single send.
        
        Args:
            id: The ID of the single send
            **kwargs: Additional parameters
        
        Returns:
            SingleSend

    `list(self, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SingleSend], SinglesendsListResultMeta]`
    :   Returns all single sends.
        
        Args:
            page_size: Maximum number of single sends to return per page
            **kwargs: Additional parameters
        
        Returns:
            SinglesendsListResult

<a id="SpamReportsQuery"></a>

`SpamReportsQuery(connector: SendgridConnector)`
:   Query class for SpamReports entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SpamReport], SpamReportsListResultMeta]`
    :   Returns all spam report records.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            SpamReportsListResult

<a id="SuppressionGroupMembersQuery"></a>

`SuppressionGroupMembersQuery(connector: SendgridConnector)`
:   Query class for SuppressionGroupMembers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SuppressionGroupMembersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupMembersSearchData]`
    :   Search suppression_group_members records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SuppressionGroupMembersSearchFilter):
        - created_at: Unix timestamp when the suppression was created
        - email: The suppressed email address
        - group_id: ID of the suppression group
        - group_name: Name of the suppression group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SuppressionGroupMembersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, limit: int | None = None, offset: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SuppressionGroupMember], SuppressionGroupMembersListResultMeta]`
    :   Returns all suppressions across all groups.
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip for pagination
            **kwargs: Additional parameters
        
        Returns:
            SuppressionGroupMembersListResult

<a id="SuppressionGroupsQuery"></a>

`SuppressionGroupsQuery(connector: SendgridConnector)`
:   Query class for SuppressionGroups entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SuppressionGroupsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupsSearchData]`
    :   Search suppression_groups records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SuppressionGroupsSearchFilter):
        - description: Description of the suppression group
        - id: Unique suppression group identifier
        - is_default: Whether this is the default suppression group
        - name: Suppression group name
        - unsubscribes: Number of unsubscribes in this group
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SuppressionGroupsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, group_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SuppressionGroup`
    :   Returns information about a single suppression group.
        
        Args:
            group_id: The ID of the suppression group
            **kwargs: Additional parameters
        
        Returns:
            SuppressionGroup

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult[list[SuppressionGroup]]`
    :   Returns all suppression (unsubscribe) groups.
        
        Returns:
            SuppressionGroupsListResult

<a id="TemplatesQuery"></a>

`TemplatesQuery(connector: SendgridConnector)`
:   Query class for Templates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TemplatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[TemplatesSearchData]`
    :   Search templates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TemplatesSearchFilter):
        - generation: Template generation (legacy or dynamic)
        - id: Unique template identifier
        - name: Template name
        - updated_at: When the template was last updated
        - versions: Template versions
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TemplatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, template_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.Template`
    :   Returns a single transactional template.
        
        Args:
            template_id: The ID of the template
            **kwargs: Additional parameters
        
        Returns:
            Template

    `list(self, generations: str | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Template], TemplatesListResultMeta]`
    :   Returns paged transactional templates (legacy and dynamic).
        
        Args:
            generations: Template generations to return
            page_size: Number of templates per page
            **kwargs: Additional parameters
        
        Returns:
            TemplatesListResult