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

    `list(self, page_token: str | None = None, page_size: int | None = None, drive_id: str | None = None, include_items_from_all_drives: bool | None = None, supports_all_drives: bool | None = None, spaces: str | None = None, include_removed: bool | None = None, restrict_to_my_drive: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.google_drive.models.GoogleDriveExecuteResultWithMeta[list[Change], ChangesListResultMeta]`
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
    :   Exports a Google-NATIVE Workspace file (Docs, Sheets, Slides, Drawings --
        mimeType `application/vnd.google-apps.*`) to a specified format. Use this ONLY for
        those native types: exporting a binary file (PDF, image, uploaded .docx/.xlsx) returns
        403 `fileNotExportable` -- for those use the `files` `download` action instead. If unsure
        of a file's type, check its `mimeType` with `files.get` first.
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

    `download_base64(self, file_id: str, mime_type: str, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Exports a Google-NATIVE Workspace file (Docs, Sheets, Slides, Drawings --
        mimeType `application/vnd.google-apps.*`) to a specified format. Use this ONLY for
        those native types: exporting a binary file (PDF, image, uploaded .docx/.xlsx) returns
        403 `fileNotExportable` -- for those use the `files` `download` action instead. If unsure
        of a file's type, check its `mimeType` with `files.get` first.
        Common export formats:
        - application/pdf (all types)
        - text/plain (Docs)
        - text/csv (Sheets)
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document (Docs to .docx)
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (Sheets to .xlsx)
        - application/vnd.openxmlformats-officedocument.presentationml.presentation (Slides to .pptx)
        Note: Export has a 10MB limit. For larger files, use the Drive UI.
         and return a JSON-safe base64 chunk.

    `download_local(self, file_id: str, mime_type: str, path: str, range_header: str | None = None, **kwargs) ‑> Path`
    :   Exports a Google-NATIVE Workspace file (Docs, Sheets, Slides, Drawings --
        mimeType `application/vnd.google-apps.*`) to a specified format. Use this ONLY for
        those native types: exporting a binary file (PDF, image, uploaded .docx/.xlsx) returns
        403 `fileNotExportable` -- for those use the `files` `download` action instead. If unsure
        of a file's type, check its `mimeType` with `files.get` first.
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

    `download_text(self, file_id: str, mime_type: str, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Exports a Google-NATIVE Workspace file (Docs, Sheets, Slides, Drawings --
        mimeType `application/vnd.google-apps.*`) to a specified format. Use this ONLY for
        those native types: exporting a binary file (PDF, image, uploaded .docx/.xlsx) returns
        403 `fileNotExportable` -- for those use the `files` `download` action instead. If unsure
        of a file's type, check its `mimeType` with `files.get` first.
        Common export formats:
        - application/pdf (all types)
        - text/plain (Docs)
        - text/csv (Sheets)
        - application/vnd.openxmlformats-officedocument.wordprocessingml.document (Docs to .docx)
        - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (Sheets to .xlsx)
        - application/vnd.openxmlformats-officedocument.presentationml.presentation (Slides to .pptx)
        Note: Export has a 10MB limit. For larger files, use the Drive UI.
         and return a JSON-safe UTF-8 text chunk.

<a id="FilesQuery"></a>

`FilesQuery(connector: GoogleDriveConnector)`
:   Query class for Files entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: FilesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.google_drive.models.AirbyteSearchResult[FilesSearchData]`
    :   Search files records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (FilesSearchFilter):
        - id: Unique identifier of the file in Google Drive.
        - updated_at: Timestamp of the last modification to the file.
        - file_name: Name of the file.
        - file_path: Full path of the file within the synced Drive folder.
        - mime_type: MIME type of the file.
        - content: Extracted text content of the file.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            FilesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

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

    `download(self, file_id: str, alt: str | None = None, acknowledge_abuse: bool | None = None, supports_all_drives: bool | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads the raw binary content of a file (PDF, image, zip, uploaded .docx/.xlsx, etc.).
        The Drive `alt=media` query parameter is applied automatically by this action, so you
        normally do NOT need to pass `alt` -- the response is the file's bytes. (Without
        `alt=media` Drive returns file metadata JSON instead of content, so it is forced here.)
        This only works for binary files: for Google Workspace files (Docs, Sheets, Slides,
        Drawings) use the `files_export` action with a `mimeType` instead -- downloading them
        directly returns 403.
        
        
                Args:
                    file_id: The ID of the file to download
                    alt: Applied automatically as 'media' by this action; you do not need to set it.
                    acknowledge_abuse: Whether the user is acknowledging the risk of downloading known malware or other abusive files
                    supports_all_drives: Whether the requesting application supports both My Drives and shared drives
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_base64(self, file_id: str, alt: str | None = None, acknowledge_abuse: bool | None = None, supports_all_drives: bool | None = None, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Downloads the raw binary content of a file (PDF, image, zip, uploaded .docx/.xlsx, etc.).
        The Drive `alt=media` query parameter is applied automatically by this action, so you
        normally do NOT need to pass `alt` -- the response is the file's bytes. (Without
        `alt=media` Drive returns file metadata JSON instead of content, so it is forced here.)
        This only works for binary files: for Google Workspace files (Docs, Sheets, Slides,
        Drawings) use the `files_export` action with a `mimeType` instead -- downloading them
        directly returns 403.
         and return a JSON-safe base64 chunk.

    `download_local(self, file_id: str, path: str, alt: str | None = None, acknowledge_abuse: bool | None = None, supports_all_drives: bool | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads the raw binary content of a file (PDF, image, zip, uploaded .docx/.xlsx, etc.).
        The Drive `alt=media` query parameter is applied automatically by this action, so you
        normally do NOT need to pass `alt` -- the response is the file's bytes. (Without
        `alt=media` Drive returns file metadata JSON instead of content, so it is forced here.)
        This only works for binary files: for Google Workspace files (Docs, Sheets, Slides,
        Drawings) use the `files_export` action with a `mimeType` instead -- downloading them
        directly returns 403.
         and save to file.
        
                Args:
                    file_id: The ID of the file to download
                    alt: Applied automatically as 'media' by this action; you do not need to set it.
                    acknowledge_abuse: Whether the user is acknowledging the risk of downloading known malware or other abusive files
                    supports_all_drives: Whether the requesting application supports both My Drives and shared drives
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

    `download_text(self, file_id: str, alt: str | None = None, acknowledge_abuse: bool | None = None, supports_all_drives: bool | None = None, range_header: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Downloads the raw binary content of a file (PDF, image, zip, uploaded .docx/.xlsx, etc.).
        The Drive `alt=media` query parameter is applied automatically by this action, so you
        normally do NOT need to pass `alt` -- the response is the file's bytes. (Without
        `alt=media` Drive returns file metadata JSON instead of content, so it is forced here.)
        This only works for binary files: for Google Workspace files (Docs, Sheets, Slides,
        Drawings) use the `files_export` action with a `mimeType` instead -- downloading them
        directly returns 403.
         and return a JSON-safe UTF-8 text chunk.

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
            connector = GoogleDriveConnector(...)
        
            @GoogleDriveConnector.agent_tool()
            async def execute(entity: str, action: str, params: dict | None = None):
                return await connector.execute(entity=entity, action=action, params=params or \{\})
        
            @GoogleDriveConnector.agent_tool()
            async def inspect_connector():
                return await connector.inspect_connector()
        
            @GoogleDriveConnector.agent_tool()
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
        
        connector = GoogleDriveConnector()
        mcp = FastMCP("Connector Agent")
        
        @mcp.tool()
        @GoogleDriveConnector.tool_utils
        async def execute(entity: str, action: str, params: dict):
            ...
        ```
        
        Configure documentation, output limits, framework translation, and
        retries when needed:
        
        ```python
        @mcp.tool()
        @GoogleDriveConnector.tool_utils(update_docstring=False, max_output_chars=None)
        async def execute(entity: str, action: str, params: dict):
            ...
        
        @mcp.tool()
        @GoogleDriveConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'create', 'update', 'delete', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None, *, select_fields: list[str] | None = None, exclude_fields: list[str] | None = None, skip_truncation: bool = True) ‑> Any`
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