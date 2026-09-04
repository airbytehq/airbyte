---
id: airbyte_agent_sdk-connectors-greenhouse-types
title: airbyte_agent_sdk.connectors.greenhouse.types
---

Module airbyte_agent_sdk.connectors.greenhouse.types
====================================================
Type definitions for greenhouse connector.

Classes
-------

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="ApplicationsAndCondition"></a>

`ApplicationsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition]`
    :   The type of the None singleton.

<a id="ApplicationsAnyCondition"></a>

`ApplicationsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ApplicationsAnyValueFilter"></a>

`ApplicationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_note_id: Any`
    :   Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency.

    `answers: Any`
    :   Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer.

    `candidate_id: Any`
    :   Id of the candidate (person) this application belongs to.

    `coordinator_id: Any`
    :   Id of the user assigned as coordinator on the application's job, or `null` when unassigned.

    `created_at: Any`
    :   Created at from the Greenhouse v3 applications record.

    `custom_fields: Any`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: Any`
    :   Id from the Greenhouse v3 applications record.

    `job_id: Any`
    :   Id of the job this application is on. `null` for jobless prospect applications.

    `job_interview_stage_id: Any`
    :   Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `job_post_id: Any`
    :   Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role.

    `last_activity_at: Any`
    :   Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601.

    `location_address: Any`
    :   Free-form location string captured on the application (typically from the job post's location question).

    `needs_decision: Any`
    :   `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage.

    `prospect: Any`
    :   `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job.

    `prospective_job_ids: Any`
    :   For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects.

    `recruiter_id: Any`
    :   Id of the user assigned as recruiter on the application's job, or `null` when unassigned.

    `referrer_id: Any`
    :   Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user.

    `rejected_at: Any`
    :   Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected.

    `rejection_reason_id: Any`
    :   Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected.

    `source_id: Any`
    :   Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set.

    `stage_id: Any`
    :   Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `stage_name: Any`
    :   Display name of the candidate's current interview stage on this application.

    `status: Any`
    :   Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 applications record.

<a id="ApplicationsArrayContainsCondition"></a>

`ApplicationsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ApplicationsContainsCondition"></a>

`ApplicationsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ApplicationsEndswithCondition"></a>

`ApplicationsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsEqCondition"></a>

`ApplicationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsFuzzyCondition"></a>

`ApplicationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsGtCondition"></a>

`ApplicationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsGteCondition"></a>

`ApplicationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsInCondition"></a>

`ApplicationsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInFilter`
    :   The type of the None singleton.

<a id="ApplicationsInFilter"></a>

`ApplicationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_note_id: list[int]`
    :   Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency.

    `answers: list[list[typing.Any]]`
    :   Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer.

    `candidate_id: list[int]`
    :   Id of the candidate (person) this application belongs to.

    `coordinator_id: list[int]`
    :   Id of the user assigned as coordinator on the application's job, or `null` when unassigned.

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 applications record.

    `custom_fields: list[dict[str, typing.Any]]`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: list[int]`
    :   Id from the Greenhouse v3 applications record.

    `job_id: list[int]`
    :   Id of the job this application is on. `null` for jobless prospect applications.

    `job_interview_stage_id: list[int]`
    :   Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `job_post_id: list[int]`
    :   Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role.

    `last_activity_at: list[str]`
    :   Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601.

    `location_address: list[str]`
    :   Free-form location string captured on the application (typically from the job post's location question).

    `needs_decision: list[bool]`
    :   `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage.

    `prospect: list[bool]`
    :   `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job.

    `prospective_job_ids: list[list[typing.Any]]`
    :   For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects.

    `recruiter_id: list[int]`
    :   Id of the user assigned as recruiter on the application's job, or `null` when unassigned.

    `referrer_id: list[int]`
    :   Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user.

    `rejected_at: list[str]`
    :   Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected.

    `rejection_reason_id: list[int]`
    :   Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected.

    `source_id: list[int]`
    :   Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set.

    `stage_id: list[int]`
    :   Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `stage_name: list[str]`
    :   Display name of the candidate's current interview stage on this application.

    `status: list[str]`
    :   Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 applications record.

<a id="ApplicationsKeywordCondition"></a>

`ApplicationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsListParams"></a>

`ApplicationsListParams(*args, **kwargs)`
:   Parameters for applications.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="ApplicationsLtCondition"></a>

`ApplicationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsLteCondition"></a>

`ApplicationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsNeqCondition"></a>

`ApplicationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsNotCondition"></a>

`ApplicationsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition`
    :   The type of the None singleton.

<a id="ApplicationsOrCondition"></a>

`ApplicationsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition]`
    :   The type of the None singleton.

<a id="ApplicationsSearchFilter"></a>

`ApplicationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering applications search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ApplicationsSearchQuery"></a>

`ApplicationsSearchQuery(*args, **kwargs)`
:   Search query for applications entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSortFilter]`
    :   The type of the None singleton.

<a id="ApplicationsSortFilter"></a>

`ApplicationsSortFilter(*args, **kwargs)`
:   Available fields for sorting applications search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_note_id: Literal['asc', 'desc']`
    :   Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency.

    `answers: Literal['asc', 'desc']`
    :   Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer.

    `candidate_id: Literal['asc', 'desc']`
    :   Id of the candidate (person) this application belongs to.

    `coordinator_id: Literal['asc', 'desc']`
    :   Id of the user assigned as coordinator on the application's job, or `null` when unassigned.

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 applications record.

    `custom_fields: Literal['asc', 'desc']`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 applications record.

    `job_id: Literal['asc', 'desc']`
    :   Id of the job this application is on. `null` for jobless prospect applications.

    `job_interview_stage_id: Literal['asc', 'desc']`
    :   Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `job_post_id: Literal['asc', 'desc']`
    :   Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role.

    `last_activity_at: Literal['asc', 'desc']`
    :   Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601.

    `location_address: Literal['asc', 'desc']`
    :   Free-form location string captured on the application (typically from the job post's location question).

    `needs_decision: Literal['asc', 'desc']`
    :   `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage.

    `prospect: Literal['asc', 'desc']`
    :   `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job.

    `prospective_job_ids: Literal['asc', 'desc']`
    :   For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects.

    `recruiter_id: Literal['asc', 'desc']`
    :   Id of the user assigned as recruiter on the application's job, or `null` when unassigned.

    `referrer_id: Literal['asc', 'desc']`
    :   Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user.

    `rejected_at: Literal['asc', 'desc']`
    :   Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected.

    `rejection_reason_id: Literal['asc', 'desc']`
    :   Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected.

    `source_id: Literal['asc', 'desc']`
    :   Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set.

    `stage_id: Literal['asc', 'desc']`
    :   Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `stage_name: Literal['asc', 'desc']`
    :   Display name of the candidate's current interview stage on this application.

    `status: Literal['asc', 'desc']`
    :   Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 applications record.

<a id="ApplicationsStartswithCondition"></a>

`ApplicationsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsStringFilter"></a>

`ApplicationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_note_id: str`
    :   Id of the note created when the candidate was submitted by an agency, or `null` if the application did not come through an agency.

    `answers: str`
    :   Free-text answers the candidate provided on the job post application form. Each entry pairs the question text with the candidate's answer.

    `candidate_id: str`
    :   Id of the candidate (person) this application belongs to.

    `coordinator_id: str`
    :   Id of the user assigned as coordinator on the application's job, or `null` when unassigned.

    `created_at: str`
    :   Created at from the Greenhouse v3 applications record.

    `custom_fields: str`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: str`
    :   Id from the Greenhouse v3 applications record.

    `job_id: str`
    :   Id of the job this application is on. `null` for jobless prospect applications.

    `job_interview_stage_id: str`
    :   Id of the job interview stage definition (see `GET /v3/job_interview_stages`) the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `job_post_id: str`
    :   Id of the job post the candidate applied through, or `null` if the application was created internally rather than from a posted role.

    `last_activity_at: str`
    :   Timestamp of the most recent activity on this application (notes, emails, stage changes, etc.), in ISO 8601.

    `location_address: str`
    :   Free-form location string captured on the application (typically from the job post's location question).

    `needs_decision: str`
    :   `true` when the application is waiting on a hiring-team decision (scorecard completion, advance/reject, etc.) in its current stage.

    `prospect: str`
    :   `true` for prospect applications (sourced candidates not yet attached to a single job), `false` for candidate applications on a specific job.

    `prospective_job_ids: str`
    :   For prospect applications, the ids of jobs the prospect is being considered for. Empty for non-prospect applications and for jobless prospects.

    `recruiter_id: str`
    :   Id of the user assigned as recruiter on the application's job, or `null` when unassigned.

    `referrer_id: str`
    :   Id of the referrer who credited this application, or `null` if there was no referral. References a referrer, not a Greenhouse user.

    `rejected_at: str`
    :   Timestamp the application was rejected, in ISO 8601. `null` for applications that have not been rejected.

    `rejection_reason_id: str`
    :   Id of the rejection reason selected for the application. References a `/v3/rejection_reasons` row scoped to the organization. `null` when the application was rejected without a reason, or has not been rejected.

    `source_id: str`
    :   Id of the source the application is attributed to (e.g. a job board, an event, an employee referral source). `null` if no source is set.

    `stage_id: str`
    :   Id of the interview stage the candidate is currently in for this application. `null` for prospect applications and applications in a terminal state.

    `stage_name: str`
    :   Display name of the candidate's current interview stage on this application.

    `status: str`
    :   Lifecycle status of the application. `in_process` for active candidates, `rejected` for rejected applications, `hired` once an offer is closed and the hire endpoint has fired, and `converted` for prospect applications that have been promoted to a candidate application via `convert_to_candidate`.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 applications record.

<a id="AttachmentsDownloadParams"></a>

`AttachmentsDownloadParams(*args, **kwargs)`
:   Parameters for attachments.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ids: list[int]`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

<a id="AttachmentsListParams"></a>

`AttachmentsListParams(*args, **kwargs)`
:   Parameters for attachments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_ids: list[int]`
    :   The type of the None singleton.

    `candidate_ids: list[int]`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="CandidatesAndCondition"></a>

`CandidatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition]`
    :   The type of the None singleton.

<a id="CandidatesAnyCondition"></a>

`CandidatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

<a id="CandidatesAnyValueFilter"></a>

`CandidatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `addresses: Any`
    :   Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`.

    `can_email: Any`
    :   Whether this candidate has consented to receive email communication from your organization.

    `company: Any`
    :   Candidate's current company, as entered on their profile.

    `created_at: Any`
    :   Created at from the Greenhouse v3 candidates record.

    `custom_fields: Any`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `email_addresses: Any`
    :   Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`.

    `first_name: Any`
    :   First name from the Greenhouse v3 candidates record.

    `id: Any`
    :   Id from the Greenhouse v3 candidates record.

    `last_activity_at: Any`
    :   Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601.

    `last_name: Any`
    :   Last name from the Greenhouse v3 candidates record.

    `linked_user_ids: Any`
    :   Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record).

    `phone_numbers: Any`
    :   Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`.

    `preferred_name: Any`
    :   Preferred or chosen name the candidate goes by, when different from their legal first name.

    `private: Any`
    :   If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`.

    `social_media_addresses: Any`
    :   Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned.

    `tags: Any`
    :   Candidate tag names applied to this candidate within your organization.

    `time_zone: Any`
    :   Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`).

    `title: Any`
    :   Candidate's current job title, as entered on their profile.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 candidates record.

    `website_addresses: Any`
    :   Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`.

<a id="CandidatesArrayContainsCondition"></a>

`CandidatesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

<a id="CandidatesContainsCondition"></a>

`CandidatesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

<a id="CandidatesEndswithCondition"></a>

`CandidatesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesEqCondition"></a>

`CandidatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesFuzzyCondition"></a>

`CandidatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesGtCondition"></a>

`CandidatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesGteCondition"></a>

`CandidatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesInCondition"></a>

`CandidatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInFilter`
    :   The type of the None singleton.

<a id="CandidatesInFilter"></a>

`CandidatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `addresses: list[list[typing.Any]]`
    :   Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`.

    `can_email: list[bool]`
    :   Whether this candidate has consented to receive email communication from your organization.

    `company: list[str]`
    :   Candidate's current company, as entered on their profile.

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 candidates record.

    `custom_fields: list[dict[str, typing.Any]]`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `email_addresses: list[list[typing.Any]]`
    :   Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`.

    `first_name: list[str]`
    :   First name from the Greenhouse v3 candidates record.

    `id: list[int]`
    :   Id from the Greenhouse v3 candidates record.

    `last_activity_at: list[str]`
    :   Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601.

    `last_name: list[str]`
    :   Last name from the Greenhouse v3 candidates record.

    `linked_user_ids: list[list[typing.Any]]`
    :   Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record).

    `phone_numbers: list[list[typing.Any]]`
    :   Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`.

    `preferred_name: list[str]`
    :   Preferred or chosen name the candidate goes by, when different from their legal first name.

    `private: list[bool]`
    :   If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`.

    `social_media_addresses: list[list[typing.Any]]`
    :   Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned.

    `tags: list[list[typing.Any]]`
    :   Candidate tag names applied to this candidate within your organization.

    `time_zone: list[str]`
    :   Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`).

    `title: list[str]`
    :   Candidate's current job title, as entered on their profile.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 candidates record.

    `website_addresses: list[list[typing.Any]]`
    :   Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`.

<a id="CandidatesKeywordCondition"></a>

`CandidatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesListParams"></a>

`CandidatesListParams(*args, **kwargs)`
:   Parameters for candidates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="CandidatesLtCondition"></a>

`CandidatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesLteCondition"></a>

`CandidatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesNeqCondition"></a>

`CandidatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesNotCondition"></a>

`CandidatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition`
    :   The type of the None singleton.

<a id="CandidatesOrCondition"></a>

`CandidatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition]`
    :   The type of the None singleton.

<a id="CandidatesSearchFilter"></a>

`CandidatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering candidates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CandidatesSearchQuery"></a>

`CandidatesSearchQuery(*args, **kwargs)`
:   Search query for candidates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.CandidatesSortFilter]`
    :   The type of the None singleton.

<a id="CandidatesSortFilter"></a>

`CandidatesSortFilter(*args, **kwargs)`
:   Available fields for sorting candidates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `addresses: Literal['asc', 'desc']`
    :   Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`.

    `can_email: Literal['asc', 'desc']`
    :   Whether this candidate has consented to receive email communication from your organization.

    `company: Literal['asc', 'desc']`
    :   Candidate's current company, as entered on their profile.

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 candidates record.

    `custom_fields: Literal['asc', 'desc']`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `email_addresses: Literal['asc', 'desc']`
    :   Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`.

    `first_name: Literal['asc', 'desc']`
    :   First name from the Greenhouse v3 candidates record.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 candidates record.

    `last_activity_at: Literal['asc', 'desc']`
    :   Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601.

    `last_name: Literal['asc', 'desc']`
    :   Last name from the Greenhouse v3 candidates record.

    `linked_user_ids: Literal['asc', 'desc']`
    :   Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record).

    `phone_numbers: Literal['asc', 'desc']`
    :   Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`.

    `preferred_name: Literal['asc', 'desc']`
    :   Preferred or chosen name the candidate goes by, when different from their legal first name.

    `private: Literal['asc', 'desc']`
    :   If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`.

    `social_media_addresses: Literal['asc', 'desc']`
    :   Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned.

    `tags: Literal['asc', 'desc']`
    :   Candidate tag names applied to this candidate within your organization.

    `time_zone: Literal['asc', 'desc']`
    :   Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`).

    `title: Literal['asc', 'desc']`
    :   Candidate's current job title, as entered on their profile.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 candidates record.

    `website_addresses: Literal['asc', 'desc']`
    :   Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`.

<a id="CandidatesStartswithCondition"></a>

`CandidatesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesStringFilter"></a>

`CandidatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `addresses: str`
    :   Postal addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `home`, `work`, or `other`.

    `can_email: str`
    :   Whether this candidate has consented to receive email communication from your organization.

    `company: str`
    :   Candidate's current company, as entered on their profile.

    `created_at: str`
    :   Created at from the Greenhouse v3 candidates record.

    `custom_fields: str`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `email_addresses: str`
    :   Email addresses on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `work`, or `other`.

    `first_name: str`
    :   First name from the Greenhouse v3 candidates record.

    `id: str`
    :   Id from the Greenhouse v3 candidates record.

    `last_activity_at: str`
    :   Timestamp of the most recent activity on any of the candidate's applications (notes, emails, stage changes, etc.), in ISO 8601.

    `last_name: str`
    :   Last name from the Greenhouse v3 candidates record.

    `linked_user_ids: str`
    :   Ids of Greenhouse users linked to this candidate (employees represented by both a user record and a candidate record).

    `phone_numbers: str`
    :   Phone numbers on the candidate's profile. Each entry pairs the `value` with a `type` such as `mobile`, `home`, `work`, `skype`, or `other`.

    `preferred_name: str`
    :   Preferred or chosen name the candidate goes by, when different from their legal first name.

    `private: str`
    :   If true, the candidate is restricted to users with `View Private Candidates` access. Defaults to `false`.

    `social_media_addresses: str`
    :   Social media handles or URLs on the candidate's profile. Social entries are untyped — only the `value` is returned.

    `tags: str`
    :   Candidate tag names applied to this candidate within your organization.

    `time_zone: str`
    :   Candidate's time zone as a Rails-style identifier (for example `Eastern Time (US & Canada)`).

    `title: str`
    :   Candidate's current job title, as entered on their profile.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 candidates record.

    `website_addresses: str`
    :   Personal websites or portfolio URLs on the candidate's profile. Each entry pairs the `value` with a `type` such as `personal`, `company`, `portfolio`, `blog`, or `other`.

<a id="DepartmentsAndCondition"></a>

`DepartmentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition]`
    :   The type of the None singleton.

<a id="DepartmentsAnyCondition"></a>

`DepartmentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="DepartmentsAnyValueFilter"></a>

`DepartmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Created at from the Greenhouse v3 departments record.

    `external_id: Any`
    :   Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set.

    `id: Any`
    :   Id from the Greenhouse v3 departments record.

    `name: Any`
    :   Display name of the department (e.g. `Engineering`, `Marketing`).

    `parent_id: Any`
    :   Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 departments record.

<a id="DepartmentsArrayContainsCondition"></a>

`DepartmentsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="DepartmentsContainsCondition"></a>

`DepartmentsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="DepartmentsEndswithCondition"></a>

`DepartmentsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsEqCondition"></a>

`DepartmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsFuzzyCondition"></a>

`DepartmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsGtCondition"></a>

`DepartmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsGteCondition"></a>

`DepartmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsInCondition"></a>

`DepartmentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInFilter`
    :   The type of the None singleton.

<a id="DepartmentsInFilter"></a>

`DepartmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 departments record.

    `external_id: list[str]`
    :   Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set.

    `id: list[int]`
    :   Id from the Greenhouse v3 departments record.

    `name: list[str]`
    :   Display name of the department (e.g. `Engineering`, `Marketing`).

    `parent_id: list[int]`
    :   Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 departments record.

<a id="DepartmentsKeywordCondition"></a>

`DepartmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsListParams"></a>

`DepartmentsListParams(*args, **kwargs)`
:   Parameters for departments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="DepartmentsLtCondition"></a>

`DepartmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsLteCondition"></a>

`DepartmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsNeqCondition"></a>

`DepartmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsNotCondition"></a>

`DepartmentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition`
    :   The type of the None singleton.

<a id="DepartmentsOrCondition"></a>

`DepartmentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition]`
    :   The type of the None singleton.

<a id="DepartmentsSearchFilter"></a>

`DepartmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering departments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Created at from the Greenhouse v3 departments record.

    `external_id: str | None`
    :   Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set.

    `id: int | None`
    :   Id from the Greenhouse v3 departments record.

    `name: str | None`
    :   Display name of the department (e.g. `Engineering`, `Marketing`).

    `parent_id: int | None`
    :   Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 departments record.

<a id="DepartmentsSearchQuery"></a>

`DepartmentsSearchQuery(*args, **kwargs)`
:   Search query for departments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSortFilter]`
    :   The type of the None singleton.

<a id="DepartmentsSortFilter"></a>

`DepartmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting departments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 departments record.

    `external_id: Literal['asc', 'desc']`
    :   Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 departments record.

    `name: Literal['asc', 'desc']`
    :   Display name of the department (e.g. `Engineering`, `Marketing`).

    `parent_id: Literal['asc', 'desc']`
    :   Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 departments record.

<a id="DepartmentsStartswithCondition"></a>

`DepartmentsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsStringFilter"></a>

`DepartmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Created at from the Greenhouse v3 departments record.

    `external_id: str`
    :   Partner-supplied identifier for the department, typically the matching id from an HRIS or other external system. Free-form string and `null` when no external id has been set.

    `id: str`
    :   Id from the Greenhouse v3 departments record.

    `name: str`
    :   Display name of the department (e.g. `Engineering`, `Marketing`).

    `parent_id: str`
    :   Id of the parent department in the organization's department tree. `null` for top-level departments. References another `/v3/departments` row.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 departments record.

<a id="InterviewsListParams"></a>

`InterviewsListParams(*args, **kwargs)`
:   Parameters for interviews.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="JobPostsAndCondition"></a>

`JobPostsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition]`
    :   The type of the None singleton.

<a id="JobPostsAnyCondition"></a>

`JobPostsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobPostsAnyValueFilter"></a>

`JobPostsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them.

    `content: Any`
    :   HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded.

    `created_at: Any`
    :   Created at from the Greenhouse v3 job posts record.

    `demographic_question_set_id: Any`
    :   Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data.

    `featured: Any`
    :   If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time.

    `first_published_at: Any`
    :   Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published.

    `id: Any`
    :   Id from the Greenhouse v3 job posts record.

    `internal: Any`
    :   If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time.

    `internal_content: Any`
    :   HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`.

    `job_board_id: Any`
    :   Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time.

    `job_id: Any`
    :   Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan.

    `language: Any`
    :   ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen.

    `live: Any`
    :   If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled.

    `public_url: Any`
    :   Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured.

    `questions: Any`
    :   Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form.

    `title: Any`
    :   Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 job posts record.

<a id="JobPostsArrayContainsCondition"></a>

`JobPostsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobPostsContainsCondition"></a>

`JobPostsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobPostsEndswithCondition"></a>

`JobPostsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStringFilter`
    :   The type of the None singleton.

<a id="JobPostsEqCondition"></a>

`JobPostsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostsFuzzyCondition"></a>

`JobPostsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStringFilter`
    :   The type of the None singleton.

<a id="JobPostsGtCondition"></a>

`JobPostsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostsGteCondition"></a>

`JobPostsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostsInCondition"></a>

`JobPostsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInFilter`
    :   The type of the None singleton.

<a id="JobPostsInFilter"></a>

`JobPostsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them.

    `content: list[str]`
    :   HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded.

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 job posts record.

    `demographic_question_set_id: list[int]`
    :   Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data.

    `featured: list[bool]`
    :   If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time.

    `first_published_at: list[str]`
    :   Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published.

    `id: list[int]`
    :   Id from the Greenhouse v3 job posts record.

    `internal: list[bool]`
    :   If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time.

    `internal_content: list[str]`
    :   HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`.

    `job_board_id: list[int]`
    :   Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time.

    `job_id: list[int]`
    :   Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan.

    `language: list[str]`
    :   ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen.

    `live: list[bool]`
    :   If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled.

    `public_url: list[str]`
    :   Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured.

    `questions: list[list[typing.Any]]`
    :   Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form.

    `title: list[str]`
    :   Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 job posts record.

<a id="JobPostsKeywordCondition"></a>

`JobPostsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStringFilter`
    :   The type of the None singleton.

<a id="JobPostsListParams"></a>

`JobPostsListParams(*args, **kwargs)`
:   Parameters for job_posts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="JobPostsLtCondition"></a>

`JobPostsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostsLteCondition"></a>

`JobPostsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostsNeqCondition"></a>

`JobPostsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostsNotCondition"></a>

`JobPostsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition`
    :   The type of the None singleton.

<a id="JobPostsOrCondition"></a>

`JobPostsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition]`
    :   The type of the None singleton.

<a id="JobPostsSearchFilter"></a>

`JobPostsSearchFilter(*args, **kwargs)`
:   Available fields for filtering job_posts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `public_url: str | None`
    :   Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured.

    `questions: list[typing.Any] | None`
    :   Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form.

    `title: str | None`
    :   Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 job posts record.

<a id="JobPostsSearchQuery"></a>

`JobPostsSearchQuery(*args, **kwargs)`
:   Search query for job_posts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.JobPostsSortFilter]`
    :   The type of the None singleton.

<a id="JobPostsSortFilter"></a>

`JobPostsSortFilter(*args, **kwargs)`
:   Available fields for sorting job_posts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them.

    `content: Literal['asc', 'desc']`
    :   HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded.

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 job posts record.

    `demographic_question_set_id: Literal['asc', 'desc']`
    :   Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data.

    `featured: Literal['asc', 'desc']`
    :   If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time.

    `first_published_at: Literal['asc', 'desc']`
    :   Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 job posts record.

    `internal: Literal['asc', 'desc']`
    :   If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time.

    `internal_content: Literal['asc', 'desc']`
    :   HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`.

    `job_board_id: Literal['asc', 'desc']`
    :   Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time.

    `job_id: Literal['asc', 'desc']`
    :   Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan.

    `language: Literal['asc', 'desc']`
    :   ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen.

    `live: Literal['asc', 'desc']`
    :   If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled.

    `public_url: Literal['asc', 'desc']`
    :   Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured.

    `questions: Literal['asc', 'desc']`
    :   Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form.

    `title: Literal['asc', 'desc']`
    :   Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 job posts record.

<a id="JobPostsStartswithCondition"></a>

`JobPostsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStringFilter`
    :   The type of the None singleton.

<a id="JobPostsStringFilter"></a>

`JobPostsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   If `true`, the post has not been deleted. Deleted posts are excluded by default; pass `active=false` on the list endpoint to retrieve them.

    `content: str`
    :   HTML body of the post shown to candidates on the job board. For internal posts this returns the `internal_content` instead. Sanitized server-side — only a limited element/attribute allowlist (including `iframe`, `video`, `source`) survives. `null` while the post is still being scaffolded.

    `created_at: str`
    :   Created at from the Greenhouse v3 job posts record.

    `demographic_question_set_id: str`
    :   Id of the demographic question set surfaced to candidates on this post for diversity, equity, and inclusion (DE&I) reporting. `null` when the post does not collect demographic data.

    `featured: str`
    :   If `true`, the post is currently featured on the organization's internal job board and surfaces in the weekly internal-jobs email. Only internal posts can be featured, and at most three can be featured at a time.

    `first_published_at: str`
    :   Timestamp the post first transitioned to `live`, in ISO 8601. `null` for posts that have never been published.

    `id: str`
    :   Id from the Greenhouse v3 job posts record.

    `internal: str`
    :   If `true`, the post lives on an internal job board and is visible only to existing employees signed in to the internal board. If `false`, the post is external and lives on a public-facing `job_board`. Set by the board the post is associated with at create time.

    `internal_content: str`
    :   HTML body shown on the internal job board when the post is also configured as internal. `null` for external-only posts. Same sanitization rules as `content`.

    `job_board_id: str`
    :   Id of the `job_board` this post is published to. Resolves to either an external (careers site, syndicated board) or internal job board depending on `internal`. Each post belongs to exactly one board at a time.

    `job_id: str`
    :   Id of the parent job (requisition) this post belongs to. A single job can have multiple posts; the job is the source of truth for the hiring team, openings, and interview plan.

    `language: str`
    :   ISO 639-1 locale of the post, used to render the candidate-facing application form in the matching language (e.g. `en`, `fr`, `ja`). `null` when no locale has been chosen.

    `live: str`
    :   If `true`, the post is published (`job_application_status` is `live`) and its job board is also live. A post on an unpublished board is **not** `live` — its `public_url` returns a 404 until the board is enabled.

    `public_url: str`
    :   Canonical public URL of the post on its job board, including the `gh_jid` tracking parameter. `null` when the post has no associated job board or the board has no public URL configured.

    `questions: str`
    :   Application form questions presented to candidates on this post, including default questions (resume, cover letter, basic info) and any custom questions configured by the hiring team. Ordered as they appear on the form.

    `title: str`
    :   Public-facing title shown to candidates on the job board (e.g. `Senior Backend Engineer, Remote`). Distinct from the internal `job.name` — a single job can have several posts with different titles, one per board, language, or geography.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 job posts record.

<a id="JobsAndCondition"></a>

`JobsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition]`
    :   The type of the None singleton.

<a id="JobsAnyCondition"></a>

`JobsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobsAnyValueFilter"></a>

`JobsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: Any`
    :   Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`.

    `confidential: Any`
    :   If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled.

    `copied_from_id: Any`
    :   Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job.

    `created_at: Any`
    :   Created at from the Greenhouse v3 jobs record.

    `custom_fields: Any`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `department_id: Any`
    :   Id of the department this job is assigned to. `null` when no department is set.

    `id: Any`
    :   Id from the Greenhouse v3 jobs record.

    `is_template: Any`
    :   If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`.

    `name: Any`
    :   Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`.

    `notes: Any`
    :   Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts.

    `office_ids: Any`
    :   Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set.

    `opened_at: Any`
    :   Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`.

    `requisition_id: Any`
    :   Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set.

    `status: Any`
    :   Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/{id}`.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 jobs record.

<a id="JobsArrayContainsCondition"></a>

`JobsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobsContainsCondition"></a>

`JobsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobsEndswithCondition"></a>

`JobsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsEqCondition"></a>

`JobsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsFuzzyCondition"></a>

`JobsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsGtCondition"></a>

`JobsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsGteCondition"></a>

`JobsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsInCondition"></a>

`JobsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.JobsInFilter`
    :   The type of the None singleton.

<a id="JobsInFilter"></a>

`JobsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: list[str]`
    :   Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`.

    `confidential: list[bool]`
    :   If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled.

    `copied_from_id: list[int]`
    :   Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job.

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 jobs record.

    `custom_fields: list[dict[str, typing.Any]]`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `department_id: list[int]`
    :   Id of the department this job is assigned to. `null` when no department is set.

    `id: list[int]`
    :   Id from the Greenhouse v3 jobs record.

    `is_template: list[bool]`
    :   If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`.

    `name: list[str]`
    :   Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`.

    `notes: list[str]`
    :   Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts.

    `office_ids: list[list[typing.Any]]`
    :   Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set.

    `opened_at: list[str]`
    :   Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`.

    `requisition_id: list[str]`
    :   Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set.

    `status: list[str]`
    :   Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/{id}`.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 jobs record.

<a id="JobsKeywordCondition"></a>

`JobsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsListParams"></a>

`JobsListParams(*args, **kwargs)`
:   Parameters for jobs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="JobsLtCondition"></a>

`JobsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsLteCondition"></a>

`JobsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsNeqCondition"></a>

`JobsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsNotCondition"></a>

`JobsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition`
    :   The type of the None singleton.

<a id="JobsOrCondition"></a>

`JobsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition]`
    :   The type of the None singleton.

<a id="JobsSearchFilter"></a>

`JobsSearchFilter(*args, **kwargs)`
:   Available fields for filtering jobs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="JobsSearchQuery"></a>

`JobsSearchQuery(*args, **kwargs)`
:   Search query for jobs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.JobsSortFilter]`
    :   The type of the None singleton.

<a id="JobsSortFilter"></a>

`JobsSortFilter(*args, **kwargs)`
:   Available fields for sorting jobs search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: Literal['asc', 'desc']`
    :   Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`.

    `confidential: Literal['asc', 'desc']`
    :   If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled.

    `copied_from_id: Literal['asc', 'desc']`
    :   Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job.

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 jobs record.

    `custom_fields: Literal['asc', 'desc']`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `department_id: Literal['asc', 'desc']`
    :   Id of the department this job is assigned to. `null` when no department is set.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 jobs record.

    `is_template: Literal['asc', 'desc']`
    :   If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`.

    `name: Literal['asc', 'desc']`
    :   Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`.

    `notes: Literal['asc', 'desc']`
    :   Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts.

    `office_ids: Literal['asc', 'desc']`
    :   Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set.

    `opened_at: Literal['asc', 'desc']`
    :   Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`.

    `requisition_id: Literal['asc', 'desc']`
    :   Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set.

    `status: Literal['asc', 'desc']`
    :   Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/{id}`.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 jobs record.

<a id="JobsStartswithCondition"></a>

`JobsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsStringFilter"></a>

`JobsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: str`
    :   Timestamp the job most recently transitioned to `closed`, in ISO 8601. `null` for jobs that are still `open` or `draft`.

    `confidential: str`
    :   If `true`, the job is restricted to users explicitly granted access on the Hiring Team. The legacy Confidential Jobs feature has been sunset — this flag cannot be set on new jobs and is preserved for jobs that already had it enabled.

    `copied_from_id: str`
    :   Id of the job (typically a template) this job was copied from on creation. `null` when the job was not created from another job.

    `created_at: str`
    :   Created at from the Greenhouse v3 jobs record.

    `custom_fields: str`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `department_id: str`
    :   Id of the department this job is assigned to. `null` when no department is set.

    `id: str`
    :   Id from the Greenhouse v3 jobs record.

    `is_template: str`
    :   If `true`, this job is a template used as the source for new jobs rather than a real requisition. Templates do not accept applications; reference them via `template_job_id` on `POST /v3/jobs`.

    `name: str`
    :   Internal job title shown to the hiring team in Greenhouse (e.g. `Senior Backend Engineer`). Distinct from the external-facing title on each `job_post`.

    `notes: str`
    :   Internal HTML notes about the job, surfaced to the hiring team in the Greenhouse UI. Not exposed on public job posts.

    `office_ids: str`
    :   Ids of the offices this job is assigned to. A job can span multiple offices; empty array or `null` when no offices are set.

    `opened_at: str`
    :   Timestamp the job first transitioned to `open`, in ISO 8601. `null` while the job is still in `draft`.

    `requisition_id: str`
    :   Partner-supplied external identifier for the requisition (e.g. an HRIS or ATS code). Free-form string, not unique across the organization, and `null` when no external id has been set.

    `status: str`
    :   Lifecycle status of the job. `draft` while it is being scaffolded, `open` once it has at least one open opening, and `closed` after every opening is closed. A job moves to `closed` automatically when its last open opening is closed via `PATCH /v3/openings/{id}`.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 jobs record.

<a id="OffersAndCondition"></a>

`OffersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition]`
    :   The type of the None singleton.

<a id="OffersAnyCondition"></a>

`OffersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyValueFilter`
    :   The type of the None singleton.

<a id="OffersAnyValueFilter"></a>

`OffersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: Any`
    :   Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted.

    `candidate_id: Any`
    :   Id of the candidate (person) receiving this offer. Resolved through the offer's application.

    `created_at: Any`
    :   Created at from the Greenhouse v3 offers record.

    `custom_fields: Any`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: Any`
    :   Id from the Greenhouse v3 offers record.

    `job_id: Any`
    :   Id of the job this offer's application is on.

    `opening_id: Any`
    :   Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening.

    `resolved_at: Any`
    :   Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/{id}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution.

    `sent_on: Any`
    :   Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent.

    `starts_on: Any`
    :   Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer.

    `status: Any`
    :   Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status).

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 offers record.

    `version: Any`
    :   Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application.

<a id="OffersArrayContainsCondition"></a>

`OffersArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyValueFilter`
    :   The type of the None singleton.

<a id="OffersContainsCondition"></a>

`OffersContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyValueFilter`
    :   The type of the None singleton.

<a id="OffersEndswithCondition"></a>

`OffersEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.OffersStringFilter`
    :   The type of the None singleton.

<a id="OffersEqCondition"></a>

`OffersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.OffersSearchFilter`
    :   The type of the None singleton.

<a id="OffersFuzzyCondition"></a>

`OffersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.OffersStringFilter`
    :   The type of the None singleton.

<a id="OffersGtCondition"></a>

`OffersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.OffersSearchFilter`
    :   The type of the None singleton.

<a id="OffersGteCondition"></a>

`OffersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.OffersSearchFilter`
    :   The type of the None singleton.

<a id="OffersInCondition"></a>

`OffersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.OffersInFilter`
    :   The type of the None singleton.

<a id="OffersInFilter"></a>

`OffersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: list[int]`
    :   Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted.

    `candidate_id: list[int]`
    :   Id of the candidate (person) receiving this offer. Resolved through the offer's application.

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 offers record.

    `custom_fields: list[dict[str, typing.Any]]`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: list[int]`
    :   Id from the Greenhouse v3 offers record.

    `job_id: list[int]`
    :   Id of the job this offer's application is on.

    `opening_id: list[int]`
    :   Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening.

    `resolved_at: list[str]`
    :   Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/{id}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution.

    `sent_on: list[str]`
    :   Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent.

    `starts_on: list[str]`
    :   Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer.

    `status: list[str]`
    :   Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status).

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 offers record.

    `version: list[int]`
    :   Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application.

<a id="OffersKeywordCondition"></a>

`OffersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.OffersStringFilter`
    :   The type of the None singleton.

<a id="OffersListParams"></a>

`OffersListParams(*args, **kwargs)`
:   Parameters for offers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="OffersLtCondition"></a>

`OffersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.OffersSearchFilter`
    :   The type of the None singleton.

<a id="OffersLteCondition"></a>

`OffersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.OffersSearchFilter`
    :   The type of the None singleton.

<a id="OffersNeqCondition"></a>

`OffersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.OffersSearchFilter`
    :   The type of the None singleton.

<a id="OffersNotCondition"></a>

`OffersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition`
    :   The type of the None singleton.

<a id="OffersOrCondition"></a>

`OffersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition]`
    :   The type of the None singleton.

<a id="OffersSearchFilter"></a>

`OffersSearchFilter(*args, **kwargs)`
:   Available fields for filtering offers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="OffersSearchQuery"></a>

`OffersSearchQuery(*args, **kwargs)`
:   Search query for offers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.OffersSortFilter]`
    :   The type of the None singleton.

<a id="OffersSortFilter"></a>

`OffersSortFilter(*args, **kwargs)`
:   Available fields for sorting offers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: Literal['asc', 'desc']`
    :   Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted.

    `candidate_id: Literal['asc', 'desc']`
    :   Id of the candidate (person) receiving this offer. Resolved through the offer's application.

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 offers record.

    `custom_fields: Literal['asc', 'desc']`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 offers record.

    `job_id: Literal['asc', 'desc']`
    :   Id of the job this offer's application is on.

    `opening_id: Literal['asc', 'desc']`
    :   Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening.

    `resolved_at: Literal['asc', 'desc']`
    :   Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/{id}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution.

    `sent_on: Literal['asc', 'desc']`
    :   Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent.

    `starts_on: Literal['asc', 'desc']`
    :   Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer.

    `status: Literal['asc', 'desc']`
    :   Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status).

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 offers record.

    `version: Literal['asc', 'desc']`
    :   Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application.

<a id="OffersStartswithCondition"></a>

`OffersStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.OffersStringFilter`
    :   The type of the None singleton.

<a id="OffersStringFilter"></a>

`OffersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: str`
    :   Id of the application this offer is extended on. Every offer belongs to exactly one application; the offer is voided if the application is rejected or deleted.

    `candidate_id: str`
    :   Id of the candidate (person) receiving this offer. Resolved through the offer's application.

    `created_at: str`
    :   Created at from the Greenhouse v3 offers record.

    `custom_fields: str`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `id: str`
    :   Id from the Greenhouse v3 offers record.

    `job_id: str`
    :   Id of the job this offer's application is on.

    `opening_id: str`
    :   Id of the specific opening this offer is being extended for. `null` when the offer has not yet been linked to an opening.

    `resolved_at: str`
    :   Timestamp the offer was resolved (`Accepted` or `Rejected`), in ISO 8601. Date updates submitted through `PATCH /v3/offers/{id}` are normalized to noon UTC on the supplied date. `null` while the offer is still `Created` or has been superseded as `Deprecated` without a resolution.

    `sent_on: str`
    :   Date the offer was sent to the candidate, in ISO 8601 (YYYY-MM-DD). `null` until the offer has been sent.

    `starts_on: str`
    :   Candidate's proposed start date, in ISO 8601 (YYYY-MM-DD). `null` when no start date has been set on the offer.

    `status: str`
    :   Lifecycle status of the offer. `Created` for offers still being drafted or pending approval, `Accepted` once the candidate accepts, `Rejected` if declined or withdrawn, and `Deprecated` for superseded prior versions (a new offer version replaces an earlier one with this status).

    `updated_at: str`
    :   Updated at from the Greenhouse v3 offers record.

    `version: str`
    :   Revision number of this offer within its application. Greenhouse creates a new offer row (incrementing `version`) whenever a tracked field on an existing offer changes — typically `starts_on`, `opening_id`, or a custom field configured to trigger a new version. Pair with `current_only=true` to filter the list endpoint down to the latest version per application.

<a id="OfficesAndCondition"></a>

`OfficesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition]`
    :   The type of the None singleton.

<a id="OfficesAnyCondition"></a>

`OfficesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyValueFilter`
    :   The type of the None singleton.

<a id="OfficesAnyValueFilter"></a>

`OfficesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Created at from the Greenhouse v3 offices record.

    `external_id: Any`
    :   Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled.

    `id: Any`
    :   Id from the Greenhouse v3 offices record.

    `location: Any`
    :   Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices.

    `name: Any`
    :   Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization.

    `parent_id: Any`
    :   Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization.

    `primary_in_house_contact_user_id: Any`
    :   Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 offices record.

<a id="OfficesArrayContainsCondition"></a>

`OfficesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyValueFilter`
    :   The type of the None singleton.

<a id="OfficesContainsCondition"></a>

`OfficesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyValueFilter`
    :   The type of the None singleton.

<a id="OfficesEndswithCondition"></a>

`OfficesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.OfficesStringFilter`
    :   The type of the None singleton.

<a id="OfficesEqCondition"></a>

`OfficesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.OfficesSearchFilter`
    :   The type of the None singleton.

<a id="OfficesFuzzyCondition"></a>

`OfficesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.OfficesStringFilter`
    :   The type of the None singleton.

<a id="OfficesGtCondition"></a>

`OfficesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.OfficesSearchFilter`
    :   The type of the None singleton.

<a id="OfficesGteCondition"></a>

`OfficesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.OfficesSearchFilter`
    :   The type of the None singleton.

<a id="OfficesInCondition"></a>

`OfficesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.OfficesInFilter`
    :   The type of the None singleton.

<a id="OfficesInFilter"></a>

`OfficesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 offices record.

    `external_id: list[str]`
    :   Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled.

    `id: list[int]`
    :   Id from the Greenhouse v3 offices record.

    `location: list[str]`
    :   Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices.

    `name: list[str]`
    :   Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization.

    `parent_id: list[int]`
    :   Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization.

    `primary_in_house_contact_user_id: list[int]`
    :   Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 offices record.

<a id="OfficesKeywordCondition"></a>

`OfficesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.OfficesStringFilter`
    :   The type of the None singleton.

<a id="OfficesListParams"></a>

`OfficesListParams(*args, **kwargs)`
:   Parameters for offices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="OfficesLtCondition"></a>

`OfficesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.OfficesSearchFilter`
    :   The type of the None singleton.

<a id="OfficesLteCondition"></a>

`OfficesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.OfficesSearchFilter`
    :   The type of the None singleton.

<a id="OfficesNeqCondition"></a>

`OfficesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.OfficesSearchFilter`
    :   The type of the None singleton.

<a id="OfficesNotCondition"></a>

`OfficesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition`
    :   The type of the None singleton.

<a id="OfficesOrCondition"></a>

`OfficesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition]`
    :   The type of the None singleton.

<a id="OfficesSearchFilter"></a>

`OfficesSearchFilter(*args, **kwargs)`
:   Available fields for filtering offices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Created at from the Greenhouse v3 offices record.

    `external_id: str | None`
    :   Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled.

    `id: int | None`
    :   Id from the Greenhouse v3 offices record.

    `location: str | None`
    :   Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices.

    `name: str | None`
    :   Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization.

    `parent_id: int | None`
    :   Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization.

    `primary_in_house_contact_user_id: int | None`
    :   Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 offices record.

<a id="OfficesSearchQuery"></a>

`OfficesSearchQuery(*args, **kwargs)`
:   Search query for offices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.OfficesSortFilter]`
    :   The type of the None singleton.

<a id="OfficesSortFilter"></a>

`OfficesSortFilter(*args, **kwargs)`
:   Available fields for sorting offices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 offices record.

    `external_id: Literal['asc', 'desc']`
    :   Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 offices record.

    `location: Literal['asc', 'desc']`
    :   Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices.

    `name: Literal['asc', 'desc']`
    :   Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization.

    `parent_id: Literal['asc', 'desc']`
    :   Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization.

    `primary_in_house_contact_user_id: Literal['asc', 'desc']`
    :   Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 offices record.

<a id="OfficesStartswithCondition"></a>

`OfficesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.OfficesStringFilter`
    :   The type of the None singleton.

<a id="OfficesStringFilter"></a>

`OfficesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Created at from the Greenhouse v3 offices record.

    `external_id: str`
    :   Stable identifier supplied by the customer or HRIS for cross-system reconciliation. `null` when no external id has been set. Available when the `org_structure_external_id` product flag is enabled.

    `id: str`
    :   Id from the Greenhouse v3 offices record.

    `location: str`
    :   Free-form physical location string for the office (e.g. `New York, NY, USA`). `null` for offices that have no location set, including most remote offices.

    `name: str`
    :   Display name of the office (e.g. `San Francisco`, `Remote (US)`). Unique among active offices in the same organization.

    `parent_id: str`
    :   Id of the parent office when offices are organized hierarchically. `null` for top-level offices. References another `/v3/offices` row in the same organization.

    `primary_in_house_contact_user_id: str`
    :   Id of the Greenhouse user designated as the office's primary internal contact, typically the local recruiting lead. References a `/v3/users` row. `null` when no contact has been assigned.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 offices record.

<a id="SourcesAndCondition"></a>

`SourcesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition]`
    :   The type of the None singleton.

<a id="SourcesAnyCondition"></a>

`SourcesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="SourcesAnyValueFilter"></a>

`SourcesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Created at from the Greenhouse v3 sources record.

    `id: Any`
    :   Id from the Greenhouse v3 sources record.

    `name: Any`
    :   Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name.

    `type_: Any`
    :   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 sources record.

<a id="SourcesArrayContainsCondition"></a>

`SourcesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="SourcesContainsCondition"></a>

`SourcesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyValueFilter`
    :   The type of the None singleton.

<a id="SourcesEndswithCondition"></a>

`SourcesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.SourcesStringFilter`
    :   The type of the None singleton.

<a id="SourcesEqCondition"></a>

`SourcesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.SourcesSearchFilter`
    :   The type of the None singleton.

<a id="SourcesFuzzyCondition"></a>

`SourcesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.SourcesStringFilter`
    :   The type of the None singleton.

<a id="SourcesGtCondition"></a>

`SourcesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.SourcesSearchFilter`
    :   The type of the None singleton.

<a id="SourcesGteCondition"></a>

`SourcesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.SourcesSearchFilter`
    :   The type of the None singleton.

<a id="SourcesInCondition"></a>

`SourcesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.SourcesInFilter`
    :   The type of the None singleton.

<a id="SourcesInFilter"></a>

`SourcesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 sources record.

    `id: list[int]`
    :   Id from the Greenhouse v3 sources record.

    `name: list[str]`
    :   Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name.

    `type_: list[dict[str, typing.Any]]`
    :   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 sources record.

<a id="SourcesKeywordCondition"></a>

`SourcesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.SourcesStringFilter`
    :   The type of the None singleton.

<a id="SourcesListParams"></a>

`SourcesListParams(*args, **kwargs)`
:   Parameters for sources.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="SourcesLtCondition"></a>

`SourcesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.SourcesSearchFilter`
    :   The type of the None singleton.

<a id="SourcesLteCondition"></a>

`SourcesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.SourcesSearchFilter`
    :   The type of the None singleton.

<a id="SourcesNeqCondition"></a>

`SourcesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.SourcesSearchFilter`
    :   The type of the None singleton.

<a id="SourcesNotCondition"></a>

`SourcesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition`
    :   The type of the None singleton.

<a id="SourcesOrCondition"></a>

`SourcesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition]`
    :   The type of the None singleton.

<a id="SourcesSearchFilter"></a>

`SourcesSearchFilter(*args, **kwargs)`
:   Available fields for filtering sources search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Created at from the Greenhouse v3 sources record.

    `id: int | None`
    :   Id from the Greenhouse v3 sources record.

    `name: str | None`
    :   Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name.

    `type_: dict[str, typing.Any] | None`
    :   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.

    `updated_at: str | None`
    :   Updated at from the Greenhouse v3 sources record.

<a id="SourcesSearchQuery"></a>

`SourcesSearchQuery(*args, **kwargs)`
:   Search query for sources entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.SourcesSortFilter]`
    :   The type of the None singleton.

<a id="SourcesSortFilter"></a>

`SourcesSortFilter(*args, **kwargs)`
:   Available fields for sorting sources search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 sources record.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 sources record.

    `name: Literal['asc', 'desc']`
    :   Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name.

    `type_: Literal['asc', 'desc']`
    :   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 sources record.

<a id="SourcesStartswithCondition"></a>

`SourcesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.SourcesStringFilter`
    :   The type of the None singleton.

<a id="SourcesStringFilter"></a>

`SourcesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Created at from the Greenhouse v3 sources record.

    `id: str`
    :   Id from the Greenhouse v3 sources record.

    `name: str`
    :   Display name of the source as recruiters see it in Greenhouse (e.g. `LinkedIn (Prospecting)`, `Indeed`, `Referral`, `Internal Applicant`, or a custom agency name). For organization-specific sources this is the label the org configured; for global Greenhouse sources it is the standard public name.

    `type_: str`
    :   The sourcing strategy this source rolls up to — the broader category used for reporting. Sources are grouped under sourcing strategies such as `Agencies`, `Referral`, `Third-party boards`, `Prospecting`, `Social media`, `Company marketing`, `In person event`, `MyGreenhouse`, and `Other`. Use the strategy when aggregating candidate volume by channel; use the source itself when reporting on a specific channel within that category.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 sources record.

<a id="UsersAndCondition"></a>

`UsersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersAnyCondition"></a>

`UsersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_id: Any`
    :   Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users.

    `created_at: Any`
    :   Created at from the Greenhouse v3 users record.

    `custom_fields: Any`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `deactivated: Any`
    :   Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/{id}/deactivate` and `POST /v3/users/{id}/activate`.

    `department_ids: Any`
    :   Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department.

    `emails: Any`
    :   All email addresses on the user's account, including the primary address and any additional verified addresses.

    `employee_id: Any`
    :   Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set.

    `first_name: Any`
    :   First name from the Greenhouse v3 users record.

    `id: Any`
    :   Id from the Greenhouse v3 users record.

    `interviewer_tags: Any`
    :   Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`.

    `job_title: Any`
    :   Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title.

    `last_name: Any`
    :   Last name from the Greenhouse v3 users record.

    `linked_candidate_ids: Any`
    :   Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications).

    `name: Any`
    :   Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly.

    `office_ids: Any`
    :   Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office.

    `primary_email: Any`
    :   Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string.

    `site_admin: Any`
    :   Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/{id}/revoke_permissions`.

    `updated_at: Any`
    :   Updated at from the Greenhouse v3 users record.

<a id="UsersArrayContainsCondition"></a>

`UsersArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEndswithCondition"></a>

`UsersEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.greenhouse.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.greenhouse.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.greenhouse.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.greenhouse.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.greenhouse.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersInCondition"></a>

`UsersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.greenhouse.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_id: list[int]`
    :   Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users.

    `created_at: list[str]`
    :   Created at from the Greenhouse v3 users record.

    `custom_fields: list[dict[str, typing.Any]]`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `deactivated: list[bool]`
    :   Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/{id}/deactivate` and `POST /v3/users/{id}/activate`.

    `department_ids: list[list[typing.Any]]`
    :   Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department.

    `emails: list[list[typing.Any]]`
    :   All email addresses on the user's account, including the primary address and any additional verified addresses.

    `employee_id: list[str]`
    :   Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set.

    `first_name: list[str]`
    :   First name from the Greenhouse v3 users record.

    `id: list[int]`
    :   Id from the Greenhouse v3 users record.

    `interviewer_tags: list[list[typing.Any]]`
    :   Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`.

    `job_title: list[str]`
    :   Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title.

    `last_name: list[str]`
    :   Last name from the Greenhouse v3 users record.

    `linked_candidate_ids: list[list[typing.Any]]`
    :   Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications).

    `name: list[str]`
    :   Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly.

    `office_ids: list[list[typing.Any]]`
    :   Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office.

    `primary_email: list[str]`
    :   Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string.

    `site_admin: list[bool]`
    :   Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/{id}/revoke_permissions`.

    `updated_at: list[str]`
    :   Updated at from the Greenhouse v3 users record.

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `ids: list[int]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `show_service_accounts: bool`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.greenhouse.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.greenhouse.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.greenhouse.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNotCondition"></a>

`UsersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition`
    :   The type of the None singleton.

<a id="UsersOrCondition"></a>

`UsersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_id: Literal['asc', 'desc']`
    :   Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users.

    `created_at: Literal['asc', 'desc']`
    :   Created at from the Greenhouse v3 users record.

    `custom_fields: Literal['asc', 'desc']`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `deactivated: Literal['asc', 'desc']`
    :   Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/{id}/deactivate` and `POST /v3/users/{id}/activate`.

    `department_ids: Literal['asc', 'desc']`
    :   Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department.

    `emails: Literal['asc', 'desc']`
    :   All email addresses on the user's account, including the primary address and any additional verified addresses.

    `employee_id: Literal['asc', 'desc']`
    :   Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set.

    `first_name: Literal['asc', 'desc']`
    :   First name from the Greenhouse v3 users record.

    `id: Literal['asc', 'desc']`
    :   Id from the Greenhouse v3 users record.

    `interviewer_tags: Literal['asc', 'desc']`
    :   Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`.

    `job_title: Literal['asc', 'desc']`
    :   Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title.

    `last_name: Literal['asc', 'desc']`
    :   Last name from the Greenhouse v3 users record.

    `linked_candidate_ids: Literal['asc', 'desc']`
    :   Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications).

    `name: Literal['asc', 'desc']`
    :   Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly.

    `office_ids: Literal['asc', 'desc']`
    :   Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office.

    `primary_email: Literal['asc', 'desc']`
    :   Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string.

    `site_admin: Literal['asc', 'desc']`
    :   Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/{id}/revoke_permissions`.

    `updated_at: Literal['asc', 'desc']`
    :   Updated at from the Greenhouse v3 users record.

<a id="UsersStartswithCondition"></a>

`UsersStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.greenhouse.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agency_id: str`
    :   Id of the staffing agency this user belongs to, when the user is an external agency recruiter rather than an employee of your organization. `null` for in-house users.

    `created_at: str`
    :   Created at from the Greenhouse v3 users record.

    `custom_fields: str`
    :   Org-defined custom fields keyed by the field's `name_key`. Each value carries the field's display `name`, its `type`, and its `value`.

    `deactivated: str`
    :   Whether the user has been deactivated. Deactivated users cannot sign in or be assigned to new jobs, but their historical activity (notes, scorecards, emails) is preserved. Toggle via `POST /v3/users/{id}/deactivate` and `POST /v3/users/{id}/activate`.

    `department_ids: str`
    :   Ids of the departments this user is assigned to. Used to scope future job permissions and to filter the user list by department. Empty when the user is not pinned to any department.

    `emails: str`
    :   All email addresses on the user's account, including the primary address and any additional verified addresses.

    `employee_id: str`
    :   Partner-supplied external employee identifier, typically the user's HRIS or payroll id. Free-form string; not unique across organizations and `null` when no employee id has been set.

    `first_name: str`
    :   First name from the Greenhouse v3 users record.

    `id: str`
    :   Id from the Greenhouse v3 users record.

    `interviewer_tags: str`
    :   Interviewer tags applied to this user — the labeled skill or panel groupings (e.g. `Senior Engineer`, `Bar Raiser`) used to suggest qualified interviewers when building an interview plan. Each entry pairs the tag's `id` with its `name`.

    `job_title: str`
    :   Free-form job title set on the user's Greenhouse profile (e.g. `Senior Recruiter`). Not synchronized with any HRIS title.

    `last_name: str`
    :   Last name from the Greenhouse v3 users record.

    `linked_candidate_ids: str`
    :   Ids of candidate records linked to this user. Populated when an employee is represented by both a user record (for Greenhouse access) and a candidate record (for past or internal applications).

    `name: str`
    :   Concatenation of `first_name` and `last_name` rendered as a single display string. Provided for convenience; partners that need either component should read `first_name`/`last_name` directly.

    `office_ids: str`
    :   Ids of the offices this user is assigned to. Used to scope future job permissions and to filter the user list by office. Empty when the user is not pinned to any office.

    `primary_email: str`
    :   Primary email address on the user's account. Sign-in identifier and the address Greenhouse uses for outbound mail; additional verified addresses are not surfaced here. Service accounts (integration/ISU users) have no email and are excluded from this endpoint by default; when included via `show_service_accounts=true`, their `primary_email` is an empty string.

    `site_admin: str`
    :   Whether the user holds the Site Admin role. Site admins have unrestricted access to every non-confidential job and to organization-level settings. Demote a site admin to a Basic user with `POST /v3/users/{id}/revoke_permissions`.

    `updated_at: str`
    :   Updated at from the Greenhouse v3 users record.