---
id: airbyte_agent_sdk-connectors-ashby-connector
title: airbyte_agent_sdk.connectors.ashby.connector
---

Module airbyte_agent_sdk.connectors.ashby.connector
===================================================
Ashby connector.

Classes
-------

<a id="ApplicationsQuery"></a>

`ApplicationsQuery(connector: AshbyConnector)`
:   Query class for Applications entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ApplicationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[ApplicationsSearchData]`
    :   Search applications records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ApplicationsSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ApplicationsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, application_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single application by ID
        
        Args:
            application_id: Application ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Application], ApplicationsListResultMeta]`
    :   Gets all applications in the organization
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            ApplicationsListResult

<a id="ArchiveReasonsQuery"></a>

`ArchiveReasonsQuery(connector: AshbyConnector)`
:   Query class for ArchiveReasons entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[ArchiveReason], ArchiveReasonsListResultMeta]`
    :   List all archive reasons
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            ArchiveReasonsListResult

<a id="AshbyConnector"></a>

`AshbyConnector(auth_config: AshbyAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Ashby API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new ashby connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., AshbyAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = AshbyConnector(auth_config=AshbyAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = AshbyConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = AshbyConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'AshbyAuthConfig'", name: str | None = None, replication_config: "'AshbyReplicationConfig' | None" = None, source_template_id: str | None = None)`
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
            A AshbyConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await AshbyConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AshbyAuthConfig(api_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await AshbyConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=AshbyAuthConfig(api_key="..."),
                replication_config=AshbyReplicationConfig(start_date="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @AshbyConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @AshbyConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await AshbyConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            AshbyCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="CandidateTagsQuery"></a>

`CandidateTagsQuery(connector: AshbyConnector)`
:   Query class for CandidateTags entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[CandidateTag], CandidateTagsListResultMeta]`
    :   List all candidate tags
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            CandidateTagsListResult

<a id="CandidatesQuery"></a>

`CandidatesQuery(connector: AshbyConnector)`
:   Query class for Candidates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CandidatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[CandidatesSearchData]`
    :   Search candidates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CandidatesSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CandidatesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single candidate by ID
        
        Args:
            id: Candidate ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta]`
    :   Lists all candidates in the organization
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            CandidatesListResult

<a id="CustomFieldsQuery"></a>

`CustomFieldsQuery(connector: AshbyConnector)`
:   Query class for CustomFields entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[CustomField], CustomFieldsListResultMeta]`
    :   List all custom fields
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            CustomFieldsListResult

<a id="DepartmentsQuery"></a>

`DepartmentsQuery(connector: AshbyConnector)`
:   Query class for Departments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, department_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single department by ID
        
        Args:
            department_id: Department ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Department], DepartmentsListResultMeta]`
    :   List all departments
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            DepartmentsListResult

<a id="FeedbackFormDefinitionsQuery"></a>

`FeedbackFormDefinitionsQuery(connector: AshbyConnector)`
:   Query class for FeedbackFormDefinitions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[FeedbackFormDefinition], FeedbackFormDefinitionsListResultMeta]`
    :   List all feedback form definitions
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            FeedbackFormDefinitionsListResult

<a id="JobPostingsQuery"></a>

`JobPostingsQuery(connector: AshbyConnector)`
:   Query class for JobPostings entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: JobPostingsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[JobPostingsSearchData]`
    :   Search job_postings records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (JobPostingsSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            JobPostingsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, job_posting_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single job posting by ID
        
        Args:
            job_posting_id: Job posting ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[JobPosting], JobPostingsListResultMeta]`
    :   List all job postings
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            JobPostingsListResult

<a id="JobsQuery"></a>

`JobsQuery(connector: AshbyConnector)`
:   Query class for Jobs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: JobsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[JobsSearchData]`
    :   Search jobs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (JobsSearchFilter):
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            JobsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single job by ID
        
        Args:
            id: Job ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Job], JobsListResultMeta]`
    :   List all open, closed, and archived jobs
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            JobsListResult

<a id="LocationsQuery"></a>

`LocationsQuery(connector: AshbyConnector)`
:   Query class for Locations entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, location_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single location by ID
        
        Args:
            location_id: Location ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Location], LocationsListResultMeta]`
    :   List all locations
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            LocationsListResult

<a id="SourcesQuery"></a>

`SourcesQuery(connector: AshbyConnector)`
:   Query class for Sources entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Source], SourcesListResultMeta]`
    :   List all candidate sources
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            SourcesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: AshbyConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        
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

    `get(self, user_id: str, **kwargs) ‑> dict[str, typing.Any]`
    :   Get a single user by ID
        
        Args:
            user_id: User ID
            **kwargs: Additional parameters
        
        Returns:
            dict[str, Any]

    `list(self, cursor: str | None = None, limit: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   List all users in the organization
        
        Args:
            cursor: Pagination cursor for next page
            limit: Maximum number of records to return per page
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult