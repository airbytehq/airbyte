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

<a id="ApplicationAttachmentDownloadParams"></a>

`ApplicationAttachmentDownloadParams(*args, **kwargs)`
:   Parameters for application_attachment.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_index: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `range_header: str`
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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition]`
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

    `answers: Any`
    :   Answers provided in the application.

    `applied_at: Any`
    :   Timestamp when the candidate applied.

    `attachments: Any`
    :   Attachments uploaded with the application.

    `candidate_id: Any`
    :   Unique identifier for the candidate.

    `credited_to: Any`
    :   Information about the employee who credited the application.

    `current_stage: Any`
    :   Current stage of the application process.

    `id: Any`
    :   Unique identifier for the application.

    `job_post_id: Any`
    :   The type of the None singleton.

    `jobs: Any`
    :   Jobs applied for by the candidate.

    `last_activity_at: Any`
    :   Timestamp of the last activity on the application.

    `location: Any`
    :   Location related to the application.

    `prospect: Any`
    :   Status of the application prospect.

    `prospect_detail: Any`
    :   Details related to the application prospect.

    `prospective_department: Any`
    :   Prospective department for the candidate.

    `prospective_office: Any`
    :   Prospective office for the candidate.

    `rejected_at: Any`
    :   Timestamp when the application was rejected.

    `rejection_details: Any`
    :   Details related to the application rejection.

    `rejection_reason: Any`
    :   Reason for the application rejection.

    `source: Any`
    :   Source of the application.

    `status: Any`
    :   Status of the application.

<a id="ApplicationsContainsCondition"></a>

`ApplicationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyValueFilter`
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

<a id="ApplicationsGetParams"></a>

`ApplicationsGetParams(*args, **kwargs)`
:   Parameters for applications.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

    `answers: list[list[typing.Any]]`
    :   Answers provided in the application.

    `applied_at: list[str]`
    :   Timestamp when the candidate applied.

    `attachments: list[list[typing.Any]]`
    :   Attachments uploaded with the application.

    `candidate_id: list[int]`
    :   Unique identifier for the candidate.

    `credited_to: list[dict[str, typing.Any]]`
    :   Information about the employee who credited the application.

    `current_stage: list[dict[str, typing.Any]]`
    :   Current stage of the application process.

    `id: list[int]`
    :   Unique identifier for the application.

    `job_post_id: list[int]`
    :   The type of the None singleton.

    `jobs: list[list[typing.Any]]`
    :   Jobs applied for by the candidate.

    `last_activity_at: list[str]`
    :   Timestamp of the last activity on the application.

    `location: list[str]`
    :   Location related to the application.

    `prospect: list[bool]`
    :   Status of the application prospect.

    `prospect_detail: list[dict[str, typing.Any]]`
    :   Details related to the application prospect.

    `prospective_department: list[str]`
    :   Prospective department for the candidate.

    `prospective_office: list[str]`
    :   Prospective office for the candidate.

    `rejected_at: list[str]`
    :   Timestamp when the application was rejected.

    `rejection_details: list[dict[str, typing.Any]]`
    :   Details related to the application rejection.

    `rejection_reason: list[dict[str, typing.Any]]`
    :   Reason for the application rejection.

    `source: list[dict[str, typing.Any]]`
    :   Source of the application.

    `status: list[str]`
    :   Status of the application.

<a id="ApplicationsKeywordCondition"></a>

`ApplicationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsLikeCondition"></a>

`ApplicationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsListParams"></a>

`ApplicationsListParams(*args, **kwargs)`
:   Parameters for applications.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `job_id: int`
    :   The type of the None singleton.

    `last_activity_after: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `status: str`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition]`
    :   The type of the None singleton.

<a id="ApplicationsSearchFilter"></a>

`ApplicationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering applications search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ApplicationsSearchQuery"></a>

`ApplicationsSearchQuery(*args, **kwargs)`
:   Search query for applications entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.ApplicationsSortFilter]`
    :   The type of the None singleton.

<a id="ApplicationsSortFilter"></a>

`ApplicationsSortFilter(*args, **kwargs)`
:   Available fields for sorting applications search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: Literal['asc', 'desc']`
    :   Answers provided in the application.

    `applied_at: Literal['asc', 'desc']`
    :   Timestamp when the candidate applied.

    `attachments: Literal['asc', 'desc']`
    :   Attachments uploaded with the application.

    `candidate_id: Literal['asc', 'desc']`
    :   Unique identifier for the candidate.

    `credited_to: Literal['asc', 'desc']`
    :   Information about the employee who credited the application.

    `current_stage: Literal['asc', 'desc']`
    :   Current stage of the application process.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the application.

    `job_post_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `jobs: Literal['asc', 'desc']`
    :   Jobs applied for by the candidate.

    `last_activity_at: Literal['asc', 'desc']`
    :   Timestamp of the last activity on the application.

    `location: Literal['asc', 'desc']`
    :   Location related to the application.

    `prospect: Literal['asc', 'desc']`
    :   Status of the application prospect.

    `prospect_detail: Literal['asc', 'desc']`
    :   Details related to the application prospect.

    `prospective_department: Literal['asc', 'desc']`
    :   Prospective department for the candidate.

    `prospective_office: Literal['asc', 'desc']`
    :   Prospective office for the candidate.

    `rejected_at: Literal['asc', 'desc']`
    :   Timestamp when the application was rejected.

    `rejection_details: Literal['asc', 'desc']`
    :   Details related to the application rejection.

    `rejection_reason: Literal['asc', 'desc']`
    :   Reason for the application rejection.

    `source: Literal['asc', 'desc']`
    :   Source of the application.

    `status: Literal['asc', 'desc']`
    :   Status of the application.

<a id="ApplicationsStringFilter"></a>

`ApplicationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: str`
    :   Answers provided in the application.

    `applied_at: str`
    :   Timestamp when the candidate applied.

    `attachments: str`
    :   Attachments uploaded with the application.

    `candidate_id: str`
    :   Unique identifier for the candidate.

    `credited_to: str`
    :   Information about the employee who credited the application.

    `current_stage: str`
    :   Current stage of the application process.

    `id: str`
    :   Unique identifier for the application.

    `job_post_id: str`
    :   The type of the None singleton.

    `jobs: str`
    :   Jobs applied for by the candidate.

    `last_activity_at: str`
    :   Timestamp of the last activity on the application.

    `location: str`
    :   Location related to the application.

    `prospect: str`
    :   Status of the application prospect.

    `prospect_detail: str`
    :   Details related to the application prospect.

    `prospective_department: str`
    :   Prospective department for the candidate.

    `prospective_office: str`
    :   Prospective office for the candidate.

    `rejected_at: str`
    :   Timestamp when the application was rejected.

    `rejection_details: str`
    :   Details related to the application rejection.

    `rejection_reason: str`
    :   Reason for the application rejection.

    `source: str`
    :   Source of the application.

    `status: str`
    :   Status of the application.

<a id="CandidateAttachmentDownloadParams"></a>

`CandidateAttachmentDownloadParams(*args, **kwargs)`
:   Parameters for candidate_attachment.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_index: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `range_header: str`
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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition]`
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
    :   Candidate's addresses

    `application_ids: Any`
    :   List of application IDs

    `applications: Any`
    :   An array of all applications made by candidates.

    `attachments: Any`
    :   Attachments related to the candidate

    `can_email: Any`
    :   Indicates if candidate can be emailed

    `company: Any`
    :   Company where the candidate is associated

    `coordinator: Any`
    :   Coordinator assigned to the candidate

    `created_at: Any`
    :   Date and time of creation

    `custom_fields: Any`
    :   Custom fields associated with the candidate

    `educations: Any`
    :   List of candidate's educations

    `email_addresses: Any`
    :   Candidate's email addresses

    `employments: Any`
    :   List of candidate's employments

    `first_name: Any`
    :   Candidate's first name

    `id: Any`
    :   Candidate's ID

    `is_private: Any`
    :   Indicates if the candidate's data is private

    `keyed_custom_fields: Any`
    :   Keyed custom fields associated with the candidate

    `last_activity: Any`
    :   Details of the last activity related to the candidate

    `last_name: Any`
    :   Candidate's last name

    `phone_numbers: Any`
    :   Candidate's phone numbers

    `photo_url: Any`
    :   URL of the candidate's profile photo

    `recruiter: Any`
    :   Recruiter assigned to the candidate

    `social_media_addresses: Any`
    :   Candidate's social media addresses

    `tags: Any`
    :   Tags associated with the candidate

    `title: Any`
    :   Candidate's title (e.g., Mr., Mrs., Dr.)

    `updated_at: Any`
    :   Date and time of last update

    `website_addresses: Any`
    :   List of candidate's website addresses

<a id="CandidatesContainsCondition"></a>

`CandidatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyValueFilter`
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

<a id="CandidatesGetParams"></a>

`CandidatesGetParams(*args, **kwargs)`
:   Parameters for candidates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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
    :   Candidate's addresses

    `application_ids: list[list[typing.Any]]`
    :   List of application IDs

    `applications: list[list[typing.Any]]`
    :   An array of all applications made by candidates.

    `attachments: list[list[typing.Any]]`
    :   Attachments related to the candidate

    `can_email: list[bool]`
    :   Indicates if candidate can be emailed

    `company: list[str]`
    :   Company where the candidate is associated

    `coordinator: list[str]`
    :   Coordinator assigned to the candidate

    `created_at: list[str]`
    :   Date and time of creation

    `custom_fields: list[dict[str, typing.Any]]`
    :   Custom fields associated with the candidate

    `educations: list[list[typing.Any]]`
    :   List of candidate's educations

    `email_addresses: list[list[typing.Any]]`
    :   Candidate's email addresses

    `employments: list[list[typing.Any]]`
    :   List of candidate's employments

    `first_name: list[str]`
    :   Candidate's first name

    `id: list[int]`
    :   Candidate's ID

    `is_private: list[bool]`
    :   Indicates if the candidate's data is private

    `keyed_custom_fields: list[dict[str, typing.Any]]`
    :   Keyed custom fields associated with the candidate

    `last_activity: list[str]`
    :   Details of the last activity related to the candidate

    `last_name: list[str]`
    :   Candidate's last name

    `phone_numbers: list[list[typing.Any]]`
    :   Candidate's phone numbers

    `photo_url: list[str]`
    :   URL of the candidate's profile photo

    `recruiter: list[str]`
    :   Recruiter assigned to the candidate

    `social_media_addresses: list[list[typing.Any]]`
    :   Candidate's social media addresses

    `tags: list[list[typing.Any]]`
    :   Tags associated with the candidate

    `title: list[str]`
    :   Candidate's title (e.g., Mr., Mrs., Dr.)

    `updated_at: list[str]`
    :   Date and time of last update

    `website_addresses: list[list[typing.Any]]`
    :   List of candidate's website addresses

<a id="CandidatesKeywordCondition"></a>

`CandidatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesLikeCondition"></a>

`CandidatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesListParams"></a>

`CandidatesListParams(*args, **kwargs)`
:   Parameters for candidates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition]`
    :   The type of the None singleton.

<a id="CandidatesSearchFilter"></a>

`CandidatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering candidates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CandidatesSearchQuery"></a>

`CandidatesSearchQuery(*args, **kwargs)`
:   Search query for candidates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.CandidatesAnyCondition`
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
    :   Candidate's addresses

    `application_ids: Literal['asc', 'desc']`
    :   List of application IDs

    `applications: Literal['asc', 'desc']`
    :   An array of all applications made by candidates.

    `attachments: Literal['asc', 'desc']`
    :   Attachments related to the candidate

    `can_email: Literal['asc', 'desc']`
    :   Indicates if candidate can be emailed

    `company: Literal['asc', 'desc']`
    :   Company where the candidate is associated

    `coordinator: Literal['asc', 'desc']`
    :   Coordinator assigned to the candidate

    `created_at: Literal['asc', 'desc']`
    :   Date and time of creation

    `custom_fields: Literal['asc', 'desc']`
    :   Custom fields associated with the candidate

    `educations: Literal['asc', 'desc']`
    :   List of candidate's educations

    `email_addresses: Literal['asc', 'desc']`
    :   Candidate's email addresses

    `employments: Literal['asc', 'desc']`
    :   List of candidate's employments

    `first_name: Literal['asc', 'desc']`
    :   Candidate's first name

    `id: Literal['asc', 'desc']`
    :   Candidate's ID

    `is_private: Literal['asc', 'desc']`
    :   Indicates if the candidate's data is private

    `keyed_custom_fields: Literal['asc', 'desc']`
    :   Keyed custom fields associated with the candidate

    `last_activity: Literal['asc', 'desc']`
    :   Details of the last activity related to the candidate

    `last_name: Literal['asc', 'desc']`
    :   Candidate's last name

    `phone_numbers: Literal['asc', 'desc']`
    :   Candidate's phone numbers

    `photo_url: Literal['asc', 'desc']`
    :   URL of the candidate's profile photo

    `recruiter: Literal['asc', 'desc']`
    :   Recruiter assigned to the candidate

    `social_media_addresses: Literal['asc', 'desc']`
    :   Candidate's social media addresses

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the candidate

    `title: Literal['asc', 'desc']`
    :   Candidate's title (e.g., Mr., Mrs., Dr.)

    `updated_at: Literal['asc', 'desc']`
    :   Date and time of last update

    `website_addresses: Literal['asc', 'desc']`
    :   List of candidate's website addresses

<a id="CandidatesStringFilter"></a>

`CandidatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `addresses: str`
    :   Candidate's addresses

    `application_ids: str`
    :   List of application IDs

    `applications: str`
    :   An array of all applications made by candidates.

    `attachments: str`
    :   Attachments related to the candidate

    `can_email: str`
    :   Indicates if candidate can be emailed

    `company: str`
    :   Company where the candidate is associated

    `coordinator: str`
    :   Coordinator assigned to the candidate

    `created_at: str`
    :   Date and time of creation

    `custom_fields: str`
    :   Custom fields associated with the candidate

    `educations: str`
    :   List of candidate's educations

    `email_addresses: str`
    :   Candidate's email addresses

    `employments: str`
    :   List of candidate's employments

    `first_name: str`
    :   Candidate's first name

    `id: str`
    :   Candidate's ID

    `is_private: str`
    :   Indicates if the candidate's data is private

    `keyed_custom_fields: str`
    :   Keyed custom fields associated with the candidate

    `last_activity: str`
    :   Details of the last activity related to the candidate

    `last_name: str`
    :   Candidate's last name

    `phone_numbers: str`
    :   Candidate's phone numbers

    `photo_url: str`
    :   URL of the candidate's profile photo

    `recruiter: str`
    :   Recruiter assigned to the candidate

    `social_media_addresses: str`
    :   Candidate's social media addresses

    `tags: str`
    :   Tags associated with the candidate

    `title: str`
    :   Candidate's title (e.g., Mr., Mrs., Dr.)

    `updated_at: str`
    :   Date and time of last update

    `website_addresses: str`
    :   List of candidate's website addresses

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition]`
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

    `child_department_external_ids: Any`
    :   External IDs of child departments associated with this department.

    `child_ids: Any`
    :   Unique IDs of child departments associated with this department.

    `external_id: Any`
    :   External ID of this department.

    `id: Any`
    :   Unique ID of this department.

    `name: Any`
    :   Name of the department.

    `parent_department_external_id: Any`
    :   External ID of the parent department of this department.

    `parent_id: Any`
    :   Unique ID of the parent department of this department.

<a id="DepartmentsContainsCondition"></a>

`DepartmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyValueFilter`
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

<a id="DepartmentsGetParams"></a>

`DepartmentsGetParams(*args, **kwargs)`
:   Parameters for departments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

    `child_department_external_ids: list[list[typing.Any]]`
    :   External IDs of child departments associated with this department.

    `child_ids: list[list[typing.Any]]`
    :   Unique IDs of child departments associated with this department.

    `external_id: list[str]`
    :   External ID of this department.

    `id: list[int]`
    :   Unique ID of this department.

    `name: list[str]`
    :   Name of the department.

    `parent_department_external_id: list[str]`
    :   External ID of the parent department of this department.

    `parent_id: list[int]`
    :   Unique ID of the parent department of this department.

<a id="DepartmentsKeywordCondition"></a>

`DepartmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsLikeCondition"></a>

`DepartmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsListParams"></a>

`DepartmentsListParams(*args, **kwargs)`
:   Parameters for departments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition]`
    :   The type of the None singleton.

<a id="DepartmentsSearchFilter"></a>

`DepartmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering departments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `child_department_external_ids: list[typing.Any] | None`
    :   External IDs of child departments associated with this department.

    `child_ids: list[typing.Any] | None`
    :   Unique IDs of child departments associated with this department.

    `external_id: str | None`
    :   External ID of this department.

    `id: int | None`
    :   Unique ID of this department.

    `name: str | None`
    :   Name of the department.

    `parent_department_external_id: str | None`
    :   External ID of the parent department of this department.

    `parent_id: int | None`
    :   Unique ID of the parent department of this department.

<a id="DepartmentsSearchQuery"></a>

`DepartmentsSearchQuery(*args, **kwargs)`
:   Search query for departments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.DepartmentsSortFilter]`
    :   The type of the None singleton.

<a id="DepartmentsSortFilter"></a>

`DepartmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting departments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `child_department_external_ids: Literal['asc', 'desc']`
    :   External IDs of child departments associated with this department.

    `child_ids: Literal['asc', 'desc']`
    :   Unique IDs of child departments associated with this department.

    `external_id: Literal['asc', 'desc']`
    :   External ID of this department.

    `id: Literal['asc', 'desc']`
    :   Unique ID of this department.

    `name: Literal['asc', 'desc']`
    :   Name of the department.

    `parent_department_external_id: Literal['asc', 'desc']`
    :   External ID of the parent department of this department.

    `parent_id: Literal['asc', 'desc']`
    :   Unique ID of the parent department of this department.

<a id="DepartmentsStringFilter"></a>

`DepartmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `child_department_external_ids: str`
    :   External IDs of child departments associated with this department.

    `child_ids: str`
    :   Unique IDs of child departments associated with this department.

    `external_id: str`
    :   External ID of this department.

    `id: str`
    :   Unique ID of this department.

    `name: str`
    :   Name of the department.

    `parent_department_external_id: str`
    :   External ID of the parent department of this department.

    `parent_id: str`
    :   Unique ID of the parent department of this department.

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition]`
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
    :   Flag indicating if the job post is active or not.

    `content: Any`
    :   Content or description of the job post.

    `created_at: Any`
    :   Date and time when the job post was created.

    `demographic_question_set_id: Any`
    :   ID of the demographic question set associated with the job post.

    `external: Any`
    :   Flag indicating if the job post is external or not.

    `first_published_at: Any`
    :   Date and time when the job post was first published.

    `id: Any`
    :   Unique identifier of the job post.

    `internal: Any`
    :   Flag indicating if the job post is internal or not.

    `internal_content: Any`
    :   Internal content or description of the job post.

    `job_id: Any`
    :   ID of the job associated with the job post.

    `live: Any`
    :   Flag indicating if the job post is live or not.

    `location: Any`
    :   Details about the job post location.

    `questions: Any`
    :   List of questions related to the job post.

    `title: Any`
    :   Title or headline of the job post.

    `updated_at: Any`
    :   Date and time when the job post was last updated.

<a id="JobPostsContainsCondition"></a>

`JobPostsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyValueFilter`
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

<a id="JobPostsGetParams"></a>

`JobPostsGetParams(*args, **kwargs)`
:   Parameters for job_posts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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
    :   Flag indicating if the job post is active or not.

    `content: list[str]`
    :   Content or description of the job post.

    `created_at: list[str]`
    :   Date and time when the job post was created.

    `demographic_question_set_id: list[int]`
    :   ID of the demographic question set associated with the job post.

    `external: list[bool]`
    :   Flag indicating if the job post is external or not.

    `first_published_at: list[str]`
    :   Date and time when the job post was first published.

    `id: list[int]`
    :   Unique identifier of the job post.

    `internal: list[bool]`
    :   Flag indicating if the job post is internal or not.

    `internal_content: list[str]`
    :   Internal content or description of the job post.

    `job_id: list[int]`
    :   ID of the job associated with the job post.

    `live: list[bool]`
    :   Flag indicating if the job post is live or not.

    `location: list[dict[str, typing.Any]]`
    :   Details about the job post location.

    `questions: list[list[typing.Any]]`
    :   List of questions related to the job post.

    `title: list[str]`
    :   Title or headline of the job post.

    `updated_at: list[str]`
    :   Date and time when the job post was last updated.

<a id="JobPostsKeywordCondition"></a>

`JobPostsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStringFilter`
    :   The type of the None singleton.

<a id="JobPostsLikeCondition"></a>

`JobPostsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsStringFilter`
    :   The type of the None singleton.

<a id="JobPostsListParams"></a>

`JobPostsListParams(*args, **kwargs)`
:   Parameters for job_posts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `live: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition]`
    :   The type of the None singleton.

<a id="JobPostsSearchFilter"></a>

`JobPostsSearchFilter(*args, **kwargs)`
:   Available fields for filtering job_posts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `questions: list[typing.Any] | None`
    :   List of questions related to the job post.

    `title: str | None`
    :   Title or headline of the job post.

    `updated_at: str | None`
    :   Date and time when the job post was last updated.

<a id="JobPostsSearchQuery"></a>

`JobPostsSearchQuery(*args, **kwargs)`
:   Search query for job_posts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.JobPostsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobPostsAnyCondition`
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
    :   Flag indicating if the job post is active or not.

    `content: Literal['asc', 'desc']`
    :   Content or description of the job post.

    `created_at: Literal['asc', 'desc']`
    :   Date and time when the job post was created.

    `demographic_question_set_id: Literal['asc', 'desc']`
    :   ID of the demographic question set associated with the job post.

    `external: Literal['asc', 'desc']`
    :   Flag indicating if the job post is external or not.

    `first_published_at: Literal['asc', 'desc']`
    :   Date and time when the job post was first published.

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the job post.

    `internal: Literal['asc', 'desc']`
    :   Flag indicating if the job post is internal or not.

    `internal_content: Literal['asc', 'desc']`
    :   Internal content or description of the job post.

    `job_id: Literal['asc', 'desc']`
    :   ID of the job associated with the job post.

    `live: Literal['asc', 'desc']`
    :   Flag indicating if the job post is live or not.

    `location: Literal['asc', 'desc']`
    :   Details about the job post location.

    `questions: Literal['asc', 'desc']`
    :   List of questions related to the job post.

    `title: Literal['asc', 'desc']`
    :   Title or headline of the job post.

    `updated_at: Literal['asc', 'desc']`
    :   Date and time when the job post was last updated.

<a id="JobPostsStringFilter"></a>

`JobPostsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Flag indicating if the job post is active or not.

    `content: str`
    :   Content or description of the job post.

    `created_at: str`
    :   Date and time when the job post was created.

    `demographic_question_set_id: str`
    :   ID of the demographic question set associated with the job post.

    `external: str`
    :   Flag indicating if the job post is external or not.

    `first_published_at: str`
    :   Date and time when the job post was first published.

    `id: str`
    :   Unique identifier of the job post.

    `internal: str`
    :   Flag indicating if the job post is internal or not.

    `internal_content: str`
    :   Internal content or description of the job post.

    `job_id: str`
    :   ID of the job associated with the job post.

    `live: str`
    :   Flag indicating if the job post is live or not.

    `location: str`
    :   Details about the job post location.

    `questions: str`
    :   List of questions related to the job post.

    `title: str`
    :   Title or headline of the job post.

    `updated_at: str`
    :   Date and time when the job post was last updated.

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition]`
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
    :   The date and time the job was closed

    `confidential: Any`
    :   Indicates if the job details are confidential

    `copied_from_id: Any`
    :   The ID of the job from which this job was copied

    `created_at: Any`
    :   The date and time the job was created

    `custom_fields: Any`
    :   Custom fields related to the job

    `departments: Any`
    :   Departments associated with the job

    `hiring_team: Any`
    :   Members of the hiring team for the job

    `id: Any`
    :   Unique ID of the job

    `is_template: Any`
    :   Indicates if the job is a template

    `keyed_custom_fields: Any`
    :   Keyed custom fields related to the job

    `name: Any`
    :   Name of the job

    `notes: Any`
    :   Additional notes or comments about the job

    `offices: Any`
    :   Offices associated with the job

    `opened_at: Any`
    :   The date and time the job was opened

    `openings: Any`
    :   Openings associated with the job

    `requisition_id: Any`
    :   ID associated with the job requisition

    `status: Any`
    :   Current status of the job

    `updated_at: Any`
    :   The date and time the job was last updated

<a id="JobsContainsCondition"></a>

`JobsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyValueFilter`
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

<a id="JobsGetParams"></a>

`JobsGetParams(*args, **kwargs)`
:   Parameters for jobs.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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
    :   The date and time the job was closed

    `confidential: list[bool]`
    :   Indicates if the job details are confidential

    `copied_from_id: list[int]`
    :   The ID of the job from which this job was copied

    `created_at: list[str]`
    :   The date and time the job was created

    `custom_fields: list[dict[str, typing.Any]]`
    :   Custom fields related to the job

    `departments: list[list[typing.Any]]`
    :   Departments associated with the job

    `hiring_team: list[dict[str, typing.Any]]`
    :   Members of the hiring team for the job

    `id: list[int]`
    :   Unique ID of the job

    `is_template: list[bool]`
    :   Indicates if the job is a template

    `keyed_custom_fields: list[dict[str, typing.Any]]`
    :   Keyed custom fields related to the job

    `name: list[str]`
    :   Name of the job

    `notes: list[str]`
    :   Additional notes or comments about the job

    `offices: list[list[typing.Any]]`
    :   Offices associated with the job

    `opened_at: list[str]`
    :   The date and time the job was opened

    `openings: list[list[typing.Any]]`
    :   Openings associated with the job

    `requisition_id: list[str]`
    :   ID associated with the job requisition

    `status: list[str]`
    :   Current status of the job

    `updated_at: list[str]`
    :   The date and time the job was last updated

<a id="JobsKeywordCondition"></a>

`JobsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsLikeCondition"></a>

`JobsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsListParams"></a>

`JobsListParams(*args, **kwargs)`
:   Parameters for jobs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition]`
    :   The type of the None singleton.

<a id="JobsSearchFilter"></a>

`JobsSearchFilter(*args, **kwargs)`
:   Available fields for filtering jobs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="JobsSearchQuery"></a>

`JobsSearchQuery(*args, **kwargs)`
:   Search query for jobs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.JobsEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsInCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.JobsAnyCondition`
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
    :   The date and time the job was closed

    `confidential: Literal['asc', 'desc']`
    :   Indicates if the job details are confidential

    `copied_from_id: Literal['asc', 'desc']`
    :   The ID of the job from which this job was copied

    `created_at: Literal['asc', 'desc']`
    :   The date and time the job was created

    `custom_fields: Literal['asc', 'desc']`
    :   Custom fields related to the job

    `departments: Literal['asc', 'desc']`
    :   Departments associated with the job

    `hiring_team: Literal['asc', 'desc']`
    :   Members of the hiring team for the job

    `id: Literal['asc', 'desc']`
    :   Unique ID of the job

    `is_template: Literal['asc', 'desc']`
    :   Indicates if the job is a template

    `keyed_custom_fields: Literal['asc', 'desc']`
    :   Keyed custom fields related to the job

    `name: Literal['asc', 'desc']`
    :   Name of the job

    `notes: Literal['asc', 'desc']`
    :   Additional notes or comments about the job

    `offices: Literal['asc', 'desc']`
    :   Offices associated with the job

    `opened_at: Literal['asc', 'desc']`
    :   The date and time the job was opened

    `openings: Literal['asc', 'desc']`
    :   Openings associated with the job

    `requisition_id: Literal['asc', 'desc']`
    :   ID associated with the job requisition

    `status: Literal['asc', 'desc']`
    :   Current status of the job

    `updated_at: Literal['asc', 'desc']`
    :   The date and time the job was last updated

<a id="JobsStringFilter"></a>

`JobsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: str`
    :   The date and time the job was closed

    `confidential: str`
    :   Indicates if the job details are confidential

    `copied_from_id: str`
    :   The ID of the job from which this job was copied

    `created_at: str`
    :   The date and time the job was created

    `custom_fields: str`
    :   Custom fields related to the job

    `departments: str`
    :   Departments associated with the job

    `hiring_team: str`
    :   Members of the hiring team for the job

    `id: str`
    :   Unique ID of the job

    `is_template: str`
    :   Indicates if the job is a template

    `keyed_custom_fields: str`
    :   Keyed custom fields related to the job

    `name: str`
    :   Name of the job

    `notes: str`
    :   Additional notes or comments about the job

    `offices: str`
    :   Offices associated with the job

    `opened_at: str`
    :   The date and time the job was opened

    `openings: str`
    :   Openings associated with the job

    `requisition_id: str`
    :   ID associated with the job requisition

    `status: str`
    :   Current status of the job

    `updated_at: str`
    :   The date and time the job was last updated

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition]`
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
    :   Unique identifier for the application associated with the offer

    `candidate_id: Any`
    :   Unique identifier for the candidate associated with the offer

    `created_at: Any`
    :   Timestamp indicating when the offer was created

    `custom_fields: Any`
    :   Additional custom fields related to the offer

    `id: Any`
    :   Unique identifier for the offer

    `job_id: Any`
    :   Unique identifier for the job associated with the offer

    `keyed_custom_fields: Any`
    :   Keyed custom fields associated with the offer

    `opening: Any`
    :   Details about the job opening

    `resolved_at: Any`
    :   Timestamp indicating when the offer was resolved

    `sent_at: Any`
    :   Timestamp indicating when the offer was sent

    `starts_at: Any`
    :   Timestamp indicating when the offer starts

    `status: Any`
    :   Status of the offer

    `updated_at: Any`
    :   Timestamp indicating when the offer was last updated

    `version: Any`
    :   Version of the offer data

<a id="OffersContainsCondition"></a>

`OffersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyValueFilter`
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

<a id="OffersGetParams"></a>

`OffersGetParams(*args, **kwargs)`
:   Parameters for offers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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
    :   Unique identifier for the application associated with the offer

    `candidate_id: list[int]`
    :   Unique identifier for the candidate associated with the offer

    `created_at: list[str]`
    :   Timestamp indicating when the offer was created

    `custom_fields: list[dict[str, typing.Any]]`
    :   Additional custom fields related to the offer

    `id: list[int]`
    :   Unique identifier for the offer

    `job_id: list[int]`
    :   Unique identifier for the job associated with the offer

    `keyed_custom_fields: list[dict[str, typing.Any]]`
    :   Keyed custom fields associated with the offer

    `opening: list[dict[str, typing.Any]]`
    :   Details about the job opening

    `resolved_at: list[str]`
    :   Timestamp indicating when the offer was resolved

    `sent_at: list[str]`
    :   Timestamp indicating when the offer was sent

    `starts_at: list[str]`
    :   Timestamp indicating when the offer starts

    `status: list[str]`
    :   Status of the offer

    `updated_at: list[str]`
    :   Timestamp indicating when the offer was last updated

    `version: list[int]`
    :   Version of the offer data

<a id="OffersKeywordCondition"></a>

`OffersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.OffersStringFilter`
    :   The type of the None singleton.

<a id="OffersLikeCondition"></a>

`OffersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.OffersStringFilter`
    :   The type of the None singleton.

<a id="OffersListParams"></a>

`OffersListParams(*args, **kwargs)`
:   Parameters for offers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `resolved_after: str`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition]`
    :   The type of the None singleton.

<a id="OffersSearchFilter"></a>

`OffersSearchFilter(*args, **kwargs)`
:   Available fields for filtering offers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="OffersSearchQuery"></a>

`OffersSearchQuery(*args, **kwargs)`
:   Search query for offers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.OffersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OffersAnyCondition`
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
    :   Unique identifier for the application associated with the offer

    `candidate_id: Literal['asc', 'desc']`
    :   Unique identifier for the candidate associated with the offer

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the offer was created

    `custom_fields: Literal['asc', 'desc']`
    :   Additional custom fields related to the offer

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the offer

    `job_id: Literal['asc', 'desc']`
    :   Unique identifier for the job associated with the offer

    `keyed_custom_fields: Literal['asc', 'desc']`
    :   Keyed custom fields associated with the offer

    `opening: Literal['asc', 'desc']`
    :   Details about the job opening

    `resolved_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the offer was resolved

    `sent_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the offer was sent

    `starts_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the offer starts

    `status: Literal['asc', 'desc']`
    :   Status of the offer

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the offer was last updated

    `version: Literal['asc', 'desc']`
    :   Version of the offer data

<a id="OffersStringFilter"></a>

`OffersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: str`
    :   Unique identifier for the application associated with the offer

    `candidate_id: str`
    :   Unique identifier for the candidate associated with the offer

    `created_at: str`
    :   Timestamp indicating when the offer was created

    `custom_fields: str`
    :   Additional custom fields related to the offer

    `id: str`
    :   Unique identifier for the offer

    `job_id: str`
    :   Unique identifier for the job associated with the offer

    `keyed_custom_fields: str`
    :   Keyed custom fields associated with the offer

    `opening: str`
    :   Details about the job opening

    `resolved_at: str`
    :   Timestamp indicating when the offer was resolved

    `sent_at: str`
    :   Timestamp indicating when the offer was sent

    `starts_at: str`
    :   Timestamp indicating when the offer starts

    `status: str`
    :   Status of the offer

    `updated_at: str`
    :   Timestamp indicating when the offer was last updated

    `version: str`
    :   Version of the offer data

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition]`
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

    `child_ids: Any`
    :   IDs of child offices associated with this office

    `child_office_external_ids: Any`
    :   External IDs of child offices associated with this office

    `external_id: Any`
    :   Unique identifier for this office in the external system

    `id: Any`
    :   Unique identifier for this office in the API system

    `location: Any`
    :   Location details of this office

    `name: Any`
    :   Name of the office

    `parent_id: Any`
    :   ID of the parent office, if this office is a branch office

    `parent_office_external_id: Any`
    :   External ID of the parent office in the external system

    `primary_contact_user_id: Any`
    :   User ID of the primary contact person for this office

<a id="OfficesContainsCondition"></a>

`OfficesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyValueFilter`
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

<a id="OfficesGetParams"></a>

`OfficesGetParams(*args, **kwargs)`
:   Parameters for offices.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

    `child_ids: list[list[typing.Any]]`
    :   IDs of child offices associated with this office

    `child_office_external_ids: list[list[typing.Any]]`
    :   External IDs of child offices associated with this office

    `external_id: list[str]`
    :   Unique identifier for this office in the external system

    `id: list[int]`
    :   Unique identifier for this office in the API system

    `location: list[dict[str, typing.Any]]`
    :   Location details of this office

    `name: list[str]`
    :   Name of the office

    `parent_id: list[int]`
    :   ID of the parent office, if this office is a branch office

    `parent_office_external_id: list[str]`
    :   External ID of the parent office in the external system

    `primary_contact_user_id: list[int]`
    :   User ID of the primary contact person for this office

<a id="OfficesKeywordCondition"></a>

`OfficesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.OfficesStringFilter`
    :   The type of the None singleton.

<a id="OfficesLikeCondition"></a>

`OfficesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.OfficesStringFilter`
    :   The type of the None singleton.

<a id="OfficesListParams"></a>

`OfficesListParams(*args, **kwargs)`
:   Parameters for offices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition]`
    :   The type of the None singleton.

<a id="OfficesSearchFilter"></a>

`OfficesSearchFilter(*args, **kwargs)`
:   Available fields for filtering offices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `name: str | None`
    :   Name of the office

    `parent_id: int | None`
    :   ID of the parent office, if this office is a branch office

    `parent_office_external_id: str | None`
    :   External ID of the parent office in the external system

    `primary_contact_user_id: int | None`
    :   User ID of the primary contact person for this office

<a id="OfficesSearchQuery"></a>

`OfficesSearchQuery(*args, **kwargs)`
:   Search query for offices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.OfficesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.OfficesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.OfficesSortFilter]`
    :   The type of the None singleton.

<a id="OfficesSortFilter"></a>

`OfficesSortFilter(*args, **kwargs)`
:   Available fields for sorting offices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `child_ids: Literal['asc', 'desc']`
    :   IDs of child offices associated with this office

    `child_office_external_ids: Literal['asc', 'desc']`
    :   External IDs of child offices associated with this office

    `external_id: Literal['asc', 'desc']`
    :   Unique identifier for this office in the external system

    `id: Literal['asc', 'desc']`
    :   Unique identifier for this office in the API system

    `location: Literal['asc', 'desc']`
    :   Location details of this office

    `name: Literal['asc', 'desc']`
    :   Name of the office

    `parent_id: Literal['asc', 'desc']`
    :   ID of the parent office, if this office is a branch office

    `parent_office_external_id: Literal['asc', 'desc']`
    :   External ID of the parent office in the external system

    `primary_contact_user_id: Literal['asc', 'desc']`
    :   User ID of the primary contact person for this office

<a id="OfficesStringFilter"></a>

`OfficesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `child_ids: str`
    :   IDs of child offices associated with this office

    `child_office_external_ids: str`
    :   External IDs of child offices associated with this office

    `external_id: str`
    :   Unique identifier for this office in the external system

    `id: str`
    :   Unique identifier for this office in the API system

    `location: str`
    :   Location details of this office

    `name: str`
    :   Name of the office

    `parent_id: str`
    :   ID of the parent office, if this office is a branch office

    `parent_office_external_id: str`
    :   External ID of the parent office in the external system

    `primary_contact_user_id: str`
    :   User ID of the primary contact person for this office

<a id="ScheduledInterviewsGetParams"></a>

`ScheduledInterviewsGetParams(*args, **kwargs)`
:   Parameters for scheduled_interviews.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ScheduledInterviewsListParams"></a>

`ScheduledInterviewsListParams(*args, **kwargs)`
:   Parameters for scheduled_interviews.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `ends_before: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `starts_after: str`
    :   The type of the None singleton.

    `updated_after: str`
    :   The type of the None singleton.

    `updated_before: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition]`
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

    `id: Any`
    :   The unique identifier for the source.

    `name: Any`
    :   The name of the source.

    `type_: Any`
    :   Type of the data source

<a id="SourcesContainsCondition"></a>

`SourcesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyValueFilter`
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

    `id: list[int]`
    :   The unique identifier for the source.

    `name: list[str]`
    :   The name of the source.

    `type_: list[dict[str, typing.Any]]`
    :   Type of the data source

<a id="SourcesKeywordCondition"></a>

`SourcesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.SourcesStringFilter`
    :   The type of the None singleton.

<a id="SourcesLikeCondition"></a>

`SourcesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.SourcesStringFilter`
    :   The type of the None singleton.

<a id="SourcesListParams"></a>

`SourcesListParams(*args, **kwargs)`
:   Parameters for sources.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition]`
    :   The type of the None singleton.

<a id="SourcesSearchFilter"></a>

`SourcesSearchFilter(*args, **kwargs)`
:   Available fields for filtering sources search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int | None`
    :   The unique identifier for the source.

    `name: str | None`
    :   The name of the source.

    `type_: dict[str, typing.Any] | None`
    :   Type of the data source

<a id="SourcesSearchQuery"></a>

`SourcesSearchQuery(*args, **kwargs)`
:   Search query for sources entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.SourcesEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesInCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.SourcesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.SourcesSortFilter]`
    :   The type of the None singleton.

<a id="SourcesSortFilter"></a>

`SourcesSortFilter(*args, **kwargs)`
:   Available fields for sorting sources search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   The unique identifier for the source.

    `name: Literal['asc', 'desc']`
    :   The name of the source.

    `type_: Literal['asc', 'desc']`
    :   Type of the data source

<a id="SourcesStringFilter"></a>

`SourcesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The unique identifier for the source.

    `name: str`
    :   The name of the source.

    `type_: str`
    :   Type of the data source

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

    `and: list[airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition]`
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

    `created_at: Any`
    :   The date and time when the user account was created.

    `departments: Any`
    :   List of departments associated with users

    `disabled: Any`
    :   Indicates whether the user account is disabled.

    `emails: Any`
    :   Email addresses of the users

    `employee_id: Any`
    :   Employee identifier for the user.

    `first_name: Any`
    :   The first name of the user.

    `id: Any`
    :   Unique identifier for the user.

    `last_name: Any`
    :   The last name of the user.

    `linked_candidate_ids: Any`
    :   IDs of candidates linked to the user.

    `name: Any`
    :   The full name of the user.

    `offices: Any`
    :   List of office locations where users are based

    `primary_email_address: Any`
    :   The primary email address of the user.

    `site_admin: Any`
    :   Indicates whether the user is a site administrator.

    `updated_at: Any`
    :   The date and time when the user account was last updated.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyValueFilter`
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

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

    `created_at: list[str]`
    :   The date and time when the user account was created.

    `departments: list[list[typing.Any]]`
    :   List of departments associated with users

    `disabled: list[bool]`
    :   Indicates whether the user account is disabled.

    `emails: list[list[typing.Any]]`
    :   Email addresses of the users

    `employee_id: list[str]`
    :   Employee identifier for the user.

    `first_name: list[str]`
    :   The first name of the user.

    `id: list[int]`
    :   Unique identifier for the user.

    `last_name: list[str]`
    :   The last name of the user.

    `linked_candidate_ids: list[list[typing.Any]]`
    :   IDs of candidates linked to the user.

    `name: list[str]`
    :   The full name of the user.

    `offices: list[list[typing.Any]]`
    :   List of office locations where users are based

    `primary_email_address: list[str]`
    :   The primary email address of the user.

    `site_admin: list[bool]`
    :   Indicates whether the user is a site administrator.

    `updated_at: list[str]`
    :   The date and time when the user account was last updated.

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.greenhouse.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.greenhouse.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_after: str`
    :   The type of the None singleton.

    `updated_before: str`
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

    `not: airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.greenhouse.types.UsersEqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNeqCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersGteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLtCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLteCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersInCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersLikeCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersContainsCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersNotCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAndCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersOrCondition | airbyte_agent_sdk.connectors.greenhouse.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.greenhouse.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the user account was created.

    `departments: Literal['asc', 'desc']`
    :   List of departments associated with users

    `disabled: Literal['asc', 'desc']`
    :   Indicates whether the user account is disabled.

    `emails: Literal['asc', 'desc']`
    :   Email addresses of the users

    `employee_id: Literal['asc', 'desc']`
    :   Employee identifier for the user.

    `first_name: Literal['asc', 'desc']`
    :   The first name of the user.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user.

    `last_name: Literal['asc', 'desc']`
    :   The last name of the user.

    `linked_candidate_ids: Literal['asc', 'desc']`
    :   IDs of candidates linked to the user.

    `name: Literal['asc', 'desc']`
    :   The full name of the user.

    `offices: Literal['asc', 'desc']`
    :   List of office locations where users are based

    `primary_email_address: Literal['asc', 'desc']`
    :   The primary email address of the user.

    `site_admin: Literal['asc', 'desc']`
    :   Indicates whether the user is a site administrator.

    `updated_at: Literal['asc', 'desc']`
    :   The date and time when the user account was last updated.

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   The date and time when the user account was created.

    `departments: str`
    :   List of departments associated with users

    `disabled: str`
    :   Indicates whether the user account is disabled.

    `emails: str`
    :   Email addresses of the users

    `employee_id: str`
    :   Employee identifier for the user.

    `first_name: str`
    :   The first name of the user.

    `id: str`
    :   Unique identifier for the user.

    `last_name: str`
    :   The last name of the user.

    `linked_candidate_ids: str`
    :   IDs of candidates linked to the user.

    `name: str`
    :   The full name of the user.

    `offices: str`
    :   List of office locations where users are based

    `primary_email_address: str`
    :   The primary email address of the user.

    `site_admin: str`
    :   Indicates whether the user is a site administrator.

    `updated_at: str`
    :   The date and time when the user account was last updated.