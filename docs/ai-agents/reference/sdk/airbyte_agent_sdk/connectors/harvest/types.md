---
id: airbyte_agent_sdk-connectors-harvest-types
title: airbyte_agent_sdk.connectors.harvest.types
---

Module airbyte_agent_sdk.connectors.harvest.types
=================================================
Type definitions for harvest connector.

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

`ClientsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition]`
    :   The type of the None singleton.

`ClientsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.ClientsAnyValueFilter`
    :   The type of the None singleton.

`ClientsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: Any`
    :   The client's postal address

    `created_at: Any`
    :   When the client record was created

    `currency: Any`
    :   The currency used by the client

    `id: Any`
    :   Unique identifier for the client

    `is_active: Any`
    :   Whether the client is active

    `name: Any`
    :   The client's name

    `updated_at: Any`
    :   When the client record was last updated

`ClientsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ClientsAnyValueFilter`
    :   The type of the None singleton.

`ClientsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

`ClientsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

`ClientsGetParams(*args, **kwargs)`
:   Parameters for clients.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ClientsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

`ClientsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

`ClientsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.ClientsInFilter`
    :   The type of the None singleton.

`ClientsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: list[str]`
    :   The client's postal address

    `created_at: list[str]`
    :   When the client record was created

    `currency: list[str]`
    :   The currency used by the client

    `id: list[int]`
    :   Unique identifier for the client

    `is_active: list[bool]`
    :   Whether the client is active

    `name: list[str]`
    :   The client's name

    `updated_at: list[str]`
    :   When the client record was last updated

`ClientsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

`ClientsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

`ClientsListParams(*args, **kwargs)`
:   Parameters for clients.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`ClientsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

`ClientsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

`ClientsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

`ClientsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition`
    :   The type of the None singleton.

`ClientsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition]`
    :   The type of the None singleton.

`ClientsSearchFilter(*args, **kwargs)`
:   Available fields for filtering clients search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: str | None`
    :   The client's postal address

    `created_at: str | None`
    :   When the client record was created

    `currency: str | None`
    :   The currency used by the client

    `id: int | None`
    :   Unique identifier for the client

    `is_active: bool | None`
    :   Whether the client is active

    `name: str | None`
    :   The client's name

    `updated_at: str | None`
    :   When the client record was last updated

`ClientsSearchQuery(*args, **kwargs)`
:   Search query for clients entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ClientsSortFilter]`
    :   The type of the None singleton.

`ClientsSortFilter(*args, **kwargs)`
:   Available fields for sorting clients search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: Literal['asc', 'desc']`
    :   The client's postal address

    `created_at: Literal['asc', 'desc']`
    :   When the client record was created

    `currency: Literal['asc', 'desc']`
    :   The currency used by the client

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the client

    `is_active: Literal['asc', 'desc']`
    :   Whether the client is active

    `name: Literal['asc', 'desc']`
    :   The client's name

    `updated_at: Literal['asc', 'desc']`
    :   When the client record was last updated

`ClientsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: str`
    :   The client's postal address

    `created_at: str`
    :   When the client record was created

    `currency: str`
    :   The currency used by the client

    `id: str`
    :   Unique identifier for the client

    `is_active: str`
    :   Whether the client is active

    `name: str`
    :   The client's name

    `updated_at: str`
    :   When the client record was last updated

`CompanyAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLikeCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition]`
    :   The type of the None singleton.

`CompanyAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.CompanyAnyValueFilter`
    :   The type of the None singleton.

`CompanyAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_uri: Any`
    :   The base URI

    `currency: Any`
    :   Currency used by the company

    `full_domain: Any`
    :   The full domain name

    `is_active: Any`
    :   Whether the company is active

    `name: Any`
    :   The name of the company

    `plan_type: Any`
    :   The plan type

    `weekly_capacity: Any`
    :   Weekly capacity in seconds

`CompanyContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.CompanyAnyValueFilter`
    :   The type of the None singleton.

`CompanyEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

`CompanyFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

`CompanyGetParams(*args, **kwargs)`
:   Parameters for company.get operation

    ### Ancestors (in MRO)

    * builtins.dict

`CompanyGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

`CompanyGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

`CompanyInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.CompanyInFilter`
    :   The type of the None singleton.

`CompanyInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_uri: list[str]`
    :   The base URI

    `currency: list[str]`
    :   Currency used by the company

    `full_domain: list[str]`
    :   The full domain name

    `is_active: list[bool]`
    :   Whether the company is active

    `name: list[str]`
    :   The name of the company

    `plan_type: list[str]`
    :   The plan type

    `weekly_capacity: list[int]`
    :   Weekly capacity in seconds

`CompanyKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

`CompanyLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

`CompanyLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

`CompanyLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

`CompanyNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

`CompanyNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLikeCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition`
    :   The type of the None singleton.

`CompanyOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLikeCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition]`
    :   The type of the None singleton.

`CompanySearchFilter(*args, **kwargs)`
:   Available fields for filtering company search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_uri: str | None`
    :   The base URI

    `currency: str | None`
    :   Currency used by the company

    `full_domain: str | None`
    :   The full domain name

    `is_active: bool | None`
    :   Whether the company is active

    `name: str | None`
    :   The name of the company

    `plan_type: str | None`
    :   The plan type

    `weekly_capacity: int | None`
    :   Weekly capacity in seconds

`CompanySearchQuery(*args, **kwargs)`
:   Search query for company entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLikeCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.CompanySortFilter]`
    :   The type of the None singleton.

`CompanySortFilter(*args, **kwargs)`
:   Available fields for sorting company search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_uri: Literal['asc', 'desc']`
    :   The base URI

    `currency: Literal['asc', 'desc']`
    :   Currency used by the company

    `full_domain: Literal['asc', 'desc']`
    :   The full domain name

    `is_active: Literal['asc', 'desc']`
    :   Whether the company is active

    `name: Literal['asc', 'desc']`
    :   The name of the company

    `plan_type: Literal['asc', 'desc']`
    :   The plan type

    `weekly_capacity: Literal['asc', 'desc']`
    :   Weekly capacity in seconds

`CompanyStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_uri: str`
    :   The base URI

    `currency: str`
    :   Currency used by the company

    `full_domain: str`
    :   The full domain name

    `is_active: str`
    :   Whether the company is active

    `name: str`
    :   The name of the company

    `plan_type: str`
    :   The plan type

    `weekly_capacity: str`
    :   Weekly capacity in seconds

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.harvest.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `client: Any`
    :   Client associated with the contact

    `created_at: Any`
    :   When created

    `email: Any`
    :   Email address

    `first_name: Any`
    :   First name

    `id: Any`
    :   Unique identifier

    `last_name: Any`
    :   Last name

    `title: Any`
    :   Job title

    `updated_at: Any`
    :   When last updated

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.harvest.types.ContactsInFilter`
    :   The type of the None singleton.

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `client: list[dict[str, typing.Any]]`
    :   Client associated with the contact

    `created_at: list[str]`
    :   When created

    `email: list[str]`
    :   Email address

    `first_name: list[str]`
    :   First name

    `id: list[int]`
    :   Unique identifier

    `last_name: list[str]`
    :   Last name

    `title: list[str]`
    :   Job title

    `updated_at: list[str]`
    :   When last updated

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition]`
    :   The type of the None singleton.

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `client: dict[str, typing.Any] | None`
    :   Client associated with the contact

    `created_at: str | None`
    :   When created

    `email: str | None`
    :   Email address

    `first_name: str | None`
    :   First name

    `id: int | None`
    :   Unique identifier

    `last_name: str | None`
    :   Last name

    `title: str | None`
    :   Job title

    `updated_at: str | None`
    :   When last updated

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ContactsSortFilter]`
    :   The type of the None singleton.

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `client: Literal['asc', 'desc']`
    :   Client associated with the contact

    `created_at: Literal['asc', 'desc']`
    :   When created

    `email: Literal['asc', 'desc']`
    :   Email address

    `first_name: Literal['asc', 'desc']`
    :   First name

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `last_name: Literal['asc', 'desc']`
    :   Last name

    `title: Literal['asc', 'desc']`
    :   Job title

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `client: str`
    :   Client associated with the contact

    `created_at: str`
    :   When created

    `email: str`
    :   Email address

    `first_name: str`
    :   First name

    `id: str`
    :   Unique identifier

    `last_name: str`
    :   Last name

    `title: str`
    :   Job title

    `updated_at: str`
    :   When last updated

`EstimateItemCategoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition]`
    :   The type of the None singleton.

`EstimateItemCategoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When created

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Category name

    `updated_at: Any`
    :   When last updated

`EstimateItemCategoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesGetParams(*args, **kwargs)`
:   Parameters for estimate_item_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`EstimateItemCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When created

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Category name

    `updated_at: list[str]`
    :   When last updated

`EstimateItemCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesListParams(*args, **kwargs)`
:   Parameters for estimate_item_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`EstimateItemCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

`EstimateItemCategoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition`
    :   The type of the None singleton.

`EstimateItemCategoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition]`
    :   The type of the None singleton.

`EstimateItemCategoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering estimate_item_categories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `name: str | None`
    :   Category name

    `updated_at: str | None`
    :   When last updated

`EstimateItemCategoriesSearchQuery(*args, **kwargs)`
:   Search query for estimate_item_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSortFilter]`
    :   The type of the None singleton.

`EstimateItemCategoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting estimate_item_categories search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When created

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Category name

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`EstimateItemCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When created

    `id: str`
    :   Unique identifier

    `name: str`
    :   Category name

    `updated_at: str`
    :   When last updated

`EstimatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition]`
    :   The type of the None singleton.

`EstimatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyValueFilter`
    :   The type of the None singleton.

`EstimatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Total amount

    `client: Any`
    :   Client details

    `created_at: Any`
    :   When created

    `currency: Any`
    :   Currency

    `id: Any`
    :   Unique identifier

    `issue_date: Any`
    :   Issue date

    `number: Any`
    :   Estimate number

    `state: Any`
    :   Current state

    `subject: Any`
    :   Subject

    `updated_at: Any`
    :   When last updated

`EstimatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyValueFilter`
    :   The type of the None singleton.

`EstimatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

`EstimatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

`EstimatesGetParams(*args, **kwargs)`
:   Parameters for estimates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`EstimatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

`EstimatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

`EstimatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.EstimatesInFilter`
    :   The type of the None singleton.

`EstimatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[float]`
    :   Total amount

    `client: list[dict[str, typing.Any]]`
    :   Client details

    `created_at: list[str]`
    :   When created

    `currency: list[str]`
    :   Currency

    `id: list[int]`
    :   Unique identifier

    `issue_date: list[str]`
    :   Issue date

    `number: list[str]`
    :   Estimate number

    `state: list[str]`
    :   Current state

    `subject: list[str]`
    :   Subject

    `updated_at: list[str]`
    :   When last updated

`EstimatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

`EstimatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

`EstimatesListParams(*args, **kwargs)`
:   Parameters for estimates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`EstimatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

`EstimatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

`EstimatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

`EstimatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition`
    :   The type of the None singleton.

`EstimatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition]`
    :   The type of the None singleton.

`EstimatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering estimates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: float | None`
    :   Total amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `created_at: str | None`
    :   When created

    `currency: str | None`
    :   Currency

    `id: int | None`
    :   Unique identifier

    `issue_date: str | None`
    :   Issue date

    `number: str | None`
    :   Estimate number

    `state: str | None`
    :   Current state

    `subject: str | None`
    :   Subject

    `updated_at: str | None`
    :   When last updated

`EstimatesSearchQuery(*args, **kwargs)`
:   Search query for estimates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.EstimatesSortFilter]`
    :   The type of the None singleton.

`EstimatesSortFilter(*args, **kwargs)`
:   Available fields for sorting estimates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Total amount

    `client: Literal['asc', 'desc']`
    :   Client details

    `created_at: Literal['asc', 'desc']`
    :   When created

    `currency: Literal['asc', 'desc']`
    :   Currency

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `issue_date: Literal['asc', 'desc']`
    :   Issue date

    `number: Literal['asc', 'desc']`
    :   Estimate number

    `state: Literal['asc', 'desc']`
    :   Current state

    `subject: Literal['asc', 'desc']`
    :   Subject

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`EstimatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Total amount

    `client: str`
    :   Client details

    `created_at: str`
    :   When created

    `currency: str`
    :   Currency

    `id: str`
    :   Unique identifier

    `issue_date: str`
    :   Issue date

    `number: str`
    :   Estimate number

    `state: str`
    :   Current state

    `subject: str`
    :   Subject

    `updated_at: str`
    :   When last updated

`ExpenseCategoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition]`
    :   The type of the None singleton.

`ExpenseCategoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyValueFilter`
    :   The type of the None singleton.

`ExpenseCategoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When created

    `id: Any`
    :   Unique identifier

    `is_active: Any`
    :   Whether active

    `name: Any`
    :   Category name

    `unit_name: Any`
    :   Unit name

    `unit_price: Any`
    :   Unit price

    `updated_at: Any`
    :   When last updated

`ExpenseCategoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyValueFilter`
    :   The type of the None singleton.

`ExpenseCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

`ExpenseCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

`ExpenseCategoriesGetParams(*args, **kwargs)`
:   Parameters for expense_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ExpenseCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

`ExpenseCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

`ExpenseCategoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInFilter`
    :   The type of the None singleton.

`ExpenseCategoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When created

    `id: list[int]`
    :   Unique identifier

    `is_active: list[bool]`
    :   Whether active

    `name: list[str]`
    :   Category name

    `unit_name: list[str]`
    :   Unit name

    `unit_price: list[float]`
    :   Unit price

    `updated_at: list[str]`
    :   When last updated

`ExpenseCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

`ExpenseCategoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

`ExpenseCategoriesListParams(*args, **kwargs)`
:   Parameters for expense_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`ExpenseCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

`ExpenseCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

`ExpenseCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

`ExpenseCategoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition`
    :   The type of the None singleton.

`ExpenseCategoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition]`
    :   The type of the None singleton.

`ExpenseCategoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering expense_categories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `name: str | None`
    :   Category name

    `unit_name: str | None`
    :   Unit name

    `unit_price: float | None`
    :   Unit price

    `updated_at: str | None`
    :   When last updated

`ExpenseCategoriesSearchQuery(*args, **kwargs)`
:   Search query for expense_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSortFilter]`
    :   The type of the None singleton.

`ExpenseCategoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting expense_categories search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When created

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_active: Literal['asc', 'desc']`
    :   Whether active

    `name: Literal['asc', 'desc']`
    :   Category name

    `unit_name: Literal['asc', 'desc']`
    :   Unit name

    `unit_price: Literal['asc', 'desc']`
    :   Unit price

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`ExpenseCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When created

    `id: str`
    :   Unique identifier

    `is_active: str`
    :   Whether active

    `name: str`
    :   Category name

    `unit_name: str`
    :   Unit name

    `unit_price: str`
    :   Unit price

    `updated_at: str`
    :   When last updated

`ExpensesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition]`
    :   The type of the None singleton.

`ExpensesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyValueFilter`
    :   The type of the None singleton.

`ExpensesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: Any`
    :   Whether billable

    `client: Any`
    :   Associated client

    `created_at: Any`
    :   When created

    `expense_category: Any`
    :   Expense category

    `id: Any`
    :   Unique identifier

    `is_billed: Any`
    :   Whether billed

    `notes: Any`
    :   Notes

    `project: Any`
    :   Associated project

    `spent_date: Any`
    :   Date spent

    `total_cost: Any`
    :   Total cost

    `updated_at: Any`
    :   When last updated

    `user: Any`
    :   Associated user

`ExpensesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyValueFilter`
    :   The type of the None singleton.

`ExpensesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

`ExpensesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

`ExpensesGetParams(*args, **kwargs)`
:   Parameters for expenses.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ExpensesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

`ExpensesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

`ExpensesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.ExpensesInFilter`
    :   The type of the None singleton.

`ExpensesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: list[bool]`
    :   Whether billable

    `client: list[dict[str, typing.Any]]`
    :   Associated client

    `created_at: list[str]`
    :   When created

    `expense_category: list[dict[str, typing.Any]]`
    :   Expense category

    `id: list[int]`
    :   Unique identifier

    `is_billed: list[bool]`
    :   Whether billed

    `notes: list[str]`
    :   Notes

    `project: list[dict[str, typing.Any]]`
    :   Associated project

    `spent_date: list[str]`
    :   Date spent

    `total_cost: list[float]`
    :   Total cost

    `updated_at: list[str]`
    :   When last updated

    `user: list[dict[str, typing.Any]]`
    :   Associated user

`ExpensesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

`ExpensesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

`ExpensesListParams(*args, **kwargs)`
:   Parameters for expenses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`ExpensesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

`ExpensesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

`ExpensesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

`ExpensesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition`
    :   The type of the None singleton.

`ExpensesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition]`
    :   The type of the None singleton.

`ExpensesSearchFilter(*args, **kwargs)`
:   Available fields for filtering expenses search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `client: dict[str, typing.Any] | None`
    :   Associated client

    `created_at: str | None`
    :   When created

    `expense_category: dict[str, typing.Any] | None`
    :   Expense category

    `id: int | None`
    :   Unique identifier

    `is_billed: bool | None`
    :   Whether billed

    `notes: str | None`
    :   Notes

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `spent_date: str | None`
    :   Date spent

    `total_cost: float | None`
    :   Total cost

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

`ExpensesSearchQuery(*args, **kwargs)`
:   Search query for expenses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ExpensesSortFilter]`
    :   The type of the None singleton.

`ExpensesSortFilter(*args, **kwargs)`
:   Available fields for sorting expenses search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: Literal['asc', 'desc']`
    :   Whether billable

    `client: Literal['asc', 'desc']`
    :   Associated client

    `created_at: Literal['asc', 'desc']`
    :   When created

    `expense_category: Literal['asc', 'desc']`
    :   Expense category

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_billed: Literal['asc', 'desc']`
    :   Whether billed

    `notes: Literal['asc', 'desc']`
    :   Notes

    `project: Literal['asc', 'desc']`
    :   Associated project

    `spent_date: Literal['asc', 'desc']`
    :   Date spent

    `total_cost: Literal['asc', 'desc']`
    :   Total cost

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

    `user: Literal['asc', 'desc']`
    :   Associated user

`ExpensesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: str`
    :   Whether billable

    `client: str`
    :   Associated client

    `created_at: str`
    :   When created

    `expense_category: str`
    :   Expense category

    `id: str`
    :   Unique identifier

    `is_billed: str`
    :   Whether billed

    `notes: str`
    :   Notes

    `project: str`
    :   Associated project

    `spent_date: str`
    :   Date spent

    `total_cost: str`
    :   Total cost

    `updated_at: str`
    :   When last updated

    `user: str`
    :   Associated user

`InvoiceItemCategoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition]`
    :   The type of the None singleton.

`InvoiceItemCategoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When created

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Category name

    `updated_at: Any`
    :   When last updated

    `use_as_expense: Any`
    :   Whether used as expense type

    `use_as_service: Any`
    :   Whether used as service type

`InvoiceItemCategoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesGetParams(*args, **kwargs)`
:   Parameters for invoice_item_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`InvoiceItemCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When created

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Category name

    `updated_at: list[str]`
    :   When last updated

    `use_as_expense: list[bool]`
    :   Whether used as expense type

    `use_as_service: list[bool]`
    :   Whether used as service type

`InvoiceItemCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesListParams(*args, **kwargs)`
:   Parameters for invoice_item_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`InvoiceItemCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

`InvoiceItemCategoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition`
    :   The type of the None singleton.

`InvoiceItemCategoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition]`
    :   The type of the None singleton.

`InvoiceItemCategoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering invoice_item_categories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `name: str | None`
    :   Category name

    `updated_at: str | None`
    :   When last updated

    `use_as_expense: bool | None`
    :   Whether used as expense type

    `use_as_service: bool | None`
    :   Whether used as service type

`InvoiceItemCategoriesSearchQuery(*args, **kwargs)`
:   Search query for invoice_item_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSortFilter]`
    :   The type of the None singleton.

`InvoiceItemCategoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting invoice_item_categories search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When created

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Category name

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

    `use_as_expense: Literal['asc', 'desc']`
    :   Whether used as expense type

    `use_as_service: Literal['asc', 'desc']`
    :   Whether used as service type

`InvoiceItemCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When created

    `id: str`
    :   Unique identifier

    `name: str`
    :   Category name

    `updated_at: str`
    :   When last updated

    `use_as_expense: str`
    :   Whether used as expense type

    `use_as_service: str`
    :   Whether used as service type

`InvoicesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

`InvoicesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

`InvoicesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Total amount

    `client: Any`
    :   Client details

    `created_at: Any`
    :   When created

    `currency: Any`
    :   Currency

    `due_amount: Any`
    :   Amount due

    `due_date: Any`
    :   Due date

    `id: Any`
    :   Unique identifier

    `issue_date: Any`
    :   Issue date

    `number: Any`
    :   Invoice number

    `state: Any`
    :   Current state

    `subject: Any`
    :   Subject

    `updated_at: Any`
    :   When last updated

`InvoicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

`InvoicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesGetParams(*args, **kwargs)`
:   Parameters for invoices.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`InvoicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.InvoicesInFilter`
    :   The type of the None singleton.

`InvoicesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[float]`
    :   Total amount

    `client: list[dict[str, typing.Any]]`
    :   Client details

    `created_at: list[str]`
    :   When created

    `currency: list[str]`
    :   Currency

    `due_amount: list[float]`
    :   Amount due

    `due_date: list[str]`
    :   Due date

    `id: list[int]`
    :   Unique identifier

    `issue_date: list[str]`
    :   Issue date

    `number: list[str]`
    :   Invoice number

    `state: list[str]`
    :   Current state

    `subject: list[str]`
    :   Subject

    `updated_at: list[str]`
    :   When last updated

`InvoicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesListParams(*args, **kwargs)`
:   Parameters for invoices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`InvoicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition`
    :   The type of the None singleton.

`InvoicesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

`InvoicesSearchFilter(*args, **kwargs)`
:   Available fields for filtering invoices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: float | None`
    :   Total amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `created_at: str | None`
    :   When created

    `currency: str | None`
    :   Currency

    `due_amount: float | None`
    :   Amount due

    `due_date: str | None`
    :   Due date

    `id: int | None`
    :   Unique identifier

    `issue_date: str | None`
    :   Issue date

    `number: str | None`
    :   Invoice number

    `state: str | None`
    :   Current state

    `subject: str | None`
    :   Subject

    `updated_at: str | None`
    :   When last updated

`InvoicesSearchQuery(*args, **kwargs)`
:   Search query for invoices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.InvoicesSortFilter]`
    :   The type of the None singleton.

`InvoicesSortFilter(*args, **kwargs)`
:   Available fields for sorting invoices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Total amount

    `client: Literal['asc', 'desc']`
    :   Client details

    `created_at: Literal['asc', 'desc']`
    :   When created

    `currency: Literal['asc', 'desc']`
    :   Currency

    `due_amount: Literal['asc', 'desc']`
    :   Amount due

    `due_date: Literal['asc', 'desc']`
    :   Due date

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `issue_date: Literal['asc', 'desc']`
    :   Issue date

    `number: Literal['asc', 'desc']`
    :   Invoice number

    `state: Literal['asc', 'desc']`
    :   Current state

    `subject: Literal['asc', 'desc']`
    :   Subject

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`InvoicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Total amount

    `client: str`
    :   Client details

    `created_at: str`
    :   When created

    `currency: str`
    :   Currency

    `due_amount: str`
    :   Amount due

    `due_date: str`
    :   Due date

    `id: str`
    :   Unique identifier

    `issue_date: str`
    :   Issue date

    `number: str`
    :   Invoice number

    `state: str`
    :   Current state

    `subject: str`
    :   Subject

    `updated_at: str`
    :   When last updated

`ProjectsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

`ProjectsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: Any`
    :   Budget amount

    `client: Any`
    :   Client details

    `code: Any`
    :   Project code

    `created_at: Any`
    :   When created

    `hourly_rate: Any`
    :   Hourly rate

    `id: Any`
    :   Unique identifier

    `is_active: Any`
    :   Whether active

    `is_billable: Any`
    :   Whether billable

    `name: Any`
    :   Project name

    `starts_on: Any`
    :   Start date

    `updated_at: Any`
    :   When last updated

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.ProjectsInFilter`
    :   The type of the None singleton.

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: list[float]`
    :   Budget amount

    `client: list[dict[str, typing.Any]]`
    :   Client details

    `code: list[str]`
    :   Project code

    `created_at: list[str]`
    :   When created

    `hourly_rate: list[float]`
    :   Hourly rate

    `id: list[int]`
    :   Unique identifier

    `is_active: list[bool]`
    :   Whether active

    `is_billable: list[bool]`
    :   Whether billable

    `name: list[str]`
    :   Project name

    `starts_on: list[str]`
    :   Start date

    `updated_at: list[str]`
    :   When last updated

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

`ProjectsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition`
    :   The type of the None singleton.

`ProjectsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: float | None`
    :   Budget amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `code: str | None`
    :   Project code

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_billable: bool | None`
    :   Whether billable

    `name: str | None`
    :   Project name

    `starts_on: str | None`
    :   Start date

    `updated_at: str | None`
    :   When last updated

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ProjectsSortFilter]`
    :   The type of the None singleton.

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: Literal['asc', 'desc']`
    :   Budget amount

    `client: Literal['asc', 'desc']`
    :   Client details

    `code: Literal['asc', 'desc']`
    :   Project code

    `created_at: Literal['asc', 'desc']`
    :   When created

    `hourly_rate: Literal['asc', 'desc']`
    :   Hourly rate

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_active: Literal['asc', 'desc']`
    :   Whether active

    `is_billable: Literal['asc', 'desc']`
    :   Whether billable

    `name: Literal['asc', 'desc']`
    :   Project name

    `starts_on: Literal['asc', 'desc']`
    :   Start date

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: str`
    :   Budget amount

    `client: str`
    :   Client details

    `code: str`
    :   Project code

    `created_at: str`
    :   When created

    `hourly_rate: str`
    :   Hourly rate

    `id: str`
    :   Unique identifier

    `is_active: str`
    :   Whether active

    `is_billable: str`
    :   Whether billable

    `name: str`
    :   Project name

    `starts_on: str`
    :   Start date

    `updated_at: str`
    :   When last updated

`RolesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition]`
    :   The type of the None singleton.

`RolesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.RolesAnyValueFilter`
    :   The type of the None singleton.

`RolesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When created

    `id: Any`
    :   Unique identifier

    `name: Any`
    :   Role name

    `updated_at: Any`
    :   When last updated

    `user_ids: Any`
    :   User IDs with this role

`RolesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.RolesAnyValueFilter`
    :   The type of the None singleton.

`RolesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

`RolesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

`RolesGetParams(*args, **kwargs)`
:   Parameters for roles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`RolesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

`RolesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

`RolesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.RolesInFilter`
    :   The type of the None singleton.

`RolesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When created

    `id: list[int]`
    :   Unique identifier

    `name: list[str]`
    :   Role name

    `updated_at: list[str]`
    :   When last updated

    `user_ids: list[list[typing.Any]]`
    :   User IDs with this role

`RolesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

`RolesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

`RolesListParams(*args, **kwargs)`
:   Parameters for roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`RolesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

`RolesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

`RolesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

`RolesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition`
    :   The type of the None singleton.

`RolesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition]`
    :   The type of the None singleton.

`RolesSearchFilter(*args, **kwargs)`
:   Available fields for filtering roles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `name: str | None`
    :   Role name

    `updated_at: str | None`
    :   When last updated

    `user_ids: list[typing.Any] | None`
    :   User IDs with this role

`RolesSearchQuery(*args, **kwargs)`
:   Search query for roles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.RolesSortFilter]`
    :   The type of the None singleton.

`RolesSortFilter(*args, **kwargs)`
:   Available fields for sorting roles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When created

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `name: Literal['asc', 'desc']`
    :   Role name

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

    `user_ids: Literal['asc', 'desc']`
    :   User IDs with this role

`RolesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When created

    `id: str`
    :   Unique identifier

    `name: str`
    :   Role name

    `updated_at: str`
    :   When last updated

    `user_ids: str`
    :   User IDs with this role

`TaskAssignmentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition]`
    :   The type of the None singleton.

`TaskAssignmentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyValueFilter`
    :   The type of the None singleton.

`TaskAssignmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: Any`
    :   Whether billable

    `created_at: Any`
    :   When created

    `hourly_rate: Any`
    :   Hourly rate

    `id: Any`
    :   Unique identifier

    `is_active: Any`
    :   Whether active

    `project: Any`
    :   Associated project

    `task: Any`
    :   Associated task

    `updated_at: Any`
    :   When last updated

`TaskAssignmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyValueFilter`
    :   The type of the None singleton.

`TaskAssignmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

`TaskAssignmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

`TaskAssignmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

`TaskAssignmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

`TaskAssignmentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInFilter`
    :   The type of the None singleton.

`TaskAssignmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: list[bool]`
    :   Whether billable

    `created_at: list[str]`
    :   When created

    `hourly_rate: list[float]`
    :   Hourly rate

    `id: list[int]`
    :   Unique identifier

    `is_active: list[bool]`
    :   Whether active

    `project: list[dict[str, typing.Any]]`
    :   Associated project

    `task: list[dict[str, typing.Any]]`
    :   Associated task

    `updated_at: list[str]`
    :   When last updated

`TaskAssignmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

`TaskAssignmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

`TaskAssignmentsListParams(*args, **kwargs)`
:   Parameters for task_assignments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`TaskAssignmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

`TaskAssignmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

`TaskAssignmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

`TaskAssignmentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition`
    :   The type of the None singleton.

`TaskAssignmentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition]`
    :   The type of the None singleton.

`TaskAssignmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering task_assignments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `task: dict[str, typing.Any] | None`
    :   Associated task

    `updated_at: str | None`
    :   When last updated

`TaskAssignmentsSearchQuery(*args, **kwargs)`
:   Search query for task_assignments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSortFilter]`
    :   The type of the None singleton.

`TaskAssignmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting task_assignments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: Literal['asc', 'desc']`
    :   Whether billable

    `created_at: Literal['asc', 'desc']`
    :   When created

    `hourly_rate: Literal['asc', 'desc']`
    :   Hourly rate

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_active: Literal['asc', 'desc']`
    :   Whether active

    `project: Literal['asc', 'desc']`
    :   Associated project

    `task: Literal['asc', 'desc']`
    :   Associated task

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`TaskAssignmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: str`
    :   Whether billable

    `created_at: str`
    :   When created

    `hourly_rate: str`
    :   Hourly rate

    `id: str`
    :   Unique identifier

    `is_active: str`
    :   Whether active

    `project: str`
    :   Associated project

    `task: str`
    :   Associated task

    `updated_at: str`
    :   When last updated

`TasksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_by_default: Any`
    :   Whether billable by default

    `created_at: Any`
    :   When created

    `default_hourly_rate: Any`
    :   Default hourly rate

    `id: Any`
    :   Unique identifier

    `is_active: Any`
    :   Whether active

    `name: Any`
    :   Task name

    `updated_at: Any`
    :   When last updated

`TasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.TasksInFilter`
    :   The type of the None singleton.

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_by_default: list[bool]`
    :   Whether billable by default

    `created_at: list[str]`
    :   When created

    `default_hourly_rate: list[float]`
    :   Default hourly rate

    `id: list[int]`
    :   Unique identifier

    `is_active: list[bool]`
    :   Whether active

    `name: list[str]`
    :   Task name

    `updated_at: list[str]`
    :   When last updated

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition`
    :   The type of the None singleton.

`TasksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_by_default: bool | None`
    :   Whether billable by default

    `created_at: str | None`
    :   When created

    `default_hourly_rate: float | None`
    :   Default hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `name: str | None`
    :   Task name

    `updated_at: str | None`
    :   When last updated

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TasksSortFilter]`
    :   The type of the None singleton.

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_by_default: Literal['asc', 'desc']`
    :   Whether billable by default

    `created_at: Literal['asc', 'desc']`
    :   When created

    `default_hourly_rate: Literal['asc', 'desc']`
    :   Default hourly rate

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_active: Literal['asc', 'desc']`
    :   Whether active

    `name: Literal['asc', 'desc']`
    :   Task name

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_by_default: str`
    :   Whether billable by default

    `created_at: str`
    :   When created

    `default_hourly_rate: str`
    :   Default hourly rate

    `id: str`
    :   Unique identifier

    `is_active: str`
    :   Whether active

    `name: str`
    :   Task name

    `updated_at: str`
    :   When last updated

`TimeEntriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition]`
    :   The type of the None singleton.

`TimeEntriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyValueFilter`
    :   The type of the None singleton.

`TimeEntriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: Any`
    :   Whether billable

    `client: Any`
    :   Associated client

    `created_at: Any`
    :   When created

    `hours: Any`
    :   Hours logged

    `id: Any`
    :   Unique identifier

    `is_billed: Any`
    :   Whether billed

    `notes: Any`
    :   Notes

    `project: Any`
    :   Associated project

    `spent_date: Any`
    :   Date time was spent

    `task: Any`
    :   Associated task

    `updated_at: Any`
    :   When last updated

    `user: Any`
    :   Associated user

`TimeEntriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyValueFilter`
    :   The type of the None singleton.

`TimeEntriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

`TimeEntriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

`TimeEntriesGetParams(*args, **kwargs)`
:   Parameters for time_entries.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`TimeEntriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

`TimeEntriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

`TimeEntriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInFilter`
    :   The type of the None singleton.

`TimeEntriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: list[bool]`
    :   Whether billable

    `client: list[dict[str, typing.Any]]`
    :   Associated client

    `created_at: list[str]`
    :   When created

    `hours: list[float]`
    :   Hours logged

    `id: list[int]`
    :   Unique identifier

    `is_billed: list[bool]`
    :   Whether billed

    `notes: list[str]`
    :   Notes

    `project: list[dict[str, typing.Any]]`
    :   Associated project

    `spent_date: list[str]`
    :   Date time was spent

    `task: list[dict[str, typing.Any]]`
    :   Associated task

    `updated_at: list[str]`
    :   When last updated

    `user: list[dict[str, typing.Any]]`
    :   Associated user

`TimeEntriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

`TimeEntriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

`TimeEntriesListParams(*args, **kwargs)`
:   Parameters for time_entries.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`TimeEntriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

`TimeEntriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

`TimeEntriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

`TimeEntriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition`
    :   The type of the None singleton.

`TimeEntriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition]`
    :   The type of the None singleton.

`TimeEntriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering time_entries search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `client: dict[str, typing.Any] | None`
    :   Associated client

    `created_at: str | None`
    :   When created

    `hours: float | None`
    :   Hours logged

    `id: int | None`
    :   Unique identifier

    `is_billed: bool | None`
    :   Whether billed

    `notes: str | None`
    :   Notes

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `spent_date: str | None`
    :   Date time was spent

    `task: dict[str, typing.Any] | None`
    :   Associated task

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

`TimeEntriesSearchQuery(*args, **kwargs)`
:   Search query for time_entries entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSortFilter]`
    :   The type of the None singleton.

`TimeEntriesSortFilter(*args, **kwargs)`
:   Available fields for sorting time_entries search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: Literal['asc', 'desc']`
    :   Whether billable

    `client: Literal['asc', 'desc']`
    :   Associated client

    `created_at: Literal['asc', 'desc']`
    :   When created

    `hours: Literal['asc', 'desc']`
    :   Hours logged

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_billed: Literal['asc', 'desc']`
    :   Whether billed

    `notes: Literal['asc', 'desc']`
    :   Notes

    `project: Literal['asc', 'desc']`
    :   Associated project

    `spent_date: Literal['asc', 'desc']`
    :   Date time was spent

    `task: Literal['asc', 'desc']`
    :   Associated task

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

    `user: Literal['asc', 'desc']`
    :   Associated user

`TimeEntriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable: str`
    :   Whether billable

    `client: str`
    :   Associated client

    `created_at: str`
    :   When created

    `hours: str`
    :   Hours logged

    `id: str`
    :   Unique identifier

    `is_billed: str`
    :   Whether billed

    `notes: str`
    :   Notes

    `project: str`
    :   Associated project

    `spent_date: str`
    :   Date time was spent

    `task: str`
    :   Associated task

    `updated_at: str`
    :   When last updated

    `user: str`
    :   Associated user

`TimeProjectsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition]`
    :   The type of the None singleton.

`TimeProjectsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyValueFilter`
    :   The type of the None singleton.

`TimeProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: Any`
    :   Total billable amount

    `billable_hours: Any`
    :   Number of billable hours

    `client_id: Any`
    :   Client identifier

    `client_name: Any`
    :   Client name

    `currency: Any`
    :   Currency code

    `project_id: Any`
    :   Project identifier

    `project_name: Any`
    :   Project name

    `total_hours: Any`
    :   Total hours spent

`TimeProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyValueFilter`
    :   The type of the None singleton.

`TimeProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

`TimeProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

`TimeProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

`TimeProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

`TimeProjectsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInFilter`
    :   The type of the None singleton.

`TimeProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: list[float]`
    :   Total billable amount

    `billable_hours: list[float]`
    :   Number of billable hours

    `client_id: list[int]`
    :   Client identifier

    `client_name: list[str]`
    :   Client name

    `currency: list[str]`
    :   Currency code

    `project_id: list[int]`
    :   Project identifier

    `project_name: list[str]`
    :   Project name

    `total_hours: list[float]`
    :   Total hours spent

`TimeProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

`TimeProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

`TimeProjectsListParams(*args, **kwargs)`
:   Parameters for time_projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `from_: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

`TimeProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

`TimeProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

`TimeProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

`TimeProjectsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition`
    :   The type of the None singleton.

`TimeProjectsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition]`
    :   The type of the None singleton.

`TimeProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering time_projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: float | None`
    :   Total billable amount

    `billable_hours: float | None`
    :   Number of billable hours

    `client_id: int | None`
    :   Client identifier

    `client_name: str | None`
    :   Client name

    `currency: str | None`
    :   Currency code

    `project_id: int | None`
    :   Project identifier

    `project_name: str | None`
    :   Project name

    `total_hours: float | None`
    :   Total hours spent

`TimeProjectsSearchQuery(*args, **kwargs)`
:   Search query for time_projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSortFilter]`
    :   The type of the None singleton.

`TimeProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting time_projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: Literal['asc', 'desc']`
    :   Total billable amount

    `billable_hours: Literal['asc', 'desc']`
    :   Number of billable hours

    `client_id: Literal['asc', 'desc']`
    :   Client identifier

    `client_name: Literal['asc', 'desc']`
    :   Client name

    `currency: Literal['asc', 'desc']`
    :   Currency code

    `project_id: Literal['asc', 'desc']`
    :   Project identifier

    `project_name: Literal['asc', 'desc']`
    :   Project name

    `total_hours: Literal['asc', 'desc']`
    :   Total hours spent

`TimeProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: str`
    :   Total billable amount

    `billable_hours: str`
    :   Number of billable hours

    `client_id: str`
    :   Client identifier

    `client_name: str`
    :   Client name

    `currency: str`
    :   Currency code

    `project_id: str`
    :   Project identifier

    `project_name: str`
    :   Project name

    `total_hours: str`
    :   Total hours spent

`TimeTasksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition]`
    :   The type of the None singleton.

`TimeTasksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyValueFilter`
    :   The type of the None singleton.

`TimeTasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: Any`
    :   Total billable amount

    `billable_hours: Any`
    :   Number of billable hours

    `currency: Any`
    :   Currency code

    `task_id: Any`
    :   Task identifier

    `task_name: Any`
    :   Task name

    `total_hours: Any`
    :   Total hours spent

`TimeTasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyValueFilter`
    :   The type of the None singleton.

`TimeTasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

`TimeTasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

`TimeTasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

`TimeTasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

`TimeTasksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.TimeTasksInFilter`
    :   The type of the None singleton.

`TimeTasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: list[float]`
    :   Total billable amount

    `billable_hours: list[float]`
    :   Number of billable hours

    `currency: list[str]`
    :   Currency code

    `task_id: list[int]`
    :   Task identifier

    `task_name: list[str]`
    :   Task name

    `total_hours: list[float]`
    :   Total hours spent

`TimeTasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

`TimeTasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

`TimeTasksListParams(*args, **kwargs)`
:   Parameters for time_tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `from_: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

`TimeTasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

`TimeTasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

`TimeTasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

`TimeTasksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition`
    :   The type of the None singleton.

`TimeTasksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition]`
    :   The type of the None singleton.

`TimeTasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering time_tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: float | None`
    :   Total billable amount

    `billable_hours: float | None`
    :   Number of billable hours

    `currency: str | None`
    :   Currency code

    `task_id: int | None`
    :   Task identifier

    `task_name: str | None`
    :   Task name

    `total_hours: float | None`
    :   Total hours spent

`TimeTasksSearchQuery(*args, **kwargs)`
:   Search query for time_tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLikeCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TimeTasksSortFilter]`
    :   The type of the None singleton.

`TimeTasksSortFilter(*args, **kwargs)`
:   Available fields for sorting time_tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: Literal['asc', 'desc']`
    :   Total billable amount

    `billable_hours: Literal['asc', 'desc']`
    :   Number of billable hours

    `currency: Literal['asc', 'desc']`
    :   Currency code

    `task_id: Literal['asc', 'desc']`
    :   Task identifier

    `task_name: Literal['asc', 'desc']`
    :   Task name

    `total_hours: Literal['asc', 'desc']`
    :   Total hours spent

`TimeTasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billable_amount: str`
    :   Total billable amount

    `billable_hours: str`
    :   Number of billable hours

    `currency: str`
    :   Currency code

    `task_id: str`
    :   Task identifier

    `task_name: str`
    :   Task name

    `total_hours: str`
    :   Total hours spent

`UserAssignmentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition]`
    :   The type of the None singleton.

`UserAssignmentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyValueFilter`
    :   The type of the None singleton.

`UserAssignmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: Any`
    :   Budget

    `created_at: Any`
    :   When created

    `hourly_rate: Any`
    :   Hourly rate

    `id: Any`
    :   Unique identifier

    `is_active: Any`
    :   Whether active

    `is_project_manager: Any`
    :   Whether project manager

    `project: Any`
    :   Associated project

    `updated_at: Any`
    :   When last updated

    `user: Any`
    :   Associated user

`UserAssignmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyValueFilter`
    :   The type of the None singleton.

`UserAssignmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

`UserAssignmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

`UserAssignmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

`UserAssignmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

`UserAssignmentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInFilter`
    :   The type of the None singleton.

`UserAssignmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: list[float]`
    :   Budget

    `created_at: list[str]`
    :   When created

    `hourly_rate: list[float]`
    :   Hourly rate

    `id: list[int]`
    :   Unique identifier

    `is_active: list[bool]`
    :   Whether active

    `is_project_manager: list[bool]`
    :   Whether project manager

    `project: list[dict[str, typing.Any]]`
    :   Associated project

    `updated_at: list[str]`
    :   When last updated

    `user: list[dict[str, typing.Any]]`
    :   Associated user

`UserAssignmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

`UserAssignmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

`UserAssignmentsListParams(*args, **kwargs)`
:   Parameters for user_assignments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`UserAssignmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

`UserAssignmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

`UserAssignmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

`UserAssignmentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition`
    :   The type of the None singleton.

`UserAssignmentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition]`
    :   The type of the None singleton.

`UserAssignmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering user_assignments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: float | None`
    :   Budget

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_project_manager: bool | None`
    :   Whether project manager

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

`UserAssignmentsSearchQuery(*args, **kwargs)`
:   Search query for user_assignments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSortFilter]`
    :   The type of the None singleton.

`UserAssignmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting user_assignments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: Literal['asc', 'desc']`
    :   Budget

    `created_at: Literal['asc', 'desc']`
    :   When created

    `hourly_rate: Literal['asc', 'desc']`
    :   Hourly rate

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_active: Literal['asc', 'desc']`
    :   Whether active

    `is_project_manager: Literal['asc', 'desc']`
    :   Whether project manager

    `project: Literal['asc', 'desc']`
    :   Associated project

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

    `user: Literal['asc', 'desc']`
    :   Associated user

`UserAssignmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `budget: str`
    :   Budget

    `created_at: str`
    :   When created

    `hourly_rate: str`
    :   Hourly rate

    `id: str`
    :   Unique identifier

    `is_active: str`
    :   Whether active

    `is_project_manager: str`
    :   Whether project manager

    `project: str`
    :   Associated project

    `updated_at: str`
    :   When last updated

    `user: str`
    :   Associated user

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.harvest.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Any`
    :   Avatar URL

    `cost_rate: Any`
    :   Cost rate

    `created_at: Any`
    :   When created

    `default_hourly_rate: Any`
    :   Default hourly rate

    `email: Any`
    :   Email address

    `first_name: Any`
    :   First name

    `id: Any`
    :   Unique identifier

    `is_active: Any`
    :   Whether active

    `is_contractor: Any`
    :   Whether contractor

    `last_name: Any`
    :   Last name

    `roles: Any`
    :   Assigned roles

    `telephone: Any`
    :   Phone number

    `timezone: Any`
    :   Timezone

    `updated_at: Any`
    :   When last updated

    `weekly_capacity: Any`
    :   Weekly capacity in seconds

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.harvest.types.UsersInFilter`
    :   The type of the None singleton.

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: list[str]`
    :   Avatar URL

    `cost_rate: list[float]`
    :   Cost rate

    `created_at: list[str]`
    :   When created

    `default_hourly_rate: list[float]`
    :   Default hourly rate

    `email: list[str]`
    :   Email address

    `first_name: list[str]`
    :   First name

    `id: list[int]`
    :   Unique identifier

    `is_active: list[bool]`
    :   Whether active

    `is_contractor: list[bool]`
    :   Whether contractor

    `last_name: list[str]`
    :   Last name

    `roles: list[list[typing.Any]]`
    :   Assigned roles

    `telephone: list[str]`
    :   Phone number

    `timezone: list[str]`
    :   Timezone

    `updated_at: list[str]`
    :   When last updated

    `weekly_capacity: list[int]`
    :   Weekly capacity in seconds

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition]`
    :   The type of the None singleton.

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str | None`
    :   Avatar URL

    `cost_rate: float | None`
    :   Cost rate

    `created_at: str | None`
    :   When created

    `default_hourly_rate: float | None`
    :   Default hourly rate

    `email: str | None`
    :   Email address

    `first_name: str | None`
    :   First name

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_contractor: bool | None`
    :   Whether contractor

    `last_name: str | None`
    :   Last name

    `roles: list[typing.Any] | None`
    :   Assigned roles

    `telephone: str | None`
    :   Phone number

    `timezone: str | None`
    :   Timezone

    `updated_at: str | None`
    :   When last updated

    `weekly_capacity: int | None`
    :   Weekly capacity in seconds

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLikeCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.UsersSortFilter]`
    :   The type of the None singleton.

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Literal['asc', 'desc']`
    :   Avatar URL

    `cost_rate: Literal['asc', 'desc']`
    :   Cost rate

    `created_at: Literal['asc', 'desc']`
    :   When created

    `default_hourly_rate: Literal['asc', 'desc']`
    :   Default hourly rate

    `email: Literal['asc', 'desc']`
    :   Email address

    `first_name: Literal['asc', 'desc']`
    :   First name

    `id: Literal['asc', 'desc']`
    :   Unique identifier

    `is_active: Literal['asc', 'desc']`
    :   Whether active

    `is_contractor: Literal['asc', 'desc']`
    :   Whether contractor

    `last_name: Literal['asc', 'desc']`
    :   Last name

    `roles: Literal['asc', 'desc']`
    :   Assigned roles

    `telephone: Literal['asc', 'desc']`
    :   Phone number

    `timezone: Literal['asc', 'desc']`
    :   Timezone

    `updated_at: Literal['asc', 'desc']`
    :   When last updated

    `weekly_capacity: Literal['asc', 'desc']`
    :   Weekly capacity in seconds

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str`
    :   Avatar URL

    `cost_rate: str`
    :   Cost rate

    `created_at: str`
    :   When created

    `default_hourly_rate: str`
    :   Default hourly rate

    `email: str`
    :   Email address

    `first_name: str`
    :   First name

    `id: str`
    :   Unique identifier

    `is_active: str`
    :   Whether active

    `is_contractor: str`
    :   Whether contractor

    `last_name: str`
    :   Last name

    `roles: str`
    :   Assigned roles

    `telephone: str`
    :   Phone number

    `timezone: str`
    :   Timezone

    `updated_at: str`
    :   When last updated

    `weekly_capacity: str`
    :   Weekly capacity in seconds