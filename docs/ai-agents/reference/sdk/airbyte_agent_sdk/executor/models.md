---
id: airbyte_agent_sdk-executor-models
title: airbyte_agent_sdk.executor.models
---

Module airbyte_agent_sdk.executor.models
========================================
Data models and protocols for executor implementations.

Functions
---------

<a id="find_check_operation"></a>

`find_check_operation(model: Any) ‑> tuple[str, typing.Any, dict[str, typing.Any]] | None`
:   Find the best operation for a health check from a ConnectorModel.
    
    Selection logic (same as what the platform backend uses via LocalExecutor.check):
    1. Look for any operation with preferred_for_check=True
    2. Fall back to the first LIST operation with no required parameters
    
    Args:
        model: ConnectorModel with entities containing endpoints
    
    Returns:
        Tuple of (entity_name, action, params) or None if no suitable operation found.
        For list operations, params includes \{"limit": 1\} to minimize data transfer.

<a id="has_required_params"></a>

`has_required_params(endpoint: Any) ‑> bool`
:   Check if an endpoint has required parameters without defaults.
    
    An endpoint has required params if it has path params (e.g., /v1/customers/\{id\})
    or query params marked required with no default value and no `config_inject` rule
    that will auto-populate the value from connector config at runtime.

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

<a id="AskResult"></a>

`AskResult(outcome: str, outcome_reason: str | None = None, answer: str | None = None, results: list[AskToolCallResult] = <factory>, query_id: str | None = None, execution_metadata: dict[str, Any] = <factory>)`
:   Result of a workspace-level natural language query.
    
    Fields match backend StructuredQueryResponse (customer_query/schemas.py:53-59).
    Note: execution_metadata is required in backend but made optional here for
    forward-compatibility -- the SDK should not break if the backend omits it.

    ### Static methods

    `from_response(response: dict[str, Any]) ‑> airbyte_agent_sdk.executor.models.AskResult`
    :   Parse a raw structured query API response into AskResult.

    ### Instance variables

    `answer: str | None`
    :   The type of the None singleton.

    `execution_metadata: dict[str, typing.Any]`
    :   The type of the None singleton.

    `outcome: str`
    :   The type of the None singleton.

    `outcome_reason: str | None`
    :   The type of the None singleton.

    `query_id: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.executor.models.AskToolCallResult]`
    :   The type of the None singleton.

<a id="AskToolCallResult"></a>

`AskToolCallResult(source_id: str | None = None, entity: str | None = None, action: str | None = None, params: dict[str, Any] = <factory>, status: str | None = None, data: Any = None, connector_metadata: Any = None, execution_time_ms: int | None = None)`
:   A single tool call result from a structured query.
    
    Fields match backend StructuredQueryToolCallResult (customer_query/schemas.py:36-44).

    ### Instance variables

    `action: str | None`
    :   The type of the None singleton.

    `connector_metadata: Any`
    :   The type of the None singleton.

    `data: Any`
    :   The type of the None singleton.

    `entity: str | None`
    :   The type of the None singleton.

    `execution_time_ms: int | None`
    :   The type of the None singleton.

    `params: dict[str, typing.Any]`
    :   The type of the None singleton.

    `source_id: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

<a id="AutomationInfo"></a>

`AutomationInfo(id: str, workflow_id: str, workspace_id: str, enabled: bool, trigger_type: str, cron_expression: str | None = None, timezone: str = 'UTC', completion_webhook_url: str | None = None, trigger_webhook_url: str | None = None, created_at: str | None = None, updated_at: str | None = None)`
:   An automation attached to a workflow.

    ### Instance variables

    `completion_webhook_url: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `cron_expression: str | None`
    :   The type of the None singleton.

    `enabled: bool`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `timezone: str`
    :   The type of the None singleton.

    `trigger_type: str`
    :   The type of the None singleton.

    `trigger_webhook_url: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `workflow_id: str`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.

<a id="ConnectorInfo"></a>

`ConnectorInfo(id: str, name: str, connector_type: str | None = None, created_at: str | None = None, updated_at: str | None = None)`
:   A connector instance in a workspace.

    ### Instance variables

    `connector_type: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

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

<a id="InvalidParameterError"></a>

`InvalidParameterError(*args, **kwargs)`
:   Raised when a parameter has an invalid type or value.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="MissingParameterError"></a>

`MissingParameterError(*args, **kwargs)`
:   Raised when a required parameter is missing.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="StandardExecuteResult"></a>

`StandardExecuteResult(data: dict[str, Any], metadata: dict[str, Any] | None = None)`
:   Result from standard operation handlers (GET, LIST, CREATE, UPDATE, DELETE, etc.).
    
    This is returned by _StandardOperationHandler to provide type-safe data and metadata
    returns instead of using tuples. Download operations continue to return AsyncIterator[bytes]
    directly for simplicity.
    
    Args:
        data: Response data from the operation
        metadata: Optional metadata extracted from response (e.g., pagination info)
    
    Example:
        result = StandardExecuteResult(
            data=\{"id": "1", "name": "Test"\},
            metadata=\{"pagination": \{"cursor": "next123", "totalRecords": 100\}\}
        )

    ### Instance variables

    `data: dict[str, typing.Any]`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="WorkflowInfo"></a>

`WorkflowInfo(id: str, name: str, workspace_id: str, created_at: str | None = None, updated_at: str | None = None)`
:   A workflow in a workspace.

    ### Instance variables

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.