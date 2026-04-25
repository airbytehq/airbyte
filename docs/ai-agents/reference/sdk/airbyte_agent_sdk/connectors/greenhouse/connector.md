---
id: airbyte_agent_sdk-connectors-greenhouse-connector
title: airbyte_agent_sdk.connectors.greenhouse.connector
---

Module airbyte_agent_sdk.connectors.greenhouse.connector
========================================================
Greenhouse connector.

Classes
-------

<a id="ApplicationAttachmentQuery"></a>

`ApplicationAttachmentQuery(connector: GreenhouseConnector)`
:   Query class for ApplicationAttachment entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, attachment_index: str, id: str | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads an attachment (resume, cover letter, etc.) for an application by index.
        The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
        Files should be downloaded immediately after retrieval.
        
        
                Args:
                    id: Application ID
                    attachment_index: Index of the attachment to download (0-based)
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, attachment_index: str, path: str, id: str | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads an attachment (resume, cover letter, etc.) for an application by index.
        The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
        Files should be downloaded immediately after retrieval.
         and save to file.
        
                Args:
                    id: Application ID
                    attachment_index: Index of the attachment to download (0-based)
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

<a id="ApplicationsQuery"></a>

`ApplicationsQuery(connector: GreenhouseConnector)`
:   Query class for Applications entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: ApplicationsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[ApplicationsSearchData]`
    :   Search applications records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ApplicationsSearchFilter):
        - answers: Answers provided in the application.
        - applied_at: Timestamp when the candidate applied.
        - attachments: Attachments uploaded with the application.
        - candidate_id: Unique identifier for the candidate.
        - credited_to: Information about the employee who credited the application.
        - current_stage: Current stage of the application process.
        - id: Unique identifier for the application.
        - job_post_id: 
        - jobs: Jobs applied for by the candidate.
        - last_activity_at: Timestamp of the last activity on the application.
        - location: Location related to the application.
        - prospect: Status of the application prospect.
        - prospect_detail: Details related to the application prospect.
        - prospective_department: Prospective department for the candidate.
        - prospective_office: Prospective office for the candidate.
        - rejected_at: Timestamp when the application was rejected.
        - rejection_details: Details related to the application rejection.
        - rejection_reason: Reason for the application rejection.
        - source: Source of the application.
        - status: Status of the application.
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.Application`
    :   Get a single application by ID
        
        Args:
            id: Application ID
            **kwargs: Additional parameters
        
        Returns:
            Application

    `list(self, per_page: int | None = None, page: int | None = None, created_before: str | None = None, created_after: str | None = None, last_activity_after: str | None = None, job_id: int | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Application], ApplicationsListResultMeta]`
    :   Returns a paginated list of all applications
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            created_before: Filter by applications created before this timestamp
            created_after: Filter by applications created after this timestamp
            last_activity_after: Filter by applications with activity after this timestamp
            job_id: Filter by job ID
            status: Filter by application status
            **kwargs: Additional parameters
        
        Returns:
            ApplicationsListResult

<a id="CandidateAttachmentQuery"></a>

`CandidateAttachmentQuery(connector: GreenhouseConnector)`
:   Query class for CandidateAttachment entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `download(self, attachment_index: str, id: str | None = None, range_header: str | None = None, **kwargs) ‑> AsyncIterator[bytes]`
    :   Downloads an attachment (resume, cover letter, etc.) for a candidate by index.
        The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
        Files should be downloaded immediately after retrieval.
        
        
                Args:
                    id: Candidate ID
                    attachment_index: Index of the attachment to download (0-based)
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    **kwargs: Additional parameters
        
                Returns:
                    AsyncIterator[bytes]

    `download_local(self, attachment_index: str, path: str, id: str | None = None, range_header: str | None = None, **kwargs) ‑> Path`
    :   Downloads an attachment (resume, cover letter, etc.) for a candidate by index.
        The attachment URL is a temporary signed AWS S3 URL that expires within 7 days.
        Files should be downloaded immediately after retrieval.
         and save to file.
        
                Args:
                    id: Candidate ID
                    attachment_index: Index of the attachment to download (0-based)
                    range_header: Optional Range header for partial downloads (e.g., 'bytes=0-99')
                    path: File path to save downloaded content
                    **kwargs: Additional parameters
        
                Returns:
                    str: Path to the downloaded file

<a id="CandidatesQuery"></a>

`CandidatesQuery(connector: GreenhouseConnector)`
:   Query class for Candidates entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: CandidatesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[CandidatesSearchData]`
    :   Search candidates records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CandidatesSearchFilter):
        - addresses: Candidate's addresses
        - application_ids: List of application IDs
        - applications: An array of all applications made by candidates.
        - attachments: Attachments related to the candidate
        - can_email: Indicates if candidate can be emailed
        - company: Company where the candidate is associated
        - coordinator: Coordinator assigned to the candidate
        - created_at: Date and time of creation
        - custom_fields: Custom fields associated with the candidate
        - educations: List of candidate's educations
        - email_addresses: Candidate's email addresses
        - employments: List of candidate's employments
        - first_name: Candidate's first name
        - id: Candidate's ID
        - is_private: Indicates if the candidate's data is private
        - keyed_custom_fields: Keyed custom fields associated with the candidate
        - last_activity: Details of the last activity related to the candidate
        - last_name: Candidate's last name
        - phone_numbers: Candidate's phone numbers
        - photo_url: URL of the candidate's profile photo
        - recruiter: Recruiter assigned to the candidate
        - social_media_addresses: Candidate's social media addresses
        - tags: Tags associated with the candidate
        - title: Candidate's title (e.g., Mr., Mrs., Dr.)
        - updated_at: Date and time of last update
        - website_addresses: List of candidate's website addresses
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.Candidate`
    :   Get a single candidate by ID
        
        Args:
            id: Candidate ID
            **kwargs: Additional parameters
        
        Returns:
            Candidate

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta]`
    :   Returns a paginated list of all candidates in the organization
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            **kwargs: Additional parameters
        
        Returns:
            CandidatesListResult

<a id="DepartmentsQuery"></a>

`DepartmentsQuery(connector: GreenhouseConnector)`
:   Query class for Departments entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: DepartmentsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[DepartmentsSearchData]`
    :   Search departments records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (DepartmentsSearchFilter):
        - child_department_external_ids: External IDs of child departments associated with this department.
        - child_ids: Unique IDs of child departments associated with this department.
        - external_id: External ID of this department.
        - id: Unique ID of this department.
        - name: Name of the department.
        - parent_department_external_id: External ID of the parent department of this department.
        - parent_id: Unique ID of the parent department of this department.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            DepartmentsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.Department`
    :   Get a single department by ID
        
        Args:
            id: Department ID
            **kwargs: Additional parameters
        
        Returns:
            Department

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Department], DepartmentsListResultMeta]`
    :   Returns a paginated list of all departments
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            **kwargs: Additional parameters
        
        Returns:
            DepartmentsListResult

<a id="GreenhouseConnector"></a>

`GreenhouseConnector(auth_config: GreenhouseAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Greenhouse API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new greenhouse connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GreenhouseAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GreenhouseConnector(auth_config=GreenhouseAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GreenhouseConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GreenhouseConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'GreenhouseAuthConfig'", name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.connector.GreenhouseConnector`
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
            A GreenhouseConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await GreenhouseConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=GreenhouseAuthConfig(api_key="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @GreenhouseConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GreenhouseConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await GreenhouseConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GreenhouseCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

<a id="JobPostsQuery"></a>

`JobPostsQuery(connector: GreenhouseConnector)`
:   Query class for JobPosts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: JobPostsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[JobPostsSearchData]`
    :   Search job_posts records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (JobPostsSearchFilter):
        - active: Flag indicating if the job post is active or not.
        - content: Content or description of the job post.
        - created_at: Date and time when the job post was created.
        - demographic_question_set_id: ID of the demographic question set associated with the job post.
        - external: Flag indicating if the job post is external or not.
        - first_published_at: Date and time when the job post was first published.
        - id: Unique identifier of the job post.
        - internal: Flag indicating if the job post is internal or not.
        - internal_content: Internal content or description of the job post.
        - job_id: ID of the job associated with the job post.
        - live: Flag indicating if the job post is live or not.
        - location: Details about the job post location.
        - questions: List of questions related to the job post.
        - title: Title or headline of the job post.
        - updated_at: Date and time when the job post was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            JobPostsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.JobPost`
    :   Get a single job post by ID
        
        Args:
            id: Job Post ID
            **kwargs: Additional parameters
        
        Returns:
            JobPost

    `list(self, per_page: int | None = None, page: int | None = None, live: bool | None = None, active: bool | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[JobPost], JobPostsListResultMeta]`
    :   Returns a paginated list of all job posts
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            live: Filter by live status
            active: Filter by active status
            **kwargs: Additional parameters
        
        Returns:
            JobPostsListResult

<a id="JobsQuery"></a>

`JobsQuery(connector: GreenhouseConnector)`
:   Query class for Jobs entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: JobsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[JobsSearchData]`
    :   Search jobs records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (JobsSearchFilter):
        - closed_at: The date and time the job was closed
        - confidential: Indicates if the job details are confidential
        - copied_from_id: The ID of the job from which this job was copied
        - created_at: The date and time the job was created
        - custom_fields: Custom fields related to the job
        - departments: Departments associated with the job
        - hiring_team: Members of the hiring team for the job
        - id: Unique ID of the job
        - is_template: Indicates if the job is a template
        - keyed_custom_fields: Keyed custom fields related to the job
        - name: Name of the job
        - notes: Additional notes or comments about the job
        - offices: Offices associated with the job
        - opened_at: The date and time the job was opened
        - openings: Openings associated with the job
        - requisition_id: ID associated with the job requisition
        - status: Current status of the job
        - updated_at: The date and time the job was last updated
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.Job`
    :   Get a single job by ID
        
        Args:
            id: Job ID
            **kwargs: Additional parameters
        
        Returns:
            Job

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Job], JobsListResultMeta]`
    :   Returns a paginated list of all jobs in the organization
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            **kwargs: Additional parameters
        
        Returns:
            JobsListResult

<a id="OffersQuery"></a>

`OffersQuery(connector: GreenhouseConnector)`
:   Query class for Offers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OffersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[OffersSearchData]`
    :   Search offers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OffersSearchFilter):
        - application_id: Unique identifier for the application associated with the offer
        - candidate_id: Unique identifier for the candidate associated with the offer
        - created_at: Timestamp indicating when the offer was created
        - custom_fields: Additional custom fields related to the offer
        - id: Unique identifier for the offer
        - job_id: Unique identifier for the job associated with the offer
        - keyed_custom_fields: Keyed custom fields associated with the offer
        - opening: Details about the job opening
        - resolved_at: Timestamp indicating when the offer was resolved
        - sent_at: Timestamp indicating when the offer was sent
        - starts_at: Timestamp indicating when the offer starts
        - status: Status of the offer
        - updated_at: Timestamp indicating when the offer was last updated
        - version: Version of the offer data
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OffersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.Offer`
    :   Get a single offer by ID
        
        Args:
            id: Offer ID
            **kwargs: Additional parameters
        
        Returns:
            Offer

    `list(self, per_page: int | None = None, page: int | None = None, created_before: str | None = None, created_after: str | None = None, resolved_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Offer], OffersListResultMeta]`
    :   Returns a paginated list of all offers
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            created_before: Filter by offers created before this timestamp
            created_after: Filter by offers created after this timestamp
            resolved_after: Filter by offers resolved after this timestamp
            **kwargs: Additional parameters
        
        Returns:
            OffersListResult

<a id="OfficesQuery"></a>

`OfficesQuery(connector: GreenhouseConnector)`
:   Query class for Offices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: OfficesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[OfficesSearchData]`
    :   Search offices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (OfficesSearchFilter):
        - child_ids: IDs of child offices associated with this office
        - child_office_external_ids: External IDs of child offices associated with this office
        - external_id: Unique identifier for this office in the external system
        - id: Unique identifier for this office in the API system
        - location: Location details of this office
        - name: Name of the office
        - parent_id: ID of the parent office, if this office is a branch office
        - parent_office_external_id: External ID of the parent office in the external system
        - primary_contact_user_id: User ID of the primary contact person for this office
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            OfficesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.Office`
    :   Get a single office by ID
        
        Args:
            id: Office ID
            **kwargs: Additional parameters
        
        Returns:
            Office

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Office], OfficesListResultMeta]`
    :   Returns a paginated list of all offices
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            **kwargs: Additional parameters
        
        Returns:
            OfficesListResult

<a id="ScheduledInterviewsQuery"></a>

`ScheduledInterviewsQuery(connector: GreenhouseConnector)`
:   Query class for ScheduledInterviews entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.ScheduledInterview`
    :   Get a single scheduled interview by ID
        
        Args:
            id: Scheduled Interview ID
            **kwargs: Additional parameters
        
        Returns:
            ScheduledInterview

    `list(self, per_page: int | None = None, page: int | None = None, created_before: str | None = None, created_after: str | None = None, updated_before: str | None = None, updated_after: str | None = None, starts_after: str | None = None, ends_before: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[ScheduledInterview], ScheduledInterviewsListResultMeta]`
    :   Returns a paginated list of all scheduled interviews
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            created_before: Filter by interviews created before this timestamp
            created_after: Filter by interviews created after this timestamp
            updated_before: Filter by interviews updated before this timestamp
            updated_after: Filter by interviews updated after this timestamp
            starts_after: Filter by interviews starting after this timestamp
            ends_before: Filter by interviews ending before this timestamp
            **kwargs: Additional parameters
        
        Returns:
            ScheduledInterviewsListResult

<a id="SourcesQuery"></a>

`SourcesQuery(connector: GreenhouseConnector)`
:   Query class for Sources entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: SourcesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[SourcesSearchData]`
    :   Search sources records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SourcesSearchFilter):
        - id: The unique identifier for the source.
        - name: The name of the source.
        - type_: Type of the data source
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SourcesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `list(self, per_page: int | None = None, page: int | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Source], SourcesListResultMeta]`
    :   Returns a paginated list of all sources
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            **kwargs: Additional parameters
        
        Returns:
            SourcesListResult

<a id="UsersQuery"></a>

`UsersQuery(connector: GreenhouseConnector)`
:   Query class for Users entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: UsersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[UsersSearchData]`
    :   Search users records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (UsersSearchFilter):
        - created_at: The date and time when the user account was created.
        - departments: List of departments associated with users
        - disabled: Indicates whether the user account is disabled.
        - emails: Email addresses of the users
        - employee_id: Employee identifier for the user.
        - first_name: The first name of the user.
        - id: Unique identifier for the user.
        - last_name: The last name of the user.
        - linked_candidate_ids: IDs of candidates linked to the user.
        - name: The full name of the user.
        - offices: List of office locations where users are based
        - primary_email_address: The primary email address of the user.
        - site_admin: Indicates whether the user is a site administrator.
        - updated_at: The date and time when the user account was last updated.
        
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

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.User`
    :   Get a single user by ID
        
        Args:
            id: User ID
            **kwargs: Additional parameters
        
        Returns:
            User

    `list(self, per_page: int | None = None, page: int | None = None, created_before: str | None = None, created_after: str | None = None, updated_before: str | None = None, updated_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[User], UsersListResultMeta]`
    :   Returns a paginated list of all users
        
        Args:
            per_page: Number of items to return per page (max 500)
            page: Page number for pagination
            created_before: Filter by users created before this timestamp
            created_after: Filter by users created after this timestamp
            updated_before: Filter by users updated before this timestamp
            updated_after: Filter by users updated after this timestamp
            **kwargs: Additional parameters
        
        Returns:
            UsersListResult