---
id: airbyte_agent_sdk-connectors-notion-index
title: airbyte_agent_sdk.connectors.notion.index
---

Module airbyte_agent_sdk.connectors.notion
==========================================
Notion connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.notion.connector
* airbyte_agent_sdk.connectors.notion.connector_model
* airbyte_agent_sdk.connectors.notion.models
* airbyte_agent_sdk.connectors.notion.types

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

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[BlocksSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[CommentsSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[DataSourcesSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.notion.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="BlocksSearchResult"></a>

`BlocksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CommentsSearchResult"></a>

`CommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DataSourcesSearchResult"></a>

`DataSourcesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PagesSearchResult"></a>

`PagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.notion.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BlocksSearchData"></a>

`BlocksSearchData(**data: Any)`
:   Search result data for blocks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates if the block is archived or not.

    `bookmark: dict[str, typing.Any] | None`
    :   Represents a bookmark within the block

    `breadcrumb: dict[str, typing.Any] | None`
    :   Represents a breadcrumb block.

    `bulleted_list_item: dict[str, typing.Any] | None`
    :   Represents an item in a bulleted list.

    `callout: dict[str, typing.Any] | None`
    :   Describes a callout message or content in the block

    `child_database: dict[str, typing.Any] | None`
    :   Represents a child database block.

    `child_page: dict[str, typing.Any] | None`
    :   Represents a child page block.

    `code: dict[str, typing.Any] | None`
    :   Contains code snippets or blocks in the block content

    `column: dict[str, typing.Any] | None`
    :   Represents a column block.

    `column_list: dict[str, typing.Any] | None`
    :   Represents a list of columns.

    `created_by: dict[str, typing.Any] | None`
    :   The user who created the block.

    `created_time: str | None`
    :   The timestamp when the block was created.

    `divider: dict[str, typing.Any] | None`
    :   Represents a divider block.

    `embed: dict[str, typing.Any] | None`
    :   Contains embedded content such as videos, tweets, etc.

    `equation: dict[str, typing.Any] | None`
    :   Represents an equation or mathematical formula in the block

    `file: dict[str, typing.Any] | None`
    :   Represents a file block.

    `has_children: bool | None`
    :   Indicates if the block has children or not.

    `heading_1: dict[str, typing.Any] | None`
    :   Represents a level 1 heading.

    `heading_2: dict[str, typing.Any] | None`
    :   Represents a level 2 heading.

    `heading_3: dict[str, typing.Any] | None`
    :   Represents a level 3 heading.

    `id: str | None`
    :   The unique identifier of the block.

    `image: dict[str, typing.Any] | None`
    :   Represents an image block.

    `last_edited_by: dict[str, typing.Any] | None`
    :   The user who last edited the block.

    `last_edited_time: str | None`
    :   The timestamp when the block was last edited.

    `link_preview: dict[str, typing.Any] | None`
    :   Displays a preview of an external link within the block

    `link_to_page: dict[str, typing.Any] | None`
    :   Provides a link to another page within the block

    `model_config`
    :   The type of the None singleton.

    `numbered_list_item: dict[str, typing.Any] | None`
    :   Represents an item in a numbered list.

    `object_: dict[str, typing.Any] | None`
    :   Represents an object block.

    `paragraph: dict[str, typing.Any] | None`
    :   Represents a paragraph block.

    `parent: dict[str, typing.Any] | None`
    :   The parent block of the current block.

    `pdf: dict[str, typing.Any] | None`
    :   Represents a PDF document block.

    `quote: dict[str, typing.Any] | None`
    :   Represents a quote block.

    `synced_block: dict[str, typing.Any] | None`
    :   Represents a block synced from another source

    `table: dict[str, typing.Any] | None`
    :   Represents a table within the block

    `table_of_contents: dict[str, typing.Any] | None`
    :   Contains information regarding the table of contents

    `table_row: dict[str, typing.Any] | None`
    :   Represents a row in a table within the block

    `template: dict[str, typing.Any] | None`
    :   Specifies a template used within the block

    `to_do: dict[str, typing.Any] | None`
    :   Represents a to-do list or task content

    `toggle: dict[str, typing.Any] | None`
    :   Represents a toggle block.

    `type_: dict[str, typing.Any] | None`
    :   The type of the block.

    `unsupported: dict[str, typing.Any] | None`
    :   Represents an unsupported block.

    `video: dict[str, typing.Any] | None`
    :   Represents a video block.

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

    `created_by: dict[str, typing.Any] | None`
    :   User who created the comment.

    `created_time: str | None`
    :   Date and time when the comment was created.

    `discussion_id: str | None`
    :   Discussion thread ID.

    `id: str | None`
    :   Unique identifier for the comment.

    `last_edited_time: str | None`
    :   Date and time when the comment was last edited.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   Always comment.

    `parent: dict[str, typing.Any] | None`
    :   Parent of the comment.

    `rich_text: list[typing.Any] | None`
    :   Content of the comment as rich text.

<a id="DataSourcesSearchData"></a>

`DataSourcesSearchData(**data: Any)`
:   Search result data for data_sources entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates if the data source is archived or not.

    `cover: dict[str, typing.Any] | None`
    :   URL or reference to the cover image of the data source.

    `created_by: dict[str, typing.Any] | None`
    :   The user who created the data source.

    `created_time: str | None`
    :   The timestamp when the data source was created.

    `database_parent: dict[str, typing.Any] | None`
    :   The grandparent of the data source (parent of the database).

    `description: list[typing.Any] | None`
    :   Description text associated with the data source.

    `icon: dict[str, typing.Any] | None`
    :   URL or reference to the icon of the data source.

    `id: str | None`
    :   Unique identifier of the data source.

    `is_inline: bool | None`
    :   Indicates if the data source is displayed inline.

    `last_edited_by: dict[str, typing.Any] | None`
    :   The user who last edited the data source.

    `last_edited_time: str | None`
    :   The timestamp when the data source was last edited.

    `model_config`
    :   The type of the None singleton.

    `object_: dict[str, typing.Any] | None`
    :   The type of object (data_source).

    `parent: dict[str, typing.Any] | None`
    :   The parent database of the data source.

    `properties: list[typing.Any] | None`
    :   Schema of properties for the data source.

    `public_url: str | None`
    :   Public URL to access the data source.

    `title: list[typing.Any] | None`
    :   Title or name of the data source.

    `url: str | None`
    :   URL or reference to access the data source.

<a id="NotionConnector"></a>

`NotionConnector(auth_config: NotionAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Notion API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new notion connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., NotionAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = NotionConnector(auth_config=NotionAuthConfig(client_id="...", client_secret="...", access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = NotionConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = NotionConnector(
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
            connector = NotionConnector(...)
        
            @NotionConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @NotionConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @NotionConnector.agent_tool()
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
        
        connector = NotionConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @NotionConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @NotionConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @NotionConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `check(self) ‑> airbyte_agent_sdk.connectors.notion.models.NotionCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            NotionCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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

<a id="NotionOAuthCredentials"></a>

`NotionOAuthCredentials(**data: Any)`
:   Notion OAuth App Credentials - Provide your own Notion OAuth app credentials to override the default Airbyte-managed ones.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   Your Notion OAuth integration's client ID

    `client_secret: str`
    :   Your Notion OAuth integration's client secret

    `model_config`
    :   The type of the None singleton.

<a id="PagesSearchData"></a>

`PagesSearchData(**data: Any)`
:   Search result data for pages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the page is archived or not.

    `cover: dict[str, typing.Any] | None`
    :   URL or reference to the page cover image.

    `created_by: dict[str, typing.Any] | None`
    :   User ID or name of the creator of the page.

    `created_time: str | None`
    :   Date and time when the page was created.

    `icon: dict[str, typing.Any] | None`
    :   URL or reference to the page icon.

    `id: str | None`
    :   Unique identifier of the page.

    `in_trash: bool | None`
    :   Indicates whether the page is in trash or not.

    `last_edited_by: dict[str, typing.Any] | None`
    :   User ID or name of the last editor of the page.

    `last_edited_time: str | None`
    :   Date and time when the page was last edited.

    `model_config`
    :   The type of the None singleton.

    `object_: dict[str, typing.Any] | None`
    :   Type or category of the page object.

    `parent: dict[str, typing.Any] | None`
    :   ID or reference to the parent page.

    `properties: list[typing.Any] | None`
    :   Custom properties associated with the page.

    `public_url: str | None`
    :   Publicly accessible URL of the page.

    `url: str | None`
    :   URL of the page within the service.

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | None`
    :   URL of the user's avatar

    `bot: dict[str, typing.Any] | None`
    :   Bot-specific data

    `id: str | None`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   User's display name

    `object_: dict[str, typing.Any] | None`
    :   Always user

    `person: dict[str, typing.Any] | None`
    :   Person-specific data

    `type_: dict[str, typing.Any] | None`
    :   Type of user (person or bot)