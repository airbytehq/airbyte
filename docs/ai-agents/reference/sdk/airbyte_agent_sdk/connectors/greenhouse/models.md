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
    * airbyte_agent_sdk.connectors.greenhouse.models.AirbyteSearchResult[dict[str, Any]]

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

    `agency_note_id: int | None`
    :   The type of the None singleton.

    `answers: list[airbyte_agent_sdk.connectors.greenhouse.models.ApplicationAnswersItem | None] | None`
    :   The type of the None singleton.

    `candidate_id: int | None`
    :   The type of the None singleton.

    `coordinator_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.greenhouse.models.ApplicationCustomFields] | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `job_id: int | None`
    :   The type of the None singleton.

    `job_interview_stage_id: int | None`
    :   The type of the None singleton.

    `job_post_id: int | None`
    :   The type of the None singleton.

    `last_activity_at: str | None`
    :   The type of the None singleton.

    `location_address: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `needs_decision: bool | None`
    :   The type of the None singleton.

    `prospect: bool | None`
    :   The type of the None singleton.

    `prospective_job_ids: list[int | None] | None`
    :   The type of the None singleton.

    `recruiter_id: int | None`
    :   The type of the None singleton.

    `referrer_id: int | None`
    :   The type of the None singleton.

    `rejected_at: str | None`
    :   The type of the None singleton.

    `rejection_reason_id: int | None`
    :   The type of the None singleton.

    `source_id: int | None`
    :   The type of the None singleton.

    `stage_id: int | None`
    :   The type of the None singleton.

    `stage_name: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="ApplicationAnswersItem"></a>

`ApplicationAnswersItem(**data: Any)`
:   Nested schema for Application.answers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answer: str | None`
    :   Candidate's free-text answer to the question.

    `model_config`
    :   The type of the None singleton.

    `question: str | None`
    :   Application-form question the candidate answered.

<a id="ApplicationCustomFields"></a>

`ApplicationCustomFields(**data: Any)`
:   Nested schema for Application.custom_fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: typing.Any | None`
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

    `next: str | None`
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

    `agency_note_id: int | None`
    :   Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency.

    `answers: list[typing.Any] | None`
    :   Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer.

    `candidate_id: int | None`
    :   Id of the candidate (person) this application belongs to.

    `coordinator_id: int | None`
    :   Id of the user assigned as coordinator on the application's job, or `null` when unassigned.

    `created_at: str | None`
    :   Created at from the Greenhouse v3 applications record.

    `custom_fields: dict[str, typing.Any] | None`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: int | None`
    :   Id from the Greenhouse v3 applications record.

    `job_id: int | None`
    :   Id of the job this application is on. `null` for jobless prospect applications.

    `job_interview_stage_id: int | None`
    :   Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `job_post_id: int | None`
    :   Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role.

    `last_activity_at: str | None`
    :   Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601.

    `location_address: str | None`
    :   Free-form location string captured on the application (typically from the job post's location question).

    `model_config`
    :   The type of the None singleton.

    `needs_decision: bool | None`
    :   `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage.

    `prospect: bool | None`
    :   `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job.

    `prospective_job_ids: list[typing.Any] | None`
    :   For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects.

    `recruiter_id: int | None`
    :   Id of the user assigned as recruiter on the application's job, or `null` when unassigned.

    `referrer_id: int | None`
    :   Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user.

    `rejected_at: str | None`
    :   Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected.

    `rejection_reason_id: int | None`
    :   Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected.

    `source_id: int | None`
    :   Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set.

    `stage_id: int | None`
    :   Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `stage_name: str | None`
    :   Display name of the candidate's current interview stage on this application.

    `status: str | None`
    :   Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 applications record.

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   File associated with a Greenhouse application
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application_id: int | None`
    :   The type of the None singleton.

    `candidate_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `filename: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="AttachmentsListResultMeta"></a>

`AttachmentsListResultMeta(**data: Any)`
:   Metadata for attachments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
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

    `addresses: list[airbyte_agent_sdk.connectors.greenhouse.models.CandidateAddressesItem | None] | None`
    :   The type of the None singleton.

    `can_email: bool | None`
    :   The type of the None singleton.

    `company: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.greenhouse.models.CandidateCustomFields] | None`
    :   The type of the None singleton.

    `email_addresses: list[airbyte_agent_sdk.connectors.greenhouse.models.CandidateEmailAddressesItem | None] | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `last_activity_at: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `linked_user_ids: list[int | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone_numbers: list[airbyte_agent_sdk.connectors.greenhouse.models.CandidatePhoneNumbersItem | None] | None`
    :   The type of the None singleton.

    `preferred_name: str | None`
    :   The type of the None singleton.

    `private: bool | None`
    :   The type of the None singleton.

    `social_media_addresses: list[airbyte_agent_sdk.connectors.greenhouse.models.CandidateSocialMediaAddressesItem | None] | None`
    :   The type of the None singleton.

    `tags: list[str | None] | None`
    :   The type of the None singleton.

    `time_zone: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `website_addresses: list[airbyte_agent_sdk.connectors.greenhouse.models.CandidateWebsiteAddressesItem | None] | None`
    :   The type of the None singleton.

<a id="CandidateAddressesItem"></a>

`CandidateAddressesItem(**data: Any)`
:   Nested schema for Candidate.addresses_item
    
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

    `value: str | None`
    :   The type of the None singleton.

<a id="CandidateCustomFields"></a>

`CandidateCustomFields(**data: Any)`
:   Nested schema for Candidate.custom_fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: typing.Any | None`
    :   The type of the None singleton.

<a id="CandidateEmailAddressesItem"></a>

`CandidateEmailAddressesItem(**data: Any)`
:   Nested schema for Candidate.email_addresses_item
    
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

    `value: str | None`
    :   The type of the None singleton.

<a id="CandidatePhoneNumbersItem"></a>

`CandidatePhoneNumbersItem(**data: Any)`
:   Nested schema for Candidate.phone_numbers_item
    
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

    `value: str | None`
    :   The type of the None singleton.

<a id="CandidateSocialMediaAddressesItem"></a>

`CandidateSocialMediaAddressesItem(**data: Any)`
:   Nested schema for Candidate.social_media_addresses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="CandidateWebsiteAddressesItem"></a>

`CandidateWebsiteAddressesItem(**data: Any)`
:   Nested schema for Candidate.website_addresses_item
    
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

    `value: str | None`
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

    `next: str | None`
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
    :   Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`.

    `can_email: bool | None`
    :   Whether this candidate has consented to receive email communication from your organization.

    `company: str | None`
    :   Candidate's current company, as entered on their profile.

    `created_at: str | None`
    :   Created at from the Greenhouse v3 candidates record.

    `custom_fields: dict[str, typing.Any] | None`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `email_addresses: list[typing.Any] | None`
    :   Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`.

    `first_name: str | None`
    :   First name from the Greenhouse v3 candidates record.

    `id: int | None`
    :   Id from the Greenhouse v3 candidates record.

    `last_activity_at: str | None`
    :   Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601.

    `last_name: str | None`
    :   Last name from the Greenhouse v3 candidates record.

    `linked_user_ids: list[typing.Any] | None`
    :   Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record).

    `model_config`
    :   The type of the None singleton.

    `phone_numbers: list[typing.Any] | None`
    :   Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`.

    `preferred_name: str | None`
    :   Preferred or chosen name the candidate goes by, when different from their legal first name.

    `private: bool | None`
    :   If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`.

    `social_media_addresses: list[typing.Any] | None`
    :   Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned.

    `tags: list[typing.Any] | None`
    :   Candidate tag names applied to this candidate within your organization.

    `time_zone: str | None`
    :   Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`).

    `title: str | None`
    :   Candidate's current job title, as entered on their profile.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 candidates record.

    `website_addresses: list[typing.Any] | None`
    :   Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`.

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

    `created_at: str | None`
    :   The type of the None singleton.

    `external_id: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_id: int | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
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

    `created_at: str | None`
    :   Created at from the Greenhouse v3 departments record.

    `external_id: str | None`
    :   Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set.

    `id: int | None`
    :   Id from the Greenhouse v3 departments record.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the department (e.g. `Engineering`, `Marketing`).

    `parent_id: int | None`
    :   Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 departments record.

<a id="GreenhouseAuthConfig"></a>

`GreenhouseAuthConfig(**data: Any)`
:   Greenhouse OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Access token generated through the Greenhouse OAuth consent flow (optional if refresh_token is provided)

    `client_id: str`
    :   Client ID from the Greenhouse OAuth application

    `client_secret: str`
    :   Client secret from the Greenhouse OAuth application

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Refresh token generated through the Greenhouse OAuth consent flow

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
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Attachment], AttachmentsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Candidate], CandidatesListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Department], DepartmentsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Interview], InterviewsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[JobPost], JobPostsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Job], JobsListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Offer], OffersListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Office], OfficesListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[Source], SourcesListResultMeta]
    * airbyte_agent_sdk.connectors.greenhouse.models.GreenhouseExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S | None`
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

`GreenhouseExecuteResultWithMeta[list[Attachment], AttachmentsListResultMeta](**data: Any)`
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

<a id="AttachmentsListResult"></a>

`AttachmentsListResult(**data: Any)`
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

`GreenhouseExecuteResultWithMeta[list[Interview], InterviewsListResultMeta](**data: Any)`
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

<a id="InterviewsListResult"></a>

`InterviewsListResult(**data: Any)`
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

<a id="Interview"></a>

`Interview(**data: Any)`
:   Greenhouse interview object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all_day_end_on: str | None`
    :   The type of the None singleton.

    `all_day_start_on: str | None`
    :   The type of the None singleton.

    `application_id: int | None`
    :   The type of the None singleton.

    `availability_received_at: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `ends_at: str | None`
    :   The type of the None singleton.

    `external_event_id: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `job_id: int | None`
    :   The type of the None singleton.

    `job_interview_id: int | None`
    :   The type of the None singleton.

    `location: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organizer_id: int | None`
    :   The type of the None singleton.

    `scheduled_at: str | None`
    :   The type of the None singleton.

    `starts_at: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `video_conferencing_url: str | None`
    :   The type of the None singleton.

<a id="InterviewsListResultMeta"></a>

`InterviewsListResultMeta(**data: Any)`
:   Metadata for interviews.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

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

    `closed_at: str | None`
    :   The type of the None singleton.

    `confidential: bool | None`
    :   The type of the None singleton.

    `copied_from_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.greenhouse.models.JobCustomFields] | None`
    :   The type of the None singleton.

    `department_id: int | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `is_template: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `notes: str | None`
    :   The type of the None singleton.

    `office_ids: list[int | None] | None`
    :   The type of the None singleton.

    `opened_at: str | None`
    :   The type of the None singleton.

    `requisition_id: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="JobCustomFields"></a>

`JobCustomFields(**data: Any)`
:   Nested schema for Job.custom_fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: typing.Any | None`
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

    `active: bool | None`
    :   The type of the None singleton.

    `content: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `demographic_question_set_id: int | None`
    :   The type of the None singleton.

    `featured: bool | None`
    :   The type of the None singleton.

    `first_published_at: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `internal: bool | None`
    :   The type of the None singleton.

    `internal_content: str | None`
    :   The type of the None singleton.

    `job_board_id: int | None`
    :   The type of the None singleton.

    `job_id: int | None`
    :   The type of the None singleton.

    `language: str | None`
    :   The type of the None singleton.

    `live: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `public_url: str | None`
    :   The type of the None singleton.

    `questions: list[airbyte_agent_sdk.connectors.greenhouse.models.JobPostQuestionsItem | None] | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="JobPostQuestionsItem"></a>

`JobPostQuestionsItem(**data: Any)`
:   Nested schema for JobPost.questions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `answer_type: str | None`
    :   Input type the candidate uses to answer. `short_text` and `long_text` are free-text inputs, `single_select` and `multi_select` use the `options` array, `boolean` is a yes/no, `attachment` accepts a file upload, and `hidden` is set programmatically without rendering a field.

    `description: str | None`
    :   Help text shown below the question label to give candidates additional context. `null` when no help text is set.

    `id: int | None`
    :   Id of the question. `null` for default questions that are rendered from configuration rather than persisted per post (e.g. the built-in `first_name` field).

    `label: str | None`
    :   Human-readable label rendered above the input on the application form.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Stable form-field name used when submitting an application (e.g. `question_42` for a custom question, `first_name` for a default field). Use this when mapping responses back to a question.

    `options: list[airbyte_agent_sdk.connectors.greenhouse.models.JobPostQuestionsItemOptionsItem | None] | None`
    :   Selectable answer options for `single_select` and `multi_select` questions. Empty for other answer types.

    `private: bool | None`
    :   If `true`, answers to this question are visible only to users with explicit access (e.g. private notes, API-only questions). Defaults to `false`.

    `required: bool | None`
    :   If `true`, the candidate must answer this question to submit the application. `null` for default questions whose required-ness is driven by board-level configuration.

<a id="JobPostQuestionsItemOptionsItem"></a>

`JobPostQuestionsItemOptionsItem(**data: Any)`
:   Nested schema for JobPostQuestionsItem.options_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Id of the option, stable across edits to the option label.

    `label: str | None`
    :   Human-readable text shown to the candidate for this option.

    `model_config`
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

    `next: str | None`
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
    :   If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them.

    `content: str | None`
    :   HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded.

    `created_at: str | None`
    :   Created at from the Greenhouse v3 job posts record.

    `demographic_question_set_id: int | None`
    :   Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data.

    `featured: bool | None`
    :   If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time.

    `first_published_at: str | None`
    :   Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published.

    `id: int | None`
    :   Id from the Greenhouse v3 job posts record.

    `internal: bool | None`
    :   If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time.

    `internal_content: str | None`
    :   HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`.

    `job_board_id: int | None`
    :   Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time.

    `job_id: int | None`
    :   Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan.

    `language: str | None`
    :   ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen.

    `live: bool | None`
    :   If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled.

    `model_config`
    :   The type of the None singleton.

    `public_url: str | None`
    :   Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured.

    `questions: list[typing.Any] | None`
    :   Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form.

    `title: str | None`
    :   Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 job posts record.

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

    `next: str | None`
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
    :   Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`.

    `confidential: bool | None`
    :   If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled.

    `copied_from_id: int | None`
    :   Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job.

    `created_at: str | None`
    :   Created at from the Greenhouse v3 jobs record.

    `custom_fields: dict[str, typing.Any] | None`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `department_id: int | None`
    :   Id of the department this job is assigned to. `null` when no department is set.

    `id: int | None`
    :   Id from the Greenhouse v3 jobs record.

    `is_template: bool | None`
    :   If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`.

    `notes: str | None`
    :   Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts.

    `office_ids: list[typing.Any] | None`
    :   Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set.

    `opened_at: str | None`
    :   Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`.

    `requisition_id: str | None`
    :   Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set.

    `status: str | None`
    :   Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/{id}`.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 jobs record.

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

    `application_id: int | None`
    :   The type of the None singleton.

    `candidate_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.greenhouse.models.OfferCustomFields] | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `job_id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opening_id: int | None`
    :   The type of the None singleton.

    `resolved_at: str | None`
    :   The type of the None singleton.

    `sent_on: str | None`
    :   The type of the None singleton.

    `starts_on: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `version: int | None`
    :   The type of the None singleton.

<a id="OfferCustomFields"></a>

`OfferCustomFields(**data: Any)`
:   Nested schema for Offer.custom_fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: typing.Any | None`
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

    `next: str | None`
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
    :   Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted.

    `candidate_id: int | None`
    :   Id of the candidate (person) receiving this offer. Resolved through the offer's application.

    `created_at: str | None`
    :   Created at from the Greenhouse v3 offers record.

    `custom_fields: dict[str, typing.Any] | None`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: int | None`
    :   Id from the Greenhouse v3 offers record.

    `job_id: int | None`
    :   Id of the job this offer's application is on.

    `model_config`
    :   The type of the None singleton.

    `opening_id: int | None`
    :   Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening.

    `resolved_at: str | None`
    :   Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/{id}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution.

    `sent_on: str | None`
    :   Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent.

    `starts_on: str | None`
    :   Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer.

    `status: str | None`
    :   Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status).

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 offers record.

    `version: int | None`
    :   Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application.

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

    `created_at: str | None`
    :   The type of the None singleton.

    `external_id: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `location: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_id: int | None`
    :   The type of the None singleton.

    `primary_in_house_contact_user_id: int | None`
    :   The type of the None singleton.

    `updated_at: str | None`
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

    `next: str | None`
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

    `created_at: str | None`
    :   Created at from the Greenhouse v3 offices record.

    `external_id: str | None`
    :   Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled.

    `id: int | None`
    :   Id from the Greenhouse v3 offices record.

    `location: str | None`
    :   Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization.

    `parent_id: int | None`
    :   Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization.

    `primary_in_house_contact_user_id: int | None`
    :   Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 offices record.

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

    `created_at: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: airbyte_agent_sdk.connectors.greenhouse.models.SourceType | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SourceType"></a>

`SourceType(**data: Any)`
:   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Id of the sourcing strategy. References the same strategy across all sources in the organization that roll up to it.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the sourcing strategy used in Greenhouse reporting (e.g. `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`).

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

    `next: str | None`
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

    `created_at: str | None`
    :   Created at from the Greenhouse v3 sources record.

    `id: int | None`
    :   Id from the Greenhouse v3 sources record.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name.

    `type_: dict[str, typing.Any] | None`
    :   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 sources record.

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

    `agency_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.greenhouse.models.UserCustomFields] | None`
    :   The type of the None singleton.

    `deactivated: bool | None`
    :   The type of the None singleton.

    `department_ids: list[int | None] | None`
    :   The type of the None singleton.

    `emails: list[str | None] | None`
    :   The type of the None singleton.

    `employee_id: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `interviewer_tags: list[airbyte_agent_sdk.connectors.greenhouse.models.UserInterviewerTagsItem | None] | None`
    :   The type of the None singleton.

    `job_title: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `linked_candidate_ids: list[int | None] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `office_ids: list[int | None] | None`
    :   The type of the None singleton.

    `primary_email: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="UserCustomFields"></a>

`UserCustomFields(**data: Any)`
:   Nested schema for User.custom_fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `value: typing.Any | None`
    :   The type of the None singleton.

<a id="UserInterviewerTagsItem"></a>

`UserInterviewerTagsItem(**data: Any)`
:   Nested schema for User.interviewer_tags_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
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

    `next: str | None`
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

    `agency_id: int | None`
    :   Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users.

    `created_at: str | None`
    :   Created at from the Greenhouse v3 users record.

    `custom_fields: dict[str, typing.Any] | None`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `deactivated: bool | None`
    :   Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/{id}/deactivate` and `POST /v3/users/{id}/activate`.

    `department_ids: list[typing.Any] | None`
    :   Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department.

    `emails: list[typing.Any] | None`
    :   All email addresses on the user's account, including the primary address and any additional verified addresses.

    `employee_id: str | None`
    :   Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set.

    `first_name: str | None`
    :   First name from the Greenhouse v3 users record.

    `id: int | None`
    :   Id from the Greenhouse v3 users record.

    `interviewer_tags: list[typing.Any] | None`
    :   Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`.

    `job_title: str | None`
    :   Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title.

    `last_name: str | None`
    :   Last name from the Greenhouse v3 users record.

    `linked_candidate_ids: list[typing.Any] | None`
    :   Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications).

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly.

    `office_ids: list[typing.Any] | None`
    :   Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office.

    `primary_email: str | None`
    :   Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string.

    `site_admin: bool | None`
    :   Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/{id}/revoke_permissions`.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 users record.