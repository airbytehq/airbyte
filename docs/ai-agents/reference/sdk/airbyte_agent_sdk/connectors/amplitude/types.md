---
id: airbyte_agent_sdk-connectors-amplitude-types
title: airbyte_agent_sdk.connectors.amplitude.types
---

Module airbyte_agent_sdk.connectors.amplitude.types
===================================================
Type definitions for amplitude connector.

Classes
-------

<a id="ActiveUsersAndCondition"></a>

`ActiveUsersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersEqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersInCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNotCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAndCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersOrCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="ActiveUsersAnyCondition"></a>

`ActiveUsersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="ActiveUsersAnyValueFilter"></a>

`ActiveUsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: Any`
    :   The date for which the active user data is reported

    `statistics: Any`
    :   The statistics related to the active users for the given date

<a id="ActiveUsersContainsCondition"></a>

`ActiveUsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAnyValueFilter`
    :   The type of the None singleton.

<a id="ActiveUsersEqCondition"></a>

`ActiveUsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="ActiveUsersFuzzyCondition"></a>

`ActiveUsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="ActiveUsersGtCondition"></a>

`ActiveUsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="ActiveUsersGteCondition"></a>

`ActiveUsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="ActiveUsersInCondition"></a>

`ActiveUsersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersInFilter`
    :   The type of the None singleton.

<a id="ActiveUsersInFilter"></a>

`ActiveUsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: list[str]`
    :   The date for which the active user data is reported

    `statistics: list[dict[str, typing.Any]]`
    :   The statistics related to the active users for the given date

<a id="ActiveUsersKeywordCondition"></a>

`ActiveUsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="ActiveUsersLikeCondition"></a>

`ActiveUsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersStringFilter`
    :   The type of the None singleton.

<a id="ActiveUsersListParams"></a>

`ActiveUsersListParams(*args, **kwargs)`
:   Parameters for active_users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end: str`
    :   The type of the None singleton.

    `g: str`
    :   The type of the None singleton.

    `i: int`
    :   The type of the None singleton.

    `m: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

<a id="ActiveUsersLtCondition"></a>

`ActiveUsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="ActiveUsersLteCondition"></a>

`ActiveUsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="ActiveUsersNeqCondition"></a>

`ActiveUsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSearchFilter`
    :   The type of the None singleton.

<a id="ActiveUsersNotCondition"></a>

`ActiveUsersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersEqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersInCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNotCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAndCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersOrCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAnyCondition`
    :   The type of the None singleton.

<a id="ActiveUsersOrCondition"></a>

`ActiveUsersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersEqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersInCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNotCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAndCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersOrCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAnyCondition]`
    :   The type of the None singleton.

<a id="ActiveUsersSearchFilter"></a>

`ActiveUsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering active_users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: str | None`
    :   The date for which the active user data is reported

    `statistics: dict[str, typing.Any] | None`
    :   The statistics related to the active users for the given date

<a id="ActiveUsersSearchQuery"></a>

`ActiveUsersSearchQuery(*args, **kwargs)`
:   Search query for active_users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersEqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersGteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLtCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLteCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersInCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersNotCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAndCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersOrCondition | airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amplitude.types.ActiveUsersSortFilter]`
    :   The type of the None singleton.

<a id="ActiveUsersSortFilter"></a>

`ActiveUsersSortFilter(*args, **kwargs)`
:   Available fields for sorting active_users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: Literal['asc', 'desc']`
    :   The date for which the active user data is reported

    `statistics: Literal['asc', 'desc']`
    :   The statistics related to the active users for the given date

<a id="ActiveUsersStringFilter"></a>

`ActiveUsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: str`
    :   The date for which the active user data is reported

    `statistics: str`
    :   The statistics related to the active users for the given date

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

<a id="AnnotationsAndCondition"></a>

`AnnotationsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.amplitude.types.AnnotationsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsInCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAnyCondition]`
    :   The type of the None singleton.

<a id="AnnotationsAnyCondition"></a>

`AnnotationsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAnyValueFilter`
    :   The type of the None singleton.

<a id="AnnotationsAnyValueFilter"></a>

`AnnotationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: Any`
    :   The date when the annotation was made

    `details: Any`
    :   Additional details or information related to the annotation

    `id: Any`
    :   The unique identifier for the annotation

    `label: Any`
    :   The label assigned to the annotation

<a id="AnnotationsContainsCondition"></a>

`AnnotationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAnyValueFilter`
    :   The type of the None singleton.

<a id="AnnotationsEqCondition"></a>

`AnnotationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSearchFilter`
    :   The type of the None singleton.

<a id="AnnotationsFuzzyCondition"></a>

`AnnotationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsStringFilter`
    :   The type of the None singleton.

<a id="AnnotationsGetParams"></a>

`AnnotationsGetParams(*args, **kwargs)`
:   Parameters for annotations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotation_id: str`
    :   The type of the None singleton.

<a id="AnnotationsGtCondition"></a>

`AnnotationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSearchFilter`
    :   The type of the None singleton.

<a id="AnnotationsGteCondition"></a>

`AnnotationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSearchFilter`
    :   The type of the None singleton.

<a id="AnnotationsInCondition"></a>

`AnnotationsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsInFilter`
    :   The type of the None singleton.

<a id="AnnotationsInFilter"></a>

`AnnotationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: list[str]`
    :   The date when the annotation was made

    `details: list[str]`
    :   Additional details or information related to the annotation

    `id: list[int]`
    :   The unique identifier for the annotation

    `label: list[str]`
    :   The label assigned to the annotation

<a id="AnnotationsKeywordCondition"></a>

`AnnotationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsStringFilter`
    :   The type of the None singleton.

<a id="AnnotationsLikeCondition"></a>

`AnnotationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsStringFilter`
    :   The type of the None singleton.

<a id="AnnotationsListParams"></a>

`AnnotationsListParams(*args, **kwargs)`
:   Parameters for annotations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="AnnotationsLtCondition"></a>

`AnnotationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSearchFilter`
    :   The type of the None singleton.

<a id="AnnotationsLteCondition"></a>

`AnnotationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSearchFilter`
    :   The type of the None singleton.

<a id="AnnotationsNeqCondition"></a>

`AnnotationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSearchFilter`
    :   The type of the None singleton.

<a id="AnnotationsNotCondition"></a>

`AnnotationsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsInCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAnyCondition`
    :   The type of the None singleton.

<a id="AnnotationsOrCondition"></a>

`AnnotationsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.amplitude.types.AnnotationsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsInCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAnyCondition]`
    :   The type of the None singleton.

<a id="AnnotationsSearchFilter"></a>

`AnnotationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering annotations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: str | None`
    :   The date when the annotation was made

    `details: str | None`
    :   Additional details or information related to the annotation

    `id: int | None`
    :   The unique identifier for the annotation

    `label: str | None`
    :   The label assigned to the annotation

<a id="AnnotationsSearchQuery"></a>

`AnnotationsSearchQuery(*args, **kwargs)`
:   Search query for annotations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amplitude.types.AnnotationsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsInCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AnnotationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amplitude.types.AnnotationsSortFilter]`
    :   The type of the None singleton.

<a id="AnnotationsSortFilter"></a>

`AnnotationsSortFilter(*args, **kwargs)`
:   Available fields for sorting annotations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: Literal['asc', 'desc']`
    :   The date when the annotation was made

    `details: Literal['asc', 'desc']`
    :   Additional details or information related to the annotation

    `id: Literal['asc', 'desc']`
    :   The unique identifier for the annotation

    `label: Literal['asc', 'desc']`
    :   The label assigned to the annotation

<a id="AnnotationsStringFilter"></a>

`AnnotationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: str`
    :   The date when the annotation was made

    `details: str`
    :   Additional details or information related to the annotation

    `id: str`
    :   The unique identifier for the annotation

    `label: str`
    :   The label assigned to the annotation

<a id="AverageSessionLengthAndCondition"></a>

`AverageSessionLengthAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthInCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAnyCondition]`
    :   The type of the None singleton.

<a id="AverageSessionLengthAnyCondition"></a>

`AverageSessionLengthAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAnyValueFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthAnyValueFilter"></a>

`AverageSessionLengthAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: Any`
    :   The date on which the session occurred

    `length: Any`
    :   The duration of the session in seconds

<a id="AverageSessionLengthContainsCondition"></a>

`AverageSessionLengthContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAnyValueFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthEqCondition"></a>

`AverageSessionLengthEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSearchFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthFuzzyCondition"></a>

`AverageSessionLengthFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthStringFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthGtCondition"></a>

`AverageSessionLengthGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSearchFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthGteCondition"></a>

`AverageSessionLengthGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSearchFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthInCondition"></a>

`AverageSessionLengthInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthInFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthInFilter"></a>

`AverageSessionLengthInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: list[str]`
    :   The date on which the session occurred

    `length: list[float]`
    :   The duration of the session in seconds

<a id="AverageSessionLengthKeywordCondition"></a>

`AverageSessionLengthKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthStringFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthLikeCondition"></a>

`AverageSessionLengthLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthStringFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthListParams"></a>

`AverageSessionLengthListParams(*args, **kwargs)`
:   Parameters for average_session_length.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

<a id="AverageSessionLengthLtCondition"></a>

`AverageSessionLengthLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSearchFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthLteCondition"></a>

`AverageSessionLengthLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSearchFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthNeqCondition"></a>

`AverageSessionLengthNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSearchFilter`
    :   The type of the None singleton.

<a id="AverageSessionLengthNotCondition"></a>

`AverageSessionLengthNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthInCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAnyCondition`
    :   The type of the None singleton.

<a id="AverageSessionLengthOrCondition"></a>

`AverageSessionLengthOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthInCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAnyCondition]`
    :   The type of the None singleton.

<a id="AverageSessionLengthSearchFilter"></a>

`AverageSessionLengthSearchFilter(*args, **kwargs)`
:   Available fields for filtering average_session_length search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: str | None`
    :   The date on which the session occurred

    `length: float | None`
    :   The duration of the session in seconds

<a id="AverageSessionLengthSearchQuery"></a>

`AverageSessionLengthSearchQuery(*args, **kwargs)`
:   Search query for average_session_length entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthEqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthGteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLtCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLteCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthInCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthNotCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAndCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthOrCondition | airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amplitude.types.AverageSessionLengthSortFilter]`
    :   The type of the None singleton.

<a id="AverageSessionLengthSortFilter"></a>

`AverageSessionLengthSortFilter(*args, **kwargs)`
:   Available fields for sorting average_session_length search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: Literal['asc', 'desc']`
    :   The date on which the session occurred

    `length: Literal['asc', 'desc']`
    :   The duration of the session in seconds

<a id="AverageSessionLengthStringFilter"></a>

`AverageSessionLengthStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date: str`
    :   The date on which the session occurred

    `length: str`
    :   The duration of the session in seconds

<a id="CohortsAndCondition"></a>

`CohortsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.amplitude.types.CohortsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsInCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAnyCondition]`
    :   The type of the None singleton.

<a id="CohortsAnyCondition"></a>

`CohortsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.amplitude.types.CohortsAnyValueFilter`
    :   The type of the None singleton.

<a id="CohortsAnyValueFilter"></a>

`CohortsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: Any`
    :   The unique identifier of the application

    `archived: Any`
    :   Indicates if the cohort data is archived

    `chart_id: Any`
    :   The identifier of the chart associated with the cohort

    `created_at: Any`
    :   The timestamp when the cohort was created

    `definition: Any`
    :   The specific definition or criteria for the cohort

    `description: Any`
    :   A brief explanation or summary of the cohort

    `edit_id: Any`
    :   The ID for editing purposes or version control

    `finished: Any`
    :   Indicates if the cohort data has been finalized

    `hidden: Any`
    :   Flag to determine if the cohort is hidden from view

    `id: Any`
    :   The unique identifier for the cohort

    `is_official_content: Any`
    :   Indicates if the cohort data is official content

    `is_predictive: Any`
    :   Flag to indicate if the cohort is predictive

    `last_computed: Any`
    :   Timestamp of the last computation of cohort data

    `last_mod: Any`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: Any`
    :   Timestamp when the cohort was last viewed

    `location_id: Any`
    :   Identifier of the location associated with the cohort

    `metadata: Any`
    :   Additional information or data related to the cohort

    `name: Any`
    :   The name or title of the cohort

    `owners: Any`
    :   The owners or administrators of the cohort

    `popularity: Any`
    :   Popularity rank or score of the cohort

    `published: Any`
    :   Status indicating if the cohort data is published

    `shortcut_ids: Any`
    :   Identifiers of any shortcuts associated with the cohort

    `size: Any`
    :   Size or scale of the cohort data

    `type_: Any`
    :   The type or category of the cohort

    `view_count: Any`
    :   The total count of views on the cohort data

    `viewers: Any`
    :   Users or viewers who have access to the cohort data

<a id="CohortsContainsCondition"></a>

`CohortsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amplitude.types.CohortsAnyValueFilter`
    :   The type of the None singleton.

<a id="CohortsEqCondition"></a>

`CohortsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amplitude.types.CohortsSearchFilter`
    :   The type of the None singleton.

<a id="CohortsFuzzyCondition"></a>

`CohortsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amplitude.types.CohortsStringFilter`
    :   The type of the None singleton.

<a id="CohortsGetParams"></a>

`CohortsGetParams(*args, **kwargs)`
:   Parameters for cohorts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cohort_id: str`
    :   The type of the None singleton.

<a id="CohortsGtCondition"></a>

`CohortsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amplitude.types.CohortsSearchFilter`
    :   The type of the None singleton.

<a id="CohortsGteCondition"></a>

`CohortsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amplitude.types.CohortsSearchFilter`
    :   The type of the None singleton.

<a id="CohortsInCondition"></a>

`CohortsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.amplitude.types.CohortsInFilter`
    :   The type of the None singleton.

<a id="CohortsInFilter"></a>

`CohortsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: list[int]`
    :   The unique identifier of the application

    `archived: list[bool]`
    :   Indicates if the cohort data is archived

    `chart_id: list[str]`
    :   The identifier of the chart associated with the cohort

    `created_at: list[int]`
    :   The timestamp when the cohort was created

    `definition: list[dict[str, typing.Any]]`
    :   The specific definition or criteria for the cohort

    `description: list[str]`
    :   A brief explanation or summary of the cohort

    `edit_id: list[str]`
    :   The ID for editing purposes or version control

    `finished: list[bool]`
    :   Indicates if the cohort data has been finalized

    `hidden: list[bool]`
    :   Flag to determine if the cohort is hidden from view

    `id: list[str]`
    :   The unique identifier for the cohort

    `is_official_content: list[bool]`
    :   Indicates if the cohort data is official content

    `is_predictive: list[bool]`
    :   Flag to indicate if the cohort is predictive

    `last_computed: list[int]`
    :   Timestamp of the last computation of cohort data

    `last_mod: list[int]`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: list[int]`
    :   Timestamp when the cohort was last viewed

    `location_id: list[str]`
    :   Identifier of the location associated with the cohort

    `metadata: list[list[typing.Any]]`
    :   Additional information or data related to the cohort

    `name: list[str]`
    :   The name or title of the cohort

    `owners: list[list[typing.Any]]`
    :   The owners or administrators of the cohort

    `popularity: list[int]`
    :   Popularity rank or score of the cohort

    `published: list[bool]`
    :   Status indicating if the cohort data is published

    `shortcut_ids: list[list[typing.Any]]`
    :   Identifiers of any shortcuts associated with the cohort

    `size: list[int]`
    :   Size or scale of the cohort data

    `type_: list[str]`
    :   The type or category of the cohort

    `view_count: list[int]`
    :   The total count of views on the cohort data

    `viewers: list[list[typing.Any]]`
    :   Users or viewers who have access to the cohort data

<a id="CohortsKeywordCondition"></a>

`CohortsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amplitude.types.CohortsStringFilter`
    :   The type of the None singleton.

<a id="CohortsLikeCondition"></a>

`CohortsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amplitude.types.CohortsStringFilter`
    :   The type of the None singleton.

<a id="CohortsListParams"></a>

`CohortsListParams(*args, **kwargs)`
:   Parameters for cohorts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CohortsLtCondition"></a>

`CohortsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amplitude.types.CohortsSearchFilter`
    :   The type of the None singleton.

<a id="CohortsLteCondition"></a>

`CohortsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amplitude.types.CohortsSearchFilter`
    :   The type of the None singleton.

<a id="CohortsNeqCondition"></a>

`CohortsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amplitude.types.CohortsSearchFilter`
    :   The type of the None singleton.

<a id="CohortsNotCondition"></a>

`CohortsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.amplitude.types.CohortsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsInCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAnyCondition`
    :   The type of the None singleton.

<a id="CohortsOrCondition"></a>

`CohortsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.amplitude.types.CohortsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsInCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAnyCondition]`
    :   The type of the None singleton.

<a id="CohortsSearchFilter"></a>

`CohortsSearchFilter(*args, **kwargs)`
:   Available fields for filtering cohorts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: int | None`
    :   The unique identifier of the application

    `archived: bool | None`
    :   Indicates if the cohort data is archived

    `chart_id: str | None`
    :   The identifier of the chart associated with the cohort

    `created_at: int | None`
    :   The timestamp when the cohort was created

    `definition: dict[str, typing.Any] | None`
    :   The specific definition or criteria for the cohort

    `description: str | None`
    :   A brief explanation or summary of the cohort

    `edit_id: str | None`
    :   The ID for editing purposes or version control

    `finished: bool | None`
    :   Indicates if the cohort data has been finalized

    `hidden: bool | None`
    :   Flag to determine if the cohort is hidden from view

    `id: str | None`
    :   The unique identifier for the cohort

    `is_official_content: bool | None`
    :   Indicates if the cohort data is official content

    `is_predictive: bool | None`
    :   Flag to indicate if the cohort is predictive

    `last_computed: int | None`
    :   Timestamp of the last computation of cohort data

    `last_mod: int | None`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: int | None`
    :   Timestamp when the cohort was last viewed

    `location_id: str | None`
    :   Identifier of the location associated with the cohort

    `metadata: list[typing.Any] | None`
    :   Additional information or data related to the cohort

    `name: str | None`
    :   The name or title of the cohort

    `owners: list[typing.Any] | None`
    :   The owners or administrators of the cohort

    `popularity: int | None`
    :   Popularity rank or score of the cohort

    `published: bool | None`
    :   Status indicating if the cohort data is published

    `shortcut_ids: list[typing.Any] | None`
    :   Identifiers of any shortcuts associated with the cohort

    `size: int | None`
    :   Size or scale of the cohort data

    `type_: str | None`
    :   The type or category of the cohort

    `view_count: int | None`
    :   The total count of views on the cohort data

    `viewers: list[typing.Any] | None`
    :   Users or viewers who have access to the cohort data

<a id="CohortsSearchQuery"></a>

`CohortsSearchQuery(*args, **kwargs)`
:   Search query for cohorts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amplitude.types.CohortsEqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsGteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLtCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLteCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsInCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsNotCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAndCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsOrCondition | airbyte_agent_sdk.connectors.amplitude.types.CohortsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amplitude.types.CohortsSortFilter]`
    :   The type of the None singleton.

<a id="CohortsSortFilter"></a>

`CohortsSortFilter(*args, **kwargs)`
:   Available fields for sorting cohorts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: Literal['asc', 'desc']`
    :   The unique identifier of the application

    `archived: Literal['asc', 'desc']`
    :   Indicates if the cohort data is archived

    `chart_id: Literal['asc', 'desc']`
    :   The identifier of the chart associated with the cohort

    `created_at: Literal['asc', 'desc']`
    :   The timestamp when the cohort was created

    `definition: Literal['asc', 'desc']`
    :   The specific definition or criteria for the cohort

    `description: Literal['asc', 'desc']`
    :   A brief explanation or summary of the cohort

    `edit_id: Literal['asc', 'desc']`
    :   The ID for editing purposes or version control

    `finished: Literal['asc', 'desc']`
    :   Indicates if the cohort data has been finalized

    `hidden: Literal['asc', 'desc']`
    :   Flag to determine if the cohort is hidden from view

    `id: Literal['asc', 'desc']`
    :   The unique identifier for the cohort

    `is_official_content: Literal['asc', 'desc']`
    :   Indicates if the cohort data is official content

    `is_predictive: Literal['asc', 'desc']`
    :   Flag to indicate if the cohort is predictive

    `last_computed: Literal['asc', 'desc']`
    :   Timestamp of the last computation of cohort data

    `last_mod: Literal['asc', 'desc']`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: Literal['asc', 'desc']`
    :   Timestamp when the cohort was last viewed

    `location_id: Literal['asc', 'desc']`
    :   Identifier of the location associated with the cohort

    `metadata: Literal['asc', 'desc']`
    :   Additional information or data related to the cohort

    `name: Literal['asc', 'desc']`
    :   The name or title of the cohort

    `owners: Literal['asc', 'desc']`
    :   The owners or administrators of the cohort

    `popularity: Literal['asc', 'desc']`
    :   Popularity rank or score of the cohort

    `published: Literal['asc', 'desc']`
    :   Status indicating if the cohort data is published

    `shortcut_ids: Literal['asc', 'desc']`
    :   Identifiers of any shortcuts associated with the cohort

    `size: Literal['asc', 'desc']`
    :   Size or scale of the cohort data

    `type_: Literal['asc', 'desc']`
    :   The type or category of the cohort

    `view_count: Literal['asc', 'desc']`
    :   The total count of views on the cohort data

    `viewers: Literal['asc', 'desc']`
    :   Users or viewers who have access to the cohort data

<a id="CohortsStringFilter"></a>

`CohortsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: str`
    :   The unique identifier of the application

    `archived: str`
    :   Indicates if the cohort data is archived

    `chart_id: str`
    :   The identifier of the chart associated with the cohort

    `created_at: str`
    :   The timestamp when the cohort was created

    `definition: str`
    :   The specific definition or criteria for the cohort

    `description: str`
    :   A brief explanation or summary of the cohort

    `edit_id: str`
    :   The ID for editing purposes or version control

    `finished: str`
    :   Indicates if the cohort data has been finalized

    `hidden: str`
    :   Flag to determine if the cohort is hidden from view

    `id: str`
    :   The unique identifier for the cohort

    `is_official_content: str`
    :   Indicates if the cohort data is official content

    `is_predictive: str`
    :   Flag to indicate if the cohort is predictive

    `last_computed: str`
    :   Timestamp of the last computation of cohort data

    `last_mod: str`
    :   Timestamp of the last modification made to the cohort

    `last_viewed: str`
    :   Timestamp when the cohort was last viewed

    `location_id: str`
    :   Identifier of the location associated with the cohort

    `metadata: str`
    :   Additional information or data related to the cohort

    `name: str`
    :   The name or title of the cohort

    `owners: str`
    :   The owners or administrators of the cohort

    `popularity: str`
    :   Popularity rank or score of the cohort

    `published: str`
    :   Status indicating if the cohort data is published

    `shortcut_ids: str`
    :   Identifiers of any shortcuts associated with the cohort

    `size: str`
    :   Size or scale of the cohort data

    `type_: str`
    :   The type or category of the cohort

    `view_count: str`
    :   The total count of views on the cohort data

    `viewers: str`
    :   Users or viewers who have access to the cohort data

<a id="EventsListAndCondition"></a>

`EventsListAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.amplitude.types.EventsListEqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListInCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNotCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAndCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListOrCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAnyCondition]`
    :   The type of the None singleton.

<a id="EventsListAnyCondition"></a>

`EventsListAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.amplitude.types.EventsListAnyValueFilter`
    :   The type of the None singleton.

<a id="EventsListAnyValueFilter"></a>

`EventsListAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `autohidden: Any`
    :   Whether the event is auto-hidden

    `clusters_hidden: Any`
    :   Whether the event is hidden from clusters

    `deleted: Any`
    :   Whether the event is deleted

    `display: Any`
    :   Display name of the event

    `flow_hidden: Any`
    :   Whether the event is hidden from Pathfinder

    `hidden: Any`
    :   Whether the event is hidden

    `id: Any`
    :   Unique identifier for the event type

    `in_waitroom: Any`
    :   Whether the event is in the waitroom

    `name: Any`
    :   Name of the event type

    `non_active: Any`
    :   Whether the event is marked as inactive

    `timeline_hidden: Any`
    :   Whether the event is hidden from the timeline

    `totals: Any`
    :   Total number of times the event occurred this week

    `totals_delta: Any`
    :   Change in totals from the previous period

    `value: Any`
    :   Raw event name in the data

<a id="EventsListContainsCondition"></a>

`EventsListContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amplitude.types.EventsListAnyValueFilter`
    :   The type of the None singleton.

<a id="EventsListEqCondition"></a>

`EventsListEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amplitude.types.EventsListSearchFilter`
    :   The type of the None singleton.

<a id="EventsListFuzzyCondition"></a>

`EventsListFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amplitude.types.EventsListStringFilter`
    :   The type of the None singleton.

<a id="EventsListGtCondition"></a>

`EventsListGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amplitude.types.EventsListSearchFilter`
    :   The type of the None singleton.

<a id="EventsListGteCondition"></a>

`EventsListGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amplitude.types.EventsListSearchFilter`
    :   The type of the None singleton.

<a id="EventsListInCondition"></a>

`EventsListInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.amplitude.types.EventsListInFilter`
    :   The type of the None singleton.

<a id="EventsListInFilter"></a>

`EventsListInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `autohidden: list[bool]`
    :   Whether the event is auto-hidden

    `clusters_hidden: list[bool]`
    :   Whether the event is hidden from clusters

    `deleted: list[bool]`
    :   Whether the event is deleted

    `display: list[str]`
    :   Display name of the event

    `flow_hidden: list[bool]`
    :   Whether the event is hidden from Pathfinder

    `hidden: list[bool]`
    :   Whether the event is hidden

    `id: list[float]`
    :   Unique identifier for the event type

    `in_waitroom: list[bool]`
    :   Whether the event is in the waitroom

    `name: list[str]`
    :   Name of the event type

    `non_active: list[bool]`
    :   Whether the event is marked as inactive

    `timeline_hidden: list[typing.Any]`
    :   Whether the event is hidden from the timeline

    `totals: list[float]`
    :   Total number of times the event occurred this week

    `totals_delta: list[float]`
    :   Change in totals from the previous period

    `value: list[str]`
    :   Raw event name in the data

<a id="EventsListKeywordCondition"></a>

`EventsListKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amplitude.types.EventsListStringFilter`
    :   The type of the None singleton.

<a id="EventsListLikeCondition"></a>

`EventsListLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amplitude.types.EventsListStringFilter`
    :   The type of the None singleton.

<a id="EventsListListParams"></a>

`EventsListListParams(*args, **kwargs)`
:   Parameters for events_list.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="EventsListLtCondition"></a>

`EventsListLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amplitude.types.EventsListSearchFilter`
    :   The type of the None singleton.

<a id="EventsListLteCondition"></a>

`EventsListLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amplitude.types.EventsListSearchFilter`
    :   The type of the None singleton.

<a id="EventsListNeqCondition"></a>

`EventsListNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amplitude.types.EventsListSearchFilter`
    :   The type of the None singleton.

<a id="EventsListNotCondition"></a>

`EventsListNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.amplitude.types.EventsListEqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListInCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNotCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAndCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListOrCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAnyCondition`
    :   The type of the None singleton.

<a id="EventsListOrCondition"></a>

`EventsListOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.amplitude.types.EventsListEqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListInCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNotCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAndCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListOrCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAnyCondition]`
    :   The type of the None singleton.

<a id="EventsListSearchFilter"></a>

`EventsListSearchFilter(*args, **kwargs)`
:   Available fields for filtering events_list search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `autohidden: bool | None`
    :   Whether the event is auto-hidden

    `clusters_hidden: bool | None`
    :   Whether the event is hidden from clusters

    `deleted: bool | None`
    :   Whether the event is deleted

    `display: str | None`
    :   Display name of the event

    `flow_hidden: bool | None`
    :   Whether the event is hidden from Pathfinder

    `hidden: bool | None`
    :   Whether the event is hidden

    `id: float | None`
    :   Unique identifier for the event type

    `in_waitroom: bool | None`
    :   Whether the event is in the waitroom

    `name: str | None`
    :   Name of the event type

    `non_active: bool | None`
    :   Whether the event is marked as inactive

    `timeline_hidden: Any`
    :   Whether the event is hidden from the timeline

    `totals: float | None`
    :   Total number of times the event occurred this week

    `totals_delta: float | None`
    :   Change in totals from the previous period

    `value: str | None`
    :   Raw event name in the data

<a id="EventsListSearchQuery"></a>

`EventsListSearchQuery(*args, **kwargs)`
:   Search query for events_list entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amplitude.types.EventsListEqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNeqCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListGteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLtCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLteCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListInCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListLikeCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListFuzzyCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListKeywordCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListContainsCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListNotCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAndCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListOrCondition | airbyte_agent_sdk.connectors.amplitude.types.EventsListAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amplitude.types.EventsListSortFilter]`
    :   The type of the None singleton.

<a id="EventsListSortFilter"></a>

`EventsListSortFilter(*args, **kwargs)`
:   Available fields for sorting events_list search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `autohidden: Literal['asc', 'desc']`
    :   Whether the event is auto-hidden

    `clusters_hidden: Literal['asc', 'desc']`
    :   Whether the event is hidden from clusters

    `deleted: Literal['asc', 'desc']`
    :   Whether the event is deleted

    `display: Literal['asc', 'desc']`
    :   Display name of the event

    `flow_hidden: Literal['asc', 'desc']`
    :   Whether the event is hidden from Pathfinder

    `hidden: Literal['asc', 'desc']`
    :   Whether the event is hidden

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the event type

    `in_waitroom: Literal['asc', 'desc']`
    :   Whether the event is in the waitroom

    `name: Literal['asc', 'desc']`
    :   Name of the event type

    `non_active: Literal['asc', 'desc']`
    :   Whether the event is marked as inactive

    `timeline_hidden: Literal['asc', 'desc']`
    :   Whether the event is hidden from the timeline

    `totals: Literal['asc', 'desc']`
    :   Total number of times the event occurred this week

    `totals_delta: Literal['asc', 'desc']`
    :   Change in totals from the previous period

    `value: Literal['asc', 'desc']`
    :   Raw event name in the data

<a id="EventsListStringFilter"></a>

`EventsListStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `autohidden: str`
    :   Whether the event is auto-hidden

    `clusters_hidden: str`
    :   Whether the event is hidden from clusters

    `deleted: str`
    :   Whether the event is deleted

    `display: str`
    :   Display name of the event

    `flow_hidden: str`
    :   Whether the event is hidden from Pathfinder

    `hidden: str`
    :   Whether the event is hidden

    `id: str`
    :   Unique identifier for the event type

    `in_waitroom: str`
    :   Whether the event is in the waitroom

    `name: str`
    :   Name of the event type

    `non_active: str`
    :   Whether the event is marked as inactive

    `timeline_hidden: str`
    :   Whether the event is hidden from the timeline

    `totals: str`
    :   Total number of times the event occurred this week

    `totals_delta: str`
    :   Change in totals from the previous period

    `value: str`
    :   Raw event name in the data