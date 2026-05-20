---
id: airbyte_agent_sdk-connectors-typeform-index
title: airbyte_agent_sdk.connectors.typeform.index
---

Module airbyte_agent_sdk.connectors.typeform
============================================
Typeform connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.typeform.connector
* airbyte_agent_sdk.connectors.typeform.connector_model
* airbyte_agent_sdk.connectors.typeform.models
* airbyte_agent_sdk.connectors.typeform.types

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

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[FormsSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ImagesSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ResponsesSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ThemesSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[WebhooksSearchData]
    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[WorkspacesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="FormsSearchResult"></a>

`FormsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ImagesSearchResult"></a>

`ImagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ResponsesSearchResult"></a>

`ResponsesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ThemesSearchResult"></a>

`ThemesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="WebhooksSearchResult"></a>

`WebhooksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="WorkspacesSearchResult"></a>

`WorkspacesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="FormsSearchData"></a>

`FormsSearchData(**data: Any)`
:   Search result data for forms entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Date and time when the form was created

    `fields: list[typing.Any] | None`
    :   List of fields within the form

    `id: str | None`
    :   Unique identifier of the form

    `last_updated_at: str | None`
    :   Date and time when the form was last updated

    `links: dict[str, typing.Any] | None`
    :   Links to related resources

    `logic: list[typing.Any] | None`
    :   Logic rules or conditions applied to the form fields

    `model_config`
    :   The type of the None singleton.

    `published_at: str | None`
    :   Date and time when the form was published

    `settings: dict[str, typing.Any] | None`
    :   Settings and configurations for the form

    `thankyou_screens: list[typing.Any] | None`
    :   Thank you screen configurations

    `theme: dict[str, typing.Any] | None`
    :   Theme settings for the form

    `title: str | None`
    :   Title of the form

    `type_: str | None`
    :   Type of the form

    `welcome_screens: list[typing.Any] | None`
    :   Welcome screen configurations

    `workspace: dict[str, typing.Any] | None`
    :   Workspace details where the form belongs

<a id="ImagesSearchData"></a>

`ImagesSearchData(**data: Any)`
:   Search result data for images entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg_color: str | None`
    :   Average color of the image

    `file_name: str | None`
    :   Name of the image file

    `has_alpha: bool | None`
    :   Whether the image has an alpha channel

    `height: int | None`
    :   Height of the image in pixels

    `id: str | None`
    :   Unique identifier of the image

    `media_type: str | None`
    :   MIME type of the image

    `model_config`
    :   The type of the None singleton.

    `src: str | None`
    :   URL to access the image

    `width: int | None`
    :   Width of the image in pixels

<a id="ResponsesSearchData"></a>

`ResponsesSearchData(**data: Any)`
:   Search result data for responses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answers: list[typing.Any] | None`
    :   Response data for each question in the form

    `calculated: dict[str, typing.Any] | None`
    :   Calculated data related to the response

    `form_id: str | None`
    :   ID of the form

    `hidden: dict[str, typing.Any] | None`
    :   Hidden fields in the response

    `landed_at: str | None`
    :   Timestamp when the respondent landed on the form

    `landing_id: str | None`
    :   ID of the landing page

    `metadata: dict[str, typing.Any] | None`
    :   Metadata related to the response

    `model_config`
    :   The type of the None singleton.

    `response_id: str | None`
    :   ID of the response

    `response_type: str | None`
    :   Type of the response

    `submitted_at: str | None`
    :   Timestamp when the response was submitted

    `token: str | None`
    :   Token associated with the response

    `variables: list[typing.Any] | None`
    :   Variables associated with the response

<a id="ThemesSearchData"></a>

`ThemesSearchData(**data: Any)`
:   Search result data for themes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `background: dict[str, typing.Any] | None`
    :   Background settings for the theme

    `colors: dict[str, typing.Any] | None`
    :   Color settings

    `created_at: str | None`
    :   Timestamp when the theme was created

    `fields: dict[str, typing.Any] | None`
    :   Field display settings

    `font: str | None`
    :   Font used in the theme

    `has_transparent_button: bool | None`
    :   Whether the theme has a transparent button

    `id: str | None`
    :   Unique identifier of the theme

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the theme

    `rounded_corners: str | None`
    :   Rounded corners setting

    `screens: dict[str, typing.Any] | None`
    :   Screen display settings

    `updated_at: str | None`
    :   Timestamp when the theme was last updated

    `visibility: str | None`
    :   Visibility setting of the theme

<a id="TypeformAuthConfig"></a>

`TypeformAuthConfig(**data: Any)`
:   Access Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Personal access token from your Typeform account settings

    `model_config`
    :   The type of the None singleton.

<a id="TypeformConnector"></a>

`TypeformConnector(auth_config: TypeformAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Typeform API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new typeform connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., TypeformAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = TypeformConnector(auth_config=TypeformAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = TypeformConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = TypeformConnector(
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
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @TypeformConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @TypeformConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @TypeformConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            TypeformCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="TypeformReplicationConfig"></a>

`TypeformReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Typeform
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDT00:00:00Z from which to start replicating response data.

<a id="WebhooksSearchData"></a>

`WebhooksSearchData(**data: Any)`
:   Search result data for webhooks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the webhook was created

    `enabled: bool | None`
    :   Whether the webhook is currently enabled

    `form_id: str | None`
    :   ID of the form associated with the webhook

    `id: str | None`
    :   Unique identifier of the webhook

    `model_config`
    :   The type of the None singleton.

    `tag: str | None`
    :   Tag to categorize or label the webhook

    `updated_at: str | None`
    :   Timestamp when the webhook was last updated

    `url: str | None`
    :   URL where webhook data is sent

    `verify_ssl: bool | None`
    :   Whether SSL verification is enforced

<a id="WorkspacesSearchData"></a>

`WorkspacesSearchData(**data: Any)`
:   Search result data for workspaces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   Account ID associated with the workspace

    `default: bool | None`
    :   Whether this is the default workspace

    `forms: dict[str, typing.Any] | None`
    :   Information about forms in the workspace

    `id: str | None`
    :   Unique identifier of the workspace

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the workspace

    `self: dict[str, typing.Any] | None`
    :   Self-referential link

    `shared: bool | None`
    :   Whether this workspace is shared