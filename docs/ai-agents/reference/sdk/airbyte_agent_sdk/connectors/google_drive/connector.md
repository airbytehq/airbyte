---
id: airbyte_agent_sdk-connectors-google_drive-connector
title: airbyte_agent_sdk.connectors.google_drive.connector
---

Module airbyte_agent_sdk.connectors.google_drive.connector
==========================================================
Google-Drive connector.

Classes
-------

<a id="AboutQuery"></a>

`AboutQuery(connector: GoogleDriveConnector)`
:   Query class for About entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.About`
    :   Gets information about the user, the user's Drive, and system capabilities
        
        Args:
            fields: Fields to include in the response (use * for all fields)
            **kwargs: Additional parameters
        
        Returns:
            About

<a id="ChangesQuery"></a>

`ChangesQuery(connector: GoogleDriveConnector)`
:   Query class for Changes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, page_token: str, page_size: int | None = None, drive_id: str | None = None, include_items_from_all_drives: bool | None = None, supports_all_drives: bool | None = None, spaces: str | None = None, include_removed: bool | None = None, restrict_to_my_drive: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Change], ChangesListResultMeta]`
    :   Lists the changes for a user or shared drive
        
        Args:
            page_token: Token for the page of changes to retrieve (from changes.getStartPageToken or previous response)
            page_size: Maximum number of changes to return (1-1000)
            drive_id: The shared drive from which changes are returned
            include_items_from_all_drives: Whether to include changes from all drives
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            spaces: Comma-separated list of spaces to query
            include_removed: Whether to include changes indicating that items have been removed
            restrict_to_my_drive: Whether to restrict the results to changes inside the My Drive hierarchy
            **kwargs: Additional parameters
        
        Returns:
            ChangesListResult

<a id="ChangesStartPageTokenQuery"></a>

`ChangesStartPageTokenQuery(connector: GoogleDriveConnector)`
:   Query class for ChangesStartPageToken entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, drive_id: str | None = None, supports_all_drives: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.StartPageToken`
    :   Gets the starting pageToken for listing future changes
        
        Args:
            drive_id: The ID of the shared drive for which the starting pageToken is returned
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            **kwargs: Additional parameters
        
        Returns:
            StartPageToken

<a id="CommentsQuery"></a>

`CommentsQuery(connector: GoogleDriveConnector)`
:   Query class for Comments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, file_id: str, comment_id: str, include_deleted: bool | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.Comment`
    :   Gets a comment by ID
        
        Args:
            file_id: The ID of the file
            comment_id: The ID of the comment
            include_deleted: Whether to return deleted comments
            fields: Fields to include in the response (required for comments)
            **kwargs: Additional parameters
        
        Returns:
            Comment

    `list(self, file_id: str, page_size: int | None = None, page_token: str | None = None, start_modified_time: str | None = None, include_deleted: bool | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Comment], CommentsListResultMeta]`
    :   Lists a file's comments
        
        Args:
            file_id: The ID of the file
            page_size: Maximum number of comments to return (1-100)
            page_token: Token for continuing a previous list request
            start_modified_time: Minimum value of modifiedTime to filter by (RFC 3339)
            include_deleted: Whether to include deleted comments
            fields: Fields to include in the response (required for comments)
            **kwargs: Additional parameters
        
        Returns:
            CommentsListResult

<a id="DrivesQuery"></a>

`DrivesQuery(connector: GoogleDriveConnector)`
:   Query class for Drives entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, drive_id: str, use_domain_admin_access: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.Drive`
    :   Gets a shared drive's metadata by ID
        
        Args:
            drive_id: The ID of the shared drive
            use_domain_admin_access: Issue the request as a domain administrator
            **kwargs: Additional parameters
        
        Returns:
            Drive

    `list(self, page_size: int | None = None, page_token: str | None = None, q: str | None = None, use_domain_admin_access: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Drive], DrivesListResultMeta]`
    :   Lists the user's shared drives
        
        Args:
            page_size: Maximum number of shared drives to return (1-100)
            page_token: Token for continuing a previous list request
            q: Query string for searching shared drives
            use_domain_admin_access: Issue the request as a domain administrator
            **kwargs: Additional parameters
        
        Returns:
            DrivesListResult

<a id="FilesExportQuery"></a>

`FilesExportQuery(connector: GoogleDriveConnector)`
:   Query class for FilesExport entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, file_id: str, mime_type: str, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Exports a Google Workspace file (Docs, Sheets, Slides, Drawings) to a specified format.
        Common export formats:
        - application/pdf (all types)
        - text/plain (Docs)
        - text/csv (Sheets)
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document (Docs to .docx)
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (Sheets to .xlsx)
        - application/vnd.openxmlformats-officedocument.presentationml.presentation (Slides to .pptx)
        Note: Export has a 10MB limit. For larger files, use the Drive UI.
        
        
                Args:
                    file_id: The ID of the Google Workspace file to export
                    mime_type: The MIME type of the format to export to. Common values:
        - application/pdf
        - text/plain
        - text/csv
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        - application/vnd.openxmlformats-officedocument.presentationml.presentation
        
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, file_id: str, mime_type: str, path: str, range_header: str | None = None, **kwargs) ‑> Path`
    :   Exports a Google Workspace file (Docs, Sheets, Slides, Drawings) to a specified format.
        Common export formats:
        - application/pdf (all types)
        - text/plain (Docs)
        - text/csv (Sheets)
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document (Docs to .docx)
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (Sheets to .xlsx)
        - application/vnd.openxmlformats-officedocument.presentationml.presentation (Slides to .pptx)
        Note: Export has a 10MB limit. For larger files, use the Drive UI.
         and save to file.
        
                Args:
                    file_id: The ID of the Google Workspace file to export
                    mime_type: The MIME type of the format to export to. Common values:
        - application/pdf
        - text/plain
        - text/csv
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        - application/vnd.openxmlformats-officedocument.presentationml.presentation
        
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

<a id="FilesQuery"></a>

`FilesQuery(connector: GoogleDriveConnector)`
:   Query class for Files entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, mime_type: str | None = None, parents: list[str] | None = None, description: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.File`
    :   Creates a new file or folder in Google Drive (metadata only, no content).
        To create a folder, set mimeType to 'application/vnd.google-apps.folder'.
        To create a Google Doc, use 'application/vnd.google-apps.document'.
        To create a Google Sheet, use 'application/vnd.google-apps.spreadsheet'.
        
        
                Args:
                    name: The name of the file or folder
                    mime_type: The MIME type of the file. Use 'application/vnd.google-apps.folder' for folders,
        'application/vnd.google-apps.document' for Google Docs,
        'application/vnd.google-apps.spreadsheet' for Google Sheets.
        
                    parents: The IDs of the parent folders. If not specified, the file is placed in My Drive root.
                    description: A short description of the file
                    **kwargs: Additional parameters
        
                Returns:
                    File

    `delete(self, file_id: str, supports_all_drives: bool | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Permanently deletes a file owned by the user without moving it to the trash.
        
        Args:
            file_id: The ID of the file to delete
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `download(self, file_id: str, alt: str, acknowledge_abuse: bool | None = None, supports_all_drives: bool | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the binary content of a file. This works for non-Google Workspace files
        (PDFs, images, zip files, etc.). For Google Docs, Sheets, Slides, or Drawings,
        use the export action instead.
        
        
                Args:
                    file_id: The ID of the file to download
                    alt: Must be set to 'media' to download file content
                    acknowledge_abuse: Whether the user is acknowledging the risk of downloading known malware or other abusive files
                    supports_all_drives: Whether the requesting application supports both My Drives and shared drives
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, file_id: str, alt: str, path: str, acknowledge_abuse: bool | None = None, supports_all_drives: bool | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the binary content of a file. This works for non-Google Workspace files
        (PDFs, images, zip files, etc.). For Google Docs, Sheets, Slides, or Drawings,
        use the export action instead.
         and save to file.
        
                Args:
                    file_id: The ID of the file to download
                    alt: Must be set to 'media' to download file content
                    acknowledge_abuse: Whether the user is acknowledging the risk of downloading known malware or other abusive files
                    supports_all_drives: Whether the requesting application supports both My Drives and shared drives
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

    `get(self, file_id: str, fields: str | None = None, supports_all_drives: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.File`
    :   Gets a file's metadata by ID
        
        Args:
            file_id: The ID of the file
            fields: Fields to include in the response
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            **kwargs: Additional parameters
        
        Returns:
            File

    `list(self, page_size: int | None = None, page_token: str | None = None, q: str | None = None, order_by: str | None = None, fields: str | None = None, spaces: str | None = None, corpora: str | None = None, drive_id: str | None = None, include_items_from_all_drives: bool | None = None, supports_all_drives: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[File], FilesListResultMeta]`
    :   Lists the user's files. Returns a paginated list of files.
        
        Args:
            page_size: Maximum number of files to return per page (1-1000)
            page_token: Token for continuing a previous list request
            q: Query string for searching files
            order_by: Sort order (e.g., 'modifiedTime desc', 'name')
            fields: Fields to include in the response
            spaces: Comma-separated list of spaces to query (drive, appDataFolder)
            corpora: Bodies of items to search (user, drive, allDrives)
            drive_id: ID of the shared drive to search
            include_items_from_all_drives: Whether to include items from all drives
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            **kwargs: Additional parameters
        
        Returns:
            FilesListResult

    `update(self, file_id: str, name: str | None = None, description: str | None = None, mime_type: str | None = None, add_parents: str | None = None, remove_parents: str | None = None, supports_all_drives: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.File`
    :   Updates a file's metadata. Use addParents/removeParents query parameters
        to move a file between folders.
        
        
                Args:
                    name: The new name of the file
                    description: A new description for the file
                    mime_type: The new MIME type of the file
                    file_id: The ID of the file to update
                    add_parents: Comma-separated list of parent IDs to add
                    remove_parents: Comma-separated list of parent IDs to remove
                    supports_all_drives: Whether the requesting application supports both My Drives and shared drives
                    **kwargs: Additional parameters
        
                Returns:
                    File

<a id="FilesUploadQuery"></a>

`FilesUploadQuery(connector: GoogleDriveConnector)`
:   Query class for FilesUpload entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `create(self, name: str, file_content: str, mime_type: str | None = None, parents: list[str] | None = None, description: str | None = None, file_mime_type: str | None = None, upload_type: str | None = None, supports_all_drives: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.File`
    :   Uploads a new file to Google Drive with both metadata and file content.
        The file content must be base64-encoded in the file_content parameter.
        Suitable for files up to 5MB. For larger files, use the Drive UI.
        
        
                Args:
                    name: The name of the file
                    file_content: Base64-encoded file content to upload
                    mime_type: The MIME type for the file metadata in Google Drive
                    parents: The IDs of the parent folders
                    description: A short description of the file
                    file_mime_type: The MIME type of the actual file content (e.g., 'application/pdf', 'image/png'). Defaults to 'application/octet-stream'.
                    upload_type: The type of upload request (must be 'multipart')
                    supports_all_drives: Whether the requesting application supports both My Drives and shared drives
                    **kwargs: Additional parameters
        
                Returns:
                    File

<a id="GoogleDriveConnector"></a>

`GoogleDriveConnector(auth_config: GoogleDriveAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Google-Drive API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new google-drive connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GoogleDriveAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GoogleDriveConnector(auth_config=GoogleDriveAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GoogleDriveConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GoogleDriveConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GoogleDriveAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: "'GoogleDriveReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A GoogleDriveConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GoogleDriveConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleDriveAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With replication config (required for this connector):
            connector = await GoogleDriveConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GoogleDriveAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
                replication_config=GoogleDriveReplicationConfig(folder_url="...", streams="..."),
            )
        
            # With server-side OAuth:
            connector = await GoogleDriveConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
                replication_config=GoogleDriveReplicationConfig(folder_url="...", streams="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: "'GoogleDriveReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            replication_config: Typed replication settings. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await GoogleDriveConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Google-Drive Source",
                replication_config=GoogleDriveReplicationConfig(folder_url="...", streams="..."),
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GoogleDriveConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GoogleDriveConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GoogleDriveConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GoogleDriveCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'delete', 'download']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="PermissionsQuery"></a>

`PermissionsQuery(connector: GoogleDriveConnector)`
:   Query class for Permissions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, file_id: str, permission_id: str, supports_all_drives: bool | None = None, use_domain_admin_access: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.Permission`
    :   Gets a permission by ID
        
        Args:
            file_id: The ID of the file
            permission_id: The ID of the permission
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            use_domain_admin_access: Issue the request as a domain administrator
            **kwargs: Additional parameters
        
        Returns:
            Permission

    `list(self, file_id: str, page_size: int | None = None, page_token: str | None = None, supports_all_drives: bool | None = None, use_domain_admin_access: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Permission], PermissionsListResultMeta]`
    :   Lists a file's or shared drive's permissions
        
        Args:
            file_id: The ID of the file or shared drive
            page_size: Maximum number of permissions to return (1-100)
            page_token: Token for continuing a previous list request
            supports_all_drives: Whether the requesting application supports both My Drives and shared drives
            use_domain_admin_access: Issue the request as a domain administrator
            **kwargs: Additional parameters
        
        Returns:
            PermissionsListResult

<a id="RepliesQuery"></a>

`RepliesQuery(connector: GoogleDriveConnector)`
:   Query class for Replies entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, file_id: str, comment_id: str, reply_id: str, include_deleted: bool | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.Reply`
    :   Gets a reply by ID
        
        Args:
            file_id: The ID of the file
            comment_id: The ID of the comment
            reply_id: The ID of the reply
            include_deleted: Whether to return deleted replies
            fields: Fields to include in the response (required for replies)
            **kwargs: Additional parameters
        
        Returns:
            Reply

    `list(self, file_id: str, comment_id: str, page_size: int | None = None, page_token: str | None = None, include_deleted: bool | None = None, fields: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Reply], RepliesListResultMeta]`
    :   Lists a comment's replies
        
        Args:
            file_id: The ID of the file
            comment_id: The ID of the comment
            page_size: Maximum number of replies to return (1-100)
            page_token: Token for continuing a previous list request
            include_deleted: Whether to include deleted replies
            fields: Fields to include in the response (required for replies)
            **kwargs: Additional parameters
        
        Returns:
            RepliesListResult

<a id="RevisionsQuery"></a>

`RevisionsQuery(connector: GoogleDriveConnector)`
:   Query class for Revisions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, file_id: str, revision_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.Revision`
    :   Gets a revision's metadata by ID
        
        Args:
            file_id: The ID of the file
            revision_id: The ID of the revision
            **kwargs: Additional parameters
        
        Returns:
            Revision

    `list(self, file_id: str, page_size: int | None = None, page_token: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Revision], RevisionsListResultMeta]`
    :   Lists a file's revisions
        
        Args:
            file_id: The ID of the file
            page_size: Maximum number of revisions to return (1-1000)
            page_token: Token for continuing a previous list request
            **kwargs: Additional parameters
        
        Returns:
            RevisionsListResult