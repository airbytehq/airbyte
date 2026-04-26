---
id: airbyte_agent_sdk-connectors-typeform-connector
title: airbyte_agent_sdk.connectors.typeform.connector
---

Module airbyte_agent_sdk.connectors.typeform.connector
======================================================
Typeform connector.

Classes
-------

<a id="FormsQuery"></a>

`FormsQuery(connector: TypeformConnector)`
:   Query class for Forms entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FormsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[FormsSearchData]`
    :   Search forms records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FormsSearchFilter):
        - links: Links to related resources
        - created_at: Date and time when the form was created
        - fields: List of fields within the form
        - id: Unique identifier of the form
        - last_updated_at: Date and time when the form was last updated
        - logic: Logic rules or conditions applied to the form fields
        - published_at: Date and time when the form was published
        - settings: Settings and configurations for the form
        - thankyou_screens: Thank you screen configurations
        - theme: Theme settings for the form
        - title: Title of the form
        - type_: Type of the form
        - welcome_screens: Welcome screen configurations
        - workspace: Workspace details where the form belongs
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FormsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, form_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.Form`
    :   Retrieves a single form by its ID, including fields, settings, and logic
        
        Args:
            form_id: Unique ID of the form
            **kwargs: Additional parameters
        
        Returns:
            Form

    `list(self, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Form], FormsListResultMeta]`
    :   Returns a paginated list of forms in the account
        
        Args:
            page: Page number to retrieve
            page_size: Number of forms per page
            **kwargs: Additional parameters
        
        Returns:
            FormsListResult

<a id="ImagesQuery"></a>

`ImagesQuery(connector: TypeformConnector)`
:   Query class for Images entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ImagesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ImagesSearchData]`
    :   Search images records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ImagesSearchFilter):
        - avg_color: Average color of the image
        - file_name: Name of the image file
        - has_alpha: Whether the image has an alpha channel
        - height: Height of the image in pixels
        - id: Unique identifier of the image
        - media_type: MIME type of the image
        - src: URL to access the image
        - width: Width of the image in pixels
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ImagesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult[list[Image]]`
    :   Returns a list of images in the account
        
        Returns:
            ImagesListResult

<a id="ResponsesQuery"></a>

`ResponsesQuery(connector: TypeformConnector)`
:   Query class for Responses entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ResponsesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ResponsesSearchData]`
    :   Search responses records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ResponsesSearchFilter):
        - answers: Response data for each question in the form
        - calculated: Calculated data related to the response
        - form_id: ID of the form
        - hidden: Hidden fields in the response
        - landed_at: Timestamp when the respondent landed on the form
        - landing_id: ID of the landing page
        - metadata: Metadata related to the response
        - response_id: ID of the response
        - response_type: Type of the response
        - submitted_at: Timestamp when the response was submitted
        - token: Token associated with the response
        - variables: Variables associated with the response
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ResponsesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, form_id: str, page_size: int | None = None, since: str | None = None, until: str | None = None, after: str | None = None, before: str | None = None, sort: str | None = None, completed: bool | None = None, query: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Response], ResponsesListResultMeta]`
    :   Returns a paginated list of responses for a given form
        
        Args:
            form_id: Unique ID of the form
            page_size: Number of responses per page
            since: Limit responses to those submitted since the specified date/time (ISO 8601 format, e.g. 2021-03-01T00:00:00Z)
            until: Limit responses to those submitted until the specified date/time (ISO 8601 format)
            after: Cursor token for pagination; returns responses after this token
            before: Cursor token for pagination; returns responses before this token
            sort: Sort order for responses, e.g. submitted_at,asc
            completed: Filter by completed status (true or false)
            query: Search query to filter responses
            **kwargs: Additional parameters
        
        Returns:
            ResponsesListResult

<a id="ThemesQuery"></a>

`ThemesQuery(connector: TypeformConnector)`
:   Query class for Themes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ThemesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[ThemesSearchData]`
    :   Search themes records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ThemesSearchFilter):
        - background: Background settings for the theme
        - colors: Color settings
        - created_at: Timestamp when the theme was created
        - fields: Field display settings
        - font: Font used in the theme
        - has_transparent_button: Whether the theme has a transparent button
        - id: Unique identifier of the theme
        - name: Name of the theme
        - rounded_corners: Rounded corners setting
        - screens: Screen display settings
        - updated_at: Timestamp when the theme was last updated
        - visibility: Visibility setting of the theme
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ThemesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Theme], ThemesListResultMeta]`
    :   Returns a paginated list of themes in the account
        
        Args:
            page: Page number to retrieve
            page_size: Number of themes per page
            **kwargs: Additional parameters
        
        Returns:
            ThemesListResult

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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'TypeformAuthConfig'", name: str | None = None, replication_config: "'TypeformReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A TypeformConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await TypeformConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=TypeformAuthConfig(access_token="..."),
            )
        
            # With replication config (required for this connector):
            connector = await TypeformConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=TypeformAuthConfig(access_token="..."),
                replication_config=TypeformReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @TypeformConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @TypeformConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await TypeformConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

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

<a id="WebhooksQuery"></a>

`WebhooksQuery(connector: TypeformConnector)`
:   Query class for Webhooks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WebhooksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[WebhooksSearchData]`
    :   Search webhooks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WebhooksSearchFilter):
        - created_at: Timestamp when the webhook was created
        - enabled: Whether the webhook is currently enabled
        - form_id: ID of the form associated with the webhook
        - id: Unique identifier of the webhook
        - tag: Tag to categorize or label the webhook
        - updated_at: Timestamp when the webhook was last updated
        - url: URL where webhook data is sent
        - verify_ssl: Whether SSL verification is enforced
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            WebhooksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, form_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResult[list[Webhook]]`
    :   Returns webhooks configured for a given form
        
        Args:
            form_id: Unique ID of the form
            **kwargs: Additional parameters
        
        Returns:
            WebhooksListResult

<a id="WorkspacesQuery"></a>

`WorkspacesQuery(connector: TypeformConnector)`
:   Query class for Workspaces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WorkspacesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.typeform.models.AirbyteSearchResult[WorkspacesSearchData]`
    :   Search workspaces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WorkspacesSearchFilter):
        - account_id: Account ID associated with the workspace
        - default: Whether this is the default workspace
        - forms: Information about forms in the workspace
        - id: Unique identifier of the workspace
        - name: Name of the workspace
        - self: Self-referential link
        - shared: Whether this workspace is shared
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            WorkspacesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, page: int | None = None, page_size: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.typeform.models.TypeformExecuteResultWithMeta[list[Workspace], WorkspacesListResultMeta]`
    :   Returns a paginated list of workspaces in the account
        
        Args:
            page: Page number to retrieve
            page_size: Number of workspaces per page
            **kwargs: Additional parameters
        
        Returns:
            WorkspacesListResult