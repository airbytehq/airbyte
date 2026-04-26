---
id: airbyte_agent_sdk-types
title: airbyte_agent_sdk.types
---

Module airbyte_agent_sdk.types
==============================
Type definitions for Airbyte SDK.

Classes
-------

<a id="Action"></a>

`Action(*args, **kwds)`
:   Supported actions for Entity operations.
    
    Standard CRUD actions:
        GET, CREATE, UPDATE, DELETE, LIST
    
    Special actions:
        API_SEARCH - Search via API endpoint
        DOWNLOAD - Download file content
        AUTHORIZE - OAuth authorization flow

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `API_SEARCH`
    :   The type of the None singleton.

    `AUTHORIZE`
    :   The type of the None singleton.

    `CREATE`
    :   The type of the None singleton.

    `DELETE`
    :   The type of the None singleton.

    `DOWNLOAD`
    :   The type of the None singleton.

    `GET`
    :   The type of the None singleton.

    `LIST`
    :   The type of the None singleton.

    `UPDATE`
    :   The type of the None singleton.

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

<a id="AuthConfig"></a>

`AuthConfig(**data: Any)`
:   Authentication configuration supporting single or multiple auth methods.
    
    Connectors can define either:
    - Single auth: One authentication method (backwards compatible)
    - Multi-auth: Multiple authentication methods (user/agent selects one)
    
    For single-auth connectors (most common):
        AuthConfig(type=OAUTH2, config=\{...\}, user_config_spec=\{...\})
    
    For multi-auth connectors:
        AuthConfig(options=[
            AuthOption(scheme_name="oauth", type=OAUTH2, ...),
            AuthOption(scheme_name="apikey", type=BEARER, ...)
        ])
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `config: dict[str, typing.Any]`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `options: list[airbyte_agent_sdk.types.AuthOption] | None`
    :   The type of the None singleton.

    `type: airbyte_agent_sdk.types.AuthType | None`
    :   The type of the None singleton.

    `user_config_spec: airbyte_agent_sdk.schema.security.AuthConfigSpec | None`
    :   The type of the None singleton.

    ### Methods

    `get_single_option(self) ‑> airbyte_agent_sdk.types.AuthOption`
    :   Get single auth option (for backwards compatibility).
        
        Converts single-auth config to AuthOption format for uniform handling.
        
        Returns:
            AuthOption containing the single auth configuration
        
        Raises:
            ValueError: If this is a multi-auth config or invalid

    `is_multi_auth(self) ‑> bool`
    :   Check if this configuration supports multiple authentication methods.
        
        Returns:
            True if multiple auth options are available, False for single-auth

<a id="AuthOption"></a>

`AuthOption(**data: Any)`
:   A single authentication option in a multi-auth connector.
    
    Represents one security scheme from OpenAPI components.securitySchemes.
    Each option defines a complete authentication method with its own type,
    configuration, and user-facing credential specification.
    
    Example:
        For a connector supporting both OAuth2 and API Key auth:
        - AuthOption(scheme_name="oauth", type=OAUTH2, ...)
        - AuthOption(scheme_name="apikey", type=BEARER, ...)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `config: dict[str, typing.Any]`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `scheme_name: str`
    :   The type of the None singleton.

    `type: airbyte_agent_sdk.types.AuthType`
    :   The type of the None singleton.

    `untested: bool`
    :   The type of the None singleton.

    `user_config_spec: airbyte_agent_sdk.schema.security.AuthConfigSpec | None`
    :   The type of the None singleton.

<a id="AuthType"></a>

`AuthType(*args, **kwds)`
:   Supported authentication types.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `API_KEY`
    :   The type of the None singleton.

    `BASIC`
    :   The type of the None singleton.

    `BEARER`
    :   The type of the None singleton.

    `HTTP`
    :   The type of the None singleton.

    `OAUTH2`
    :   The type of the None singleton.

<a id="ConnectorModel"></a>

`ConnectorModel(**data: Any)`
:   Complete connector model loaded from YAML definition.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auth: airbyte_agent_sdk.types.AuthConfig`
    :   The type of the None singleton.

    `base_url: str`
    :   The type of the None singleton.

    `entities: list[airbyte_agent_sdk.types.EntityDefinition]`
    :   The type of the None singleton.

    `example_questions: typing.Any | None`
    :   The type of the None singleton.

    `id: uuid.UUID`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `openapi_spec: typing.Any | None`
    :   The type of the None singleton.

    `response_error_check: airbyte_agent_sdk.schema.base.ResponseErrorCheck | None`
    :   The type of the None singleton.

    `retry_config: airbyte_agent_sdk.schema.extensions.RetryConfig | None`
    :   The type of the None singleton.

    `scoping: list[airbyte_agent_sdk.schema.extensions.ScopingParamConfig]`
    :   The type of the None singleton.

    `search_field_paths: dict[str, list[str]] | None`
    :   The type of the None singleton.

    `server_variable_defaults: dict[str, str]`
    :   The type of the None singleton.

    `version: str`
    :   The type of the None singleton.

<a id="ContentType"></a>

`ContentType(*args, **kwds)`
:   Supported content types for request bodies.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `FORM_DATA`
    :   The type of the None singleton.

    `FORM_URLENCODED`
    :   The type of the None singleton.

    `JSON`
    :   The type of the None singleton.

    `MULTIPART_RELATED`
    :   The type of the None singleton.

<a id="EndpointDefinition"></a>

`EndpointDefinition(**data: Any)`
:   Definition of an API endpoint.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: airbyte_agent_sdk.types.Action | None`
    :   The type of the None singleton.

    `ai_hints: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `body_fields: list[str]`
    :   The type of the None singleton.

    `content_type: airbyte_agent_sdk.types.ContentType`
    :   The type of the None singleton.

    `deep_object_params: list[str]`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `file_field: str | None`
    :   The type of the None singleton.

    `graphql_body: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `header_params: list[str]`
    :   The type of the None singleton.

    `header_params_schema: dict[str, dict[str, typing.Any]]`
    :   The type of the None singleton.

    `meta_extractor: dict[str, str] | None`
    :   The type of the None singleton.

    `method: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `no_content_response: bool`
    :   The type of the None singleton.

    `no_pagination: str | None`
    :   The type of the None singleton.

    `path: str`
    :   The type of the None singleton.

    `path_override: airbyte_agent_sdk.schema.components.PathOverrideConfig | None`
    :   The type of the None singleton.

    `path_params: list[str]`
    :   The type of the None singleton.

    `path_params_schema: dict[str, dict[str, typing.Any]]`
    :   The type of the None singleton.

    `preferred_for_check: bool`
    :   The type of the None singleton.

    `query_params: list[str]`
    :   The type of the None singleton.

    `query_params_schema: dict[str, dict[str, typing.Any]]`
    :   The type of the None singleton.

    `record_extractor: str | None`
    :   The type of the None singleton.

    `request_body_defaults: dict[str, typing.Any]`
    :   The type of the None singleton.

    `request_schema: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `response_schema: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `untested: bool`
    :   The type of the None singleton.

    `upload_file_param: str | None`
    :   The type of the None singleton.

<a id="EntityDefinition"></a>

`EntityDefinition(**data: Any)`
:   Definition of an API entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[airbyte_agent_sdk.types.Action]`
    :   The type of the None singleton.

    `ai_hints: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `endpoints: dict[airbyte_agent_sdk.types.Action, airbyte_agent_sdk.types.EndpointDefinition]`
    :   The type of the None singleton.

    `entity_schema: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `relationships: list[airbyte_agent_sdk.schema.extensions.EntityRelationshipConfig]`
    :   The type of the None singleton.

    `stream_name: str | None`
    :   The type of the None singleton.

<a id="ParameterLocation"></a>

`ParameterLocation(*args, **kwds)`
:   Location of operation parameters.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `COOKIE`
    :   The type of the None singleton.

    `HEADER`
    :   The type of the None singleton.

    `PATH`
    :   The type of the None singleton.

    `QUERY`
    :   The type of the None singleton.