---
id: airbyte_agent_sdk-executor-hosted_executor
title: airbyte_agent_sdk.executor.hosted_executor
---

Module airbyte_agent_sdk.executor.hosted_executor
=================================================
Hosted executor for proxying operations through the cloud API.

Classes
-------

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