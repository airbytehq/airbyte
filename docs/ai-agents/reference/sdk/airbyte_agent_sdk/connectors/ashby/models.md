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

`Application(**data: Any)`
:   Application object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applied_via_job_posting_id: str | Any | None`
    :   The type of the None singleton.

    `archive_reason: Any`
    :   The type of the None singleton.

    `archived_at: str | Any | None`
    :   The type of the None singleton.

    `candidate: Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `credited_to_user: Any`
    :   The type of the None singleton.

    `current_interview_stage: Any`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `hiring_team: list[airbyte_agent_sdk.connectors.ashby.models.ApplicationHiringteamItem] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `job: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: Any`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `submitter_client_ip: str | Any | None`
    :   The type of the None singleton.

    `submitter_user_agent: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`ApplicationHiringteamItem(**data: Any)`
:   Nested schema for Application.hiringTeam_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `user_id: str | Any | None`
    :   The type of the None singleton.

`ApplicationsListResultMeta(**data: Any)`
:   Metadata for applications.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ApplicationsSearchData(**data: Any)`
:   Search result data for applications entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ArchiveReason(**data: Any)`
:   Archive reason object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason_type: str | Any | None`
    :   The type of the None singleton.

    `text: str | Any | None`
    :   The type of the None singleton.

`ArchiveReasonsListResultMeta(**data: Any)`
:   Metadata for archive_reasons.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

`Candidate(**data: Any)`
:   Candidate object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_ids: list[str | None] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `credited_to_user: Any`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `email_addresses: list[airbyte_agent_sdk.connectors.ashby.models.CandidateEmailaddressesItem] | Any | None`
    :   The type of the None singleton.

    `file_handles: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone_numbers: list[airbyte_agent_sdk.connectors.ashby.models.CandidatePhonenumbersItem] | Any | None`
    :   The type of the None singleton.

    `profile_url: str | Any | None`
    :   The type of the None singleton.

    `social_links: list[airbyte_agent_sdk.connectors.ashby.models.CandidateSociallinksItem] | Any | None`
    :   The type of the None singleton.

    `source: Any`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.ashby.models.CandidateTagsItem] | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`CandidateEmailaddressesItem(**data: Any)`
:   Nested schema for Candidate.emailAddresses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_primary: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

`CandidatePhonenumbersItem(**data: Any)`
:   Nested schema for Candidate.phoneNumbers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_primary: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

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

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

`CandidateTag(**data: Any)`
:   Candidate tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

`CandidateTagsItem(**data: Any)`
:   Nested schema for Candidate.tags_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

`CandidateTagsListResultMeta(**data: Any)`
:   Metadata for candidate_tags.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CandidatesListResultMeta(**data: Any)`
:   Metadata for candidates.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CandidatesSearchData(**data: Any)`
:   Search result data for candidates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CustomField(**data: Any)`
:   Custom field definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_type: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_private: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_type: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

`CustomFieldsListResultMeta(**data: Any)`
:   Metadata for custom_fields.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`Department(**data: Any)`
:   Department object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `external_name: str | Any | None`
    :   The type of the None singleton.

    `extra_data: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `parent_id: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`DepartmentsListResultMeta(**data: Any)`
:   Metadata for departments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`FeedbackFormDefinition(**data: Any)`
:   Feedback form definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `form_definition: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `interview_id: str | Any | None`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_default_form: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

`FeedbackFormDefinitionsListResultMeta(**data: Any)`
:   Metadata for feedback_form_definitions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`Job(**data: Any)`
:   Job object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: Any`
    :   The type of the None singleton.

    `brand_id: str | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `confidential: bool | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `custom_fields: list[airbyte_agent_sdk.connectors.ashby.models.JobCustomfieldsItem] | Any | None`
    :   The type of the None singleton.

    `custom_requisition_id: str | Any | None`
    :   The type of the None singleton.

    `default_interview_plan_id: str | Any | None`
    :   The type of the None singleton.

    `department_id: str | Any | None`
    :   The type of the None singleton.

    `employment_type: str | Any | None`
    :   The type of the None singleton.

    `hiring_team: list[airbyte_agent_sdk.connectors.ashby.models.JobHiringteamItem] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `interview_plan_ids: list[str | None] | Any | None`
    :   The type of the None singleton.

    `job_posting_ids: list[str | None] | Any | None`
    :   The type of the None singleton.

    `location_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opened_at: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`JobCustomfieldsItem(**data: Any)`
:   Nested schema for Job.customFields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_private: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

    `value_label: str | Any | None`
    :   The type of the None singleton.

`JobHiringteamItem(**data: Any)`
:   Nested schema for Job.hiringTeam_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `user_id: str | Any | None`
    :   The type of the None singleton.

`JobPosting(**data: Any)`
:   Job posting object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_deadline: str | Any | None`
    :   The type of the None singleton.

    `apply_link: str | Any | None`
    :   The type of the None singleton.

    `compensation_tier_summary: str | Any | None`
    :   The type of the None singleton.

    `department_name: str | Any | None`
    :   The type of the None singleton.

    `employment_type: str | Any | None`
    :   The type of the None singleton.

    `external_link: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_listed: bool | Any | None`
    :   The type of the None singleton.

    `job_id: str | Any | None`
    :   The type of the None singleton.

    `location_external_name: str | Any | None`
    :   The type of the None singleton.

    `location_ids: Any`
    :   The type of the None singleton.

    `location_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `published_date: str | Any | None`
    :   The type of the None singleton.

    `should_display_compensation_on_job_board: bool | Any | None`
    :   The type of the None singleton.

    `team_name: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `workplace_type: str | Any | None`
    :   The type of the None singleton.

`JobPostingsListResultMeta(**data: Any)`
:   Metadata for job_postings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`JobPostingsSearchData(**data: Any)`
:   Search result data for job_postings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`JobsListResultMeta(**data: Any)`
:   Metadata for jobs.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`JobsSearchData(**data: Any)`
:   Search result data for jobs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Location(**data: Any)`
:   Location object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: Any`
    :   The type of the None singleton.

    `external_name: str | Any | None`
    :   The type of the None singleton.

    `extra_data: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `is_remote: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `parent_location_id: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `workplace_type: str | Any | None`
    :   The type of the None singleton.

`LocationsListResultMeta(**data: Any)`
:   Metadata for locations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`Source(**data: Any)`
:   Candidate source object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source_type: Any`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

`SourcesListResultMeta(**data: Any)`
:   Metadata for sources.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`User(**data: Any)`
:   User object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `global_role: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_enabled: bool | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`UsersListResultMeta(**data: Any)`
:   Metadata for users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.