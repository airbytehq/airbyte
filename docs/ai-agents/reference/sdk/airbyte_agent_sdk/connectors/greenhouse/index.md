---
id: airbyte_agent_sdk-connectors-greenhouse-index
title: airbyte_agent_sdk.connectors.greenhouse.index
---

Module airbyte_agent_sdk.connectors.greenhouse
==============================================
Greenhouse connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.greenhouse.connector
* airbyte_agent_sdk.connectors.greenhouse.connector_model
* airbyte_agent_sdk.connectors.greenhouse.models
* airbyte_agent_sdk.connectors.greenhouse.types

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

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[ApplicationsSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[CandidatesSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[DepartmentsSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[JobPostsSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[JobsSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[OffersSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[OfficesSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[SourcesSearchData]
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="ApplicationsSearchResult"></a>

`ApplicationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CandidatesSearchResult"></a>

`CandidatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="JobPostsSearchResult"></a>

`JobPostsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="JobsSearchResult"></a>

`JobsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OffersSearchResult"></a>

`OffersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OfficesSearchResult"></a>

`OfficesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SourcesSearchResult"></a>

`SourcesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ApplicationsSearchData"></a>

`ApplicationsSearchData(**data: Any)`
:   Search result data for applications entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answers: list[typing.Any] | None`
    :   Answers provided in the application.

    `applied_at: str | None`
    :   Timestamp when the candidate applied.

    `attachments: list[typing.Any] | None`
    :   Attachments uploaded with the application.

    `candidate_id: int | None`
    :   Unique identifier for the candidate.

    `credited_to: dict[str, typing.Any] | None`
    :   Information about the employee who credited the application.

    `current_stage: dict[str, typing.Any] | None`
    :   Current stage of the application process.

    `id: int | None`
    :   Unique identifier for the application.

    `job_post_id: int | None`
    :   The type of the None singleton.

    `jobs: list[typing.Any] | None`
    :   Jobs applied for by the candidate.

    `last_activity_at: str | None`
    :   Timestamp of the last activity on the application.

    `location: str | None`
    :   Location related to the application.

    `model_config`
    :   The type of the None singleton.

    `prospect: bool | None`
    :   Status of the application prospect.

    `prospect_detail: dict[str, typing.Any] | None`
    :   Details related to the application prospect.

    `prospective_department: str | None`
    :   Prospective department for the candidate.

    `prospective_office: str | None`
    :   Prospective office for the candidate.

    `rejected_at: str | None`
    :   Timestamp when the application was rejected.

    `rejection_details: dict[str, typing.Any] | None`
    :   Details related to the application rejection.

    `rejection_reason: dict[str, typing.Any] | None`
    :   Reason for the application rejection.

    `source: dict[str, typing.Any] | None`
    :   Source of the application.

    `status: str | None`
    :   Status of the application.

<a id="CandidatesSearchData"></a>

`CandidatesSearchData(**data: Any)`
:   Search result data for candidates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[typing.Any] | None`
    :   Candidate's addresses

    `application_ids: list[typing.Any] | None`
    :   List of application IDs

    `applications: list[typing.Any] | None`
    :   An array of all applications made by candidates.

    `attachments: list[typing.Any] | None`
    :   Attachments related to the candidate

    `can_email: bool | None`
    :   Indicates if candidate can be emailed

    `company: str | None`
    :   Company where the candidate is associated

    `coordinator: str | None`
    :   Coordinator assigned to the candidate

    `created_at: str | None`
    :   Date and time of creation

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the candidate

    `educations: list[typing.Any] | None`
    :   List of candidate's educations

    `email_addresses: list[typing.Any] | None`
    :   Candidate's email addresses

    `employments: list[typing.Any] | None`
    :   List of candidate's employments

    `first_name: str | None`
    :   Candidate's first name

    `id: int | None`
    :   Candidate's ID

    `is_private: bool | None`
    :   Indicates if the candidate's data is private

    `keyed_custom_fields: dict[str, typing.Any] | None`
    :   Keyed custom fields associated with the candidate

    `last_activity: str | None`
    :   Details of the last activity related to the candidate

    `last_name: str | None`
    :   Candidate's last name

    `model_config`
    :   The type of the None singleton.

    `phone_numbers: list[typing.Any] | None`
    :   Candidate's phone numbers

    `photo_url: str | None`
    :   URL of the candidate's profile photo

    `recruiter: str | None`
    :   Recruiter assigned to the candidate

    `social_media_addresses: list[typing.Any] | None`
    :   Candidate's social media addresses

    `tags: list[typing.Any] | None`
    :   Tags associated with the candidate

    `title: str | None`
    :   Candidate's title (e.g., Mr., Mrs., Dr.)

    `updated_at: str | None`
    :   Date and time of last update

    `website_addresses: list[typing.Any] | None`
    :   List of candidate's website addresses

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

    `child_department_external_ids: list[typing.Any] | None`
    :   External IDs of child departments associated with this department.

    `child_ids: list[typing.Any] | None`
    :   Unique IDs of child departments associated with this department.

    `external_id: str | None`
    :   External ID of this department.

    `id: int | None`
    :   Unique ID of this department.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the department.

    `parent_department_external_id: str | None`
    :   External ID of the parent department of this department.

    `parent_id: int | None`
    :   Unique ID of the parent department of this department.

<a id="GreenhouseAuthConfig"></a>

`GreenhouseAuthConfig(**data: Any)`
:   Harvest API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Greenhouse Harvest API Key from the Dev Center

    `model_config`
    :   The type of the None singleton.

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

<a id="JobPostsSearchData"></a>

`JobPostsSearchData(**data: Any)`
:   Search result data for job_posts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Flag indicating if the job post is active or not.

    `content: str | None`
    :   Content or description of the job post.

    `created_at: str | None`
    :   Date and time when the job post was created.

    `demographic_question_set_id: int | None`
    :   ID of the demographic question set associated with the job post.

    `external: bool | None`
    :   Flag indicating if the job post is external or not.

    `first_published_at: str | None`
    :   Date and time when the job post was first published.

    `id: int | None`
    :   Unique identifier of the job post.

    `internal: bool | None`
    :   Flag indicating if the job post is internal or not.

    `internal_content: str | None`
    :   Internal content or description of the job post.

    `job_id: int | None`
    :   ID of the job associated with the job post.

    `live: bool | None`
    :   Flag indicating if the job post is live or not.

    `location: dict[str, typing.Any] | None`
    :   Details about the job post location.

    `model_config`
    :   The type of the None singleton.

    `questions: list[typing.Any] | None`
    :   List of questions related to the job post.

    `title: str | None`
    :   Title or headline of the job post.

    `updated_at: str | None`
    :   Date and time when the job post was last updated.

<a id="JobsSearchData"></a>

`JobsSearchData(**data: Any)`
:   Search result data for jobs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `closed_at: str | None`
    :   The date and time the job was closed

    `confidential: bool | None`
    :   Indicates if the job details are confidential

    `copied_from_id: int | None`
    :   The ID of the job from which this job was copied

    `created_at: str | None`
    :   The date and time the job was created

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields related to the job

    `departments: list[typing.Any] | None`
    :   Departments associated with the job

    `hiring_team: dict[str, typing.Any] | None`
    :   Members of the hiring team for the job

    `id: int | None`
    :   Unique ID of the job

    `is_template: bool | None`
    :   Indicates if the job is a template

    `keyed_custom_fields: dict[str, typing.Any] | None`
    :   Keyed custom fields related to the job

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the job

    `notes: str | None`
    :   Additional notes or comments about the job

    `offices: list[typing.Any] | None`
    :   Offices associated with the job

    `opened_at: str | None`
    :   The date and time the job was opened

    `openings: list[typing.Any] | None`
    :   Openings associated with the job

    `requisition_id: str | None`
    :   ID associated with the job requisition

    `status: str | None`
    :   Current status of the job

    `updated_at: str | None`
    :   The date and time the job was last updated

<a id="OffersSearchData"></a>

`OffersSearchData(**data: Any)`
:   Search result data for offers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_id: int | None`
    :   Unique identifier for the application associated with the offer

    `candidate_id: int | None`
    :   Unique identifier for the candidate associated with the offer

    `created_at: str | None`
    :   Timestamp indicating when the offer was created

    `custom_fields: dict[str, typing.Any] | None`
    :   Additional custom fields related to the offer

    `id: int | None`
    :   Unique identifier for the offer

    `job_id: int | None`
    :   Unique identifier for the job associated with the offer

    `keyed_custom_fields: dict[str, typing.Any] | None`
    :   Keyed custom fields associated with the offer

    `model_config`
    :   The type of the None singleton.

    `opening: dict[str, typing.Any] | None`
    :   Details about the job opening

    `resolved_at: str | None`
    :   Timestamp indicating when the offer was resolved

    `sent_at: str | None`
    :   Timestamp indicating when the offer was sent

    `starts_at: str | None`
    :   Timestamp indicating when the offer starts

    `status: str | None`
    :   Status of the offer

    `updated_at: str | None`
    :   Timestamp indicating when the offer was last updated

    `version: int | None`
    :   Version of the offer data

<a id="OfficesSearchData"></a>

`OfficesSearchData(**data: Any)`
:   Search result data for offices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `child_ids: list[typing.Any] | None`
    :   IDs of child offices associated with this office

    `child_office_external_ids: list[typing.Any] | None`
    :   External IDs of child offices associated with this office

    `external_id: str | None`
    :   Unique identifier for this office in the external system

    `id: int | None`
    :   Unique identifier for this office in the API system

    `location: dict[str, typing.Any] | None`
    :   Location details of this office

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the office

    `parent_id: int | None`
    :   ID of the parent office, if this office is a branch office

    `parent_office_external_id: str | None`
    :   External ID of the parent office in the external system

    `primary_contact_user_id: int | None`
    :   User ID of the primary contact person for this office

<a id="SourcesSearchData"></a>

`SourcesSearchData(**data: Any)`
:   Search result data for sources entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   The unique identifier for the source.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the source.

    `type_: dict[str, typing.Any] | None`
    :   Type of the data source

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The date and time when the user account was created.

    `departments: list[typing.Any] | None`
    :   List of departments associated with users

    `disabled: bool | None`
    :   Indicates whether the user account is disabled.

    `emails: list[typing.Any] | None`
    :   Email addresses of the users

    `employee_id: str | None`
    :   Employee identifier for the user.

    `first_name: str | None`
    :   The first name of the user.

    `id: int | None`
    :   Unique identifier for the user.

    `last_name: str | None`
    :   The last name of the user.

    `linked_candidate_ids: list[typing.Any] | None`
    :   IDs of candidates linked to the user.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The full name of the user.

    `offices: list[typing.Any] | None`
    :   List of office locations where users are based

    `primary_email_address: str | None`
    :   The primary email address of the user.

    `site_admin: bool | None`
    :   Indicates whether the user is a site administrator.

    `updated_at: str | None`
    :   The date and time when the user account was last updated.