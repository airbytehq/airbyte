---
id: airbyte_agent_sdk-connectors-greenhouse-models
title: airbyte_agent_sdk.connectors.greenhouse.models
---

Module airbyte_agent_sdk.connectors.greenhouse.models
=====================================================
Pydantic models for greenhouse connector.

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

`AirbyteSearchResult[ApplicationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CandidatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DepartmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[JobPostsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[JobsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OffersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[OfficesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[SourcesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Application"></a>

`Application(**data: Any)`
:   Greenhouse application object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `applied_at: str | Any`
    :   The type of the None singleton.

    `attachments: list[airbyte_agent_sdk.connectors.greenhouse.models.Attachment] | Any`
    :   The type of the None singleton.

    `candidate_id: int | Any`
    :   The type of the None singleton.

    `credited_to: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `current_stage: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `job_post_id: int | Any | None`
    :   The type of the None singleton.

    `jobs: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `last_activity_at: str | Any`
    :   The type of the None singleton.

    `location: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `prospect: bool | Any`
    :   The type of the None singleton.

    `prospect_detail: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `prospective_department: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prospective_office: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `rejected_at: str | Any | None`
    :   The type of the None singleton.

    `rejection_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `rejection_reason: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `source: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `status: str | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   File attachment (resume, cover letter, etc.)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `filename: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="Candidate"></a>

`Candidate(**data: Any)`
:   Greenhouse candidate object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `addresses: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `application_ids: list[int] | Any`
    :   The type of the None singleton.

    `attachments: list[airbyte_agent_sdk.connectors.greenhouse.models.Attachment] | Any`
    :   The type of the None singleton.

    `can_email: bool | Any`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `coordinator: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `email_addresses: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `first_name: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_private: bool | Any`
    :   The type of the None singleton.

    `last_activity: str | Any`
    :   The type of the None singleton.

    `last_name: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone_numbers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `photo_url: str | Any | None`
    :   The type of the None singleton.

    `recruiter: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `social_media_addresses: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `website_addresses: list[dict[str, typing.Any]] | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

<a id="Department"></a>

`Department(**data: Any)`
:   Greenhouse department object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `child_department_external_ids: list[str] | Any`
    :   The type of the None singleton.

    `child_ids: list[int] | Any`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `parent_department_external_id: str | Any | None`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

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

<a id="GreenhouseCheckResult"></a>

`GreenhouseCheckResult(**data: Any)`
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

<a id="GreenhouseExecuteResult"></a>

`GreenhouseExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GreenhouseExecuteResultWithMeta"></a>

`GreenhouseExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Application], ApplicationsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Department], DepartmentsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[JobPost], JobPostsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Job], JobsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Offer], OffersListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Office], OfficesListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[ScheduledInterview], ScheduledInterviewsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Source], SourcesListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GreenhouseExecuteResultWithMeta[list[Application], ApplicationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[Department], DepartmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[JobPost], JobPostsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="JobPostsListResult"></a>

`JobPostsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[Job], JobsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[Offer], OffersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OffersListResult"></a>

`OffersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[Office], OfficesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OfficesListResult"></a>

`OfficesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[ScheduledInterview], ScheduledInterviewsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ScheduledInterviewsListResult"></a>

`ScheduledInterviewsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[Source], SourcesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GreenhouseExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
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

    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Job"></a>

`Job(**data: Any)`
:   Greenhouse job object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `confidential: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `departments: list[dict[str, typing.Any] | None] | Any`
    :   The type of the None singleton.

    `hiring_team: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `offices: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `opened_at: str | Any`
    :   The type of the None singleton.

    `openings: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `requisition_id: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="JobPost"></a>

`JobPost(**data: Any)`
:   Greenhouse job post object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `content: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `demographic_question_set_id: int | Any | None`
    :   The type of the None singleton.

    `external: bool | Any`
    :   The type of the None singleton.

    `first_published_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `internal: bool | Any`
    :   The type of the None singleton.

    `internal_content: str | Any | None`
    :   The type of the None singleton.

    `job_id: int | Any`
    :   The type of the None singleton.

    `live: bool | Any`
    :   The type of the None singleton.

    `location: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `questions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="JobPostsListResultMeta"></a>

`JobPostsListResultMeta(**data: Any)`
:   Metadata for job_posts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

<a id="Offer"></a>

`Offer(**data: Any)`
:   Greenhouse offer object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_id: int | Any`
    :   The type of the None singleton.

    `candidate_id: int | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `job_id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opening: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `resolved_at: str | Any | None`
    :   The type of the None singleton.

    `sent_at: str | Any | None`
    :   The type of the None singleton.

    `starts_at: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `version: int | Any`
    :   The type of the None singleton.

<a id="OffersListResultMeta"></a>

`OffersListResultMeta(**data: Any)`
:   Metadata for offers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

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

<a id="Office"></a>

`Office(**data: Any)`
:   Greenhouse office object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `child_ids: list[int] | Any`
    :   The type of the None singleton.

    `child_office_external_ids: list[str] | Any`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `location: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
    :   The type of the None singleton.

    `parent_office_external_id: str | Any | None`
    :   The type of the None singleton.

    `primary_contact_user_id: int | Any | None`
    :   The type of the None singleton.

<a id="OfficesListResultMeta"></a>

`OfficesListResultMeta(**data: Any)`
:   Metadata for offices.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

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

<a id="ScheduledInterview"></a>

`ScheduledInterview(**data: Any)`
:   Greenhouse scheduled interview object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_id: int | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `end: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `external_event_id: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `interview: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `interviewers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `location: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organizer: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `start: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `video_conferencing_url: str | Any | None`
    :   The type of the None singleton.

<a id="ScheduledInterviewsListResultMeta"></a>

`ScheduledInterviewsListResultMeta(**data: Any)`
:   Metadata for scheduled_interviews.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="Source"></a>

`Source(**data: Any)`
:   Greenhouse source object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `type_: dict[str, typing.Any] | Any | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

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

<a id="User"></a>

`User(**data: Any)`
:   Greenhouse user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `departments: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `disabled: bool | Any`
    :   The type of the None singleton.

    `emails: list[str] | Any`
    :   The type of the None singleton.

    `employee_id: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `last_name: str | Any`
    :   The type of the None singleton.

    `linked_candidate_ids: list[int] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `offices: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `primary_email_address: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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