---
id: airbyte_agent_sdk-connectors-snowflake-connector
title: airbyte_agent_sdk.connectors.snowflake.connector
---

Module airbyte_agent_sdk.connectors.snowflake.connector
=======================================================
Snowflake connector.

Classes
-------

<a id="ColumnsQuery"></a>

`ColumnsQuery(connector: SnowflakeConnector)`
:   Query class for Columns entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, statement: str | None = None, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[ColumnsResponse, ColumnsListResultMeta]`
    :   List columns
        
        Args:
            statement: SQL statement to execute
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            ColumnsListResult

<a id="DatabasesQuery"></a>

`DatabasesQuery(connector: SnowflakeConnector)`
:   Query class for Databases entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, statement: str | None = None, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[DatabasesResponse, DatabasesListResultMeta]`
    :   List databases
        
        Args:
            statement: SQL statement to execute
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            DatabasesListResult

<a id="RecordQuery"></a>

`RecordQuery(connector: SnowflakeConnector)`
:   Query class for Record entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, statement: str, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, request_id: str | None = None, retry: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.RecordResponse`
    :   Execute a SQL INSERT statement to create one or more new rows in a Snowflake table (e.g., INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')). Intended for row insertion only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE TABLE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.
        
        Args:
            statement: SQL INSERT statement to create new records (e.g., INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'))
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            request_id: Unique request ID for this DML statement. Reuse the SAME requestId when resubmitting after a network error or timeout so Snowflake deduplicates instead of executing the statement again.
            retry: Set to true when resubmitting a previously-sent statement with the same requestId, so Snowflake treats it as a safe retry rather than a new DML.
            **kwargs: Additional parameters
        
        Returns:
            RecordResponse

    `delete(self, statement: str, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, request_id: str | None = None, retry: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.RecordResponse`
    :   Execute a SQL DELETE statement to remove rows from a Snowflake table (e.g., DELETE FROM logs WHERE id = 99). Intended for row deletion only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.
        
        Args:
            statement: SQL DELETE statement to remove records (e.g., DELETE FROM logs WHERE id = 99)
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            request_id: Unique request ID for this DML statement. Reuse the SAME requestId when resubmitting after a network error or timeout so Snowflake deduplicates instead of executing the statement again.
            retry: Set to true when resubmitting a previously-sent statement with the same requestId, so Snowflake treats it as a safe retry rather than a new DML.
            **kwargs: Additional parameters
        
        Returns:
            RecordResponse

    `get(self, statement: str, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.RecordResponse`
    :   Execute a SQL SELECT statement and return the result set. Typically used to retrieve a single row by filtering on a unique identifier (e.g., SELECT * FROM users WHERE id = 42). The result is returned as rows, the same shape as the list action; when the SELECT targets one row the result contains a single row. Intended for row retrieval only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.
        
        Args:
            statement: SQL SELECT statement to retrieve a single record (e.g., SELECT * FROM users WHERE id = 42)
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            RecordResponse

    `list(self, statement: str, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[RecordResponse, RecordListResultMeta]`
    :   Execute a SQL SELECT query that returns multiple records from a Snowflake table or view. Use this action when you need to retrieve a set of rows, optionally with filtering, sorting, or limiting (e.g., SELECT * FROM orders WHERE status = 'active' ORDER BY created_at DESC LIMIT 100). Intended for row retrieval only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, CREATE) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.
        
        Args:
            statement: SQL SELECT statement to retrieve multiple records (e.g., SELECT * FROM orders WHERE status = 'active' LIMIT 100)
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            RecordListResult

    `update(self, statement: str, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, request_id: str | None = None, retry: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.RecordResponse`
    :   Execute a SQL UPDATE statement to modify existing rows in a Snowflake table (e.g., UPDATE users SET email = 'new@example.com' WHERE id = 7). Intended for row modification only. This is not a general-purpose SQL endpoint: it does not perform DDL/DCL (DROP, TRUNCATE, GRANT, ALTER) — issue the matching CRUD action for the operation you intend. Parameterized bind variables (the SQL API bindings field / ? placeholders) are not supported in this beta; inline literal values into the statement.
        
        Args:
            statement: SQL UPDATE statement to modify existing records (e.g., UPDATE users SET email = 'new@example.com' WHERE id = 7)
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            request_id: Unique request ID for this DML statement. Reuse the SAME requestId when resubmitting after a network error or timeout so Snowflake deduplicates instead of executing the statement again.
            retry: Set to true when resubmitting a previously-sent statement with the same requestId, so Snowflake treats it as a safe retry rather than a new DML.
            **kwargs: Additional parameters
        
        Returns:
            RecordResponse

<a id="ResultPartitionsQuery"></a>

`ResultPartitionsQuery(connector: SnowflakeConnector)`
:   Query class for ResultPartitions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, statement_handle: str, partition: int, request_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.ResultPartitionResponse`
    :   Continuation helper for Snowflake list actions. Use this only after a databases, schemas, tables, views, warehouses, or columns list response includes a next_page_url or multiple partitionInfo entries. The initial list response contains partition 0; call this action with partition 1, 2, and so on to retrieve additional rows for the same SHOW statement. This is not a standalone Snowflake resource and does not execute new SQL.
        
        Args:
            statement_handle: Statement handle returned by the initial list response metadata. Reuse this value when fetching additional partitions for that same result set.
            partition: Zero-based partition number to retrieve. The initial list response contains partition 0; request partition 1 or higher for subsequent pages.
            request_id: Optional request ID from the initial list response metadata. Pass it through when available to continue the same Snowflake SQL API request.
            **kwargs: Additional parameters
        
        Returns:
            ResultPartitionResponse

<a id="SchemasQuery"></a>

`SchemasQuery(connector: SnowflakeConnector)`
:   Query class for Schemas entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, statement: str | None = None, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[SchemasResponse, SchemasListResultMeta]`
    :   List schemas
        
        Args:
            statement: SQL statement to execute
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            SchemasListResult

<a id="SnowflakeConnector"></a>

`SnowflakeConnector(auth_config: SnowflakeAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, account: str | None = None)`
:   Type-safe Snowflake API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new snowflake connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., SnowflakeAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            account: Snowflake account identifier in the format orgname-accountname (e.g., myorg-myaccount)
    Examples:
        # Local mode (direct API calls)
        connector = SnowflakeConnector(auth_config=SnowflakeAuthConfig(programmatic_access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = SnowflakeConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = SnowflakeConnector(
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
        
        connector = SnowflakeConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @SnowflakeConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @SnowflakeConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @SnowflakeConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            SnowflakeCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'delete']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="TablesQuery"></a>

`TablesQuery(connector: SnowflakeConnector)`
:   Query class for Tables entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, statement: str | None = None, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[TablesResponse, TablesListResultMeta]`
    :   List tables
        
        Args:
            statement: SQL statement to execute
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            TablesListResult

<a id="ViewsQuery"></a>

`ViewsQuery(connector: SnowflakeConnector)`
:   Query class for Views entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, statement: str | None = None, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[ViewsResponse, ViewsListResultMeta]`
    :   List views
        
        Args:
            statement: SQL statement to execute
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            ViewsListResult

<a id="WarehousesQuery"></a>

`WarehousesQuery(connector: SnowflakeConnector)`
:   Query class for Warehouses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, statement: str | None = None, database: str | None = None, schema: str | None = None, warehouse: str | None = None, role: str | None = None, timeout: int | None = None, parameters: dict[str, Any] | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.snowflake.models.SnowflakeExecuteResultWithMeta[WarehousesResponse, WarehousesListResultMeta]`
    :   List warehouses
        
        Args:
            statement: SQL statement to execute
            database: Database context for the statement
            schema: Schema context for the statement
            warehouse: Warehouse to use for execution
            role: Role to use for execution
            timeout: Timeout in seconds for the statement execution
            parameters: Session parameters for the statement execution
            **kwargs: Additional parameters
        
        Returns:
            WarehousesListResult