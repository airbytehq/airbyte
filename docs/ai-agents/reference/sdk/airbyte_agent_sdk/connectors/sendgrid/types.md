---
id: airbyte_agent_sdk-connectors-sendgrid-types
title: airbyte_agent_sdk.connectors.sendgrid.types
---

Module airbyte_agent_sdk.connectors.sendgrid.types
==================================================
Type definitions for sendgrid connector.

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

<a id="BlocksAndCondition"></a>

`BlocksAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.BlocksEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyCondition]`
    :   The type of the None singleton.

<a id="BlocksAnyCondition"></a>

`BlocksAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyValueFilter`
    :   The type of the None singleton.

<a id="BlocksAnyValueFilter"></a>

`BlocksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Any`
    :   Unix timestamp when the block occurred

    `email: Any`
    :   The blocked email address

    `reason: Any`
    :   The reason for the block

    `status: Any`
    :   The status code for the block

<a id="BlocksContainsCondition"></a>

`BlocksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyValueFilter`
    :   The type of the None singleton.

<a id="BlocksEqCondition"></a>

`BlocksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksFuzzyCondition"></a>

`BlocksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.BlocksStringFilter`
    :   The type of the None singleton.

<a id="BlocksGtCondition"></a>

`BlocksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksGteCondition"></a>

`BlocksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksInCondition"></a>

`BlocksInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.BlocksInFilter`
    :   The type of the None singleton.

<a id="BlocksInFilter"></a>

`BlocksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: list[int]`
    :   Unix timestamp when the block occurred

    `email: list[str]`
    :   The blocked email address

    `reason: list[str]`
    :   The reason for the block

    `status: list[str]`
    :   The status code for the block

<a id="BlocksKeywordCondition"></a>

`BlocksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.BlocksStringFilter`
    :   The type of the None singleton.

<a id="BlocksLikeCondition"></a>

`BlocksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.BlocksStringFilter`
    :   The type of the None singleton.

<a id="BlocksListParams"></a>

`BlocksListParams(*args, **kwargs)`
:   Parameters for blocks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="BlocksLtCondition"></a>

`BlocksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksLteCondition"></a>

`BlocksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksNeqCondition"></a>

`BlocksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

<a id="BlocksNotCondition"></a>

`BlocksNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.BlocksEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyCondition`
    :   The type of the None singleton.

<a id="BlocksOrCondition"></a>

`BlocksOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.BlocksEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyCondition]`
    :   The type of the None singleton.

<a id="BlocksSearchFilter"></a>

`BlocksSearchFilter(*args, **kwargs)`
:   Available fields for filtering blocks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the block occurred

    `email: str | None`
    :   The blocked email address

    `reason: str | None`
    :   The reason for the block

    `status: str | None`
    :   The status code for the block

<a id="BlocksSearchQuery"></a>

`BlocksSearchQuery(*args, **kwargs)`
:   Search query for blocks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.BlocksEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.BlocksSortFilter]`
    :   The type of the None singleton.

<a id="BlocksSortFilter"></a>

`BlocksSortFilter(*args, **kwargs)`
:   Available fields for sorting blocks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   Unix timestamp when the block occurred

    `email: Literal['asc', 'desc']`
    :   The blocked email address

    `reason: Literal['asc', 'desc']`
    :   The reason for the block

    `status: Literal['asc', 'desc']`
    :   The status code for the block

<a id="BlocksStringFilter"></a>

`BlocksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   Unix timestamp when the block occurred

    `email: str`
    :   The blocked email address

    `reason: str`
    :   The reason for the block

    `status: str`
    :   The status code for the block

<a id="BouncesAndCondition"></a>

`BouncesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.BouncesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyCondition]`
    :   The type of the None singleton.

<a id="BouncesAnyCondition"></a>

`BouncesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyValueFilter`
    :   The type of the None singleton.

<a id="BouncesAnyValueFilter"></a>

`BouncesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Any`
    :   Unix timestamp when the bounce occurred

    `email: Any`
    :   The email address that bounced

    `reason: Any`
    :   The reason for the bounce

    `status: Any`
    :   The enhanced status code for the bounce

<a id="BouncesContainsCondition"></a>

`BouncesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyValueFilter`
    :   The type of the None singleton.

<a id="BouncesEqCondition"></a>

`BouncesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

<a id="BouncesFuzzyCondition"></a>

`BouncesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.BouncesStringFilter`
    :   The type of the None singleton.

<a id="BouncesGtCondition"></a>

`BouncesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

<a id="BouncesGteCondition"></a>

`BouncesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

<a id="BouncesInCondition"></a>

`BouncesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.BouncesInFilter`
    :   The type of the None singleton.

<a id="BouncesInFilter"></a>

`BouncesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: list[int]`
    :   Unix timestamp when the bounce occurred

    `email: list[str]`
    :   The email address that bounced

    `reason: list[str]`
    :   The reason for the bounce

    `status: list[str]`
    :   The enhanced status code for the bounce

<a id="BouncesKeywordCondition"></a>

`BouncesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.BouncesStringFilter`
    :   The type of the None singleton.

<a id="BouncesLikeCondition"></a>

`BouncesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.BouncesStringFilter`
    :   The type of the None singleton.

<a id="BouncesListParams"></a>

`BouncesListParams(*args, **kwargs)`
:   Parameters for bounces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="BouncesLtCondition"></a>

`BouncesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

<a id="BouncesLteCondition"></a>

`BouncesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

<a id="BouncesNeqCondition"></a>

`BouncesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

<a id="BouncesNotCondition"></a>

`BouncesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.BouncesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyCondition`
    :   The type of the None singleton.

<a id="BouncesOrCondition"></a>

`BouncesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.BouncesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyCondition]`
    :   The type of the None singleton.

<a id="BouncesSearchFilter"></a>

`BouncesSearchFilter(*args, **kwargs)`
:   Available fields for filtering bounces search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the bounce occurred

    `email: str | None`
    :   The email address that bounced

    `reason: str | None`
    :   The reason for the bounce

    `status: str | None`
    :   The enhanced status code for the bounce

<a id="BouncesSearchQuery"></a>

`BouncesSearchQuery(*args, **kwargs)`
:   Search query for bounces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.BouncesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.BouncesSortFilter]`
    :   The type of the None singleton.

<a id="BouncesSortFilter"></a>

`BouncesSortFilter(*args, **kwargs)`
:   Available fields for sorting bounces search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   Unix timestamp when the bounce occurred

    `email: Literal['asc', 'desc']`
    :   The email address that bounced

    `reason: Literal['asc', 'desc']`
    :   The reason for the bounce

    `status: Literal['asc', 'desc']`
    :   The enhanced status code for the bounce

<a id="BouncesStringFilter"></a>

`BouncesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   Unix timestamp when the bounce occurred

    `email: str`
    :   The email address that bounced

    `reason: str`
    :   The reason for the bounce

    `status: str`
    :   The enhanced status code for the bounce

<a id="CampaignsAndCondition"></a>

`CampaignsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsAnyCondition"></a>

`CampaignsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channels: Any`
    :   Channels for this campaign

    `created_at: Any`
    :   When the campaign was created

    `id: Any`
    :   Unique campaign identifier

    `is_abtest: Any`
    :   Whether this campaign is an A/B test

    `name: Any`
    :   Campaign name

    `status: Any`
    :   Campaign status

    `updated_at: Any`
    :   When the campaign was last updated

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsInCondition"></a>

`CampaignsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channels: list[list[typing.Any]]`
    :   Channels for this campaign

    `created_at: list[str]`
    :   When the campaign was created

    `id: list[str]`
    :   Unique campaign identifier

    `is_abtest: list[bool]`
    :   Whether this campaign is an A/B test

    `name: list[str]`
    :   Campaign name

    `status: list[str]`
    :   Campaign status

    `updated_at: list[str]`
    :   When the campaign was last updated

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNotCondition"></a>

`CampaignsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignsOrCondition"></a>

`CampaignsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channels: list[typing.Any] | None`
    :   Channels for this campaign

    `created_at: str | None`
    :   When the campaign was created

    `id: str | None`
    :   Unique campaign identifier

    `is_abtest: bool | None`
    :   Whether this campaign is an A/B test

    `name: str | None`
    :   Campaign name

    `status: str | None`
    :   Campaign status

    `updated_at: str | None`
    :   When the campaign was last updated

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channels: Literal['asc', 'desc']`
    :   Channels for this campaign

    `created_at: Literal['asc', 'desc']`
    :   When the campaign was created

    `id: Literal['asc', 'desc']`
    :   Unique campaign identifier

    `is_abtest: Literal['asc', 'desc']`
    :   Whether this campaign is an A/B test

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `status: Literal['asc', 'desc']`
    :   Campaign status

    `updated_at: Literal['asc', 'desc']`
    :   When the campaign was last updated

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `channels: str`
    :   Channels for this campaign

    `created_at: str`
    :   When the campaign was created

    `id: str`
    :   Unique campaign identifier

    `is_abtest: str`
    :   Whether this campaign is an A/B test

    `name: str`
    :   Campaign name

    `status: str`
    :   Campaign status

    `updated_at: str`
    :   When the campaign was last updated

<a id="ContactsAndCondition"></a>

`ContactsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.ContactsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsAnyCondition"></a>

`ContactsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsAnyValueFilter"></a>

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_line_1: Any`
    :   Address line 1

    `address_line_2: Any`
    :   Address line 2

    `alternate_emails: Any`
    :   Alternate email addresses

    `city: Any`
    :   City

    `contact_id: Any`
    :   Unique contact identifier used by Airbyte

    `country: Any`
    :   Country

    `created_at: Any`
    :   When the contact was created

    `custom_fields: Any`
    :   Custom field values

    `email: Any`
    :   Contact email address

    `facebook: Any`
    :   Facebook ID

    `first_name: Any`
    :   Contact first name

    `last_name: Any`
    :   Contact last name

    `line: Any`
    :   LINE ID

    `list_ids: Any`
    :   IDs of lists the contact belongs to

    `phone_number: Any`
    :   Phone number

    `postal_code: Any`
    :   Postal code

    `state_province_region: Any`
    :   State, province, or region

    `unique_name: Any`
    :   Unique name for the contact

    `updated_at: Any`
    :   When the contact was last updated

    `whatsapp: Any`
    :   WhatsApp number

<a id="ContactsContainsCondition"></a>

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsEqCondition"></a>

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsFuzzyCondition"></a>

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsGetParams"></a>

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ContactsGtCondition"></a>

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsGteCondition"></a>

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsInCondition"></a>

`ContactsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.ContactsInFilter`
    :   The type of the None singleton.

<a id="ContactsInFilter"></a>

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_line_1: list[str]`
    :   Address line 1

    `address_line_2: list[str]`
    :   Address line 2

    `alternate_emails: list[list[typing.Any]]`
    :   Alternate email addresses

    `city: list[str]`
    :   City

    `contact_id: list[str]`
    :   Unique contact identifier used by Airbyte

    `country: list[str]`
    :   Country

    `created_at: list[str]`
    :   When the contact was created

    `custom_fields: list[dict[str, typing.Any]]`
    :   Custom field values

    `email: list[str]`
    :   Contact email address

    `facebook: list[str]`
    :   Facebook ID

    `first_name: list[str]`
    :   Contact first name

    `last_name: list[str]`
    :   Contact last name

    `line: list[str]`
    :   LINE ID

    `list_ids: list[list[typing.Any]]`
    :   IDs of lists the contact belongs to

    `phone_number: list[str]`
    :   Phone number

    `postal_code: list[str]`
    :   Postal code

    `state_province_region: list[str]`
    :   State, province, or region

    `unique_name: list[str]`
    :   Unique name for the contact

    `updated_at: list[str]`
    :   When the contact was last updated

    `whatsapp: list[str]`
    :   WhatsApp number

<a id="ContactsKeywordCondition"></a>

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsLikeCondition"></a>

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ContactsLtCondition"></a>

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsLteCondition"></a>

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNeqCondition"></a>

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNotCondition"></a>

`ContactsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.ContactsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyCondition`
    :   The type of the None singleton.

<a id="ContactsOrCondition"></a>

`ContactsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.ContactsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsSearchFilter"></a>

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_line_1: str | None`
    :   Address line 1

    `address_line_2: str | None`
    :   Address line 2

    `alternate_emails: list[typing.Any] | None`
    :   Alternate email addresses

    `city: str | None`
    :   City

    `contact_id: str | None`
    :   Unique contact identifier used by Airbyte

    `country: str | None`
    :   Country

    `created_at: str | None`
    :   When the contact was created

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom field values

    `email: str | None`
    :   Contact email address

    `facebook: str | None`
    :   Facebook ID

    `first_name: str | None`
    :   Contact first name

    `last_name: str | None`
    :   Contact last name

    `line: str | None`
    :   LINE ID

    `list_ids: list[typing.Any] | None`
    :   IDs of lists the contact belongs to

    `phone_number: str | None`
    :   Phone number

    `postal_code: str | None`
    :   Postal code

    `state_province_region: str | None`
    :   State, province, or region

    `unique_name: str | None`
    :   Unique name for the contact

    `updated_at: str | None`
    :   When the contact was last updated

    `whatsapp: str | None`
    :   WhatsApp number

<a id="ContactsSearchQuery"></a>

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.ContactsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.ContactsSortFilter]`
    :   The type of the None singleton.

<a id="ContactsSortFilter"></a>

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_line_1: Literal['asc', 'desc']`
    :   Address line 1

    `address_line_2: Literal['asc', 'desc']`
    :   Address line 2

    `alternate_emails: Literal['asc', 'desc']`
    :   Alternate email addresses

    `city: Literal['asc', 'desc']`
    :   City

    `contact_id: Literal['asc', 'desc']`
    :   Unique contact identifier used by Airbyte

    `country: Literal['asc', 'desc']`
    :   Country

    `created_at: Literal['asc', 'desc']`
    :   When the contact was created

    `custom_fields: Literal['asc', 'desc']`
    :   Custom field values

    `email: Literal['asc', 'desc']`
    :   Contact email address

    `facebook: Literal['asc', 'desc']`
    :   Facebook ID

    `first_name: Literal['asc', 'desc']`
    :   Contact first name

    `last_name: Literal['asc', 'desc']`
    :   Contact last name

    `line: Literal['asc', 'desc']`
    :   LINE ID

    `list_ids: Literal['asc', 'desc']`
    :   IDs of lists the contact belongs to

    `phone_number: Literal['asc', 'desc']`
    :   Phone number

    `postal_code: Literal['asc', 'desc']`
    :   Postal code

    `state_province_region: Literal['asc', 'desc']`
    :   State, province, or region

    `unique_name: Literal['asc', 'desc']`
    :   Unique name for the contact

    `updated_at: Literal['asc', 'desc']`
    :   When the contact was last updated

    `whatsapp: Literal['asc', 'desc']`
    :   WhatsApp number

<a id="ContactsStringFilter"></a>

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address_line_1: str`
    :   Address line 1

    `address_line_2: str`
    :   Address line 2

    `alternate_emails: str`
    :   Alternate email addresses

    `city: str`
    :   City

    `contact_id: str`
    :   Unique contact identifier used by Airbyte

    `country: str`
    :   Country

    `created_at: str`
    :   When the contact was created

    `custom_fields: str`
    :   Custom field values

    `email: str`
    :   Contact email address

    `facebook: str`
    :   Facebook ID

    `first_name: str`
    :   Contact first name

    `last_name: str`
    :   Contact last name

    `line: str`
    :   LINE ID

    `list_ids: str`
    :   IDs of lists the contact belongs to

    `phone_number: str`
    :   Phone number

    `postal_code: str`
    :   Postal code

    `state_province_region: str`
    :   State, province, or region

    `unique_name: str`
    :   Unique name for the contact

    `updated_at: str`
    :   When the contact was last updated

    `whatsapp: str`
    :   WhatsApp number

<a id="GlobalSuppressionsAndCondition"></a>

`GlobalSuppressionsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyCondition]`
    :   The type of the None singleton.

<a id="GlobalSuppressionsAnyCondition"></a>

`GlobalSuppressionsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyValueFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsAnyValueFilter"></a>

`GlobalSuppressionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Any`
    :   Unix timestamp when the global suppression was created

    `email: Any`
    :   The globally suppressed email address

<a id="GlobalSuppressionsContainsCondition"></a>

`GlobalSuppressionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyValueFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsEqCondition"></a>

`GlobalSuppressionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsFuzzyCondition"></a>

`GlobalSuppressionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsStringFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsGtCondition"></a>

`GlobalSuppressionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsGteCondition"></a>

`GlobalSuppressionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsInCondition"></a>

`GlobalSuppressionsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsInFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsInFilter"></a>

`GlobalSuppressionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: list[int]`
    :   Unix timestamp when the global suppression was created

    `email: list[str]`
    :   The globally suppressed email address

<a id="GlobalSuppressionsKeywordCondition"></a>

`GlobalSuppressionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsStringFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsLikeCondition"></a>

`GlobalSuppressionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsStringFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsListParams"></a>

`GlobalSuppressionsListParams(*args, **kwargs)`
:   Parameters for global_suppressions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="GlobalSuppressionsLtCondition"></a>

`GlobalSuppressionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsLteCondition"></a>

`GlobalSuppressionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsNeqCondition"></a>

`GlobalSuppressionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

<a id="GlobalSuppressionsNotCondition"></a>

`GlobalSuppressionsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyCondition`
    :   The type of the None singleton.

<a id="GlobalSuppressionsOrCondition"></a>

`GlobalSuppressionsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyCondition]`
    :   The type of the None singleton.

<a id="GlobalSuppressionsSearchFilter"></a>

`GlobalSuppressionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering global_suppressions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the global suppression was created

    `email: str | None`
    :   The globally suppressed email address

<a id="GlobalSuppressionsSearchQuery"></a>

`GlobalSuppressionsSearchQuery(*args, **kwargs)`
:   Search query for global_suppressions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSortFilter]`
    :   The type of the None singleton.

<a id="GlobalSuppressionsSortFilter"></a>

`GlobalSuppressionsSortFilter(*args, **kwargs)`
:   Available fields for sorting global_suppressions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   Unix timestamp when the global suppression was created

    `email: Literal['asc', 'desc']`
    :   The globally suppressed email address

<a id="GlobalSuppressionsStringFilter"></a>

`GlobalSuppressionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   Unix timestamp when the global suppression was created

    `email: str`
    :   The globally suppressed email address

<a id="InvalidEmailsAndCondition"></a>

`InvalidEmailsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyCondition]`
    :   The type of the None singleton.

<a id="InvalidEmailsAnyCondition"></a>

`InvalidEmailsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyValueFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsAnyValueFilter"></a>

`InvalidEmailsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Any`
    :   Unix timestamp when the invalid email was recorded

    `email: Any`
    :   The invalid email address

    `reason: Any`
    :   The reason the email is invalid

<a id="InvalidEmailsContainsCondition"></a>

`InvalidEmailsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyValueFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsEqCondition"></a>

`InvalidEmailsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsFuzzyCondition"></a>

`InvalidEmailsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsStringFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsGtCondition"></a>

`InvalidEmailsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsGteCondition"></a>

`InvalidEmailsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsInCondition"></a>

`InvalidEmailsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsInFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsInFilter"></a>

`InvalidEmailsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: list[int]`
    :   Unix timestamp when the invalid email was recorded

    `email: list[str]`
    :   The invalid email address

    `reason: list[str]`
    :   The reason the email is invalid

<a id="InvalidEmailsKeywordCondition"></a>

`InvalidEmailsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsStringFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsLikeCondition"></a>

`InvalidEmailsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsStringFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsListParams"></a>

`InvalidEmailsListParams(*args, **kwargs)`
:   Parameters for invalid_emails.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="InvalidEmailsLtCondition"></a>

`InvalidEmailsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsLteCondition"></a>

`InvalidEmailsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsNeqCondition"></a>

`InvalidEmailsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

<a id="InvalidEmailsNotCondition"></a>

`InvalidEmailsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyCondition`
    :   The type of the None singleton.

<a id="InvalidEmailsOrCondition"></a>

`InvalidEmailsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyCondition]`
    :   The type of the None singleton.

<a id="InvalidEmailsSearchFilter"></a>

`InvalidEmailsSearchFilter(*args, **kwargs)`
:   Available fields for filtering invalid_emails search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the invalid email was recorded

    `email: str | None`
    :   The invalid email address

    `reason: str | None`
    :   The reason the email is invalid

<a id="InvalidEmailsSearchQuery"></a>

`InvalidEmailsSearchQuery(*args, **kwargs)`
:   Search query for invalid_emails entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSortFilter]`
    :   The type of the None singleton.

<a id="InvalidEmailsSortFilter"></a>

`InvalidEmailsSortFilter(*args, **kwargs)`
:   Available fields for sorting invalid_emails search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   Unix timestamp when the invalid email was recorded

    `email: Literal['asc', 'desc']`
    :   The invalid email address

    `reason: Literal['asc', 'desc']`
    :   The reason the email is invalid

<a id="InvalidEmailsStringFilter"></a>

`InvalidEmailsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   Unix timestamp when the invalid email was recorded

    `email: str`
    :   The invalid email address

    `reason: str`
    :   The reason the email is invalid

<a id="ListsAndCondition"></a>

`ListsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.ListsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyCondition]`
    :   The type of the None singleton.

<a id="ListsAnyCondition"></a>

`ListsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsAnyValueFilter"></a>

`ListsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contact_count: Any`
    :   Number of contacts in the list

    `id: Any`
    :   Unique list identifier

    `metadata: Any`
    :   Metadata about the list resource

    `name: Any`
    :   Name of the list

<a id="ListsContainsCondition"></a>

`ListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsEqCondition"></a>

`ListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsFuzzyCondition"></a>

`ListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsGetParams"></a>

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ListsGtCondition"></a>

`ListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsGteCondition"></a>

`ListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsInCondition"></a>

`ListsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.ListsInFilter`
    :   The type of the None singleton.

<a id="ListsInFilter"></a>

`ListsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contact_count: list[int]`
    :   Number of contacts in the list

    `id: list[str]`
    :   Unique list identifier

    `metadata: list[dict[str, typing.Any]]`
    :   Metadata about the list resource

    `name: list[str]`
    :   Name of the list

<a id="ListsKeywordCondition"></a>

`ListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsLikeCondition"></a>

`ListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsListParams"></a>

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

<a id="ListsLtCondition"></a>

`ListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsLteCondition"></a>

`ListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNeqCondition"></a>

`ListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNotCondition"></a>

`ListsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.ListsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyCondition`
    :   The type of the None singleton.

<a id="ListsOrCondition"></a>

`ListsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.ListsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyCondition]`
    :   The type of the None singleton.

<a id="ListsSearchFilter"></a>

`ListsSearchFilter(*args, **kwargs)`
:   Available fields for filtering lists search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contact_count: int | None`
    :   Number of contacts in the list

    `id: str | None`
    :   Unique list identifier

    `metadata: dict[str, typing.Any] | None`
    :   Metadata about the list resource

    `name: str | None`
    :   Name of the list

<a id="ListsSearchQuery"></a>

`ListsSearchQuery(*args, **kwargs)`
:   Search query for lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.ListsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.ListsSortFilter]`
    :   The type of the None singleton.

<a id="ListsSortFilter"></a>

`ListsSortFilter(*args, **kwargs)`
:   Available fields for sorting lists search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contact_count: Literal['asc', 'desc']`
    :   Number of contacts in the list

    `id: Literal['asc', 'desc']`
    :   Unique list identifier

    `metadata: Literal['asc', 'desc']`
    :   Metadata about the list resource

    `name: Literal['asc', 'desc']`
    :   Name of the list

<a id="ListsStringFilter"></a>

`ListsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contact_count: str`
    :   Number of contacts in the list

    `id: str`
    :   Unique list identifier

    `metadata: str`
    :   Metadata about the list resource

    `name: str`
    :   Name of the list

<a id="SegmentsAndCondition"></a>

`SegmentsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyCondition]`
    :   The type of the None singleton.

<a id="SegmentsAnyCondition"></a>

`SegmentsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="SegmentsAnyValueFilter"></a>

`SegmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contacts_count: Any`
    :   Number of contacts in the segment

    `created_at: Any`
    :   When the segment was created

    `id: Any`
    :   Unique segment identifier

    `name: Any`
    :   Segment name

    `next_sample_update: Any`
    :   When the next sample update will occur

    `parent_list_ids: Any`
    :   IDs of parent lists

    `query_version: Any`
    :   Query version used

    `sample_updated_at: Any`
    :   When the sample was last updated

    `status: Any`
    :   Segment status details

    `updated_at: Any`
    :   When the segment was last updated

<a id="SegmentsContainsCondition"></a>

`SegmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="SegmentsEqCondition"></a>

`SegmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsFuzzyCondition"></a>

`SegmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsStringFilter`
    :   The type of the None singleton.

<a id="SegmentsGetParams"></a>

`SegmentsGetParams(*args, **kwargs)`
:   Parameters for segments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `segment_id: str`
    :   The type of the None singleton.

<a id="SegmentsGtCondition"></a>

`SegmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsGteCondition"></a>

`SegmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsInCondition"></a>

`SegmentsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsInFilter`
    :   The type of the None singleton.

<a id="SegmentsInFilter"></a>

`SegmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contacts_count: list[int]`
    :   Number of contacts in the segment

    `created_at: list[str]`
    :   When the segment was created

    `id: list[str]`
    :   Unique segment identifier

    `name: list[str]`
    :   Segment name

    `next_sample_update: list[str]`
    :   When the next sample update will occur

    `parent_list_ids: list[list[typing.Any]]`
    :   IDs of parent lists

    `query_version: list[str]`
    :   Query version used

    `sample_updated_at: list[str]`
    :   When the sample was last updated

    `status: list[dict[str, typing.Any]]`
    :   Segment status details

    `updated_at: list[str]`
    :   When the segment was last updated

<a id="SegmentsKeywordCondition"></a>

`SegmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsStringFilter`
    :   The type of the None singleton.

<a id="SegmentsLikeCondition"></a>

`SegmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsStringFilter`
    :   The type of the None singleton.

<a id="SegmentsListParams"></a>

`SegmentsListParams(*args, **kwargs)`
:   Parameters for segments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="SegmentsLtCondition"></a>

`SegmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsLteCondition"></a>

`SegmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsNeqCondition"></a>

`SegmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsNotCondition"></a>

`SegmentsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyCondition`
    :   The type of the None singleton.

<a id="SegmentsOrCondition"></a>

`SegmentsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyCondition]`
    :   The type of the None singleton.

<a id="SegmentsSearchFilter"></a>

`SegmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering segments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contacts_count: int | None`
    :   Number of contacts in the segment

    `created_at: str | None`
    :   When the segment was created

    `id: str | None`
    :   Unique segment identifier

    `name: str | None`
    :   Segment name

    `next_sample_update: str | None`
    :   When the next sample update will occur

    `parent_list_ids: list[typing.Any] | None`
    :   IDs of parent lists

    `query_version: str | None`
    :   Query version used

    `sample_updated_at: str | None`
    :   When the sample was last updated

    `status: dict[str, typing.Any] | None`
    :   Segment status details

    `updated_at: str | None`
    :   When the segment was last updated

<a id="SegmentsSearchQuery"></a>

`SegmentsSearchQuery(*args, **kwargs)`
:   Search query for segments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSortFilter]`
    :   The type of the None singleton.

<a id="SegmentsSortFilter"></a>

`SegmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting segments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contacts_count: Literal['asc', 'desc']`
    :   Number of contacts in the segment

    `created_at: Literal['asc', 'desc']`
    :   When the segment was created

    `id: Literal['asc', 'desc']`
    :   Unique segment identifier

    `name: Literal['asc', 'desc']`
    :   Segment name

    `next_sample_update: Literal['asc', 'desc']`
    :   When the next sample update will occur

    `parent_list_ids: Literal['asc', 'desc']`
    :   IDs of parent lists

    `query_version: Literal['asc', 'desc']`
    :   Query version used

    `sample_updated_at: Literal['asc', 'desc']`
    :   When the sample was last updated

    `status: Literal['asc', 'desc']`
    :   Segment status details

    `updated_at: Literal['asc', 'desc']`
    :   When the segment was last updated

<a id="SegmentsStringFilter"></a>

`SegmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contacts_count: str`
    :   Number of contacts in the segment

    `created_at: str`
    :   When the segment was created

    `id: str`
    :   Unique segment identifier

    `name: str`
    :   Segment name

    `next_sample_update: str`
    :   When the next sample update will occur

    `parent_list_ids: str`
    :   IDs of parent lists

    `query_version: str`
    :   Query version used

    `sample_updated_at: str`
    :   When the sample was last updated

    `status: str`
    :   Segment status details

    `updated_at: str`
    :   When the segment was last updated

<a id="SinglesendStatsAndCondition"></a>

`SinglesendStatsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyCondition]`
    :   The type of the None singleton.

<a id="SinglesendStatsAnyCondition"></a>

`SinglesendStatsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyValueFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsAnyValueFilter"></a>

`SinglesendStatsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_phase: Any`
    :   The A/B test phase

    `ab_variation: Any`
    :   The A/B test variation

    `aggregation: Any`
    :   The aggregation type

    `id: Any`
    :   The single send ID

    `stats: Any`
    :   Email statistics for the single send

<a id="SinglesendStatsContainsCondition"></a>

`SinglesendStatsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyValueFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsEqCondition"></a>

`SinglesendStatsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsFuzzyCondition"></a>

`SinglesendStatsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsStringFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsGtCondition"></a>

`SinglesendStatsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsGteCondition"></a>

`SinglesendStatsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsInCondition"></a>

`SinglesendStatsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsInFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsInFilter"></a>

`SinglesendStatsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_phase: list[str]`
    :   The A/B test phase

    `ab_variation: list[str]`
    :   The A/B test variation

    `aggregation: list[str]`
    :   The aggregation type

    `id: list[str]`
    :   The single send ID

    `stats: list[dict[str, typing.Any]]`
    :   Email statistics for the single send

<a id="SinglesendStatsKeywordCondition"></a>

`SinglesendStatsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsStringFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsLikeCondition"></a>

`SinglesendStatsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsStringFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsListParams"></a>

`SinglesendStatsListParams(*args, **kwargs)`
:   Parameters for singlesend_stats.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

<a id="SinglesendStatsLtCondition"></a>

`SinglesendStatsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsLteCondition"></a>

`SinglesendStatsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsNeqCondition"></a>

`SinglesendStatsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendStatsNotCondition"></a>

`SinglesendStatsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyCondition`
    :   The type of the None singleton.

<a id="SinglesendStatsOrCondition"></a>

`SinglesendStatsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyCondition]`
    :   The type of the None singleton.

<a id="SinglesendStatsSearchFilter"></a>

`SinglesendStatsSearchFilter(*args, **kwargs)`
:   Available fields for filtering singlesend_stats search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_phase: str | None`
    :   The A/B test phase

    `ab_variation: str | None`
    :   The A/B test variation

    `aggregation: str | None`
    :   The aggregation type

    `id: str | None`
    :   The single send ID

    `stats: dict[str, typing.Any] | None`
    :   Email statistics for the single send

<a id="SinglesendStatsSearchQuery"></a>

`SinglesendStatsSearchQuery(*args, **kwargs)`
:   Search query for singlesend_stats entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSortFilter]`
    :   The type of the None singleton.

<a id="SinglesendStatsSortFilter"></a>

`SinglesendStatsSortFilter(*args, **kwargs)`
:   Available fields for sorting singlesend_stats search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_phase: Literal['asc', 'desc']`
    :   The A/B test phase

    `ab_variation: Literal['asc', 'desc']`
    :   The A/B test variation

    `aggregation: Literal['asc', 'desc']`
    :   The aggregation type

    `id: Literal['asc', 'desc']`
    :   The single send ID

    `stats: Literal['asc', 'desc']`
    :   Email statistics for the single send

<a id="SinglesendStatsStringFilter"></a>

`SinglesendStatsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_phase: str`
    :   The A/B test phase

    `ab_variation: str`
    :   The A/B test variation

    `aggregation: str`
    :   The aggregation type

    `id: str`
    :   The single send ID

    `stats: str`
    :   Email statistics for the single send

<a id="SinglesendsAndCondition"></a>

`SinglesendsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyCondition]`
    :   The type of the None singleton.

<a id="SinglesendsAnyCondition"></a>

`SinglesendsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyValueFilter`
    :   The type of the None singleton.

<a id="SinglesendsAnyValueFilter"></a>

`SinglesendsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `categories: Any`
    :   Categories associated with this single send

    `created_at: Any`
    :   When the single send was created

    `id: Any`
    :   Unique single send identifier

    `is_abtest: Any`
    :   Whether this is an A/B test

    `name: Any`
    :   Single send name

    `send_at: Any`
    :   Scheduled send time

    `status: Any`
    :   Current status: draft, scheduled, or triggered

    `updated_at: Any`
    :   When the single send was last updated

<a id="SinglesendsContainsCondition"></a>

`SinglesendsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyValueFilter`
    :   The type of the None singleton.

<a id="SinglesendsEqCondition"></a>

`SinglesendsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendsFuzzyCondition"></a>

`SinglesendsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsStringFilter`
    :   The type of the None singleton.

<a id="SinglesendsGetParams"></a>

`SinglesendsGetParams(*args, **kwargs)`
:   Parameters for singlesends.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SinglesendsGtCondition"></a>

`SinglesendsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendsGteCondition"></a>

`SinglesendsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendsInCondition"></a>

`SinglesendsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsInFilter`
    :   The type of the None singleton.

<a id="SinglesendsInFilter"></a>

`SinglesendsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `categories: list[list[typing.Any]]`
    :   Categories associated with this single send

    `created_at: list[str]`
    :   When the single send was created

    `id: list[str]`
    :   Unique single send identifier

    `is_abtest: list[bool]`
    :   Whether this is an A/B test

    `name: list[str]`
    :   Single send name

    `send_at: list[str]`
    :   Scheduled send time

    `status: list[str]`
    :   Current status: draft, scheduled, or triggered

    `updated_at: list[str]`
    :   When the single send was last updated

<a id="SinglesendsKeywordCondition"></a>

`SinglesendsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsStringFilter`
    :   The type of the None singleton.

<a id="SinglesendsLikeCondition"></a>

`SinglesendsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsStringFilter`
    :   The type of the None singleton.

<a id="SinglesendsListParams"></a>

`SinglesendsListParams(*args, **kwargs)`
:   Parameters for singlesends.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

<a id="SinglesendsLtCondition"></a>

`SinglesendsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendsLteCondition"></a>

`SinglesendsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendsNeqCondition"></a>

`SinglesendsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

<a id="SinglesendsNotCondition"></a>

`SinglesendsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyCondition`
    :   The type of the None singleton.

<a id="SinglesendsOrCondition"></a>

`SinglesendsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyCondition]`
    :   The type of the None singleton.

<a id="SinglesendsSearchFilter"></a>

`SinglesendsSearchFilter(*args, **kwargs)`
:   Available fields for filtering singlesends search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `categories: list[typing.Any] | None`
    :   Categories associated with this single send

    `created_at: str | None`
    :   When the single send was created

    `id: str | None`
    :   Unique single send identifier

    `is_abtest: bool | None`
    :   Whether this is an A/B test

    `name: str | None`
    :   Single send name

    `send_at: str | None`
    :   Scheduled send time

    `status: str | None`
    :   Current status: draft, scheduled, or triggered

    `updated_at: str | None`
    :   When the single send was last updated

<a id="SinglesendsSearchQuery"></a>

`SinglesendsSearchQuery(*args, **kwargs)`
:   Search query for singlesends entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSortFilter]`
    :   The type of the None singleton.

<a id="SinglesendsSortFilter"></a>

`SinglesendsSortFilter(*args, **kwargs)`
:   Available fields for sorting singlesends search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `categories: Literal['asc', 'desc']`
    :   Categories associated with this single send

    `created_at: Literal['asc', 'desc']`
    :   When the single send was created

    `id: Literal['asc', 'desc']`
    :   Unique single send identifier

    `is_abtest: Literal['asc', 'desc']`
    :   Whether this is an A/B test

    `name: Literal['asc', 'desc']`
    :   Single send name

    `send_at: Literal['asc', 'desc']`
    :   Scheduled send time

    `status: Literal['asc', 'desc']`
    :   Current status: draft, scheduled, or triggered

    `updated_at: Literal['asc', 'desc']`
    :   When the single send was last updated

<a id="SinglesendsStringFilter"></a>

`SinglesendsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `categories: str`
    :   Categories associated with this single send

    `created_at: str`
    :   When the single send was created

    `id: str`
    :   Unique single send identifier

    `is_abtest: str`
    :   Whether this is an A/B test

    `name: str`
    :   Single send name

    `send_at: str`
    :   Scheduled send time

    `status: str`
    :   Current status: draft, scheduled, or triggered

    `updated_at: str`
    :   When the single send was last updated

<a id="SpamReportsListParams"></a>

`SpamReportsListParams(*args, **kwargs)`
:   Parameters for spam_reports.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersAndCondition"></a>

`SuppressionGroupMembersAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyCondition]`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersAnyCondition"></a>

`SuppressionGroupMembersAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyValueFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersAnyValueFilter"></a>

`SuppressionGroupMembersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Unix timestamp when the suppression was created

    `email: Any`
    :   The suppressed email address

    `group_id: Any`
    :   ID of the suppression group

    `group_name: Any`
    :   Name of the suppression group

<a id="SuppressionGroupMembersContainsCondition"></a>

`SuppressionGroupMembersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyValueFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersEqCondition"></a>

`SuppressionGroupMembersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersFuzzyCondition"></a>

`SuppressionGroupMembersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersStringFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersGtCondition"></a>

`SuppressionGroupMembersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersGteCondition"></a>

`SuppressionGroupMembersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersInCondition"></a>

`SuppressionGroupMembersInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersInFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersInFilter"></a>

`SuppressionGroupMembersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[int]`
    :   Unix timestamp when the suppression was created

    `email: list[str]`
    :   The suppressed email address

    `group_id: list[int]`
    :   ID of the suppression group

    `group_name: list[str]`
    :   Name of the suppression group

<a id="SuppressionGroupMembersKeywordCondition"></a>

`SuppressionGroupMembersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersStringFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersLikeCondition"></a>

`SuppressionGroupMembersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersStringFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersListParams"></a>

`SuppressionGroupMembersListParams(*args, **kwargs)`
:   Parameters for suppression_group_members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersLtCondition"></a>

`SuppressionGroupMembersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersLteCondition"></a>

`SuppressionGroupMembersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersNeqCondition"></a>

`SuppressionGroupMembersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersNotCondition"></a>

`SuppressionGroupMembersNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyCondition`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersOrCondition"></a>

`SuppressionGroupMembersOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyCondition]`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersSearchFilter"></a>

`SuppressionGroupMembersSearchFilter(*args, **kwargs)`
:   Available fields for filtering suppression_group_members search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: int | None`
    :   Unix timestamp when the suppression was created

    `email: str | None`
    :   The suppressed email address

    `group_id: int | None`
    :   ID of the suppression group

    `group_name: str | None`
    :   Name of the suppression group

<a id="SuppressionGroupMembersSearchQuery"></a>

`SuppressionGroupMembersSearchQuery(*args, **kwargs)`
:   Search query for suppression_group_members entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSortFilter]`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersSortFilter"></a>

`SuppressionGroupMembersSortFilter(*args, **kwargs)`
:   Available fields for sorting suppression_group_members search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Unix timestamp when the suppression was created

    `email: Literal['asc', 'desc']`
    :   The suppressed email address

    `group_id: Literal['asc', 'desc']`
    :   ID of the suppression group

    `group_name: Literal['asc', 'desc']`
    :   Name of the suppression group

<a id="SuppressionGroupMembersStringFilter"></a>

`SuppressionGroupMembersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Unix timestamp when the suppression was created

    `email: str`
    :   The suppressed email address

    `group_id: str`
    :   ID of the suppression group

    `group_name: str`
    :   Name of the suppression group

<a id="SuppressionGroupsAndCondition"></a>

`SuppressionGroupsAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="SuppressionGroupsAnyCondition"></a>

`SuppressionGroupsAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsAnyValueFilter"></a>

`SuppressionGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Any`
    :   Description of the suppression group

    `id: Any`
    :   Unique suppression group identifier

    `is_default: Any`
    :   Whether this is the default suppression group

    `name: Any`
    :   Suppression group name

    `unsubscribes: Any`
    :   Number of unsubscribes in this group

<a id="SuppressionGroupsContainsCondition"></a>

`SuppressionGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsEqCondition"></a>

`SuppressionGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsFuzzyCondition"></a>

`SuppressionGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsStringFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsGetParams"></a>

`SuppressionGroupsGetParams(*args, **kwargs)`
:   Parameters for suppression_groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

<a id="SuppressionGroupsGtCondition"></a>

`SuppressionGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsGteCondition"></a>

`SuppressionGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsInCondition"></a>

`SuppressionGroupsInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsInFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsInFilter"></a>

`SuppressionGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: list[str]`
    :   Description of the suppression group

    `id: list[int]`
    :   Unique suppression group identifier

    `is_default: list[bool]`
    :   Whether this is the default suppression group

    `name: list[str]`
    :   Suppression group name

    `unsubscribes: list[int]`
    :   Number of unsubscribes in this group

<a id="SuppressionGroupsKeywordCondition"></a>

`SuppressionGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsStringFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsLikeCondition"></a>

`SuppressionGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsStringFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsListParams"></a>

`SuppressionGroupsListParams(*args, **kwargs)`
:   Parameters for suppression_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="SuppressionGroupsLtCondition"></a>

`SuppressionGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsLteCondition"></a>

`SuppressionGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsNeqCondition"></a>

`SuppressionGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

<a id="SuppressionGroupsNotCondition"></a>

`SuppressionGroupsNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyCondition`
    :   The type of the None singleton.

<a id="SuppressionGroupsOrCondition"></a>

`SuppressionGroupsOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="SuppressionGroupsSearchFilter"></a>

`SuppressionGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering suppression_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str | None`
    :   Description of the suppression group

    `id: int | None`
    :   Unique suppression group identifier

    `is_default: bool | None`
    :   Whether this is the default suppression group

    `name: str | None`
    :   Suppression group name

    `unsubscribes: int | None`
    :   Number of unsubscribes in this group

<a id="SuppressionGroupsSearchQuery"></a>

`SuppressionGroupsSearchQuery(*args, **kwargs)`
:   Search query for suppression_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSortFilter]`
    :   The type of the None singleton.

<a id="SuppressionGroupsSortFilter"></a>

`SuppressionGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting suppression_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: Literal['asc', 'desc']`
    :   Description of the suppression group

    `id: Literal['asc', 'desc']`
    :   Unique suppression group identifier

    `is_default: Literal['asc', 'desc']`
    :   Whether this is the default suppression group

    `name: Literal['asc', 'desc']`
    :   Suppression group name

    `unsubscribes: Literal['asc', 'desc']`
    :   Number of unsubscribes in this group

<a id="SuppressionGroupsStringFilter"></a>

`SuppressionGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   Description of the suppression group

    `id: str`
    :   Unique suppression group identifier

    `is_default: str`
    :   Whether this is the default suppression group

    `name: str`
    :   Suppression group name

    `unsubscribes: str`
    :   Number of unsubscribes in this group

<a id="TemplatesAndCondition"></a>

`TemplatesAndCondition(*args, **kwargs)`
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

    `and: list[airbyte_agent_sdk.connectors.sendgrid.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyCondition]`
    :   The type of the None singleton.

<a id="TemplatesAnyCondition"></a>

`TemplatesAnyCondition(*args, **kwargs)`
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

    `any: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TemplatesAnyValueFilter"></a>

`TemplatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generation: Any`
    :   Template generation (legacy or dynamic)

    `id: Any`
    :   Unique template identifier

    `name: Any`
    :   Template name

    `updated_at: Any`
    :   When the template was last updated

    `versions: Any`
    :   Template versions

<a id="TemplatesContainsCondition"></a>

`TemplatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyValueFilter`
    :   The type of the None singleton.

<a id="TemplatesEqCondition"></a>

`TemplatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesFuzzyCondition"></a>

`TemplatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesGetParams"></a>

`TemplatesGetParams(*args, **kwargs)`
:   Parameters for templates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `template_id: str`
    :   The type of the None singleton.

<a id="TemplatesGtCondition"></a>

`TemplatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesGteCondition"></a>

`TemplatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesInCondition"></a>

`TemplatesInCondition(*args, **kwargs)`
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

    `in: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesInFilter`
    :   The type of the None singleton.

<a id="TemplatesInFilter"></a>

`TemplatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generation: list[str]`
    :   Template generation (legacy or dynamic)

    `id: list[str]`
    :   Unique template identifier

    `name: list[str]`
    :   Template name

    `updated_at: list[str]`
    :   When the template was last updated

    `versions: list[list[typing.Any]]`
    :   Template versions

<a id="TemplatesKeywordCondition"></a>

`TemplatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesLikeCondition"></a>

`TemplatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesStringFilter`
    :   The type of the None singleton.

<a id="TemplatesListParams"></a>

`TemplatesListParams(*args, **kwargs)`
:   Parameters for templates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generations: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="TemplatesLtCondition"></a>

`TemplatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesLteCondition"></a>

`TemplatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesNeqCondition"></a>

`TemplatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

<a id="TemplatesNotCondition"></a>

`TemplatesNotCondition(*args, **kwargs)`
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

    `not: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyCondition`
    :   The type of the None singleton.

<a id="TemplatesOrCondition"></a>

`TemplatesOrCondition(*args, **kwargs)`
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

    `or: list[airbyte_agent_sdk.connectors.sendgrid.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyCondition]`
    :   The type of the None singleton.

<a id="TemplatesSearchFilter"></a>

`TemplatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering templates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generation: str | None`
    :   Template generation (legacy or dynamic)

    `id: str | None`
    :   Unique template identifier

    `name: str | None`
    :   Template name

    `updated_at: str | None`
    :   When the template was last updated

    `versions: list[typing.Any] | None`
    :   Template versions

<a id="TemplatesSearchQuery"></a>

`TemplatesSearchQuery(*args, **kwargs)`
:   Search query for templates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSortFilter]`
    :   The type of the None singleton.

<a id="TemplatesSortFilter"></a>

`TemplatesSortFilter(*args, **kwargs)`
:   Available fields for sorting templates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generation: Literal['asc', 'desc']`
    :   Template generation (legacy or dynamic)

    `id: Literal['asc', 'desc']`
    :   Unique template identifier

    `name: Literal['asc', 'desc']`
    :   Template name

    `updated_at: Literal['asc', 'desc']`
    :   When the template was last updated

    `versions: Literal['asc', 'desc']`
    :   Template versions

<a id="TemplatesStringFilter"></a>

`TemplatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generation: str`
    :   Template generation (legacy or dynamic)

    `id: str`
    :   Unique template identifier

    `name: str`
    :   Template name

    `updated_at: str`
    :   When the template was last updated

    `versions: str`
    :   Template versions