---
id: airbyte_agent_sdk-connectors-ashby-types
title: airbyte_agent_sdk.connectors.ashby.types
---

Module airbyte_agent_sdk.connectors.ashby.types
===============================================
Type definitions for ashby connector.

Classes
-------

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

`ApplicationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`ApplicationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

`ApplicationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

`ApplicationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.ApplicationsStringFilter`
    :   The type of the None singleton.

`ApplicationsGetParams(*args, **kwargs)`
:   Parameters for applications.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: str`
    :   The type of the None singleton.

`ApplicationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

`ApplicationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.ashby.types.ApplicationsInFilter`
    :   The type of the None singleton.

`ApplicationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`ApplicationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.ApplicationsStringFilter`
    :   The type of the None singleton.

`ApplicationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.ApplicationsStringFilter`
    :   The type of the None singleton.

`ApplicationsListParams(*args, **kwargs)`
:   Parameters for applications.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`ApplicationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

`ApplicationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

`ApplicationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition]`
    :   The type of the None singleton.

`ApplicationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering applications search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`ApplicationsSearchQuery(*args, **kwargs)`
:   Search query for applications entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.ApplicationsSortFilter]`
    :   The type of the None singleton.

`ApplicationsSortFilter(*args, **kwargs)`
:   Available fields for sorting applications search results.

    ### Ancestors (in MRO)

    * builtins.dict

`ApplicationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`ArchiveReasonsListParams(*args, **kwargs)`
:   Parameters for archive_reasons.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`CandidateTagsListParams(*args, **kwargs)`
:   Parameters for candidate_tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

`CandidatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`CandidatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

`CandidatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

`CandidatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.CandidatesStringFilter`
    :   The type of the None singleton.

`CandidatesGetParams(*args, **kwargs)`
:   Parameters for candidates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`CandidatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

`CandidatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.ashby.types.CandidatesInFilter`
    :   The type of the None singleton.

`CandidatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`CandidatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.CandidatesStringFilter`
    :   The type of the None singleton.

`CandidatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.CandidatesStringFilter`
    :   The type of the None singleton.

`CandidatesListParams(*args, **kwargs)`
:   Parameters for candidates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`CandidatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

`CandidatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

`CandidatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition]`
    :   The type of the None singleton.

`CandidatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering candidates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`CandidatesSearchQuery(*args, **kwargs)`
:   Search query for candidates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.CandidatesSortFilter]`
    :   The type of the None singleton.

`CandidatesSortFilter(*args, **kwargs)`
:   Available fields for sorting candidates search results.

    ### Ancestors (in MRO)

    * builtins.dict

`CandidatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`CustomFieldsListParams(*args, **kwargs)`
:   Parameters for custom_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`DepartmentsGetParams(*args, **kwargs)`
:   Parameters for departments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `department_id: str`
    :   The type of the None singleton.

`DepartmentsListParams(*args, **kwargs)`
:   Parameters for departments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`FeedbackFormDefinitionsListParams(*args, **kwargs)`
:   Parameters for feedback_form_definitions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`JobPostingsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.JobPostingsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyCondition]`
    :   The type of the None singleton.

`JobPostingsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyValueFilter`
    :   The type of the None singleton.

`JobPostingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`JobPostingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyValueFilter`
    :   The type of the None singleton.

`JobPostingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

`JobPostingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.JobPostingsStringFilter`
    :   The type of the None singleton.

`JobPostingsGetParams(*args, **kwargs)`
:   Parameters for job_postings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `job_posting_id: str`
    :   The type of the None singleton.

`JobPostingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

`JobPostingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

`JobPostingsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.ashby.types.JobPostingsInFilter`
    :   The type of the None singleton.

`JobPostingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`JobPostingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.JobPostingsStringFilter`
    :   The type of the None singleton.

`JobPostingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.JobPostingsStringFilter`
    :   The type of the None singleton.

`JobPostingsListParams(*args, **kwargs)`
:   Parameters for job_postings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`JobPostingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

`JobPostingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

`JobPostingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

`JobPostingsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.ashby.types.JobPostingsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyCondition`
    :   The type of the None singleton.

`JobPostingsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.JobPostingsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyCondition]`
    :   The type of the None singleton.

`JobPostingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering job_postings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`JobPostingsSearchQuery(*args, **kwargs)`
:   Search query for job_postings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.JobPostingsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.JobPostingsSortFilter]`
    :   The type of the None singleton.

`JobPostingsSortFilter(*args, **kwargs)`
:   Available fields for sorting job_postings search results.

    ### Ancestors (in MRO)

    * builtins.dict

`JobPostingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.ashby.types.JobsAnyValueFilter`
    :   The type of the None singleton.

`JobsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`JobsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.JobsAnyValueFilter`
    :   The type of the None singleton.

`JobsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

`JobsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.JobsStringFilter`
    :   The type of the None singleton.

`JobsGetParams(*args, **kwargs)`
:   Parameters for jobs.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`JobsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

`JobsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.ashby.types.JobsInFilter`
    :   The type of the None singleton.

`JobsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`JobsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.JobsStringFilter`
    :   The type of the None singleton.

`JobsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.JobsStringFilter`
    :   The type of the None singleton.

`JobsListParams(*args, **kwargs)`
:   Parameters for jobs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`JobsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

`JobsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

`JobsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition]`
    :   The type of the None singleton.

`JobsSearchFilter(*args, **kwargs)`
:   Available fields for filtering jobs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`JobsSearchQuery(*args, **kwargs)`
:   Search query for jobs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.JobsSortFilter]`
    :   The type of the None singleton.

`JobsSortFilter(*args, **kwargs)`
:   Available fields for sorting jobs search results.

    ### Ancestors (in MRO)

    * builtins.dict

`JobsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`LocationsGetParams(*args, **kwargs)`
:   Parameters for locations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `location_id: str`
    :   The type of the None singleton.

`LocationsListParams(*args, **kwargs)`
:   Parameters for locations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`SourcesListParams(*args, **kwargs)`
:   Parameters for sources.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition]`
    :   The type of the None singleton.

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

    `any: airbyte_agent_sdk.connectors.ashby.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_id: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

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

    `in: airbyte_agent_sdk.connectors.ashby.types.UsersInFilter`
    :   The type of the None singleton.

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

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

    `not: airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition`
    :   The type of the None singleton.

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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition]`
    :   The type of the None singleton.

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.UsersSortFilter]`
    :   The type of the None singleton.

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict