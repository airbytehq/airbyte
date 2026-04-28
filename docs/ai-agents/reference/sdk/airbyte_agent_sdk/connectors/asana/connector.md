---
id: airbyte_agent_sdk-connectors-asana-connector
title: airbyte_agent_sdk.connectors.asana.connector
---

Module airbyte_agent_sdk.connectors.asana.connector
===================================================
Asana connector.

Classes
-------

<a id="AsanaConnector"></a>

`AsanaConnector(auth_config: AsanaAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Asana API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new asana connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., AsanaAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = AsanaConnector(auth_config=AsanaAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = AsanaConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = AsanaConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AsanaAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Supports two authentication modes:
        1. Direct credentials: Provide `auth_config` with typed credentials
        2. Server-side OAuth: Provide `server_side_oauth_secret_id` from OAuth flow
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config. Required unless using server_side_oauth_secret_id.
            server_side_oauth_secret_id: OAuth secret ID from get_consent_url redirect.
                When provided, auth_config is not required.
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A AsanaConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AsanaConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AsanaAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With server-side OAuth:
            connector = await AsanaConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
    :   Initiate server-side OAuth flow with auto-source creation.
        
        Returns a consent URL where the end user should be redirected to grant access.
        After completing consent, the source is automatically created and the user is
        redirected to your redirect_url with a `connector_id` query parameter.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            redirect_url: URL where users will be redirected after OAuth consent.
                After consent, user arrives at: redirect_url?connector_id=...
            name: Optional name for the source. Defaults to connector name + workspace_name.
            replication_config: Optional replication settings dict. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await AsanaConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Asana Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AsanaConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AsanaConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AsanaConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AsanaCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'delete', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="AttachmentsQuery"></a>

`AttachmentsQuery(connector: AsanaConnector)`
:   Query class for Attachments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AttachmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[AttachmentsSearchData]`
    :   Search attachments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AttachmentsSearchFilter):
        - connected_to_app: 
        - created_at: 
        - download_url: 
        - gid: 
        - host: 
        - name: 
        - parent: 
        - permanent_url: 
        - resource_subtype: 
        - resource_type: 
        - size: 
        - view_url: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AttachmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `download(self, attachment_gid: str, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the file content of an attachment. This operation first retrieves the attachment
        metadata to get the download_url, then downloads the file from that URL.
        
        
                Args:
                    attachment_gid: Globally unique identifier for the attachment
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, attachment_gid: str, path: str, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the file content of an attachment. This operation first retrieves the attachment
        metadata to get the download_url, then downloads the file from that URL.
         and save to file.
        
                Args:
                    attachment_gid: Globally unique identifier for the attachment
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

    `get(self, attachment_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Attachment`
    :   Get details for a single attachment by its GID
        
        Args:
            attachment_gid: Globally unique identifier for the attachment
            **kwargs: Additional parameters
        
        Returns:
            Attachment

    `list(self, parent: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[AttachmentCompact], AttachmentsListResultMeta]`
    :   Returns a list of attachments for an object (task, project, etc.)
        
        Args:
            parent: Globally unique identifier for the object to fetch attachments for (e.g., a task GID)
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            AttachmentsListResult

<a id="ProjectSectionsQuery"></a>

`ProjectSectionsQuery(connector: AsanaConnector)`
:   Query class for ProjectSections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, data: ProjectSectionsCreateParamsData, project_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Section`
    :   Creates a new section in a project. Returns the full record of the newly created section.
        
        
        Args:
            data: Parameter data
            project_gid: Globally unique identifier for the project
            **kwargs: Additional parameters
        
        Returns:
            Section

    `list(self, project_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[SectionCompact], ProjectSectionsListResultMeta]`
    :   Returns all sections in a project
        
        Args:
            project_gid: Project GID to list sections from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            ProjectSectionsListResult

<a id="ProjectTasksQuery"></a>

`ProjectTasksQuery(connector: AsanaConnector)`
:   Query class for ProjectTasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, project_gid: str, limit: int | None = None, offset: str | None = None, completed_since: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], ProjectTasksListResultMeta]`
    :   Returns all tasks in a project
        
        Args:
            project_gid: Project GID to list tasks from
            limit: Number of items to return per page
            offset: Pagination offset token
            completed_since: Only return tasks that have been completed since this time
            **kwargs: Additional parameters
        
        Returns:
            ProjectTasksListResult

<a id="ProjectsQuery"></a>

`ProjectsQuery(connector: AsanaConnector)`
:   Query class for Projects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ProjectsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[ProjectsSearchData]`
    :   Search projects records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ProjectsSearchFilter):
        - archived: 
        - color: 
        - created_at: 
        - current_status: 
        - custom_field_settings: 
        - custom_fields: 
        - default_view: 
        - due_date: 
        - due_on: 
        - followers: 
        - gid: 
        - html_notes: 
        - icon: 
        - is_template: 
        - members: 
        - modified_at: 
        - name: 
        - notes: 
        - owner: 
        - permalink_url: 
        - public: 
        - resource_type: 
        - start_on: 
        - team: 
        - workspace: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ProjectsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, data: ProjectsCreateParamsData, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Project`
    :   Create a new project in a workspace or team. Every project is required to be
        created in a specific workspace or organization, and this cannot be changed once set.
        
        
                Args:
                    data: Parameter data
                    **kwargs: Additional parameters
        
                Returns:
                    Project

    `delete(self, project_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Deletes a specific, existing project. Returns an empty data record.
        
        
        Args:
            project_gid: The project to delete
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `get(self, project_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Project`
    :   Get a single project by its ID
        
        Args:
            project_gid: Project GID
            **kwargs: Additional parameters
        
        Returns:
            Project

    `list(self, limit: int | None = None, offset: str | None = None, workspace: str | None = None, team: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], ProjectsListResultMeta]`
    :   Returns a paginated list of projects
        
        Args:
            limit: Number of items to return per page
            offset: Pagination offset token
            workspace: The workspace to filter projects on
            team: The team to filter projects on
            archived: Filter by archived status
            **kwargs: Additional parameters
        
        Returns:
            ProjectsListResult

    `update(self, data: ProjectsUpdateParamsData, project_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Project`
    :   Updates an existing project. Only the fields provided in the data block will be updated;
        any unspecified fields will remain unchanged. When using this method, it is best to
        specify only those fields you wish to change.
        
        
                Args:
                    data: Parameter data
                    project_gid: The project to update
                    **kwargs: Additional parameters
        
                Returns:
                    Project

<a id="SectionTasksQuery"></a>

`SectionTasksQuery(connector: AsanaConnector)`
:   Query class for SectionTasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, data: SectionTasksCreateParamsData, section_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Add a task to a specific, existing section. This will remove the task from other
        sections of the project. The task will be inserted at the top of the section unless
        an insert_before or insert_after parameter is declared.
        
        
                Args:
                    data: Parameter data
                    section_gid: The globally unique identifier for the section
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `list(self, section_gid: str, limit: int | None = None, offset: str | None = None, completed_since: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], SectionTasksListResultMeta]`
    :   Returns the compact task records for all tasks within the given section.
        
        Args:
            section_gid: The globally unique identifier for the section
            limit: Number of items to return per page
            offset: Pagination offset token
            completed_since: Only return tasks that are either incomplete or that have been completed since this time
            **kwargs: Additional parameters
        
        Returns:
            SectionTasksListResult

<a id="SectionsQuery"></a>

`SectionsQuery(connector: AsanaConnector)`
:   Query class for Sections entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SectionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[SectionsSearchData]`
    :   Search sections records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SectionsSearchFilter):
        - created_at: 
        - gid: 
        - name: 
        - project: 
        - resource_type: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SectionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `delete(self, section_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   A specific, existing section can be deleted by making a DELETE request on the URL
        for that section. Note that sections must be empty to be deleted. The last remaining
        section in a project cannot be deleted.
        
        
                Args:
                    section_gid: The section to delete
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `get(self, section_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Section`
    :   Get a single section by its ID
        
        Args:
            section_gid: Section GID
            **kwargs: Additional parameters
        
        Returns:
            Section

    `update(self, data: SectionsUpdateParamsData, section_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Section`
    :   A specific, existing section can be updated by making a PUT request on the URL for
        that section. Only the fields provided in the data block will be updated; any unspecified
        fields will remain unchanged. Currently only the name field can be updated.
        
        
                Args:
                    data: Parameter data
                    section_gid: The section to update
                    **kwargs: Additional parameters
        
                Returns:
                    Section

<a id="TagTasksQuery"></a>

`TagTasksQuery(connector: AsanaConnector)`
:   Query class for TagTasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, tag_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TagTasksListResultMeta]`
    :   Returns the compact task records for all tasks with the given tag.
        Tasks can have more than one tag at a time.
        
        
                Args:
                    tag_gid: Globally unique identifier for the tag
                    limit: Number of items to return per page
                    offset: Pagination offset token
                    **kwargs: Additional parameters
        
                Returns:
                    TagTasksListResult

<a id="TagsQuery"></a>

`TagsQuery(connector: AsanaConnector)`
:   Query class for Tags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TagsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[TagsSearchData]`
    :   Search tags records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TagsSearchFilter):
        - color: 
        - followers: 
        - gid: 
        - name: 
        - permalink_url: 
        - resource_type: 
        - workspace: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TagsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `delete(self, tag_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   A specific, existing tag can be deleted by making a DELETE request on the URL
        for that tag. Returns an empty data record.
        
        
                Args:
                    tag_gid: The tag to delete
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `get(self, tag_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Tag`
    :   Get a single tag by its ID
        
        Args:
            tag_gid: Tag GID
            **kwargs: Additional parameters
        
        Returns:
            Tag

    `update(self, data: TagsUpdateParamsData, tag_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Tag`
    :   Updates the properties of a tag. Only the fields provided in the data block will
        be updated; any unspecified fields will remain unchanged. Returns the complete
        updated tag record.
        
        
                Args:
                    data: Parameter data
                    tag_gid: The tag to update
                    **kwargs: Additional parameters
        
                Returns:
                    Tag

<a id="TaskDependenciesQuery"></a>

`TaskDependenciesQuery(connector: AsanaConnector)`
:   Query class for TaskDependencies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, task_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TaskDependenciesListResultMeta]`
    :   Returns all tasks that this task depends on
        
        Args:
            task_gid: Task GID to list dependencies from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            TaskDependenciesListResult

<a id="TaskDependentsQuery"></a>

`TaskDependentsQuery(connector: AsanaConnector)`
:   Query class for TaskDependents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, task_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TaskDependentsListResultMeta]`
    :   Returns all tasks that depend on this task
        
        Args:
            task_gid: Task GID to list dependents from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            TaskDependentsListResult

<a id="TaskProjectsQuery"></a>

`TaskProjectsQuery(connector: AsanaConnector)`
:   Query class for TaskProjects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, task_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], TaskProjectsListResultMeta]`
    :   Returns all projects a task is in
        
        Args:
            task_gid: Task GID to list projects from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            TaskProjectsListResult

<a id="TaskStoriesQuery"></a>

`TaskStoriesQuery(connector: AsanaConnector)`
:   Query class for TaskStories entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, data: TaskStoriesCreateParamsData, task_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Story`
    :   Adds a comment to a task. The comment will be authored by the currently
        authenticated user, and timestamped when the server receives the request.
        
        
                Args:
                    data: Parameter data
                    task_gid: The task to add a comment to
                    **kwargs: Additional parameters
        
                Returns:
                    Story

<a id="TaskSubtasksQuery"></a>

`TaskSubtasksQuery(connector: AsanaConnector)`
:   Query class for TaskSubtasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, task_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TaskSubtasksListResultMeta]`
    :   Returns all subtasks of a task
        
        Args:
            task_gid: Task GID to list subtasks from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            TaskSubtasksListResult

<a id="TaskTagsQuery"></a>

`TaskTagsQuery(connector: AsanaConnector)`
:   Query class for TaskTags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, data: TaskTagsCreateParamsData, task_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Adds a tag to a task. Returns an empty data block.
        
        
        Args:
            data: Parameter data
            task_gid: The task to operate on
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `delete(self, data: TaskTagsDeleteParamsData, task_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Removes a tag from a task. Returns an empty data block.
        
        
        Args:
            data: Parameter data
            task_gid: The task to operate on
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

<a id="TasksQuery"></a>

`TasksQuery(connector: AsanaConnector)`
:   Query class for Tasks entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TasksSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[TasksSearchData]`
    :   Search tasks records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TasksSearchFilter):
        - actual_time_minutes: The actual time spent on the task in minutes
        - approval_status: 
        - assignee: 
        - completed: 
        - completed_at: 
        - completed_by: 
        - created_at: 
        - custom_fields: 
        - dependencies: 
        - dependents: 
        - due_at: 
        - due_on: 
        - external: 
        - followers: 
        - gid: 
        - hearted: 
        - hearts: 
        - html_notes: 
        - is_rendered_as_separator: 
        - liked: 
        - likes: 
        - memberships: 
        - modified_at: 
        - name: 
        - notes: 
        - num_hearts: 
        - num_likes: 
        - num_subtasks: 
        - parent: 
        - permalink_url: 
        - projects: 
        - resource_subtype: 
        - resource_type: 
        - start_on: 
        - tags: 
        - workspace: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TasksSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, data: TasksCreateParamsData, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Task`
    :   Creates a new task. Every task is required to be created in a specific workspace,
        and this workspace cannot be changed once set. The workspace need not be set explicitly
        if you specify projects or a parent task instead.
        
        
                Args:
                    data: Parameter data
                    **kwargs: Additional parameters
        
                Returns:
                    Task

    `delete(self, task_gid: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Deletes a specific, existing task. Deleted tasks go into the trash of the user
        making the delete request. Tasks can be recovered from the trash within 30 days;
        afterward they are completely removed from the system.
        
        
                Args:
                    task_gid: The task to delete
                    **kwargs: Additional parameters
        
                Returns:
                    dict[str, Any]

    `get(self, task_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Task`
    :   Get a single task by its ID
        
        Args:
            task_gid: Task GID
            **kwargs: Additional parameters
        
        Returns:
            Task

    `list(self, limit: int | None = None, offset: str | None = None, project: str | None = None, workspace: str | None = None, section: str | None = None, assignee: str | None = None, completed_since: str | None = None, modified_since: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TasksListResultMeta]`
    :   Returns a paginated list of tasks. Must include either a project OR a section OR a workspace AND assignee parameter.
        
        Args:
            limit: Number of items to return per page
            offset: Pagination offset token
            project: The project to filter tasks on
            workspace: The workspace to filter tasks on
            section: The workspace to filter tasks on
            assignee: The assignee to filter tasks on
            completed_since: Only return tasks that have been completed since this time
            modified_since: Only return tasks that have been completed since this time
            **kwargs: Additional parameters
        
        Returns:
            TasksListResult

    `update(self, data: TasksUpdateParamsData, task_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Task`
    :   Updates an existing task. Only the fields provided in the data block will be updated;
        any unspecified fields will remain unchanged. When using this method, it is best to
        specify only those fields you wish to change.
        
        
                Args:
                    data: Parameter data
                    task_gid: The task to update
                    **kwargs: Additional parameters
        
                Returns:
                    Task

<a id="TeamProjectsQuery"></a>

`TeamProjectsQuery(connector: AsanaConnector)`
:   Query class for TeamProjects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, team_gid: str, limit: int | None = None, offset: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], TeamProjectsListResultMeta]`
    :   Returns all projects for a team
        
        Args:
            team_gid: Team GID to list projects from
            limit: Number of items to return per page
            offset: Pagination offset token
            archived: Filter by archived status
            **kwargs: Additional parameters
        
        Returns:
            TeamProjectsListResult

<a id="TeamUsersQuery"></a>

`TeamUsersQuery(connector: AsanaConnector)`
:   Query class for TeamUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, team_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[UserCompact], TeamUsersListResultMeta]`
    :   Returns all users in a team
        
        Args:
            team_gid: Team GID to list users from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            TeamUsersListResult

<a id="TeamsQuery"></a>

`TeamsQuery(connector: AsanaConnector)`
:   Query class for Teams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: TeamsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[TeamsSearchData]`
    :   Search teams records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (TeamsSearchFilter):
        - description: 
        - gid: 
        - html_description: 
        - name: 
        - organization: 
        - permalink_url: 
        - resource_type: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            TeamsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, team_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Team`
    :   Get a single team by its ID
        
        Args:
            team_gid: Team GID
            **kwargs: Additional parameters
        
        Returns:
            Team

<a id="UserTeamsQuery"></a>

`UserTeamsQuery(connector: AsanaConnector)`
:   Query class for UserTeams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, user_gid: str, organization: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TeamCompact], UserTeamsListResultMeta]`
    :   Returns all teams a user is a member of
        
        Args:
            user_gid: User GID to list teams from
            organization: The workspace or organization to filter teams on
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            UserTeamsListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: AsanaConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - email: 
        - gid: 
        - name: 
        - photo: 
        - resource_type: 
        - workspaces: 
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            UsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, user_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.User`
    :   Get a single user by their ID
        
        Args:
            user_gid: User GID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, limit: int | None = None, offset: str | None = None, workspace: str | None = None, team: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[UserCompact], UsersListResultMeta]`
    :   Returns a paginated list of users
        
        Args:
            limit: Number of items to return per page
            offset: Pagination offset token
            workspace: The workspace to filter users on
            team: The team to filter users on
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult

<a id="WorkspaceMembershipsQuery"></a>

`WorkspaceMembershipsQuery(connector: AsanaConnector)`
:   Query class for WorkspaceMemberships entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, data: WorkspaceMembershipsCreateParamsData, workspace_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.User`
    :   Add a user to a workspace or organization. The user can be referenced by their
        globally unique user ID or their email address. Returns the full user record
        for the invited user.
        
        
                Args:
                    data: Parameter data
                    workspace_gid: The workspace or organization to add the user to
                    **kwargs: Additional parameters
        
                Returns:
                    User

<a id="WorkspaceProjectsQuery"></a>

`WorkspaceProjectsQuery(connector: AsanaConnector)`
:   Query class for WorkspaceProjects entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_gid: str, limit: int | None = None, offset: str | None = None, archived: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], WorkspaceProjectsListResultMeta]`
    :   Returns all projects in a workspace
        
        Args:
            workspace_gid: Workspace GID to list projects from
            limit: Number of items to return per page
            offset: Pagination offset token
            archived: Filter by archived status
            **kwargs: Additional parameters
        
        Returns:
            WorkspaceProjectsListResult

<a id="WorkspaceTagsQuery"></a>

`WorkspaceTagsQuery(connector: AsanaConnector)`
:   Query class for WorkspaceTags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, data: WorkspaceTagsCreateParamsData, workspace_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Tag`
    :   Creates a new tag in a workspace or organization. Every tag is required to be
        created in a specific workspace or organization, and this cannot be changed once set.
        Returns the full record of the newly created tag.
        
        
                Args:
                    data: Parameter data
                    workspace_gid: Globally unique identifier for the workspace or organization
                    **kwargs: Additional parameters
        
                Returns:
                    Tag

    `list(self, workspace_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TagCompact], WorkspaceTagsListResultMeta]`
    :   Returns all tags in a workspace
        
        Args:
            workspace_gid: Workspace GID to list tags from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            WorkspaceTagsListResult

<a id="WorkspaceTaskSearchQuery"></a>

`WorkspaceTaskSearchQuery(connector: AsanaConnector)`
:   Query class for WorkspaceTaskSearch entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_gid: str, limit: int | None = None, offset: str | None = None, text: str | None = None, completed: bool | None = None, assignee_any: str | None = None, projects_any: str | None = None, sections_any: str | None = None, teams_any: str | None = None, followers_any: str | None = None, created_at_after: str | None = None, created_at_before: str | None = None, modified_at_after: str | None = None, modified_at_before: str | None = None, due_on_after: str | None = None, due_on_before: str | None = None, resource_subtype: str | None = None, sort_by: str | None = None, sort_ascending: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], WorkspaceTaskSearchListResultMeta]`
    :   Returns tasks that match the specified search criteria. This endpoint requires a premium Asana account.
        
        IMPORTANT: At least one search filter parameter must be provided. Valid filter parameters include: text, completed, assignee.any, projects.any, sections.any, teams.any, followers.any, created_at.after, created_at.before, modified_at.after, modified_at.before, due_on.after, due_on.before, and resource_subtype. The sort_by and sort_ascending parameters are for ordering results and do not count as search filters.
        
        
                Args:
                    workspace_gid: Workspace GID to search tasks in
                    limit: Number of items to return per page
                    offset: Pagination offset token
                    text: Search text to filter tasks
                    completed: Filter by completion status
                    assignee_any: Comma-separated list of assignee GIDs
                    projects_any: Comma-separated list of project GIDs
                    sections_any: Comma-separated list of section GIDs
                    teams_any: Comma-separated list of team GIDs
                    followers_any: Comma-separated list of follower GIDs
                    created_at_after: Filter tasks created after this date (ISO 8601 format)
                    created_at_before: Filter tasks created before this date (ISO 8601 format)
                    modified_at_after: Filter tasks modified after this date (ISO 8601 format)
                    modified_at_before: Filter tasks modified before this date (ISO 8601 format)
                    due_on_after: Filter tasks due after this date (ISO 8601 date format)
                    due_on_before: Filter tasks due before this date (ISO 8601 date format)
                    resource_subtype: Filter by task resource subtype (e.g., default_task, milestone)
                    sort_by: Field to sort by (e.g., created_at, modified_at, due_date)
                    sort_ascending: Sort order (true for ascending, false for descending)
                    **kwargs: Additional parameters
        
                Returns:
                    WorkspaceTaskSearchListResult

<a id="WorkspaceTeamsQuery"></a>

`WorkspaceTeamsQuery(connector: AsanaConnector)`
:   Query class for WorkspaceTeams entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TeamCompact], WorkspaceTeamsListResultMeta]`
    :   Returns all teams in a workspace
        
        Args:
            workspace_gid: Workspace GID to list teams from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            WorkspaceTeamsListResult

<a id="WorkspaceUsersQuery"></a>

`WorkspaceUsersQuery(connector: AsanaConnector)`
:   Query class for WorkspaceUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_gid: str, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[UserCompact], WorkspaceUsersListResultMeta]`
    :   Returns all users in a workspace
        
        Args:
            workspace_gid: Workspace GID to list users from
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            WorkspaceUsersListResult

<a id="WorkspacesQuery"></a>

`WorkspacesQuery(connector: AsanaConnector)`
:   Query class for Workspaces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: WorkspacesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[WorkspacesSearchData]`
    :   Search workspaces records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (WorkspacesSearchFilter):
        - email_domains: 
        - gid: 
        - is_organization: 
        - name: 
        - resource_type: 
        
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

    `get(self, workspace_gid: str, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.Workspace`
    :   Get a single workspace by its ID
        
        Args:
            workspace_gid: Workspace GID
            **kwargs: Additional parameters
        
        Returns:
            Workspace

    `list(self, limit: int | None = None, offset: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[WorkspaceCompact], WorkspacesListResultMeta]`
    :   Returns a paginated list of workspaces
        
        Args:
            limit: Number of items to return per page
            offset: Pagination offset token
            **kwargs: Additional parameters
        
        Returns:
            WorkspacesListResult