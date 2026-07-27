---
id: airbyte_agent_sdk-connectors-orb-connector
title: airbyte_agent_sdk.connectors.orb.connector
---

Module airbyte_agent_sdk.connectors.orb.connector
=================================================
Orb connector.

Classes
-------

<a id="CustomersQuery"></a>

`CustomersQuery(connector: OrbConnector)`
:   Query class for Customers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CustomersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[CustomersSearchData]`
    :   Search customers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomersSearchFilter):
        - id: The unique identifier of the customer
        - external_customer_id: The ID of the customer in an external system
        - name: The name of the customer
        - email: The email address of the customer
        - created_at: The date and time when the customer was created
        - payment_provider: The payment provider used by the customer
        - payment_provider_id: The ID of the customer in the payment provider's system
        - timezone: The timezone setting of the customer
        - shipping_address: The shipping address of the customer
        - billing_address: The billing address of the customer
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, customer_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Customer`
    :   Get a single customer by ID
        
        Args:
            customer_id: Customer ID
            **kwargs: Additional parameters
        
        Returns:
            Customer

    `list(self, limit: int | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Customer], CustomersListResultMeta]`
    :   Returns a paginated list of customers
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CustomersListResult

<a id="InvoicesQuery"></a>

`InvoicesQuery(connector: OrbConnector)`
:   Query class for Invoices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: InvoicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[InvoicesSearchData]`
    :   Search invoices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoicesSearchFilter):
        - id: The unique identifier of the invoice
        - created_at: The date and time when the invoice was created
        - invoice_date: The date of the invoice
        - due_date: The due date for the invoice
        - invoice_pdf: The URL to download the PDF version of the invoice
        - subtotal: The subtotal amount of the invoice
        - total: The total amount of the invoice
        - amount_due: The amount due on the invoice
        - status: The current status of the invoice
        - memo: Any additional notes or comments on the invoice
        - paid_at: The date and time when the invoice was paid
        - issued_at: The date and time when the invoice was issued
        - hosted_invoice_url: The URL to view the hosted invoice
        - line_items: The line items on the invoice
        - subscription: The subscription associated with the invoice
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvoicesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, invoice_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Invoice`
    :   Get a single invoice by ID
        
        Args:
            invoice_id: Invoice ID
            **kwargs: Additional parameters
        
        Returns:
            Invoice

    `list(self, limit: int | None = None, cursor: str | None = None, customer_id: str | None = None, external_customer_id: str | None = None, subscription_id: str | None = None, invoice_date_gt: str | None = None, invoice_date_gte: str | None = None, invoice_date_lt: str | None = None, invoice_date_lte: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]`
    :   Returns a paginated list of invoices
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            customer_id: Filter invoices by customer ID
            external_customer_id: Filter invoices by external customer ID
            subscription_id: Filter invoices by subscription ID
            invoice_date_gt: Filter invoices with invoice date greater than this value (ISO 8601 format)
            invoice_date_gte: Filter invoices with invoice date greater than or equal to this value (ISO 8601 format)
            invoice_date_lt: Filter invoices with invoice date less than this value (ISO 8601 format)
            invoice_date_lte: Filter invoices with invoice date less than or equal to this value (ISO 8601 format)
            status: Filter invoices by status
            **kwargs: Additional parameters
        
        Returns:
            InvoicesListResult

<a id="OrbConnector"></a>

`OrbConnector(auth_config: OrbAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Orb API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new orb connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., OrbAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = OrbConnector(auth_config=OrbAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = OrbConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = OrbConnector(
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
            connector = OrbConnector(...)
        
            @OrbConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @OrbConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @OrbConnector.agent_tool()
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
        
        connector = OrbConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @OrbConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @OrbConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @OrbConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.orb.models.OrbCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            OrbCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="PlansQuery"></a>

`PlansQuery(connector: OrbConnector)`
:   Query class for Plans entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: PlansSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[PlansSearchData]`
    :   Search plans records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (PlansSearchFilter):
        - id: The unique identifier of the plan
        - created_at: The date and time when the plan was created
        - name: The name of the plan
        - description: A description of the plan
        - prices: The pricing options for the plan
        - product: The product associated with the plan
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            PlansSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, plan_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Plan`
    :   Get a single plan by ID
        
        Args:
            plan_id: Plan ID
            **kwargs: Additional parameters
        
        Returns:
            Plan

    `list(self, limit: int | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Plan], PlansListResultMeta]`
    :   Returns a paginated list of plans
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            PlansListResult

<a id="SubscriptionsQuery"></a>

`SubscriptionsQuery(connector: OrbConnector)`
:   Query class for Subscriptions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SubscriptionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[SubscriptionsSearchData]`
    :   Search subscriptions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SubscriptionsSearchFilter):
        - id: The unique identifier of the subscription
        - created_at: The date and time when the subscription was created
        - start_date: The date and time when the subscription starts
        - end_date: The date and time when the subscription ends
        - status: The current status of the subscription
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SubscriptionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, subscription_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.Subscription`
    :   Get a single subscription by ID
        
        Args:
            subscription_id: Subscription ID
            **kwargs: Additional parameters
        
        Returns:
            Subscription

    `list(self, limit: int | None = None, cursor: str | None = None, customer_id: str | None = None, external_customer_id: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta]`
    :   Returns a paginated list of subscriptions
        
        Args:
            limit: Number of items to return per page
            cursor: Cursor for pagination
            customer_id: Filter subscriptions by customer ID
            external_customer_id: Filter subscriptions by external customer ID
            status: Filter subscriptions by status
            **kwargs: Additional parameters
        
        Returns:
            SubscriptionsListResult