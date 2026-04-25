---
id: airbyte_agent_sdk-connectors-gong-connector
title: airbyte_agent_sdk.connectors.gong.connector
---

Module airbyte_agent_sdk.connectors.gong.connector
==================================================
Gong connector.

Classes
-------

<a id="CallAudioQuery"></a>

`CallAudioQuery(connector: GongConnector)`
:   Query class for CallAudio entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, filter: CallAudioDownloadParamsFilter | None = None, content_selector: CallAudioDownloadParamsContentselector | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   ALWAYS configure the request with the exposedFields: \{"media": true\}. If you don't the call won't work.
        Downloads the audio media file for a call. Temporarily, the request body must be configured with:
        \{"filter": \{"callIds": [CALL_ID]\}, "contentSelector": \{"exposedFields": \{"media": true\}\}\}
        
        
                Args:
                    filter: Parameter filter
                    content_selector: Parameter contentSelector
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, path: str, filter: CallAudioDownloadParamsFilter | None = None, content_selector: CallAudioDownloadParamsContentselector | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   ALWAYS configure the request with the exposedFields: \{"media": true\}. If you don't the call won't work.
        Downloads the audio media file for a call. Temporarily, the request body must be configured with:
        \{"filter": \{"callIds": [CALL_ID]\}, "contentSelector": \{"exposedFields": \{"media": true\}\}\}
         and save to file.
        
                Args:
                    filter: Parameter filter
                    content_selector: Parameter contentSelector
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

<a id="CallTranscriptsQuery"></a>

`CallTranscriptsQuery(connector: GongConnector)`
:   Query class for CallTranscripts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, filter: CallTranscriptsListParamsFilter, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[CallTranscript], CallTranscriptsListResultMeta]`
    :   Returns transcripts for calls in a specified date range or specific call IDs
        
        Args:
            filter: Parameter filter
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CallTranscriptsListResult

<a id="CallVideoQuery"></a>

`CallVideoQuery(connector: GongConnector)`
:   Query class for CallVideo entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, filter: CallVideoDownloadParamsFilter | None = None, content_selector: CallVideoDownloadParamsContentselector | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   ALWAYS configure the request with the exposedFields: \{"media": true\}. If you don't the call won't work.
        Downloads the video media file for a call. Temporarily, the request body must be configured with:
        \{"filter": \{"callIds": [CALL_ID]\}, "contentSelector": \{"exposedFields": \{"media": true\}\}\}
        
        
                Args:
                    filter: Parameter filter
                    content_selector: Parameter contentSelector
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, path: str, filter: CallVideoDownloadParamsFilter | None = None, content_selector: CallVideoDownloadParamsContentselector | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   ALWAYS configure the request with the exposedFields: \{"media": true\}. If you don't the call won't work.
        Downloads the video media file for a call. Temporarily, the request body must be configured with:
        \{"filter": \{"callIds": [CALL_ID]\}, "contentSelector": \{"exposedFields": \{"media": true\}\}\}
         and save to file.
        
                Args:
                    filter: Parameter filter
                    content_selector: Parameter contentSelector
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

<a id="CallsExtensiveQuery"></a>

`CallsExtensiveQuery(connector: GongConnector)`
:   Query class for CallsExtensive entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallsExtensiveSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[CallsExtensiveSearchData]`
    :   Search calls_extensive records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallsExtensiveSearchFilter):
        - id: Unique identifier for the call (from metaData.id).
        - startdatetime: Datetime for extensive calls.
        - collaboration: Collaboration information added to the call
        - content: Analysis of the interaction content.
        - context: A list of the agenda of each part of the call.
        - interaction: Metrics collected around the interaction during the call.
        - media: The media urls of the call.
        - meta_data: call's metadata.
        - parties: A list of the call's participants
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallsExtensiveSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, filter: CallsExtensiveListParamsFilter, content_selector: CallsExtensiveListParamsContentselector | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[ExtensiveCall], CallsExtensiveListResultMeta]`
    :   Retrieve detailed call data including participants, interaction stats, and content
        
        Args:
            filter: Parameter filter
            content_selector: Select which content to include in the response
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CallsExtensiveListResult

<a id="CallsQuery"></a>

`CallsQuery(connector: GongConnector)`
:   Query class for Calls entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CallsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[CallsSearchData]`
    :   Search calls records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CallsSearchFilter):
        - calendar_event_id: Unique identifier for the calendar event associated with the call.
        - client_unique_id: Unique identifier for the client related to the call.
        - custom_data: Custom data associated with the call.
        - direction: Direction of the call (inbound/outbound).
        - duration: Duration of the call in seconds.
        - id: Unique identifier for the call.
        - is_private: Indicates if the call is private or not.
        - language: Language used in the call.
        - media: Media type used for communication (voice, video, etc.).
        - meeting_url: URL for accessing the meeting associated with the call.
        - primary_user_id: Unique identifier for the primary user involved in the call.
        - purpose: Purpose or topic of the call.
        - scheduled: Scheduled date and time of the call.
        - scope: Scope or extent of the call.
        - sdr_disposition: Disposition set by the sales development representative.
        - started: Start date and time of the call.
        - system: System information related to the call.
        - title: Title or headline of the call.
        - url: URL associated with the call.
        - workspace_id: Identifier for the workspace to which the call belongs.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CallsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.Call`
    :   Get specific call data by ID
        
        Args:
            id: Call ID
            **kwargs: Additional parameters
        
        Returns:
            Call

    `list(self, from_date_time: str | None = None, to_date_time: str | None = None, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[Call], CallsListResultMeta]`
    :   Retrieve calls data by date range
        
        Args:
            from_date_time: Start date in ISO 8601 format
            to_date_time: End date in ISO 8601 format
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            CallsListResult

<a id="CoachingQuery"></a>

`CoachingQuery(connector: GongConnector)`
:   Query class for Coaching entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_id: str, manager_id: str, from_: str, to: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[CoachingData]]`
    :   Retrieve coaching metrics for a manager and their direct reports
        
        Args:
            workspace_id: Workspace ID
            manager_id: Manager user ID
            from_: Start date in ISO 8601 format
            to: End date in ISO 8601 format
            **kwargs: Additional parameters
        
        Returns:
            CoachingListResult

<a id="GongConnector"></a>

`GongConnector(auth_config: GongAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Gong API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new gong connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GongAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GongConnector(auth_config=GongAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GongConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GongAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
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
            A GongConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GongConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GongAuthConfig(access_token="...", refresh_token="...", client_id="...", client_secret="..."),
            )
        
            # With server-side OAuth:
            connector = await GongConnector.create(
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
            consent_url = await GongConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Gong Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GongConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GongConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GongConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.gong.models.GongCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GongCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'download', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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

<a id="LibraryFolderContentQuery"></a>

`LibraryFolderContentQuery(connector: GongConnector)`
:   Query class for LibraryFolderContent entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, folder_id: str, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[FolderCall], LibraryFolderContentListResultMeta]`
    :   Retrieve calls in a specific library folder
        
        Args:
            folder_id: Folder ID to retrieve content from
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            LibraryFolderContentListResult

<a id="LibraryFoldersQuery"></a>

`LibraryFoldersQuery(connector: GongConnector)`
:   Query class for LibraryFolders entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[LibraryFolder]]`
    :   Retrieve the folder structure of the call library
        
        Args:
            workspace_id: Workspace ID to retrieve folders from
            **kwargs: Additional parameters
        
        Returns:
            LibraryFoldersListResult

<a id="SettingsScorecardsQuery"></a>

`SettingsScorecardsQuery(connector: GongConnector)`
:   Query class for SettingsScorecards entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SettingsScorecardsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[SettingsScorecardsSearchData]`
    :   Search settings_scorecards records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SettingsScorecardsSearchFilter):
        - created: The timestamp when the scorecard was created
        - enabled: Indicates if the scorecard is enabled or disabled
        - questions: An array of questions related to the scorecard
        - scorecard_id: The unique identifier of the scorecard
        - scorecard_name: The name of the scorecard
        - updated: The timestamp when the scorecard was last updated
        - updater_user_id: The user ID of the person who last updated the scorecard
        - workspace_id: The unique identifier of the workspace associated with the scorecard
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SettingsScorecardsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, workspace_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[Scorecard]]`
    :   Retrieve all scorecard configurations in the company
        
        Args:
            workspace_id: Filter scorecards by workspace ID
            **kwargs: Additional parameters
        
        Returns:
            SettingsScorecardsListResult

<a id="SettingsTrackersQuery"></a>

`SettingsTrackersQuery(connector: GongConnector)`
:   Query class for SettingsTrackers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, workspace_id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[Tracker]]`
    :   Retrieve all keyword tracker configurations in the company
        
        Args:
            workspace_id: Filter trackers by workspace ID
            **kwargs: Additional parameters
        
        Returns:
            SettingsTrackersListResult

<a id="StatsActivityAggregateQuery"></a>

`StatsActivityAggregateQuery(connector: GongConnector)`
:   Query class for StatsActivityAggregate entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, filter: StatsActivityAggregateListParamsFilter, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[UserAggregateActivity], StatsActivityAggregateListResultMeta]`
    :   Provides aggregated user activity metrics across a specified period
        
        Args:
            filter: Parameter filter
            **kwargs: Additional parameters
        
        Returns:
            StatsActivityAggregateListResult

<a id="StatsActivityDayByDayQuery"></a>

`StatsActivityDayByDayQuery(connector: GongConnector)`
:   Query class for StatsActivityDayByDay entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, filter: StatsActivityDayByDayListParamsFilter, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[UserDetailedActivity], StatsActivityDayByDayListResultMeta]`
    :   Delivers daily user activity metrics across a specified date range
        
        Args:
            filter: Parameter filter
            **kwargs: Additional parameters
        
        Returns:
            StatsActivityDayByDayListResult

<a id="StatsActivityScorecardsQuery"></a>

`StatsActivityScorecardsQuery(connector: GongConnector)`
:   Query class for StatsActivityScorecards entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: StatsActivityScorecardsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[StatsActivityScorecardsSearchData]`
    :   Search stats_activity_scorecards records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (StatsActivityScorecardsSearchFilter):
        - answered_scorecard_id: Unique identifier for the answered scorecard instance.
        - answers: Contains the answered questions in the scorecards
        - call_id: Unique identifier for the call associated with the answered scorecard.
        - call_start_time: Timestamp indicating the start time of the call.
        - review_time: Timestamp indicating when the review of the answered scorecard was completed.
        - reviewed_user_id: Unique identifier for the user whose performance was reviewed.
        - reviewer_user_id: Unique identifier for the user who performed the review.
        - scorecard_id: Unique identifier for the scorecard template used.
        - scorecard_name: Name or title of the scorecard template used.
        - visibility_type: Type indicating the visibility permissions for the answered scorecard.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            StatsActivityScorecardsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, filter: StatsActivityScorecardsListParamsFilter, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[AnsweredScorecard], StatsActivityScorecardsListResultMeta]`
    :   Retrieve answered scorecards for applicable reviewed users or scorecards for a date range
        
        Args:
            filter: Parameter filter
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            StatsActivityScorecardsListResult

<a id="StatsInteractionQuery"></a>

`StatsInteractionQuery(connector: GongConnector)`
:   Query class for StatsInteraction entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, filter: StatsInteractionListParamsFilter, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[UserInteractionStats], StatsInteractionListResultMeta]`
    :   Returns interaction stats for users based on calls that have Whisper turned on
        
        Args:
            filter: Parameter filter
            **kwargs: Additional parameters
        
        Returns:
            StatsInteractionListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: GongConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.gong.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - active: Indicates if the user is currently active or not
        - created: The timestamp denoting when the user account was created
        - email_address: The primary email address associated with the user
        - email_aliases: Additional email addresses that can be used to reach the user
        - extension: The phone extension number for the user
        - first_name: The first name of the user
        - id: Unique identifier for the user
        - last_name: The last name of the user
        - manager_id: The ID of the user's manager
        - meeting_consent_page_url: URL for the consent page related to meetings
        - personal_meeting_urls: URLs for personal meeting rooms assigned to the user
        - phone_number: The phone number associated with the user
        - settings: User-specific settings and configurations
        - spoken_languages: Languages spoken by the user
        - title: The job title or position of the user
        - trusted_email_address: An email address that is considered trusted for the user
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.User`
    :   Get a single user by ID
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, cursor: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a list of all users in the Gong account
        
        Args:
            cursor: Cursor for pagination
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult

<a id="WorkspacesQuery"></a>

`WorkspacesQuery(connector: GongConnector)`
:   Query class for Workspaces entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.gong.models.GongExecuteResult[list[Workspace]]`
    :   List all company workspaces
        
        Returns:
            WorkspacesListResult