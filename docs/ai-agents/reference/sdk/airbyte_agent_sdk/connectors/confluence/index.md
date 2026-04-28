---
id: airbyte_agent_sdk-connectors-confluence-index
title: airbyte_agent_sdk.connectors.confluence.index
---

Module airbyte_agent_sdk.connectors.confluence
==============================================
Confluence connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.confluence.connector
* airbyte_agent_sdk.connectors.confluence.connector_model
* airbyte_agent_sdk.connectors.confluence.models
* airbyte_agent_sdk.connectors.confluence.types

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

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[AuditSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[BlogPostsSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[SpacesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AuditSearchResult"></a>

`AuditSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BlogPostsSearchResult"></a>

`BlogPostsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GroupsSearchResult"></a>

`GroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AuditSearchData"></a>

`AuditSearchData(**data: Any)`
:   Search result data for audit entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `affected_object: dict[str, typing.Any] | None`
    :   The object that was affected by the audit event.

    `associated_objects: list[typing.Any] | None`
    :   Any associated objects related to the audit event.

    `author: dict[str, typing.Any] | None`
    :   The user who triggered the audit event.

    `category: str | None`
    :   The category under which the audit event falls.

    `changed_values: list[typing.Any] | None`
    :   Details of the values that were changed during the audit event.

    `creation_date: int | None`
    :   The date and time when the audit event was created.

    `description: str | None`
    :   A detailed description of the audit event.

    `model_config`
    :   The type of the None singleton.

    `remote_address: str | None`
    :   The IP address from which the audit event originated.

    `summary: str | None`
    :   A brief summary or title describing the audit event.

    `super_admin: bool | None`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: bool | None`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="BlogPostsSearchData"></a>

`BlogPostsSearchData(**data: Any)`
:   Search result data for blog_posts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | None`
    :   ID of the user who created the blog post

    `body: dict[str, typing.Any] | None`
    :   Blog post body content

    `created_at: str | None`
    :   Timestamp when the blog post was created

    `id: str | None`
    :   Unique blog post identifier

    `links: dict[str, typing.Any] | None`
    :   Links related to the blog post

    `model_config`
    :   The type of the None singleton.

    `space_id: str | None`
    :   ID of the space containing this blog post

    `status: str | None`
    :   Blog post status (current, draft, trashed)

    `title: str | None`
    :   Blog post title

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="ConfluenceAuthConfig"></a>

`ConfluenceAuthConfig(**data: Any)`
:   Confluence API Token Authentication - Authenticate using your Atlassian account email and API token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `password: str`
    :   Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens

    `username: str`
    :   Your Atlassian account email address

<a id="ConfluenceConnector"></a>

`ConfluenceConnector(auth_config: ConfluenceAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, subdomain: str | None = None)`
:   Type-safe Confluence API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new confluence connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ConfluenceAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            subdomain: Your Confluence Cloud subdomain (e.g., mycompany for mycompany.atlassian.net)
    Examples:
        # Local mode (direct API calls)
        connector = ConfluenceConnector(auth_config=ConfluenceAuthConfig(username="...", password="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ConfluenceConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ConfluenceConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ConfluenceAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.confluence.connector.ConfluenceConnector`
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
            A ConfluenceConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ConfluenceConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ConfluenceAuthConfig(username="...", password="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ConfluenceConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ConfluenceConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ConfluenceConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.confluence.models.ConfluenceCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ConfluenceCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="GroupsSearchData"></a>

`GroupsSearchData(**data: Any)`
:   Search result data for groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The unique identifier of the group

    `links: dict[str, typing.Any] | None`
    :   Links related to the group

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the group

    `type_: str | None`
    :   The type of group

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

    `author_id: str | None`
    :   ID of the user who created the page

    `body: dict[str, typing.Any] | None`
    :   Page body content

    `created_at: str | None`
    :   Timestamp when the page was created

    `id: str | None`
    :   Unique page identifier

    `last_owner_id: str | None`
    :   ID of the previous page owner

    `links: dict[str, typing.Any] | None`
    :   Links related to the page

    `model_config`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   ID of the current page owner

    `parent_id: str | None`
    :   ID of the parent page

    `parent_type: str | None`
    :   Type of the parent (page or space)

    `position: int | None`
    :   Position of the page among siblings

    `space_id: str | None`
    :   ID of the space containing this page

    `status: str | None`
    :   Page status (current, archived, trashed, draft)

    `title: str | None`
    :   Page title

    `version: dict[str, typing.Any] | None`
    :   Version information

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

    `author_id: str | None`
    :   ID of the user who created the space

    `created_at: str | None`
    :   Timestamp when the space was created

    `description: dict[str, typing.Any] | None`
    :   Space description in various formats

    `homepage_id: str | None`
    :   ID of the space homepage

    `icon: dict[str, typing.Any] | None`
    :   Space icon information

    `id: str | None`
    :   Unique space identifier

    `key: str | None`
    :   Space key

    `links: dict[str, typing.Any] | None`
    :   Links related to the space

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Space name

    `status: str | None`
    :   Space status (current or archived)

    `type_: str | None`
    :   Space type (global or personal)