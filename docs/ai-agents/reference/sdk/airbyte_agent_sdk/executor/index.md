---
id: airbyte_agent_sdk-executor-index
title: airbyte_agent_sdk.executor.index
---

Module airbyte_agent_sdk.executor
=================================
Executor implementations for connector operations.

Sub-modules
-----------
* airbyte_agent_sdk.executor.hosted_executor
* airbyte_agent_sdk.executor.local_executor
* airbyte_agent_sdk.executor.models

Classes
-------

<a id="ActionNotSupportedError"></a>

`ActionNotSupportedError(*args, **kwargs)`
:   Raised when an action is not supported for an entity.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="EntityNotFoundError"></a>

`EntityNotFoundError(*args, **kwargs)`
:   Raised when an entity is not found in the connector.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="ExecutionConfig"></a>

`ExecutionConfig(entity: str, action: str, *, params: dict[str, Any] | None = None)`
:   Configuration for connector execution.
    
    Used by both LocalExecutor and HostedExecutor to specify the operation to execute.
    Executor-specific configuration (like api_url for HostedExecutor) is passed to
    the executor's constructor instead of being part of the execution config.
    
    Args:
        entity: Entity name (e.g., "customers", "invoices")
        action: Operation action (e.g., "list", "get", "create")
        params: Optional parameters for the operation
            - For GET: \{"id": "cus_123"\}
            - For LIST: \{"limit": 10\}
            - For CREATE: \{"email": "...", "name": "..."\}
    
    Example:
        config = ExecutionConfig(
            entity="customers",
            action="list",
            params=\{"limit": 10\}
        )

    ### Instance variables

    `action: str`
    :   The type of the None singleton.

    `entity: str`
    :   The type of the None singleton.

    `params: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="ExecutionResult"></a>

`ExecutionResult(success: bool, data: dict[str, Any] | AsyncIterator[bytes], error: str | None = None, meta: dict[str, Any] | None = None)`
:   Result of a connector execution.
    
    This is returned by all executor implementations. It provides a consistent
    interface for handling both successful executions and execution failures.
    
    Args:
        success: True if execution completed successfully, False if it failed
        data: Response data from the execution
            - dict[str, Any] for standard operations (GET, LIST, CREATE, etc.)
            - AsyncIterator[bytes] for download operations (streaming file content)
        error: Error message if success=False, None otherwise
        meta: Optional metadata extracted from response (e.g., pagination info)
    
    Example (Success - Standard):
        result = ExecutionResult(
            success=True,
            data=[\{"id": "1"\}, \{"id": "2"\}],
            error=None,
            meta=\{"pagination": \{"cursor": "next123", "totalRecords": 100\}\}
        )
    
    Example (Success - Download):
        result = ExecutionResult(
            success=True,
            data=async_iterator_of_bytes,
            error=None
        )
    
    Example (Failure):
        result = ExecutionResult(
            success=False,
            data=\{\},
            error="Entity 'invalid' not found",
            meta=None
        )

    ### Instance variables

    `data: dict[str, typing.Any] | collections.abc.AsyncIterator[bytes]`
    :   The type of the None singleton.

    `error: str | None`
    :   The type of the None singleton.

    `meta: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `success: bool`
    :   The type of the None singleton.

<a id="ExecutorError"></a>

`ExecutorError(*args, **kwargs)`
:   Base exception for executor errors.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte_agent_sdk.executor.models.ActionNotSupportedError
    * airbyte_agent_sdk.executor.models.EntityNotFoundError
    * airbyte_agent_sdk.executor.models.InvalidParameterError
    * airbyte_agent_sdk.executor.models.MissingParameterError

<a id="ExecutorProtocol"></a>

`ExecutorProtocol(*args, **kwargs)`
:   Protocol for connector execution.
    
    This defines the interface that both LocalExecutor and HostedExecutor implement.
    Uses structural typing (Protocol) - any class with a matching execute() method
    satisfies this protocol, regardless of inheritance.
    
    The @runtime_checkable decorator allows isinstance() checks at runtime.
    
    Concrete implementations accept two call forms:
    
    1. ``execute(config)`` -- pass an :class:`ExecutionConfig` object.
    2. ``execute(entity, action, *, params=None)`` -- shorthand string form.
    
    The Protocol signature uses the first form; the overloaded shorthand is
    defined on the concrete classes via ``@overload``.
    
    Example:
        def run_connector(executor: ExecutorProtocol, config: ExecutionConfig):
            result = await executor.execute(config)
            if result.success:
                print(f"Success: \{result.data\}")
            else:
                print(f"Error: \{result.error\}")
    
        # Shorthand (on concrete implementations):
        result = await executor.execute("customers", "list", params=\{"limit": 10\})

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Returns:
            ExecutionResult with data containing:
                - status: "healthy" or "unhealthy"
                - error: Error message if unhealthy
                - checked_entity: Entity used for the check
                - checked_action: Action used for the check

    `execute(self, config: ExecutionConfig) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Execute connector with given configuration.
        
        Args:
            config: Configuration for execution (entity, action, params)
        
        Returns:
            ExecutionResult with success status, data, and optional error message
        
        Raises:
            Infrastructure exceptions (network errors, HTTP errors, auth failures)
            These are exceptional cases where the system cannot complete the request.
        
            Execution errors (entity not found, invalid operation) are returned
            in ExecutionResult.error instead of being raised.

<a id="HostedExecutor"></a>

`HostedExecutor(airbyte_client_id: str, airbyte_client_secret: str, connector_id: str | None = None, workspace_name: str | None = None, connector_definition_id: str | None = None, organization_id: str | None = None, model: Any | None = None)`
:   Executor that proxies execution through the Airbyte Cloud API.
    
    This is the "hosted mode" executor that makes HTTP calls to the cloud API
    instead of directly calling external services. The cloud API handles all
    connector logic, secrets management, and execution.
    
    The executor uses the AirbyteCloudClient to:
    1. Authenticate with the Airbyte Platform (bearer token with caching)
    2. Look up the user's connector (if connector_id not provided)
    3. Execute the connector operation via the cloud API
    
    Implements ExecutorProtocol.
    
    Example:
        # Create executor with explicit connector_id (no lookup needed)
        executor = HostedExecutor(
            airbyte_client_id="client_abc123",
            airbyte_client_secret="secret_xyz789",
            connector_id="existing-source-uuid",
        )
    
        # Or create executor with workspace_name for lookup
        executor = HostedExecutor(
            airbyte_client_id="client_abc123",
            airbyte_client_secret="secret_xyz789",
            workspace_name="user-123",
            organization_id="00000000-0000-0000-0000-000000000123",
            connector_definition_id="abc123-def456-ghi789",
        )
    
        # Execute an operation
        execution_config = ExecutionConfig(
            entity="customers",
            action="list",
            params=\{"limit": 10\}
        )
    
        result = await executor.execute(execution_config)
        if result.success:
            print(f"Data: \{result.data\}")
        else:
            print(f"Error: \{result.error\}")
    
    Initialize hosted executor.
    
    Either provide connector_id directly OR (workspace_name + connector_definition_id)
    for lookup.
    
    Args:
        airbyte_client_id: Airbyte client ID for authentication
        airbyte_client_secret: Airbyte client secret for authentication
        connector_id: Direct connector/source ID (skips lookup if provided)
        workspace_name: Workspace name for connector lookup
        connector_definition_id: Connector definition ID (for lookup)
        organization_id: Optional Airbyte organization ID for multi-org request routing
        model: Optional ConnectorModel for health check operation selection
    
    Raises:
        ValueError: If neither connector_id nor (workspace_name + connector_definition_id) provided
    
    Example:
        # With explicit connector_id (no lookup)
        executor = HostedExecutor(
            airbyte_client_id="client_abc123",
            airbyte_client_secret="secret_xyz789",
            connector_id="existing-source-uuid",
        )
    
        # With lookup by workspace_name + definition
        executor = HostedExecutor(
            airbyte_client_id="client_abc123",
            airbyte_client_secret="secret_xyz789",
            workspace_name="user-123",
            organization_id="00000000-0000-0000-0000-000000000123",
            connector_definition_id="abc123-def456-ghi789",
        )

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Perform a health check by executing a lightweight operation.
        
        Uses the shared find_check_operation() logic (same as LocalExecutor and the
        platform backend) to find a valid entity/action pair, then executes it
        through the normal hosted execute() path.
        
        Falls back to credential verification if no model is available.

    `close(self)`
    :   Close the cloud client and cleanup resources.
        
        Call this when you're done using the executor to clean up HTTP connections.
        
        Example:
            executor = HostedExecutor(...)
            try:
                result = await executor.execute(config)
            finally:
                await executor.close()

    `execute(self, config_or_entity: ExecutionConfig | str, action: str | None = None, *, params: dict[str, Any] | None = None) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Execute connector via cloud API (ExecutorProtocol implementation).
        
        Accepts either an :class:`ExecutionConfig` or positional ``(entity, action)``
        strings with an optional ``params`` keyword argument.
        
        Flow:
        1. Use provided connector_id or look up from workspace_name + definition_id
        2. Execute the connector operation via the cloud API
        3. Parse the response into ExecutionResult
        
        Args:
            config_or_entity: ExecutionConfig object *or* entity name string
            action: Action string (required when entity is a string)
            params: Optional parameters dict (only with string form)
        
        Returns:
            ExecutionResult with success/failure status
        
        Raises:
            TypeError: If action/params are passed together with an ExecutionConfig,
                or if action is omitted when using the string form
            ValueError: If no connector or multiple connectors found for user (when doing lookup)
            AuthenticationError: If API returns 401/403
            RateLimitError: If API returns 429
            ConnectorValidationError: If API returns 400/422 (retryable by LLM)
            HTTPStatusError: If API returns any other 4xx/5xx status code
            httpx.RequestError: If network request fails
        
        Example:
            config = ExecutionConfig(
                entity="customers",
                action="list",
                params=\{"limit": 10\}
            )
            result = await executor.execute(config)
        
            # Shorthand form:
            result = await executor.execute("customers", "list", params=\{"limit": 10\})

<a id="InvalidParameterError"></a>

`InvalidParameterError(*args, **kwargs)`
:   Raised when a parameter has an invalid type or value.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="LocalExecutor"></a>

`LocalExecutor(config_path: str | None = None, model: ConnectorModel | None = None, secrets: dict[str, SecretStr] | None = None, auth_config: dict[str, SecretStr] | None = None, auth_scheme: str | None = None, enable_logging: bool = False, log_file: str | None = None, execution_context: str | None = None, max_connections: int = 100, max_keepalive_connections: int = 20, max_logs: int | None = 10000, config_values: dict[str, str] | None = None, on_token_refresh: TokenRefreshCallback = None, retry_config: RetryConfig | None = None)`
:   Async executor for Entity×Action operations with direct HTTP execution.
    
    This is the "local mode" executor that makes direct HTTP calls to external APIs.
    It performs local entity/action lookups, validation, and request building.
    
    Implements ExecutorProtocol.
    
    Initialize async executor.
    
    Args:
        config_path: Path to connector.yaml.
            If neither config_path nor model is provided, an error will be raised.
        model: ConnectorModel object to execute.
        secrets: (Legacy) Auth parameters that bypass x-airbyte-auth-config mapping.
            Directly passed to auth strategies (e.g., \{"username": "...", "password": "..."\}).
            Cannot be used together with auth_config.
        auth_config: User-facing auth configuration following x-airbyte-auth-config spec.
            Will be transformed via auth_mapping to produce auth parameters.
            Cannot be used together with secrets.
        auth_scheme: (Multi-auth only) Explicit security scheme name to use.
            If None, SDK will auto-select based on provided credentials.
            Example: auth_scheme="githubOAuth"
        enable_logging: Enable request/response logging
        log_file: Path to log file (if enable_logging=True)
        execution_context: Execution context (mcp, direct, blessed, agent)
        max_connections: Maximum number of concurrent connections
        max_keepalive_connections: Maximum number of keepalive connections
        max_logs: Maximum number of logs to keep in memory before rotation.
            Set to None for unlimited (not recommended for production).
            Defaults to 10000.
        config_values: Optional dict of config values for server variable substitution
            (e.g., \{"subdomain": "acme"\} for URLs like https://\{subdomain\}.api.example.com).
        on_token_refresh: Optional callback function(new_tokens: dict) called when
            OAuth2 tokens are refreshed. Use this to persist updated tokens.
            Can be sync or async. Example: lambda tokens: save_to_db(tokens)
        retry_config: Optional retry configuration override. If provided, overrides
            the connector.yaml x-airbyte-retry-config. If None, uses connector.yaml
            config or SDK defaults.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Perform a health check by running a lightweight operation.
        
        Uses shared find_check_operation() to find the best operation, then
        executes it to verify connectivity and credentials.
        
        Returns:
            ExecutionResult with data containing status, error, and checked operation details.

    `check_entities(self, entities: list[str]) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Perform health checks for specific entities by probing their list or get operations.
        
        For each entity, looks up (entity_name, Action.LIST) in the operation index.
        If not found, falls back to (entity_name, Action.GET). Runs all probes
        concurrently and returns per-entity results.
        
        Args:
            entities: List of entity names to check.
        
        Returns:
            ExecutionResult with per-entity health check results.

    `close(self)`
    :   Close async HTTP client and logger.

    `execute(self, config_or_entity: ExecutionConfig | str, action: str | None = None, *, params: dict[str, Any] | None = None) ‑> airbyte_agent_sdk.executor.models.ExecutionResult`
    :   Execute connector operation using handler pattern.
        
        Accepts either an :class:`ExecutionConfig` or positional ``(entity, action)``
        strings with an optional ``params`` keyword argument.
        
        Args:
            config_or_entity: ExecutionConfig object *or* entity name string
            action: Action string (required when entity is a string)
            params: Optional parameters dict (only with string form)
        
        Returns:
            ExecutionResult with success/failure status and data
        
        Example:
            config = ExecutionConfig(
                entity="customers",
                action="list",
                params=\{"limit": 10\}
            )
            result = await executor.execute(config)
            if result.success:
                print(result.data)
        
            # Shorthand form:
            result = await executor.execute("customers", "list", params=\{"limit": 10\})

    `execute_batch(self, operations: list[tuple[str, str | Action, dict[str, Any] | None]]) ‑> list[dict[str, typing.Any] | collections.abc.AsyncIterator[bytes]]`
    :   Execute multiple operations concurrently (supports all action types including download).
        
        Args:
            operations: List of (entity, action, params) tuples
        
        Returns:
            List of responses in the same order as operations.
            Standard operations return dict[str, Any].
            Download operations return AsyncIterator[bytes].
        
        Raises:
            ValueError: If any entity or action not found
            HTTPClientError: If any API request fails
        
        Example:
            results = await executor.execute_batch([
                ("Customer", "list", \{"limit": 10\}),
                ("Customer", "get", \{"id": "cus_123"\}),
                ("attachments", "download", \{"id": "att_456"\}),
            ])

<a id="MissingParameterError"></a>

`MissingParameterError(*args, **kwargs)`
:   Raised when a required parameter is missing.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException