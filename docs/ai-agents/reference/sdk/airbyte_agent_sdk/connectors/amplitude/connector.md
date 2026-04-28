---
id: airbyte_agent_sdk-connectors-amplitude-connector
title: airbyte_agent_sdk.connectors.amplitude.connector
---

Module airbyte_agent_sdk.connectors.amplitude.connector
=======================================================
Amplitude connector.

Classes
-------

<a id="ActiveUsersQuery"></a>

`ActiveUsersQuery(connector: AmplitudeConnector)`
:   Query class for ActiveUsers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ActiveUsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[ActiveUsersSearchData]`
    :   Search active_users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ActiveUsersSearchFilter):
        - date: The date for which the active user data is reported
        - statistics: The statistics related to the active users for the given date
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ActiveUsersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start: str, end: str, m: str | None = None, i: int | None = None, g: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[ActiveUsersData]`
    :   Returns the number of active or new users for each day in the specified date range.
        
        
        Args:
            start: First date included in data series, formatted YYYYMMDD (e.g. 20220101)
            end: Last date included in data series, formatted YYYYMMDD (e.g. 20220131)
            m: Either 'new' or 'active' to get the desired count. Defaults to 'active'.
            i: Either 1, 7, or 30 for daily, weekly, and monthly counts. Defaults to 1.
            g: The property to group by (e.g. country, city, platform).
            **kwargs: Additional parameters
        
        Returns:
            ActiveUsersListResult

<a id="AmplitudeConnector"></a>

`AmplitudeConnector(auth_config: AmplitudeAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Amplitude API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new amplitude connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., AmplitudeAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = AmplitudeConnector(auth_config=AmplitudeAuthConfig(api_key="...", secret_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = AmplitudeConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = AmplitudeConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AmplitudeAuthConfig'", name: str | None = None, replication_config: "'AmplitudeReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A AmplitudeConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AmplitudeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmplitudeAuthConfig(api_key="...", secret_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await AmplitudeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AmplitudeAuthConfig(api_key="...", secret_key="..."),
                replication_config=AmplitudeReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AmplitudeConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AmplitudeConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AmplitudeConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AmplitudeCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="AnnotationsQuery"></a>

`AnnotationsQuery(connector: AmplitudeConnector)`
:   Query class for Annotations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AnnotationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[AnnotationsSearchData]`
    :   Search annotations records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AnnotationsSearchFilter):
        - date: The date when the annotation was made
        - details: Additional details or information related to the annotation
        - id: The unique identifier for the annotation
        - label: The label assigned to the annotation
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AnnotationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, annotation_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.AnnotationV3`
    :   Retrieves a single chart annotation by ID.
        
        Args:
            annotation_id: The ID of the annotation to retrieve
            **kwargs: Additional parameters
        
        Returns:
            AnnotationV3

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[list[Annotation]]`
    :   Returns all chart annotations for the project.
        
        Returns:
            AnnotationsListResult

<a id="AverageSessionLengthQuery"></a>

`AverageSessionLengthQuery(connector: AmplitudeConnector)`
:   Query class for AverageSessionLength entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: AverageSessionLengthSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[AverageSessionLengthSearchData]`
    :   Search average_session_length records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (AverageSessionLengthSearchFilter):
        - date: The date on which the session occurred
        - length: The duration of the session in seconds
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            AverageSessionLengthSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, start: str, end: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[AverageSessionLengthData]`
    :   Returns the average session length (in seconds) for each day in the specified date range.
        
        
        Args:
            start: First date included in data series, formatted YYYYMMDD (e.g. 20220101)
            end: Last date included in data series, formatted YYYYMMDD (e.g. 20220131)
            **kwargs: Additional parameters
        
        Returns:
            AverageSessionLengthListResult

<a id="CohortsQuery"></a>

`CohortsQuery(connector: AmplitudeConnector)`
:   Query class for Cohorts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CohortsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[CohortsSearchData]`
    :   Search cohorts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CohortsSearchFilter):
        - app_id: The unique identifier of the application
        - archived: Indicates if the cohort data is archived
        - chart_id: The identifier of the chart associated with the cohort
        - created_at: The timestamp when the cohort was created
        - definition: The specific definition or criteria for the cohort
        - description: A brief explanation or summary of the cohort
        - edit_id: The ID for editing purposes or version control
        - finished: Indicates if the cohort data has been finalized
        - hidden: Flag to determine if the cohort is hidden from view
        - id: The unique identifier for the cohort
        - is_official_content: Indicates if the cohort data is official content
        - is_predictive: Flag to indicate if the cohort is predictive
        - last_computed: Timestamp of the last computation of cohort data
        - last_mod: Timestamp of the last modification made to the cohort
        - last_viewed: Timestamp when the cohort was last viewed
        - location_id: Identifier of the location associated with the cohort
        - metadata: Additional information or data related to the cohort
        - name: The name or title of the cohort
        - owners: The owners or administrators of the cohort
        - popularity: Popularity rank or score of the cohort
        - published: Status indicating if the cohort data is published
        - shortcut_ids: Identifiers of any shortcuts associated with the cohort
        - size: Size or scale of the cohort data
        - type_: The type or category of the cohort
        - view_count: The total count of views on the cohort data
        - viewers: Users or viewers who have access to the cohort data
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CohortsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, cohort_id: str, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.Cohort`
    :   Retrieves a single cohort by ID.
        
        Args:
            cohort_id: The ID of the cohort to retrieve
            **kwargs: Additional parameters
        
        Returns:
            Cohort

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[list[Cohort]]`
    :   Returns all cohorts for the project.
        
        Returns:
            CohortsListResult

<a id="EventsListQuery"></a>

`EventsListQuery(connector: AmplitudeConnector)`
:   Query class for EventsList entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: EventsListSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.amplitude.models.AirbyteSearchResult[EventsListSearchData]`
    :   Search events_list records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (EventsListSearchFilter):
        - autohidden: Whether the event is auto-hidden
        - clusters_hidden: Whether the event is hidden from clusters
        - deleted: Whether the event is deleted
        - display: Display name of the event
        - flow_hidden: Whether the event is hidden from Pathfinder
        - hidden: Whether the event is hidden
        - id: Unique identifier for the event type
        - in_waitroom: Whether the event is in the waitroom
        - name: Name of the event type
        - non_active: Whether the event is marked as inactive
        - timeline_hidden: Whether the event is hidden from the timeline
        - totals: Total number of times the event occurred this week
        - totals_delta: Change in totals from the previous period
        - value: Raw event name in the data
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            EventsListSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, **kwargs) ‑> airbyte_agent_sdk.connectors.amplitude.models.AmplitudeExecuteResult[list[EventType]]`
    :   Returns the list of event types with the current week's totals, unique users, and percentage of DAU.
        
        
        Returns:
            EventsListListResult