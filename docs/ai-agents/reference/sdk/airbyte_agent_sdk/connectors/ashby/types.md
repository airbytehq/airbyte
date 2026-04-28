---
id: airbyte_agent_sdk-connectors-ashby-types
title: airbyte_agent_sdk.connectors.ashby.types
---

Module airbyte_agent_sdk.connectors.ashby.types
===============================================
Type definitions for ashby connector.

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ApplicationsAnyValueFilter"></a>

`ApplicationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ApplicationsContainsCondition"></a>

`ApplicationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ApplicationsEqCondition"></a>

`ApplicationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsFuzzyCondition"></a>

`ApplicationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsGetParams"></a>

`ApplicationsGetParams(*args, **kwargs)`
:   Parameters for applications.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application_id: str`
    :   The type of the None singleton.

<a id="ApplicationsGtCondition"></a>

`ApplicationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsGteCondition"></a>

`ApplicationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.ashby.types.ApplicationsInFilter`
    :   The type of the None singleton.

<a id="ApplicationsInFilter"></a>

`ApplicationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ApplicationsKeywordCondition"></a>

`ApplicationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsLikeCondition"></a>

`ApplicationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.ApplicationsStringFilter`
    :   The type of the None singleton.

<a id="ApplicationsListParams"></a>

`ApplicationsListParams(*args, **kwargs)`
:   Parameters for applications.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="ApplicationsLtCondition"></a>

`ApplicationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsLteCondition"></a>

`ApplicationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
    :   The type of the None singleton.

<a id="ApplicationsNeqCondition"></a>

`ApplicationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.ApplicationsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition]`
    :   The type of the None singleton.

<a id="ApplicationsSearchFilter"></a>

`ApplicationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering applications search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ApplicationsSearchQuery"></a>

`ApplicationsSearchQuery(*args, **kwargs)`
:   Search query for applications entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.ApplicationsEqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsGteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLtCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLteCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsInCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsNotCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAndCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsOrCondition | airbyte_agent_sdk.connectors.ashby.types.ApplicationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.ApplicationsSortFilter]`
    :   The type of the None singleton.

<a id="ApplicationsSortFilter"></a>

`ApplicationsSortFilter(*args, **kwargs)`
:   Available fields for sorting applications search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ApplicationsStringFilter"></a>

`ApplicationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ArchiveReasonsListParams"></a>

`ArchiveReasonsListParams(*args, **kwargs)`
:   Parameters for archive_reasons.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="CandidateTagsListParams"></a>

`CandidateTagsListParams(*args, **kwargs)`
:   Parameters for candidate_tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

<a id="CandidatesAnyValueFilter"></a>

`CandidatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CandidatesContainsCondition"></a>

`CandidatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyValueFilter`
    :   The type of the None singleton.

<a id="CandidatesEqCondition"></a>

`CandidatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesFuzzyCondition"></a>

`CandidatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.CandidatesStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesGteCondition"></a>

`CandidatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.ashby.types.CandidatesInFilter`
    :   The type of the None singleton.

<a id="CandidatesInFilter"></a>

`CandidatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CandidatesKeywordCondition"></a>

`CandidatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesLikeCondition"></a>

`CandidatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.CandidatesStringFilter`
    :   The type of the None singleton.

<a id="CandidatesListParams"></a>

`CandidatesListParams(*args, **kwargs)`
:   Parameters for candidates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="CandidatesLtCondition"></a>

`CandidatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesLteCondition"></a>

`CandidatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
    :   The type of the None singleton.

<a id="CandidatesNeqCondition"></a>

`CandidatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.CandidatesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition]`
    :   The type of the None singleton.

<a id="CandidatesSearchFilter"></a>

`CandidatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering candidates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CandidatesSearchQuery"></a>

`CandidatesSearchQuery(*args, **kwargs)`
:   Search query for candidates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.CandidatesEqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNeqCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesGteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLtCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLteCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesInCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesLikeCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesContainsCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesNotCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAndCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesOrCondition | airbyte_agent_sdk.connectors.ashby.types.CandidatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.CandidatesSortFilter]`
    :   The type of the None singleton.

<a id="CandidatesSortFilter"></a>

`CandidatesSortFilter(*args, **kwargs)`
:   Available fields for sorting candidates search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CandidatesStringFilter"></a>

`CandidatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CustomFieldsListParams"></a>

`CustomFieldsListParams(*args, **kwargs)`
:   Parameters for custom_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="DepartmentsGetParams"></a>

`DepartmentsGetParams(*args, **kwargs)`
:   Parameters for departments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `department_id: str`
    :   The type of the None singleton.

<a id="DepartmentsListParams"></a>

`DepartmentsListParams(*args, **kwargs)`
:   Parameters for departments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="FeedbackFormDefinitionsListParams"></a>

`FeedbackFormDefinitionsListParams(*args, **kwargs)`
:   Parameters for feedback_form_definitions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="JobPostingsAndCondition"></a>

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

<a id="JobPostingsAnyCondition"></a>

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

<a id="JobPostingsAnyValueFilter"></a>

`JobPostingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobPostingsContainsCondition"></a>

`JobPostingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobPostingsEqCondition"></a>

`JobPostingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostingsFuzzyCondition"></a>

`JobPostingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.JobPostingsStringFilter`
    :   The type of the None singleton.

<a id="JobPostingsGetParams"></a>

`JobPostingsGetParams(*args, **kwargs)`
:   Parameters for job_postings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `job_posting_id: str`
    :   The type of the None singleton.

<a id="JobPostingsGtCondition"></a>

`JobPostingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostingsGteCondition"></a>

`JobPostingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostingsInCondition"></a>

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

<a id="JobPostingsInFilter"></a>

`JobPostingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobPostingsKeywordCondition"></a>

`JobPostingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.JobPostingsStringFilter`
    :   The type of the None singleton.

<a id="JobPostingsLikeCondition"></a>

`JobPostingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.JobPostingsStringFilter`
    :   The type of the None singleton.

<a id="JobPostingsListParams"></a>

`JobPostingsListParams(*args, **kwargs)`
:   Parameters for job_postings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="JobPostingsLtCondition"></a>

`JobPostingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostingsLteCondition"></a>

`JobPostingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostingsNeqCondition"></a>

`JobPostingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.JobPostingsSearchFilter`
    :   The type of the None singleton.

<a id="JobPostingsNotCondition"></a>

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

<a id="JobPostingsOrCondition"></a>

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

<a id="JobPostingsSearchFilter"></a>

`JobPostingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering job_postings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobPostingsSearchQuery"></a>

`JobPostingsSearchQuery(*args, **kwargs)`
:   Search query for job_postings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.JobPostingsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobPostingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.JobPostingsSortFilter]`
    :   The type of the None singleton.

<a id="JobPostingsSortFilter"></a>

`JobPostingsSortFilter(*args, **kwargs)`
:   Available fields for sorting job_postings search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobPostingsStringFilter"></a>

`JobPostingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.ashby.types.JobsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobsAnyValueFilter"></a>

`JobsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobsContainsCondition"></a>

`JobsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.JobsAnyValueFilter`
    :   The type of the None singleton.

<a id="JobsEqCondition"></a>

`JobsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsFuzzyCondition"></a>

`JobsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.JobsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsGteCondition"></a>

`JobsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.ashby.types.JobsInFilter`
    :   The type of the None singleton.

<a id="JobsInFilter"></a>

`JobsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobsKeywordCondition"></a>

`JobsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsLikeCondition"></a>

`JobsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.JobsStringFilter`
    :   The type of the None singleton.

<a id="JobsListParams"></a>

`JobsListParams(*args, **kwargs)`
:   Parameters for jobs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="JobsLtCondition"></a>

`JobsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsLteCondition"></a>

`JobsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
    :   The type of the None singleton.

<a id="JobsNeqCondition"></a>

`JobsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.JobsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition]`
    :   The type of the None singleton.

<a id="JobsSearchFilter"></a>

`JobsSearchFilter(*args, **kwargs)`
:   Available fields for filtering jobs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobsSearchQuery"></a>

`JobsSearchQuery(*args, **kwargs)`
:   Search query for jobs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.JobsEqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNeqCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsGteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLtCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLteCondition | airbyte_agent_sdk.connectors.ashby.types.JobsInCondition | airbyte_agent_sdk.connectors.ashby.types.JobsLikeCondition | airbyte_agent_sdk.connectors.ashby.types.JobsFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.JobsKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.JobsContainsCondition | airbyte_agent_sdk.connectors.ashby.types.JobsNotCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAndCondition | airbyte_agent_sdk.connectors.ashby.types.JobsOrCondition | airbyte_agent_sdk.connectors.ashby.types.JobsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.JobsSortFilter]`
    :   The type of the None singleton.

<a id="JobsSortFilter"></a>

`JobsSortFilter(*args, **kwargs)`
:   Available fields for sorting jobs search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="JobsStringFilter"></a>

`JobsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="LocationsGetParams"></a>

`LocationsGetParams(*args, **kwargs)`
:   Parameters for locations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `location_id: str`
    :   The type of the None singleton.

<a id="LocationsListParams"></a>

`LocationsListParams(*args, **kwargs)`
:   Parameters for locations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="SourcesListParams"></a>

`SourcesListParams(*args, **kwargs)`
:   Parameters for sources.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.ashby.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.ashby.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.ashby.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_id: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.ashby.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.ashby.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.ashby.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.ashby.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.ashby.types.UsersEqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNeqCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersGteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLtCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLteCondition | airbyte_agent_sdk.connectors.ashby.types.UsersInCondition | airbyte_agent_sdk.connectors.ashby.types.UsersLikeCondition | airbyte_agent_sdk.connectors.ashby.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.ashby.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.ashby.types.UsersContainsCondition | airbyte_agent_sdk.connectors.ashby.types.UsersNotCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAndCondition | airbyte_agent_sdk.connectors.ashby.types.UsersOrCondition | airbyte_agent_sdk.connectors.ashby.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.ashby.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict