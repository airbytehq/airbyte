---
id: airbyte_agent_sdk-connectors-ashby-models
title: airbyte_agent_sdk.connectors.ashby.models
---

Module airbyte_agent_sdk.connectors.ashby.models
================================================
Pydantic models for ashby connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

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

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[ApplicationsSearchData]
    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[CandidatesSearchData]
    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[JobPostingsSearchData]
    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[JobsSearchData]
    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ApplicationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

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

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CandidatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CandidatesSearchResult"></a>

`CandidatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[JobPostingsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="JobPostingsSearchResult"></a>

`JobPostingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[JobsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="JobsSearchResult"></a>

`JobsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Application"></a>

`Application(**data: Any)`
:   Application object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applied_via_job_posting_id: str | None`
    :   The type of the None singleton.

    `archive_reason: typing.Any | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `candidate: typing.Any | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `credited_to_user: typing.Any | None`
    :   The type of the None singleton.

    `current_interview_stage: typing.Any | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `hiring_team: list[airbyte_agent_sdk.connectors.ashby.models.ApplicationHiringteamItem] | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `job: typing.Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: typing.Any | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `submitter_client_ip: str | None`
    :   The type of the None singleton.

    `submitter_user_agent: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="ApplicationHiringteamItem"></a>

`ApplicationHiringteamItem(**data: Any)`
:   Nested schema for Application.hiringTeam_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   The type of the None singleton.

    `user_id: str | None`
    :   The type of the None singleton.

<a id="ApplicationsListResultMeta"></a>

`ApplicationsListResultMeta(**data: Any)`
:   Metadata for applications.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `archive_reason: str | None`
    :   Reason the application was archived, if applicable

    `created_at: str | None`
    :   Timestamp when the application was created, in ISO 8601 format

    `id: str | None`
    :   Unique identifier for the application

    `model_config`
    :   The type of the None singleton.

    `status: str | None`
    :   Current application status (e.g. active, archived, hired)

    `updated_at: str | None`
    :   Timestamp when the application was last updated, in ISO 8601 format

<a id="ArchiveReason"></a>

`ArchiveReason(**data: Any)`
:   Archive reason object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason_type: str | None`
    :   The type of the None singleton.

    `text: str | None`
    :   The type of the None singleton.

<a id="ArchiveReasonsListResultMeta"></a>

`ArchiveReasonsListResultMeta(**data: Any)`
:   Metadata for archive_reasons.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AshbyAuthConfig"></a>

`AshbyAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Ashby API key

    `model_config`
    :   The type of the None singleton.

<a id="AshbyCheckResult"></a>

`AshbyCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="AshbyExecuteResult"></a>

`AshbyExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="AshbyExecuteResultWithMeta"></a>

`AshbyExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Application], ApplicationsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[ArchiveReason], ArchiveReasonsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[CandidateTag], CandidateTagsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[CustomField], CustomFieldsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Department], DepartmentsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[FeedbackFormDefinition], FeedbackFormDefinitionsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[JobPosting], JobPostingsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Job], JobsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Location], LocationsListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[Source], SourcesListResultMeta]
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`AshbyExecuteResultWithMeta[list[Application], ApplicationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ApplicationsListResult"></a>

`ApplicationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[ArchiveReason], ArchiveReasonsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ArchiveReasonsListResult"></a>

`ArchiveReasonsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[CandidateTag], CandidateTagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CandidateTagsListResult"></a>

`CandidateTagsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CandidatesListResult"></a>

`CandidatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[CustomField], CustomFieldsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomFieldsListResult"></a>

`CustomFieldsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[Department], DepartmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DepartmentsListResult"></a>

`DepartmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[FeedbackFormDefinition], FeedbackFormDefinitionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FeedbackFormDefinitionsListResult"></a>

`FeedbackFormDefinitionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[JobPosting], JobPostingsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="JobPostingsListResult"></a>

`JobPostingsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[Job], JobsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="JobsListResult"></a>

`JobsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[Location], LocationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LocationsListResult"></a>

`LocationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[Source], SourcesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SourcesListResult"></a>

`SourcesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AshbyExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResult"></a>

`UsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.ashby.models.AshbyExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AshbyReplicationConfig"></a>

`AshbyReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Ashby.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   The date from which to start replicating data, in the format YYYY-MM-DDT00:00:00Z.

<a id="Candidate"></a>

`Candidate(**data: Any)`
:   Candidate object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_ids: list[str | None] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `credited_to_user: typing.Any | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `email_addresses: list[airbyte_agent_sdk.connectors.ashby.models.CandidateEmailaddressesItem] | None`
    :   The type of the None singleton.

    `file_handles: list[typing.Any] | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone_numbers: list[airbyte_agent_sdk.connectors.ashby.models.CandidatePhonenumbersItem] | None`
    :   The type of the None singleton.

    `profile_url: str | None`
    :   The type of the None singleton.

    `social_links: list[airbyte_agent_sdk.connectors.ashby.models.CandidateSociallinksItem] | None`
    :   The type of the None singleton.

    `source: typing.Any | None`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.ashby.models.CandidateTagsItem] | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CandidateEmailaddressesItem"></a>

`CandidateEmailaddressesItem(**data: Any)`
:   Nested schema for Candidate.emailAddresses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_primary: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="CandidatePhonenumbersItem"></a>

`CandidatePhonenumbersItem(**data: Any)`
:   Nested schema for Candidate.phoneNumbers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_primary: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="CandidateSociallinksItem"></a>

`CandidateSociallinksItem(**data: Any)`
:   Nested schema for Candidate.socialLinks_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="CandidateTag"></a>

`CandidateTag(**data: Any)`
:   Candidate tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="CandidateTagsItem"></a>

`CandidateTagsItem(**data: Any)`
:   Nested schema for Candidate.tags_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="CandidateTagsListResultMeta"></a>

`CandidateTagsListResultMeta(**data: Any)`
:   Metadata for candidate_tags.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CandidatesListResultMeta"></a>

`CandidatesListResultMeta(**data: Any)`
:   Metadata for candidates.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `company: str | None`
    :   Candidate's current company

    `id: str | None`
    :   Unique identifier for the candidate

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the candidate

    `position: str | None`
    :   Candidate's current position or title

    `school: str | None`
    :   School associated with the candidate's education

<a id="CustomField"></a>

`CustomField(**data: Any)`
:   Custom field definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_type: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `is_private: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_type: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="CustomFieldsListResultMeta"></a>

`CustomFieldsListResultMeta(**data: Any)`
:   Metadata for custom_fields.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Department"></a>

`Department(**data: Any)`
:   Department object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `external_name: str | None`
    :   The type of the None singleton.

    `extra_data: typing.Any | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_id: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="DepartmentsListResultMeta"></a>

`DepartmentsListResultMeta(**data: Any)`
:   Metadata for departments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FeedbackFormDefinition"></a>

`FeedbackFormDefinition(**data: Any)`
:   Feedback form definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `form_definition: typing.Any | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `interview_id: str | None`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `is_default_form: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="FeedbackFormDefinitionsListResultMeta"></a>

`FeedbackFormDefinitionsListResultMeta(**data: Any)`
:   Metadata for feedback_form_definitions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Job"></a>

`Job(**data: Any)`
:   Job object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: typing.Any | None`
    :   The type of the None singleton.

    `brand_id: str | None`
    :   The type of the None singleton.

    `closed_at: str | None`
    :   The type of the None singleton.

    `confidential: bool | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: list[airbyte_agent_sdk.connectors.ashby.models.JobCustomfieldsItem] | None`
    :   The type of the None singleton.

    `custom_requisition_id: str | None`
    :   The type of the None singleton.

    `default_interview_plan_id: str | None`
    :   The type of the None singleton.

    `department_id: str | None`
    :   The type of the None singleton.

    `employment_type: str | None`
    :   The type of the None singleton.

    `hiring_team: list[airbyte_agent_sdk.connectors.ashby.models.JobHiringteamItem] | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `interview_plan_ids: list[str | None] | None`
    :   The type of the None singleton.

    `job_posting_ids: list[str | None] | None`
    :   The type of the None singleton.

    `location_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opened_at: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="JobCustomfieldsItem"></a>

`JobCustomfieldsItem(**data: Any)`
:   Nested schema for Job.customFields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `is_private: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

    `value_label: str | None`
    :   The type of the None singleton.

<a id="JobHiringteamItem"></a>

`JobHiringteamItem(**data: Any)`
:   Nested schema for Job.hiringTeam_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | None`
    :   The type of the None singleton.

    `user_id: str | None`
    :   The type of the None singleton.

<a id="JobPosting"></a>

`JobPosting(**data: Any)`
:   Job posting object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_deadline: str | None`
    :   The type of the None singleton.

    `apply_link: str | None`
    :   The type of the None singleton.

    `compensation_tier_summary: str | None`
    :   The type of the None singleton.

    `department_name: str | None`
    :   The type of the None singleton.

    `employment_type: str | None`
    :   The type of the None singleton.

    `external_link: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_listed: bool | None`
    :   The type of the None singleton.

    `job_id: str | None`
    :   The type of the None singleton.

    `location_external_name: str | None`
    :   The type of the None singleton.

    `location_ids: typing.Any | None`
    :   The type of the None singleton.

    `location_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_date: str | None`
    :   The type of the None singleton.

    `should_display_compensation_on_job_board: bool | None`
    :   The type of the None singleton.

    `team_name: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `workplace_type: str | None`
    :   The type of the None singleton.

<a id="JobPostingsListResultMeta"></a>

`JobPostingsListResultMeta(**data: Any)`
:   Metadata for job_postings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="JobPostingsSearchData"></a>

`JobPostingsSearchData(**data: Any)`
:   Search result data for job_postings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the job posting

    `is_listed: bool | None`
    :   Whether the job posting is currently published/listed

    `job_id: str | None`
    :   Identifier of the job this posting belongs to

    `location_name: str | None`
    :   Name of the location associated with the posting

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   Title of the job posting

<a id="JobsListResultMeta"></a>

`JobsListResultMeta(**data: Any)`
:   Metadata for jobs.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `department_id: str | None`
    :   Identifier of the department the job belongs to

    `id: str | None`
    :   Unique identifier for the job

    `location_id: str | None`
    :   Identifier of the primary location of the job

    `model_config`
    :   The type of the None singleton.

    `status: str | None`
    :   Current status of the job (e.g. open, closed, draft)

    `title: str | None`
    :   Title of the job

<a id="Location"></a>

`Location(**data: Any)`
:   Location object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: typing.Any | None`
    :   The type of the None singleton.

    `external_name: str | None`
    :   The type of the None singleton.

    `extra_data: typing.Any | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `is_remote: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_location_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `workplace_type: str | None`
    :   The type of the None singleton.

<a id="LocationsListResultMeta"></a>

`LocationsListResultMeta(**data: Any)`
:   Metadata for locations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Source"></a>

`Source(**data: Any)`
:   Candidate source object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source_type: typing.Any | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="SourcesListResultMeta"></a>

`SourcesListResultMeta(**data: Any)`
:   Metadata for sources.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="User"></a>

`User(**data: Any)`
:   User object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `global_role: str | None`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_enabled: bool | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="UsersListResultMeta"></a>

`UsersListResultMeta(**data: Any)`
:   Metadata for users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_more: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `email: str | None`
    :   Primary email address of the user

    `first_name: str | None`
    :   First name of the user

    `id: str | None`
    :   Unique identifier for the user

    `last_name: str | None`
    :   Last name of the user

    `model_config`
    :   The type of the None singleton.