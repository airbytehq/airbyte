---
id: airbyte_agent_sdk-index
title: airbyte_agent_sdk.index
---

Module airbyte_agent_sdk
========================
# Airbyte Agent SDK

A type-safe Python SDK for executing Airbyte connectors from an application
or agent. Point it at an Airbyte Cloud workspace and it exposes every
connected source (Stripe, Zendesk, HubSpot, …) as a typed Python object or
a generic hosted executor — no REST boilerplate, no OAuth plumbing.

## Setup

Supply your Airbyte Cloud credentials in one of three ways:

1. **Env vars** (recommended for apps): set `AIRBYTE_CLIENT_ID` and
   `AIRBYTE_CLIENT_SECRET`. Every entry point below picks them up
   automatically when their `client_id`/`client_secret` kwargs are
   omitted.
2. **Explicit kwargs**: pass `client_id=` and `client_secret=` directly
   to [`connect()`](#connect), [`Workspace`](#Workspace),
   [`ask()`](#ask), or [`ask_sync()`](#ask_sync).
3. **Programmatic**: call [`configure()`](#configure) once at startup to
   set process-wide defaults (useful in notebooks).

## Quickstart

```python
import asyncio
from airbyte_agent_sdk import connect

async def main():
    stripe = connect(
        "stripe",
        client_id="your_client_id",
        client_secret="your_client_secret",
        connector_id="src_123",
    )
    result = await stripe.execute("customers", "list", params={"limit": 10})
    for row in result.data:
        print(row)

asyncio.run(main())
```

Use [`ask_sync`](#ask_sync) and direct [`connect()`](#connect) for scripts
and notebooks; use [`ask`](#ask) and [`Workspace`](#Workspace) for async
applications.

## Entry points

- [`connect`](#connect) — one-call factory that returns a typed connector
  or a [`HostedExecutor`](#HostedExecutor).
- [`list_connectors`](#list_connectors) — enumerate connectors bundled
  with this SDK.
- [`ask`](#ask) / [`ask_sync`](#ask_sync) — natural-language query across
  an entire workspace.

## Workspace operations

- [`Workspace`](#Workspace) — async context manager for workspace-level
  operations (list/create/delete connectors, workflows, and automations).
- [`HostedExecutor`](#HostedExecutor) — fallback executor returned by
  [`connect()`](#connect) when no typed connector package exists.

## Results & info

- [`AskResult`](#AskResult), [`ConnectorInfo`](#ConnectorInfo),
  [`WorkflowInfo`](#WorkflowInfo), [`AutomationInfo`](#AutomationInfo),
  [`ExecutionConfig`](#ExecutionConfig),
  [`ExecutionResult`](#ExecutionResult),
  [`AirbyteAuthConfig`](#AirbyteAuthConfig).

## Errors

[`AirbyteError`](#AirbyteError) is the **root of the SDK-defined exception
hierarchy**, covering [`HTTPClientError`](#HTTPClientError) (and its
subclasses [`HTTPStatusError`](#HTTPStatusError),
[`AuthenticationError`](#AuthenticationError),
[`RateLimitError`](#RateLimitError), [`NetworkError`](#NetworkError),
[`TimeoutError`](#TimeoutError)) plus [`ExecutorError`](#ExecutorError)
and its subclasses. It does **not** catch:

- `httpx.HTTPStatusError` / `httpx.RequestError` — the hosted path
  propagates these unwrapped from `HostedExecutor.execute()`.
- `RuntimeError` — generated typed connectors raise this when an
  underlying `ExecutionResult.success` is `False`.
- `ValueError` — argument-validation failures at the entry points.

Catch both SDK-defined and hosted-path errors in one `except`:

```python
import httpx
from airbyte_agent_sdk import AirbyteError, connect

stripe = connect("stripe", connector_id="src_123")
try:
    result = await stripe.execute("customers", "list")
except (AirbyteError, httpx.HTTPError) as err:
    # AirbyteError covers SDK-owned paths; httpx.HTTPError covers the
    # hosted path which propagates httpx errors unwrapped.
    print(f"Execution failed: {err!r}")
```

## Advanced

Advanced users who need to inspect a connector's `ConnectorModel` or
traverse tool-call records should import from the submodules directly:
`airbyte_agent_sdk.types` for auth/spec types and
`airbyte_agent_sdk.executor.models` for nested result dataclasses. See
[`docs/CONTRIBUTING.md`](https://github.com/airbytehq/airbyte-embedded/blob/main/connector-sdk/docs/CONTRIBUTING.md)
for the public-API contract.

Anything not listed in `__all__` is internal and may change between
releases without notice.

Sub-modules
-----------
* airbyte_agent_sdk.auth_strategies
* airbyte_agent_sdk.config
* airbyte_agent_sdk.connectors
* airbyte_agent_sdk.constants
* airbyte_agent_sdk.executor
* airbyte_agent_sdk.http_client
* airbyte_agent_sdk.types
* airbyte_agent_sdk.utils
* airbyte_agent_sdk.workspace

Functions
---------

<a id="ask"></a>

`ask(prompt: str, *, client_id: str | None = None, client_secret: str | None = None, workspace_name: str | None = None, organization_id: str | None = None) ‑> airbyte_agent_sdk.executor.models.AskResult`
:   Ask a natural-language question across all connectors in a workspace.
    
    Simplest entry point — no [`Workspace`](#Workspace) or
    [`connect()`](#connect) needed. Credentials are read from
    `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` if not supplied.
    
    Example:
        ```python
        import os
        import asyncio
        from airbyte_agent_sdk import ask
    
        os.environ["AIRBYTE_CLIENT_ID"] = "your_client_id"
        os.environ["AIRBYTE_CLIENT_SECRET"] = "your_client_secret"
    
        async def main():
            result = await ask("list my 5 most recent Stripe customers")
            print(result.outcome, result.answer)
            for call in result.results:
                print(call.entity, call.action, call.status)
    
        asyncio.run(main())
        ```
    
    Args:
        prompt: Natural-language question to dispatch across the workspace.
        client_id: Airbyte OAuth client ID (falls back to `AIRBYTE_CLIENT_ID`).
        client_secret: Airbyte OAuth client secret (falls back to
            `AIRBYTE_CLIENT_SECRET`).
        workspace_name: Workspace to query. Defaults to `"default"`.
        organization_id: Optional organization ID for multi-org routing.
    
    Returns:
        An [`AskResult`](#AskResult) with `outcome`, optional `answer`, and a
        `results` list of per-tool-call records. Check `outcome == "success"`
        before trusting `answer`.
    
    Raises:
        ValueError: If no credentials are supplied and no env vars are set.
        httpx.HTTPStatusError: If the backend returns a 4xx/5xx response.
    
    See also:
        [`ask_sync`](#ask_sync) — blocking wrapper for scripts and notebooks.

<a id="ask_sync"></a>

`ask_sync(prompt: str, *, client_id: str | None = None, client_secret: str | None = None, workspace_name: str | None = None, organization_id: str | None = None) ‑> airbyte_agent_sdk.executor.models.AskResult`
:   Blocking variant of [`ask`](#ask). Works in scripts and notebooks.
    
    In a plain script (no running event loop) this uses `asyncio.run()`.
    Inside a Jupyter notebook or other environment that already has a running
    loop, it dispatches the coroutine to a background thread so it does not
    block the existing loop.
    
    Example:
        ```python
        from airbyte_agent_sdk import ask_sync
    
        result = ask_sync(
            "list my 5 most recent Stripe customers",
            client_id="your_client_id",
            client_secret="your_client_secret",
        )
        print(result.outcome, result.answer)
        ```
    
    Args:
        prompt: Natural-language question to dispatch across the workspace.
        client_id: Airbyte OAuth client ID (falls back to `AIRBYTE_CLIENT_ID`).
        client_secret: Airbyte OAuth client secret (falls back to
            `AIRBYTE_CLIENT_SECRET`).
        workspace_name: Workspace to query. Defaults to `"default"`.
        organization_id: Optional organization ID for multi-org routing.
    
    Returns:
        An [`AskResult`](#AskResult) — same shape as [`ask`](#ask).
    
    Raises:
        ValueError: If no credentials are supplied and no env vars are set.
        httpx.HTTPStatusError: If the backend returns a 4xx/5xx response.
    
    See also:
        [`ask`](#ask) — the async version for use in async applications.

<a id="configure"></a>

`configure(*, client_id: str, client_secret: str, organization_id: str | None = None, workspace_name: str = 'default') ‑> None`
:   Set global SDK credentials. These are used as defaults by connect(), Workspace, and ask().
    
    Calling configure() again overwrites the previous configuration.
    Explicit kwargs passed to connect()/Workspace()/ask() always take priority.

<a id="connect"></a>

`connect(connector_name: str, *, client_id: str | None = None, client_secret: str | None = None, workspace_name: str | None = None, connector_id: str | None = None, organization_id: str | None = None, auth_config: AirbyteAuthConfig | None = None) ‑> StripeConnector | HostedExecutor`
:   Create a typed connector or `HostedExecutor` for a connector by name.
    
    When a generated typed connector package exists (e.g. `StripeConnector`),
    returns the typed connector with full IDE autocompletion and type safety.
    Otherwise, falls back to a generic [`HostedExecutor`](#HostedExecutor).
    
    Example:
        ```python
        import asyncio
        from airbyte_agent_sdk import connect
    
        async def main():
            stripe = connect(
                "stripe",
                client_id="your_client_id",
                client_secret="your_client_secret",
                connector_id="src_123",
            )
            result = await stripe.execute("customers", "list", params={"limit": 10})
            print(result.data)
    
        asyncio.run(main())
        ```
    
    The returned object's `execute()` is `async` — always `await` it from inside a
    coroutine (see `asyncio.run(main())` above).
    
    Args:
        connector_name: Connector slug, e.g. `"stripe"` or `"zendesk-support"`.
        client_id: Airbyte OAuth client ID (falls back to `AIRBYTE_CLIENT_ID`).
        client_secret: Airbyte OAuth client secret (falls back to `AIRBYTE_CLIENT_SECRET`).
        workspace_name: Workspace name for connector lookup. Defaults to `"default"`.
        connector_id: Direct connector/source ID — skips lookup.
        organization_id: Airbyte organization ID for multi-org routing.
        auth_config: [`AirbyteAuthConfig`](#AirbyteAuthConfig) with hosted credentials.
    
    Returns:
        A typed connector (e.g. `StripeConnector`) if a generated package exists,
        or a [`HostedExecutor`](#HostedExecutor) for connectors with only a YAML spec.
    
    Raises:
        ValueError: If `connector_name` is not in the bundled registry, or if no
            Airbyte Cloud credentials are provided (neither arguments, env vars,
            nor `auth_config`).
    
    Note:
        The returned object's `execute()` method may raise exceptions from three
        disjoint families depending on the execution path:
    
        1. [`AirbyteError`](#AirbyteError) (root of `HTTPClientError` and
           `ExecutorError` families) — raised by SDK-owned paths such as the
           local executor, HTTP client, and auth strategies.
        2. `httpx.HTTPStatusError` / `httpx.RequestError` — propagated **unwrapped**
           from `HostedExecutor.execute()`; not covered by `AirbyteError`.
        3. `RuntimeError` — raised by generated typed connectors when the
           underlying `ExecutionResult.success` is `False`; not covered by
           `AirbyteError`.
    
        See the module-level `## Errors` section for a compound `try`/`except`
        pattern that catches both SDK-defined and hosted-path errors.

<a id="list_connectors"></a>

`list_connectors() ‑> list[str]`
:   Return a sorted list of all available connector names.

<a id="save_download"></a>

`save_download(download_iterator: AsyncIterator[bytes], path: str | Path, *, overwrite: bool = False) ‑> pathlib._local.Path`
:   Save a download iterator to a file.
    
    Args:
        download_iterator: AsyncIterator[bytes] from a download operation
        path: File path where content should be saved
        overwrite: Whether to overwrite existing file (default: False)
    
    Returns:
        Absolute Path to the saved file
    
    Raises:
        FileExistsError: If file exists and overwrite=False
        OSError: If file cannot be written
    
    Example:
        >>> from airbyte_agent_sdk.utils import save_download
        >>>
        >>> # Download and save a file
        >>> result = await connector.download_article_attachment(id="123")
        >>> file_path = await save_download(result, "./downloads/attachment.pdf")
        >>> print(f"Downloaded to \{file_path\}")
        Downloaded to /absolute/path/to/downloads/attachment.pdf
        >>>
        >>> # Overwrite existing file
        >>> file_path = await save_download(result, "./downloads/attachment.pdf", overwrite=True)

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

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

<a id="AirbyteError"></a>

`AirbyteError(*args, **kwargs)`
:   Root of the SDK exception hierarchy.
    
    Covers SDK-owned I/O error families:
    
    * ``HTTPClientError`` and subclasses (``HTTPStatusError``,
      ``AuthenticationError``, ``RateLimitError``, ``NetworkError``,
      ``TimeoutError``) raised by ``http_client.py``,
      ``http/adapters/httpx_adapter.py``, ``http/response.py``,
      ``auth_strategies.py``, and ``executor/local_executor.py``.
    * ``ExecutorError`` and subclasses (``EntityNotFoundError``,
      ``ActionNotSupportedError``, ``MissingParameterError``,
      ``InvalidParameterError``) raised by the local executor.
    
    Not caught by ``AirbyteError``:
    
    * ``ValueError`` from argument validation at ``connect()``,
      ``Workspace(...)``, ``ask()``/``ask_sync()`` (via
      ``resolve_credentials()``), and ``HostedExecutor(...)``.
    * ``httpx.HTTPStatusError`` / ``httpx.RequestError`` propagated
      unwrapped from the hosted path (``HostedExecutor.execute()`` and
      ``AirbyteCloudClient``).
    * ``RuntimeError`` raised by generated typed connectors when the
      underlying ``ExecutionResult.success`` is ``False``.
    
    If you use the hosted path or a generated typed connector, catch
    ``AirbyteError`` together with ``httpx.HTTPError`` (and optionally
    ``RuntimeError``) to cover the full failure surface.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.http.exceptions.HTTPClientError

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

<a id="AuthenticationError"></a>

`AuthenticationError(message: str, status_code: int = 401, response: HTTPResponse | None = None)`
:   Raised when authentication credentials are missing or invalid (401, 403).
    
    Initialize authentication error.
    
    Args:
        message: Error message describing the authentication issue
        status_code: HTTP status code (401 or 403)
        response: Optional HTTPResponse object for accessing details

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.http.exceptions.HTTPStatusError
    * airbyte_agent_sdk.http.exceptions.HTTPClientError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

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

<a id="ConnectorValidationError"></a>

`ConnectorValidationError(message: str, status_code: int = 400, response: HTTPResponse | None = None)`
:   Raised when a connector request fails client-side or server-side validation.
    
    Used for (1) pre-flight enum/type checks inside LocalExecutor, and (2) 400/422
    responses from the connector API whose body describes how to correct the call.
    Framework adapters translate this into a retryable ModelRetry so the LLM can
    fix its arguments and try again.
    
    Initialize connector validation error.
    
    Args:
        message: Error message describing the validation issue
        status_code: HTTP status code (400 or 422 for server-side; 400 default
            for client-side pre-flight checks)
        response: Optional HTTPResponse object for accessing details

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.http.exceptions.HTTPStatusError
    * airbyte_agent_sdk.http.exceptions.HTTPClientError
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

<a id="HTTPClientError"></a>

`HTTPClientError(*args, **kwargs)`
:   Base exception for HTTP client errors.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte_agent_sdk.http.exceptions.HTTPStatusError
    * airbyte_agent_sdk.http.exceptions.NetworkError
    * airbyte_agent_sdk.http.exceptions.TimeoutError

<a id="HTTPStatusError"></a>

`HTTPStatusError(status_code: int, message: str, response: HTTPResponse | None = None)`
:   Raised when an HTTP response has a 4xx or 5xx status code.
    
    This is the base exception for status code errors and is raised by
    HTTPResponse.raise_for_status().
    
    Initialize HTTP status error.
    
    Args:
        status_code: The HTTP status code (e.g., 404, 500)
        message: Error message describing the issue
        response: Optional HTTPResponse object for accessing details

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.http.exceptions.HTTPClientError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte_agent_sdk.http.exceptions.AuthenticationError
    * airbyte_agent_sdk.http.exceptions.ConnectorValidationError
    * airbyte_agent_sdk.http.exceptions.RateLimitError

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

<a id="MissingParameterError"></a>

`MissingParameterError(*args, **kwargs)`
:   Raised when a required parameter is missing.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.executor.models.ExecutorError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="NetworkError"></a>

`NetworkError(message: str, original_error: Exception | None = None)`
:   Raised when network connection fails.
    
    This includes connection errors, DNS resolution failures, and other
    network-level issues.
    
    Initialize network error.
    
    Args:
        message: Error message describing the network issue
        original_error: Optional original exception from the HTTP client

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.http.exceptions.HTTPClientError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="RateLimitError"></a>

`RateLimitError(message: str, retry_after: int | None = None, response: HTTPResponse | None = None)`
:   Raised when API rate limit is exceeded (429 response).
    
    Initialize rate limit error.
    
    Args:
        message: Error message describing the rate limit
        retry_after: Seconds to wait before retrying (from Retry-After header)
        response: Optional HTTPResponse object for accessing details

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.http.exceptions.HTTPStatusError
    * airbyte_agent_sdk.http.exceptions.HTTPClientError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

<a id="TimeoutError"></a>

`TimeoutError(message: str, timeout_type: str | None = None, original_error: Exception | None = None)`
:   Raised when a request times out.
    
    This can occur during connection establishment, reading the response,
    or writing the request.
    
    Note:
        This class intentionally shadows `builtins.TimeoutError` inside the
        `airbyte_agent_sdk.http.exceptions` namespace. If you need both, import
        the builtin under an alias (e.g. `import builtins as _b`).
    
    Initialize timeout error.
    
    Args:
        message: Error message describing the timeout
        timeout_type: Optional type of timeout (connect, read, write, pool)
        original_error: Optional original exception from the HTTP client

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.http.exceptions.HTTPClientError
    * airbyte_agent_sdk.errors.AirbyteError
    * builtins.Exception
    * builtins.BaseException

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

<a id="Workspace"></a>

`Workspace(*, client_id: str | None = None, client_secret: str | None = None, workspace_name: str | None = None, organization_id: str | None = None)`
:   Top-level entry point for Airbyte hosted-mode workspace operations.
    
    Provides workspace-level methods: `ask`, list/create/delete connectors,
    get a connector executor, and workflow/automation CRUD. Use `Workspace`
    when you want to operate against a whole workspace (many connectors,
    workflows, automations); use [`connect()`](#connect) when you already
    know which connector you want to execute.
    
    Example:
        ```python
        import asyncio
        from airbyte_agent_sdk import Workspace
    
        async def main():
            async with Workspace(
                client_id="your_client_id",
                client_secret="your_client_secret",
                workspace_name="my-workspace",
            ) as ws:
                result = await ws.ask("list my recent customers")
                connectors = await ws.list_connectors()
                print(result.outcome, len(connectors))
    
        asyncio.run(main())
        ```
    
    Args:
        client_id: Airbyte OAuth client ID (or set `AIRBYTE_CLIENT_ID`).
        client_secret: Airbyte OAuth client secret (or set
            `AIRBYTE_CLIENT_SECRET`).
        workspace_name: Workspace name for scoping operations. Defaults to
            `"default"`.
        organization_id: Optional org ID for multi-org routing.
    
    Raises:
        ValueError: If `client_id`/`client_secret` are not supplied and no
            `AIRBYTE_CLIENT_ID`/`AIRBYTE_CLIENT_SECRET` env vars are set.

    ### Methods

    `ask(self, prompt: str) ‑> airbyte_agent_sdk.executor.models.AskResult`
    :   Ask a natural-language question across all connectors.

    `close(self)`
    :   Close the cloud client.

    `create_automation(self, workflow_id: str, *, trigger_type: str = 'schedule', enabled: bool = True, cron_expression: str | None = None, timezone: str | None = None, completion_webhook_url: str | None = None) ‑> airbyte_agent_sdk.executor.models.AutomationInfo`
    :   Create an automation on a workflow.

    `create_connector(self, *, definition_id: str, credentials: dict[str, Any] | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
    :   Create a new connector, returns the connector ID.

    `create_workflow(self, name: str, *, tasks: list[dict[str, Any]] | None = None) ‑> airbyte_agent_sdk.executor.models.WorkflowInfo`
    :   Create a workflow in this workspace.

    `delete_automation(self, workflow_id: str, automation_id: str) ‑> None`
    :   Delete an automation.

    `delete_connector(self, connector_id: str) ‑> None`
    :   Delete a connector.

    `delete_workflow(self, workflow_id: str) ‑> None`
    :   Delete a workflow.

    `get_automation(self, workflow_id: str, automation_id: str) ‑> airbyte_agent_sdk.executor.models.AutomationInfo`
    :   Get a single automation.

    `get_connector(self, *, connector_id: str | None = None, name: str | None = None) ‑> airbyte_agent_sdk.executor.hosted_executor.HostedExecutor`
    :   Get a HostedExecutor for a specific connector.
        
        Provide exactly one of connector_id or name:
        - connector_id: Direct lookup, no API call needed.
        - name: Resolves connector slug (e.g. "stripe") to the single instance
          of that type in this workspace. Raises ValueError if 0 or >1 found.
        
        Creates an independent HostedExecutor with its own AirbyteCloudClient.
        The caller is responsible for closing the executor when done.
        
        Example:
            stripe = await ws.get_connector(name="stripe")
            try:
                result = await stripe.execute(...)
            finally:
                await stripe.close()

    `get_workflow(self, workflow_id: str) ‑> airbyte_agent_sdk.executor.models.WorkflowInfo`
    :   Get a single workflow by ID.

    `list_automations(self, workflow_id: str) ‑> list[airbyte_agent_sdk.executor.models.AutomationInfo]`
    :   List automations for a workflow.

    `list_connectors(self) ‑> list[airbyte_agent_sdk.executor.models.ConnectorInfo]`
    :   List connector instances in this workspace.

    `list_workflows(self) ‑> list[airbyte_agent_sdk.executor.models.WorkflowInfo]`
    :   List workflows in this workspace.

    `update_automation(self, workflow_id: str, automation_id: str, *, enabled: bool | None = None, trigger_type: str | None = None, cron_expression: str | None = None, timezone: str | None = None, completion_webhook_url: str | None = None) ‑> airbyte_agent_sdk.executor.models.AutomationInfo`
    :   Update an automation.

    `update_workflow(self, workflow_id: str, *, name: str | None = None) ‑> airbyte_agent_sdk.executor.models.WorkflowInfo`
    :   Update a workflow.