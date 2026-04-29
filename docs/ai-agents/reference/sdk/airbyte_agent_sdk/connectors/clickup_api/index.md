---
id: airbyte_agent_sdk-connectors-clickup_api-index
title: airbyte_agent_sdk.connectors.clickup_api.index
---

Module airbyte_agent_sdk.connectors.clickup_api
===============================================
Clickup-Api connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.clickup_api.connector
* airbyte_agent_sdk.connectors.clickup_api.connector_model
* airbyte_agent_sdk.connectors.clickup_api.models
* airbyte_agent_sdk.connectors.clickup_api.types

Classes
-------

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

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[CommentsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[FoldersSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[GoalsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[SpacesSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TimeTrackingSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[UserSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="CommentsSearchResult"></a>

`CommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FoldersSearchResult"></a>

`FoldersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GoalsSearchResult"></a>

`GoalsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListsSearchResult"></a>

`ListsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SpacesSearchResult"></a>

`SpacesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TasksSearchResult"></a>

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TeamsSearchResult"></a>

`TeamsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TimeTrackingSearchResult"></a>

`TimeTrackingSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UserSearchResult"></a>

`UserSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ClickupApiAuthConfig"></a>

`ClickupApiAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your ClickUp personal API token

    `model_config`
    :   The type of the None singleton.

<a id="ClickupApiConnector"></a>

`ClickupApiConnector(auth_config: ClickupApiAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Clickup-Api API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new clickup-api connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ClickupApiAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = ClickupApiConnector(auth_config=ClickupApiAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ClickupApiConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ClickupApiConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ClickupApiAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.clickup_api.connector.ClickupApiConnector`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A ClickupApiConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ClickupApiConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ClickupApiAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @ClickupApiConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ClickupApiConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ClickupApiConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.
            framework: One of ``"pydantic_ai" | "langchain" | "openai_agents" | "mcp"``.
                Defaults to None → auto-detect by attempting each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs) -> bool``
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                ``(error, args, kwargs) -> str | None``. Invoked after internal retries
                are exhausted OR were skipped via ``should_internal_retry`` returning
                False. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await ClickupApiConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ClickupApiCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'api_search', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
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

<a id="CommentsSearchData"></a>

`CommentsSearchData(**data: Any)`
:   Search result data for comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment_text: str | None`
    :   Plain-text content of the comment

    `date: str | None`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the comment

    `model_config`
    :   The type of the None singleton.

    `reply_count: float | None`
    :   Number of replies on the comment

<a id="FoldersSearchData"></a>

`FoldersSearchData(**data: Any)`
:   Search result data for folders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hidden: bool | None`
    :   Whether the folder is hidden from the sidebar

    `id: str | None`
    :   Unique identifier for the folder

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the folder

    `task_count: str | None`
    :   Number of tasks contained in the folder

<a id="GoalsSearchData"></a>

`GoalsSearchData(**data: Any)`
:   Search result data for goals entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Whether the goal has been archived

    `date_created: str | None`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: str | None`
    :   Description of the goal

    `due_date: str | None`
    :   Due date for the goal, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the goal

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the goal

    `percent_completed: float | None`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: bool | None`
    :   Whether the goal is pinned to the top of the list

    `private: bool | None`
    :   Whether the goal is private to its owners

    `team_id: str | None`
    :   Identifier of the team that owns the goal

<a id="ListsSearchData"></a>

`ListsSearchData(**data: Any)`
:   Search result data for lists entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Whether the list has been archived

    `due_date: str | None`
    :   Due date for the list, in ClickUp timestamp format

    `id: str | None`
    :   Unique identifier for the list

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the list

    `priority: str | None`
    :   Priority assigned to the list

    `start_date: str | None`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: int | None`
    :   Number of tasks contained in the list

<a id="SpacesSearchData"></a>

`SpacesSearchData(**data: Any)`
:   Search result data for spaces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the space

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the space

    `private: bool | None`
    :   Whether the space is private

<a id="TasksSearchData"></a>

`TasksSearchData(**data: Any)`
:   Search result data for tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date_closed: str | None`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: str | None`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: str | None`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: str | None`
    :   Due date for the task, in ClickUp timestamp format

    `id: str | None`
    :   Unique identifier for the task

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the task

    `parent: str | None`
    :   ID of the parent task, if this task is a subtask

    `start_date: str | None`
    :   Start date for the task, in ClickUp timestamp format

    `url: str | None`
    :   Permalink URL to view the task in ClickUp

<a id="TeamsSearchData"></a>

`TeamsSearchData(**data: Any)`
:   Search result data for teams entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the team (workspace)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the team

<a id="TimeTrackingSearchData"></a>

`TimeTrackingSearchData(**data: Any)`
:   Search result data for time_tracking entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `time: float | None`
    :   Total tracked time in milliseconds

    `user: dict[str, typing.Any] | None`
    :   User who tracked the time

<a id="UserSearchData"></a>

`UserSearchData(**data: Any)`
:   Search result data for user entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `username: str | None`
    :   Display name of the user