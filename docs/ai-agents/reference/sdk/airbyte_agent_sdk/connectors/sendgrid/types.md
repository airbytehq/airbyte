---
id: airbyte_agent_sdk-connectors-sendgrid-types
title: airbyte_agent_sdk.connectors.sendgrid.types
---

Module airbyte_agent_sdk.connectors.sendgrid.types
==================================================
Type definitions for sendgrid connector.

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

`BlocksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyValueFilter`
    :   The type of the None singleton.

`BlocksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.BlocksStringFilter`
    :   The type of the None singleton.

`BlocksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

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

`BlocksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.BlocksStringFilter`
    :   The type of the None singleton.

`BlocksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.BlocksStringFilter`
    :   The type of the None singleton.

`BlocksListParams(*args, **kwargs)`
:   Parameters for blocks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

`BlocksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

`BlocksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.BlocksSearchFilter`
    :   The type of the None singleton.

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

`BlocksSearchQuery(*args, **kwargs)`
:   Search query for blocks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.BlocksEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BlocksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.BlocksSortFilter]`
    :   The type of the None singleton.

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

`BouncesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyValueFilter`
    :   The type of the None singleton.

`BouncesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

`BouncesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.BouncesStringFilter`
    :   The type of the None singleton.

`BouncesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

`BouncesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

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

`BouncesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.BouncesStringFilter`
    :   The type of the None singleton.

`BouncesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.BouncesStringFilter`
    :   The type of the None singleton.

`BouncesListParams(*args, **kwargs)`
:   Parameters for bounces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

`BouncesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

`BouncesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

`BouncesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.BouncesSearchFilter`
    :   The type of the None singleton.

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

`BouncesSearchQuery(*args, **kwargs)`
:   Search query for bounces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.BouncesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.BouncesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.BouncesSortFilter]`
    :   The type of the None singleton.

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

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

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

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsStringFilter`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSearchFilter`
    :   The type of the None singleton.

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

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.CampaignsSortFilter]`
    :   The type of the None singleton.

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

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

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

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.ContactsSearchFilter`
    :   The type of the None singleton.

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

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.ContactsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.ContactsSortFilter]`
    :   The type of the None singleton.

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

`GlobalSuppressionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Any`
    :   Unix timestamp when the global suppression was created

    `email: Any`
    :   The globally suppressed email address

`GlobalSuppressionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyValueFilter`
    :   The type of the None singleton.

`GlobalSuppressionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

`GlobalSuppressionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsStringFilter`
    :   The type of the None singleton.

`GlobalSuppressionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

`GlobalSuppressionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

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

`GlobalSuppressionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: list[int]`
    :   Unix timestamp when the global suppression was created

    `email: list[str]`
    :   The globally suppressed email address

`GlobalSuppressionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsStringFilter`
    :   The type of the None singleton.

`GlobalSuppressionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsStringFilter`
    :   The type of the None singleton.

`GlobalSuppressionsListParams(*args, **kwargs)`
:   Parameters for global_suppressions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

`GlobalSuppressionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

`GlobalSuppressionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

`GlobalSuppressionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSearchFilter`
    :   The type of the None singleton.

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

`GlobalSuppressionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering global_suppressions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the global suppression was created

    `email: str | None`
    :   The globally suppressed email address

`GlobalSuppressionsSearchQuery(*args, **kwargs)`
:   Search query for global_suppressions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.GlobalSuppressionsSortFilter]`
    :   The type of the None singleton.

`GlobalSuppressionsSortFilter(*args, **kwargs)`
:   Available fields for sorting global_suppressions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: Literal['asc', 'desc']`
    :   Unix timestamp when the global suppression was created

    `email: Literal['asc', 'desc']`
    :   The globally suppressed email address

`GlobalSuppressionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: str`
    :   Unix timestamp when the global suppression was created

    `email: str`
    :   The globally suppressed email address

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

`InvalidEmailsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyValueFilter`
    :   The type of the None singleton.

`InvalidEmailsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

`InvalidEmailsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsStringFilter`
    :   The type of the None singleton.

`InvalidEmailsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

`InvalidEmailsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

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

`InvalidEmailsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsStringFilter`
    :   The type of the None singleton.

`InvalidEmailsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsStringFilter`
    :   The type of the None singleton.

`InvalidEmailsListParams(*args, **kwargs)`
:   Parameters for invalid_emails.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

`InvalidEmailsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

`InvalidEmailsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

`InvalidEmailsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSearchFilter`
    :   The type of the None singleton.

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

`InvalidEmailsSearchQuery(*args, **kwargs)`
:   Search query for invalid_emails entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.InvalidEmailsSortFilter]`
    :   The type of the None singleton.

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

`ListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyValueFilter`
    :   The type of the None singleton.

`ListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.ListsStringFilter`
    :   The type of the None singleton.

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

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

`ListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.ListsStringFilter`
    :   The type of the None singleton.

`ListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.ListsStringFilter`
    :   The type of the None singleton.

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

`ListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

`ListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.ListsSearchFilter`
    :   The type of the None singleton.

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

`ListsSearchQuery(*args, **kwargs)`
:   Search query for lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.ListsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.ListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.ListsSortFilter]`
    :   The type of the None singleton.

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

`SegmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyValueFilter`
    :   The type of the None singleton.

`SegmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

`SegmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsStringFilter`
    :   The type of the None singleton.

`SegmentsGetParams(*args, **kwargs)`
:   Parameters for segments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `segment_id: str`
    :   The type of the None singleton.

`SegmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

`SegmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

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

`SegmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsStringFilter`
    :   The type of the None singleton.

`SegmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsStringFilter`
    :   The type of the None singleton.

`SegmentsListParams(*args, **kwargs)`
:   Parameters for segments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`SegmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

`SegmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

`SegmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSearchFilter`
    :   The type of the None singleton.

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

`SegmentsSearchQuery(*args, **kwargs)`
:   Search query for segments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SegmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SegmentsSortFilter]`
    :   The type of the None singleton.

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

`SinglesendStatsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyValueFilter`
    :   The type of the None singleton.

`SinglesendStatsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

`SinglesendStatsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsStringFilter`
    :   The type of the None singleton.

`SinglesendStatsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

`SinglesendStatsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

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

`SinglesendStatsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsStringFilter`
    :   The type of the None singleton.

`SinglesendStatsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsStringFilter`
    :   The type of the None singleton.

`SinglesendStatsListParams(*args, **kwargs)`
:   Parameters for singlesend_stats.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

`SinglesendStatsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

`SinglesendStatsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

`SinglesendStatsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSearchFilter`
    :   The type of the None singleton.

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

`SinglesendStatsSearchQuery(*args, **kwargs)`
:   Search query for singlesend_stats entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendStatsSortFilter]`
    :   The type of the None singleton.

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

`SinglesendsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyValueFilter`
    :   The type of the None singleton.

`SinglesendsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

`SinglesendsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsStringFilter`
    :   The type of the None singleton.

`SinglesendsGetParams(*args, **kwargs)`
:   Parameters for singlesends.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`SinglesendsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

`SinglesendsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

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

`SinglesendsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsStringFilter`
    :   The type of the None singleton.

`SinglesendsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsStringFilter`
    :   The type of the None singleton.

`SinglesendsListParams(*args, **kwargs)`
:   Parameters for singlesends.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page_size: int`
    :   The type of the None singleton.

`SinglesendsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

`SinglesendsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

`SinglesendsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSearchFilter`
    :   The type of the None singleton.

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

`SinglesendsSearchQuery(*args, **kwargs)`
:   Search query for singlesends entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SinglesendsSortFilter]`
    :   The type of the None singleton.

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

`SpamReportsListParams(*args, **kwargs)`
:   Parameters for spam_reports.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

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

`SuppressionGroupMembersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyValueFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersStringFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

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

`SuppressionGroupMembersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersStringFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersStringFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersListParams(*args, **kwargs)`
:   Parameters for suppression_group_members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

`SuppressionGroupMembersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupMembersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSearchFilter`
    :   The type of the None singleton.

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

`SuppressionGroupMembersSearchQuery(*args, **kwargs)`
:   Search query for suppression_group_members entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupMembersSortFilter]`
    :   The type of the None singleton.

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

`SuppressionGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyValueFilter`
    :   The type of the None singleton.

`SuppressionGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsStringFilter`
    :   The type of the None singleton.

`SuppressionGroupsGetParams(*args, **kwargs)`
:   Parameters for suppression_groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

`SuppressionGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

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

`SuppressionGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsStringFilter`
    :   The type of the None singleton.

`SuppressionGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsStringFilter`
    :   The type of the None singleton.

`SuppressionGroupsListParams(*args, **kwargs)`
:   Parameters for suppression_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`SuppressionGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

`SuppressionGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSearchFilter`
    :   The type of the None singleton.

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

`SuppressionGroupsSearchQuery(*args, **kwargs)`
:   Search query for suppression_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsInCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.SuppressionGroupsSortFilter]`
    :   The type of the None singleton.

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

`TemplatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyValueFilter`
    :   The type of the None singleton.

`TemplatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

`TemplatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesStringFilter`
    :   The type of the None singleton.

`TemplatesGetParams(*args, **kwargs)`
:   Parameters for templates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `template_id: str`
    :   The type of the None singleton.

`TemplatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

`TemplatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

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

`TemplatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesStringFilter`
    :   The type of the None singleton.

`TemplatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesStringFilter`
    :   The type of the None singleton.

`TemplatesListParams(*args, **kwargs)`
:   Parameters for templates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `generations: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`TemplatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

`TemplatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

`TemplatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSearchFilter`
    :   The type of the None singleton.

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

`TemplatesSearchQuery(*args, **kwargs)`
:   Search query for templates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.sendgrid.types.TemplatesEqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNeqCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesGteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLtCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLteCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesInCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesLikeCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesFuzzyCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesKeywordCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesContainsCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesNotCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAndCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesOrCondition | airbyte_agent_sdk.connectors.sendgrid.types.TemplatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.sendgrid.types.TemplatesSortFilter]`
    :   The type of the None singleton.

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