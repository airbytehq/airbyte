---
id: airbyte_agent_sdk-executor-local_executor
title: airbyte_agent_sdk.executor.local_executor
---

Module airbyte_agent_sdk.executor.local_executor
================================================
Local executor for direct HTTP execution of connector operations.

Classes
-------

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

<a id="ParamResolutionError"></a>

`ParamResolutionError(*args, **kwargs)`
:   Raised when a path parameter cannot be resolved for entity probing.
    
    Covers structural resolution failures (unresolvable param, self-reference,
    parent with no LIST op, parent returning no records, missing parent key,
    max recursion depth). ``_probe_entity`` converts these into UNHEALTHY
    results so the backend controller classifies them as INCONCLUSIVE. SKIPPED
    is reserved exclusively for "this entity has no list/get action at all".
    
    Execution failures from probing a parent entity use ParentProbeError
    instead, so the child can inherit the parent's ``status_code`` for
    401/403 -> FAILED classification.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

<a id="ParentProbeError"></a>

`ParentProbeError(message: str, status_code: int | None = None)`
:   Raised when a parent entity's LIST probe fails during param resolution.
    
    Wraps the original exception's message with parent-entity context for
    debuggability, while preserving the parent's ``status_code`` so the child
    can be classified the same way the parent would be (401/403 -> FAILED,
    everything else -> INCONCLUSIVE at the backend controller layer).
    
    Distinct from ``ParamResolutionError`` so the ``status_code`` survives --
    both route through ``_probe_entity``'s UNHEALTHY branch, but only
    ParentProbeError carries the parent's HTTP status.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException