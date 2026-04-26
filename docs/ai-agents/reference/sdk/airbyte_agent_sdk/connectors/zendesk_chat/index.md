---
id: airbyte_agent_sdk-connectors-zendesk_chat-index
title: airbyte_agent_sdk.connectors.zendesk_chat.index
---

Module airbyte_agent_sdk.connectors.zendesk_chat
================================================
Zendesk-Chat connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.zendesk_chat.connector
* airbyte_agent_sdk.connectors.zendesk_chat.connector_model
* airbyte_agent_sdk.connectors.zendesk_chat.models
* airbyte_agent_sdk.connectors.zendesk_chat.types

Classes
-------

<a id="AgentsSearchData"></a>

`AgentsSearchData(**data: Any)`
:   Search result data for agents entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_date: str | None`
    :   When agent was created

    `departments: list[typing.Any] | None`
    :   Department IDs agent belongs to

    `display_name: str | None`
    :   Agent display name

    `email: str | None`
    :   Agent email address

    `enabled: bool | None`
    :   Whether agent is enabled

    `first_name: str | None`
    :   Agent first name

    `id: int`
    :   Unique agent identifier

    `last_name: str | None`
    :   Agent last name

    `model_config`
    :   The type of the None singleton.

    `role_id: int | None`
    :   Agent role ID

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

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[AgentsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[ChatsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[DepartmentsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[ShortcutsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult[TriggersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AgentsSearchResult"></a>

`AgentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChatsSearchResult"></a>

`ChatsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DepartmentsSearchResult"></a>

`DepartmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ShortcutsSearchResult"></a>

`ShortcutsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TriggersSearchResult"></a>

`TriggersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_chat.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ChatsSearchData"></a>

`ChatsSearchData(**data: Any)`
:   Search result data for chats entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_ids: list[typing.Any] | None`
    :   IDs of agents in chat

    `department_id: int | None`
    :   Department ID

    `department_name: str | None`
    :   Department name

    `duration: int | None`
    :   Chat duration in seconds

    `id: str`
    :   Unique chat identifier

    `missed: bool | None`
    :   Whether chat was missed

    `model_config`
    :   The type of the None singleton.

    `rating: str | None`
    :   Satisfaction rating

    `timestamp: str | None`
    :   Chat start timestamp

    `update_timestamp: str | None`
    :   Last update timestamp

<a id="DepartmentsSearchData"></a>

`DepartmentsSearchData(**data: Any)`
:   Search result data for departments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether department is enabled

    `id: int`
    :   Department ID

    `members: list[typing.Any] | None`
    :   Agent IDs in department

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Department name

<a id="ShortcutsSearchData"></a>

`ShortcutsSearchData(**data: Any)`
:   Search result data for shortcuts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int`
    :   Shortcut ID

    `message: str | None`
    :   Shortcut message content

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Shortcut name/trigger

    `tags: list[typing.Any] | None`
    :   Tags applied when shortcut is used

<a id="TriggersSearchData"></a>

`TriggersSearchData(**data: Any)`
:   Search result data for triggers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether trigger is enabled

    `id: int`
    :   Trigger ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Trigger name

<a id="ZendeskChatAuthConfig"></a>

`ZendeskChatAuthConfig(**data: Any)`
:   OAuth 2.0 Access Token - Authenticate using an OAuth 2.0 access token from Zendesk
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your Zendesk Chat OAuth 2.0 access token

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskChatConnector"></a>

`ZendeskChatConnector(auth_config: ZendeskChatAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Zendesk-Chat API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new zendesk-chat connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ZendeskChatAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Zendesk subdomain (the part before .zendesk.com in your Zendesk URL)
    Examples:
        # Local mode (direct API calls)
        connector = ZendeskChatConnector(auth_config=ZendeskChatAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ZendeskChatConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ZendeskChatConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ZendeskChatAuthConfig'", name: str | None = None, replication_config: "'ZendeskChatReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A ZendeskChatConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ZendeskChatConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskChatAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await ZendeskChatConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZendeskChatAuthConfig(access_token="..."),
                replication_config=ZendeskChatReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ZendeskChatConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ZendeskChatConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await ZendeskChatConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.zendesk_chat.models.ZendeskChatCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ZendeskChatCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['get', 'list', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="ZendeskChatReplicationConfig"></a>

`ZendeskChatReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Zendesk Chat.
    
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
    :   The date from which to start replicating data, in the format YYYY-MM-DDT00:00:00Z.