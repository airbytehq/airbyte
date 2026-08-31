---
id: airbyte_agent_sdk-connectors-harvest-types
title: airbyte_agent_sdk.connectors.harvest.types
---

Module airbyte_agent_sdk.connectors.harvest.types
=================================================
Type definitions for harvest connector.

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

<a id="ClientsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition]`
    :   The type of the None singleton.

<a id="ClientsAnyCondition"></a>

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

<a id="ClientsAnyValueFilter"></a>

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

<a id="ClientsArrayContainsCondition"></a>

`ClientsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.ClientsAnyValueFilter`
    :   The type of the None singleton.

<a id="ClientsContainsCondition"></a>

`ClientsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ClientsAnyValueFilter`
    :   The type of the None singleton.

<a id="ClientsEndswithCondition"></a>

`ClientsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

<a id="ClientsEqCondition"></a>

`ClientsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

<a id="ClientsFuzzyCondition"></a>

`ClientsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

<a id="ClientsGetParams"></a>

`ClientsGetParams(*args, **kwargs)`
:   Parameters for clients.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ClientsGtCondition"></a>

`ClientsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

<a id="ClientsGteCondition"></a>

`ClientsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

<a id="ClientsInCondition"></a>

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

<a id="ClientsInFilter"></a>

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

<a id="ClientsKeywordCondition"></a>

`ClientsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

<a id="ClientsListParams"></a>

`ClientsListParams(*args, **kwargs)`
:   Parameters for clients.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="ClientsLtCondition"></a>

`ClientsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

<a id="ClientsLteCondition"></a>

`ClientsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

<a id="ClientsNeqCondition"></a>

`ClientsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ClientsSearchFilter`
    :   The type of the None singleton.

<a id="ClientsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition`
    :   The type of the None singleton.

<a id="ClientsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition]`
    :   The type of the None singleton.

<a id="ClientsSearchFilter"></a>

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

<a id="ClientsSearchQuery"></a>

`ClientsSearchQuery(*args, **kwargs)`
:   Search query for clients entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ClientsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsInCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ClientsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ClientsSortFilter]`
    :   The type of the None singleton.

<a id="ClientsSortFilter"></a>

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

<a id="ClientsStartswithCondition"></a>

`ClientsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.ClientsStringFilter`
    :   The type of the None singleton.

<a id="ClientsStringFilter"></a>

`ClientsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="CompanyAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition]`
    :   The type of the None singleton.

<a id="CompanyAnyCondition"></a>

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

<a id="CompanyAnyValueFilter"></a>

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

<a id="CompanyArrayContainsCondition"></a>

`CompanyArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.CompanyAnyValueFilter`
    :   The type of the None singleton.

<a id="CompanyContainsCondition"></a>

`CompanyContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.CompanyAnyValueFilter`
    :   The type of the None singleton.

<a id="CompanyEndswithCondition"></a>

`CompanyEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

<a id="CompanyEqCondition"></a>

`CompanyEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

<a id="CompanyFuzzyCondition"></a>

`CompanyFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

<a id="CompanyGetParams"></a>

`CompanyGetParams(*args, **kwargs)`
:   Parameters for company.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CompanyGtCondition"></a>

`CompanyGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

<a id="CompanyGteCondition"></a>

`CompanyGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

<a id="CompanyInCondition"></a>

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

<a id="CompanyInFilter"></a>

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

<a id="CompanyKeywordCondition"></a>

`CompanyKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

<a id="CompanyLtCondition"></a>

`CompanyLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

<a id="CompanyLteCondition"></a>

`CompanyLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

<a id="CompanyNeqCondition"></a>

`CompanyNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.CompanySearchFilter`
    :   The type of the None singleton.

<a id="CompanyNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition`
    :   The type of the None singleton.

<a id="CompanyOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition]`
    :   The type of the None singleton.

<a id="CompanySearchFilter"></a>

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

<a id="CompanySearchQuery"></a>

`CompanySearchQuery(*args, **kwargs)`
:   Search query for company entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.CompanyEqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNeqCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyGteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLtCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyLteCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyInCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyNotCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAndCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyOrCondition | airbyte_agent_sdk.connectors.harvest.types.CompanyAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.CompanySortFilter]`
    :   The type of the None singleton.

<a id="CompanySortFilter"></a>

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

<a id="CompanyStartswithCondition"></a>

`CompanyStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.CompanyStringFilter`
    :   The type of the None singleton.

<a id="CompanyStringFilter"></a>

`CompanyStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.harvest.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsAnyValueFilter"></a>

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

<a id="ContactsArrayContainsCondition"></a>

`ContactsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsContainsCondition"></a>

`ContactsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsEndswithCondition"></a>

`ContactsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsEqCondition"></a>

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsFuzzyCondition"></a>

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsGteCondition"></a>

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.harvest.types.ContactsInFilter`
    :   The type of the None singleton.

<a id="ContactsInFilter"></a>

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

<a id="ContactsKeywordCondition"></a>

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="ContactsLtCondition"></a>

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsLteCondition"></a>

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNeqCondition"></a>

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ContactsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsSearchFilter"></a>

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

<a id="ContactsSearchQuery"></a>

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ContactsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsInCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ContactsSortFilter]`
    :   The type of the None singleton.

<a id="ContactsSortFilter"></a>

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

<a id="ContactsStartswithCondition"></a>

`ContactsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsStringFilter"></a>

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="EstimateItemCategoriesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesAnyCondition"></a>

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

<a id="EstimateItemCategoriesAnyValueFilter"></a>

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

<a id="EstimateItemCategoriesArrayContainsCondition"></a>

`EstimateItemCategoriesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesContainsCondition"></a>

`EstimateItemCategoriesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesEndswithCondition"></a>

`EstimateItemCategoriesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesEqCondition"></a>

`EstimateItemCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesFuzzyCondition"></a>

`EstimateItemCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesGetParams"></a>

`EstimateItemCategoriesGetParams(*args, **kwargs)`
:   Parameters for estimate_item_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesGtCondition"></a>

`EstimateItemCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesGteCondition"></a>

`EstimateItemCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesInCondition"></a>

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

<a id="EstimateItemCategoriesInFilter"></a>

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

<a id="EstimateItemCategoriesKeywordCondition"></a>

`EstimateItemCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesListParams"></a>

`EstimateItemCategoriesListParams(*args, **kwargs)`
:   Parameters for estimate_item_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesLtCondition"></a>

`EstimateItemCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesLteCondition"></a>

`EstimateItemCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesNeqCondition"></a>

`EstimateItemCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesSearchFilter"></a>

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

<a id="EstimateItemCategoriesSearchQuery"></a>

`EstimateItemCategoriesSearchQuery(*args, **kwargs)`
:   Search query for estimate_item_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesSortFilter]`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesSortFilter"></a>

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

<a id="EstimateItemCategoriesStartswithCondition"></a>

`EstimateItemCategoriesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.EstimateItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="EstimateItemCategoriesStringFilter"></a>

`EstimateItemCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="EstimatesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition]`
    :   The type of the None singleton.

<a id="EstimatesAnyCondition"></a>

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

<a id="EstimatesAnyValueFilter"></a>

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

<a id="EstimatesArrayContainsCondition"></a>

`EstimatesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyValueFilter`
    :   The type of the None singleton.

<a id="EstimatesContainsCondition"></a>

`EstimatesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyValueFilter`
    :   The type of the None singleton.

<a id="EstimatesEndswithCondition"></a>

`EstimatesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

<a id="EstimatesEqCondition"></a>

`EstimatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

<a id="EstimatesFuzzyCondition"></a>

`EstimatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

<a id="EstimatesGetParams"></a>

`EstimatesGetParams(*args, **kwargs)`
:   Parameters for estimates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="EstimatesGtCondition"></a>

`EstimatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

<a id="EstimatesGteCondition"></a>

`EstimatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

<a id="EstimatesInCondition"></a>

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

<a id="EstimatesInFilter"></a>

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

<a id="EstimatesKeywordCondition"></a>

`EstimatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

<a id="EstimatesListParams"></a>

`EstimatesListParams(*args, **kwargs)`
:   Parameters for estimates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="EstimatesLtCondition"></a>

`EstimatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

<a id="EstimatesLteCondition"></a>

`EstimatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

<a id="EstimatesNeqCondition"></a>

`EstimatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.EstimatesSearchFilter`
    :   The type of the None singleton.

<a id="EstimatesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition`
    :   The type of the None singleton.

<a id="EstimatesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition]`
    :   The type of the None singleton.

<a id="EstimatesSearchFilter"></a>

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

<a id="EstimatesSearchQuery"></a>

`EstimatesSearchQuery(*args, **kwargs)`
:   Search query for estimates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.EstimatesEqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesGteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLtCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesLteCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesInCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesNotCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAndCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesOrCondition | airbyte_agent_sdk.connectors.harvest.types.EstimatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.EstimatesSortFilter]`
    :   The type of the None singleton.

<a id="EstimatesSortFilter"></a>

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

<a id="EstimatesStartswithCondition"></a>

`EstimatesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.EstimatesStringFilter`
    :   The type of the None singleton.

<a id="EstimatesStringFilter"></a>

`EstimatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="ExpenseCategoriesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="ExpenseCategoriesAnyCondition"></a>

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

<a id="ExpenseCategoriesAnyValueFilter"></a>

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

<a id="ExpenseCategoriesArrayContainsCondition"></a>

`ExpenseCategoriesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesContainsCondition"></a>

`ExpenseCategoriesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesEndswithCondition"></a>

`ExpenseCategoriesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesEqCondition"></a>

`ExpenseCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesFuzzyCondition"></a>

`ExpenseCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesGetParams"></a>

`ExpenseCategoriesGetParams(*args, **kwargs)`
:   Parameters for expense_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ExpenseCategoriesGtCondition"></a>

`ExpenseCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesGteCondition"></a>

`ExpenseCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesInCondition"></a>

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

<a id="ExpenseCategoriesInFilter"></a>

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

<a id="ExpenseCategoriesKeywordCondition"></a>

`ExpenseCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesListParams"></a>

`ExpenseCategoriesListParams(*args, **kwargs)`
:   Parameters for expense_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="ExpenseCategoriesLtCondition"></a>

`ExpenseCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesLteCondition"></a>

`ExpenseCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesNeqCondition"></a>

`ExpenseCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition`
    :   The type of the None singleton.

<a id="ExpenseCategoriesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="ExpenseCategoriesSearchFilter"></a>

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

<a id="ExpenseCategoriesSearchQuery"></a>

`ExpenseCategoriesSearchQuery(*args, **kwargs)`
:   Search query for expense_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesSortFilter]`
    :   The type of the None singleton.

<a id="ExpenseCategoriesSortFilter"></a>

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

<a id="ExpenseCategoriesStartswithCondition"></a>

`ExpenseCategoriesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.ExpenseCategoriesStringFilter`
    :   The type of the None singleton.

<a id="ExpenseCategoriesStringFilter"></a>

`ExpenseCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="ExpensesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition]`
    :   The type of the None singleton.

<a id="ExpensesAnyCondition"></a>

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

<a id="ExpensesAnyValueFilter"></a>

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

<a id="ExpensesArrayContainsCondition"></a>

`ExpensesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyValueFilter`
    :   The type of the None singleton.

<a id="ExpensesContainsCondition"></a>

`ExpensesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyValueFilter`
    :   The type of the None singleton.

<a id="ExpensesEndswithCondition"></a>

`ExpensesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

<a id="ExpensesEqCondition"></a>

`ExpensesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

<a id="ExpensesFuzzyCondition"></a>

`ExpensesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

<a id="ExpensesGetParams"></a>

`ExpensesGetParams(*args, **kwargs)`
:   Parameters for expenses.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ExpensesGtCondition"></a>

`ExpensesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

<a id="ExpensesGteCondition"></a>

`ExpensesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

<a id="ExpensesInCondition"></a>

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

<a id="ExpensesInFilter"></a>

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

<a id="ExpensesKeywordCondition"></a>

`ExpensesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

<a id="ExpensesListParams"></a>

`ExpensesListParams(*args, **kwargs)`
:   Parameters for expenses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="ExpensesLtCondition"></a>

`ExpensesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

<a id="ExpensesLteCondition"></a>

`ExpensesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

<a id="ExpensesNeqCondition"></a>

`ExpensesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ExpensesSearchFilter`
    :   The type of the None singleton.

<a id="ExpensesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition`
    :   The type of the None singleton.

<a id="ExpensesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition]`
    :   The type of the None singleton.

<a id="ExpensesSearchFilter"></a>

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

<a id="ExpensesSearchQuery"></a>

`ExpensesSearchQuery(*args, **kwargs)`
:   Search query for expenses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ExpensesEqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesGteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLtCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesLteCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesInCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesNotCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAndCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesOrCondition | airbyte_agent_sdk.connectors.harvest.types.ExpensesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ExpensesSortFilter]`
    :   The type of the None singleton.

<a id="ExpensesSortFilter"></a>

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

<a id="ExpensesStartswithCondition"></a>

`ExpensesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.ExpensesStringFilter`
    :   The type of the None singleton.

<a id="ExpensesStringFilter"></a>

`ExpensesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="InvoiceItemCategoriesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesAnyCondition"></a>

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

<a id="InvoiceItemCategoriesAnyValueFilter"></a>

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

<a id="InvoiceItemCategoriesArrayContainsCondition"></a>

`InvoiceItemCategoriesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesContainsCondition"></a>

`InvoiceItemCategoriesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesEndswithCondition"></a>

`InvoiceItemCategoriesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesEqCondition"></a>

`InvoiceItemCategoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesFuzzyCondition"></a>

`InvoiceItemCategoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesGetParams"></a>

`InvoiceItemCategoriesGetParams(*args, **kwargs)`
:   Parameters for invoice_item_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesGtCondition"></a>

`InvoiceItemCategoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesGteCondition"></a>

`InvoiceItemCategoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesInCondition"></a>

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

<a id="InvoiceItemCategoriesInFilter"></a>

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

<a id="InvoiceItemCategoriesKeywordCondition"></a>

`InvoiceItemCategoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesListParams"></a>

`InvoiceItemCategoriesListParams(*args, **kwargs)`
:   Parameters for invoice_item_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesLtCondition"></a>

`InvoiceItemCategoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesLteCondition"></a>

`InvoiceItemCategoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesNeqCondition"></a>

`InvoiceItemCategoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSearchFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition]`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesSearchFilter"></a>

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

<a id="InvoiceItemCategoriesSearchQuery"></a>

`InvoiceItemCategoriesSearchQuery(*args, **kwargs)`
:   Search query for invoice_item_categories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesSortFilter]`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesSortFilter"></a>

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

<a id="InvoiceItemCategoriesStartswithCondition"></a>

`InvoiceItemCategoriesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.InvoiceItemCategoriesStringFilter`
    :   The type of the None singleton.

<a id="InvoiceItemCategoriesStringFilter"></a>

`InvoiceItemCategoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="InvoicesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

<a id="InvoicesAnyCondition"></a>

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

<a id="InvoicesAnyValueFilter"></a>

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

<a id="InvoicesArrayContainsCondition"></a>

`InvoicesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoicesContainsCondition"></a>

`InvoicesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoicesEndswithCondition"></a>

`InvoicesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesEqCondition"></a>

`InvoicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesFuzzyCondition"></a>

`InvoicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesGetParams"></a>

`InvoicesGetParams(*args, **kwargs)`
:   Parameters for invoices.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="InvoicesGtCondition"></a>

`InvoicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesGteCondition"></a>

`InvoicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesInCondition"></a>

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

<a id="InvoicesInFilter"></a>

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

<a id="InvoicesKeywordCondition"></a>

`InvoicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesListParams"></a>

`InvoicesListParams(*args, **kwargs)`
:   Parameters for invoices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="InvoicesLtCondition"></a>

`InvoicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesLteCondition"></a>

`InvoicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesNeqCondition"></a>

`InvoicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition`
    :   The type of the None singleton.

<a id="InvoicesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

<a id="InvoicesSearchFilter"></a>

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

<a id="InvoicesSearchQuery"></a>

`InvoicesSearchQuery(*args, **kwargs)`
:   Search query for invoices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesInCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.harvest.types.InvoicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.InvoicesSortFilter]`
    :   The type of the None singleton.

<a id="InvoicesSortFilter"></a>

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

<a id="InvoicesStartswithCondition"></a>

`InvoicesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesStringFilter"></a>

`InvoicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="ProjectsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsAnyCondition"></a>

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

<a id="ProjectsAnyValueFilter"></a>

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

<a id="ProjectsArrayContainsCondition"></a>

`ProjectsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsContainsCondition"></a>

`ProjectsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsEndswithCondition"></a>

`ProjectsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsEqCondition"></a>

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsFuzzyCondition"></a>

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsGetParams"></a>

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProjectsGtCondition"></a>

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsGteCondition"></a>

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsInCondition"></a>

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

<a id="ProjectsInFilter"></a>

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

<a id="ProjectsKeywordCondition"></a>

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsListParams"></a>

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="ProjectsLtCondition"></a>

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsLteCondition"></a>

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNeqCondition"></a>

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition`
    :   The type of the None singleton.

<a id="ProjectsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsSearchFilter"></a>

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

<a id="ProjectsSearchQuery"></a>

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.ProjectsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectsSortFilter"></a>

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

<a id="ProjectsStartswithCondition"></a>

`ProjectsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsStringFilter"></a>

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="RolesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition]`
    :   The type of the None singleton.

<a id="RolesAnyCondition"></a>

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

<a id="RolesAnyValueFilter"></a>

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

<a id="RolesArrayContainsCondition"></a>

`RolesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.RolesAnyValueFilter`
    :   The type of the None singleton.

<a id="RolesContainsCondition"></a>

`RolesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.RolesAnyValueFilter`
    :   The type of the None singleton.

<a id="RolesEndswithCondition"></a>

`RolesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

<a id="RolesEqCondition"></a>

`RolesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesFuzzyCondition"></a>

`RolesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

<a id="RolesGetParams"></a>

`RolesGetParams(*args, **kwargs)`
:   Parameters for roles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="RolesGtCondition"></a>

`RolesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesGteCondition"></a>

`RolesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesInCondition"></a>

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

<a id="RolesInFilter"></a>

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

<a id="RolesKeywordCondition"></a>

`RolesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

<a id="RolesListParams"></a>

`RolesListParams(*args, **kwargs)`
:   Parameters for roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="RolesLtCondition"></a>

`RolesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesLteCondition"></a>

`RolesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesNeqCondition"></a>

`RolesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition`
    :   The type of the None singleton.

<a id="RolesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition]`
    :   The type of the None singleton.

<a id="RolesSearchFilter"></a>

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

<a id="RolesSearchQuery"></a>

`RolesSearchQuery(*args, **kwargs)`
:   Search query for roles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.RolesEqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesGteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLtCondition | airbyte_agent_sdk.connectors.harvest.types.RolesLteCondition | airbyte_agent_sdk.connectors.harvest.types.RolesInCondition | airbyte_agent_sdk.connectors.harvest.types.RolesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.RolesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.RolesNotCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAndCondition | airbyte_agent_sdk.connectors.harvest.types.RolesOrCondition | airbyte_agent_sdk.connectors.harvest.types.RolesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.RolesSortFilter]`
    :   The type of the None singleton.

<a id="RolesSortFilter"></a>

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

<a id="RolesStartswithCondition"></a>

`RolesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.RolesStringFilter`
    :   The type of the None singleton.

<a id="RolesStringFilter"></a>

`RolesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="TaskAssignmentsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition]`
    :   The type of the None singleton.

<a id="TaskAssignmentsAnyCondition"></a>

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

<a id="TaskAssignmentsAnyValueFilter"></a>

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

<a id="TaskAssignmentsArrayContainsCondition"></a>

`TaskAssignmentsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsContainsCondition"></a>

`TaskAssignmentsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsEndswithCondition"></a>

`TaskAssignmentsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsEqCondition"></a>

`TaskAssignmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsFuzzyCondition"></a>

`TaskAssignmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsGtCondition"></a>

`TaskAssignmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsGteCondition"></a>

`TaskAssignmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsInCondition"></a>

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

<a id="TaskAssignmentsInFilter"></a>

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

<a id="TaskAssignmentsKeywordCondition"></a>

`TaskAssignmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsListParams"></a>

`TaskAssignmentsListParams(*args, **kwargs)`
:   Parameters for task_assignments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="TaskAssignmentsLtCondition"></a>

`TaskAssignmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsLteCondition"></a>

`TaskAssignmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsNeqCondition"></a>

`TaskAssignmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition`
    :   The type of the None singleton.

<a id="TaskAssignmentsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition]`
    :   The type of the None singleton.

<a id="TaskAssignmentsSearchFilter"></a>

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

<a id="TaskAssignmentsSearchQuery"></a>

`TaskAssignmentsSearchQuery(*args, **kwargs)`
:   Search query for task_assignments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsSortFilter]`
    :   The type of the None singleton.

<a id="TaskAssignmentsSortFilter"></a>

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

<a id="TaskAssignmentsStartswithCondition"></a>

`TaskAssignmentsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.TaskAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="TaskAssignmentsStringFilter"></a>

`TaskAssignmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="TasksAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksAnyCondition"></a>

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

<a id="TasksAnyValueFilter"></a>

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

<a id="TasksArrayContainsCondition"></a>

`TasksArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksContainsCondition"></a>

`TasksContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksEndswithCondition"></a>

`TasksEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksEqCondition"></a>

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksFuzzyCondition"></a>

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksGetParams"></a>

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TasksGtCondition"></a>

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksGteCondition"></a>

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksInCondition"></a>

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

<a id="TasksInFilter"></a>

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

<a id="TasksKeywordCondition"></a>

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksListParams"></a>

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="TasksLtCondition"></a>

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksLteCondition"></a>

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNeqCondition"></a>

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition`
    :   The type of the None singleton.

<a id="TasksOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksSearchFilter"></a>

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

<a id="TasksSearchQuery"></a>

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TasksSortFilter]`
    :   The type of the None singleton.

<a id="TasksSortFilter"></a>

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

<a id="TasksStartswithCondition"></a>

`TasksStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksStringFilter"></a>

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="TimeEntriesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition]`
    :   The type of the None singleton.

<a id="TimeEntriesAnyCondition"></a>

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

<a id="TimeEntriesAnyValueFilter"></a>

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

<a id="TimeEntriesArrayContainsCondition"></a>

`TimeEntriesArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeEntriesContainsCondition"></a>

`TimeEntriesContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeEntriesEndswithCondition"></a>

`TimeEntriesEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesEqCondition"></a>

`TimeEntriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesFuzzyCondition"></a>

`TimeEntriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesGetParams"></a>

`TimeEntriesGetParams(*args, **kwargs)`
:   Parameters for time_entries.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TimeEntriesGtCondition"></a>

`TimeEntriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesGteCondition"></a>

`TimeEntriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesInCondition"></a>

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

<a id="TimeEntriesInFilter"></a>

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

<a id="TimeEntriesKeywordCondition"></a>

`TimeEntriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesListParams"></a>

`TimeEntriesListParams(*args, **kwargs)`
:   Parameters for time_entries.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="TimeEntriesLtCondition"></a>

`TimeEntriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesLteCondition"></a>

`TimeEntriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesNeqCondition"></a>

`TimeEntriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition`
    :   The type of the None singleton.

<a id="TimeEntriesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition]`
    :   The type of the None singleton.

<a id="TimeEntriesSearchFilter"></a>

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

<a id="TimeEntriesSearchQuery"></a>

`TimeEntriesSearchQuery(*args, **kwargs)`
:   Search query for time_entries entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeEntriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TimeEntriesSortFilter]`
    :   The type of the None singleton.

<a id="TimeEntriesSortFilter"></a>

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

<a id="TimeEntriesStartswithCondition"></a>

`TimeEntriesStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesStringFilter"></a>

`TimeEntriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="TimeProjectsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="TimeProjectsAnyCondition"></a>

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

<a id="TimeProjectsAnyValueFilter"></a>

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

<a id="TimeProjectsArrayContainsCondition"></a>

`TimeProjectsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeProjectsContainsCondition"></a>

`TimeProjectsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeProjectsEndswithCondition"></a>

`TimeProjectsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

<a id="TimeProjectsEqCondition"></a>

`TimeProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

<a id="TimeProjectsFuzzyCondition"></a>

`TimeProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

<a id="TimeProjectsGtCondition"></a>

`TimeProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

<a id="TimeProjectsGteCondition"></a>

`TimeProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

<a id="TimeProjectsInCondition"></a>

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

<a id="TimeProjectsInFilter"></a>

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

<a id="TimeProjectsKeywordCondition"></a>

`TimeProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

<a id="TimeProjectsListParams"></a>

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

<a id="TimeProjectsLtCondition"></a>

`TimeProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

<a id="TimeProjectsLteCondition"></a>

`TimeProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

<a id="TimeProjectsNeqCondition"></a>

`TimeProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSearchFilter`
    :   The type of the None singleton.

<a id="TimeProjectsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition`
    :   The type of the None singleton.

<a id="TimeProjectsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="TimeProjectsSearchFilter"></a>

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

<a id="TimeProjectsSearchQuery"></a>

`TimeProjectsSearchQuery(*args, **kwargs)`
:   Search query for time_projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TimeProjectsSortFilter]`
    :   The type of the None singleton.

<a id="TimeProjectsSortFilter"></a>

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

<a id="TimeProjectsStartswithCondition"></a>

`TimeProjectsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.TimeProjectsStringFilter`
    :   The type of the None singleton.

<a id="TimeProjectsStringFilter"></a>

`TimeProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="TimeTasksAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition]`
    :   The type of the None singleton.

<a id="TimeTasksAnyCondition"></a>

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

<a id="TimeTasksAnyValueFilter"></a>

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

<a id="TimeTasksArrayContainsCondition"></a>

`TimeTasksArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeTasksContainsCondition"></a>

`TimeTasksContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeTasksEndswithCondition"></a>

`TimeTasksEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

<a id="TimeTasksEqCondition"></a>

`TimeTasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

<a id="TimeTasksFuzzyCondition"></a>

`TimeTasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

<a id="TimeTasksGtCondition"></a>

`TimeTasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

<a id="TimeTasksGteCondition"></a>

`TimeTasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

<a id="TimeTasksInCondition"></a>

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

<a id="TimeTasksInFilter"></a>

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

<a id="TimeTasksKeywordCondition"></a>

`TimeTasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

<a id="TimeTasksListParams"></a>

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

<a id="TimeTasksLtCondition"></a>

`TimeTasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

<a id="TimeTasksLteCondition"></a>

`TimeTasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

<a id="TimeTasksNeqCondition"></a>

`TimeTasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.TimeTasksSearchFilter`
    :   The type of the None singleton.

<a id="TimeTasksNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition`
    :   The type of the None singleton.

<a id="TimeTasksOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition]`
    :   The type of the None singleton.

<a id="TimeTasksSearchFilter"></a>

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

<a id="TimeTasksSearchQuery"></a>

`TimeTasksSearchQuery(*args, **kwargs)`
:   Search query for time_tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.TimeTasksEqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNeqCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksGteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLtCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksLteCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksInCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksNotCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAndCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksOrCondition | airbyte_agent_sdk.connectors.harvest.types.TimeTasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.TimeTasksSortFilter]`
    :   The type of the None singleton.

<a id="TimeTasksSortFilter"></a>

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

<a id="TimeTasksStartswithCondition"></a>

`TimeTasksStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.TimeTasksStringFilter`
    :   The type of the None singleton.

<a id="TimeTasksStringFilter"></a>

`TimeTasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

<a id="UserAssignmentsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition]`
    :   The type of the None singleton.

<a id="UserAssignmentsAnyCondition"></a>

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

<a id="UserAssignmentsAnyValueFilter"></a>

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

<a id="UserAssignmentsArrayContainsCondition"></a>

`UserAssignmentsArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsContainsCondition"></a>

`UserAssignmentsContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsEndswithCondition"></a>

`UserAssignmentsEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsEqCondition"></a>

`UserAssignmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsFuzzyCondition"></a>

`UserAssignmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsGtCondition"></a>

`UserAssignmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsGteCondition"></a>

`UserAssignmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsInCondition"></a>

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

<a id="UserAssignmentsInFilter"></a>

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

<a id="UserAssignmentsKeywordCondition"></a>

`UserAssignmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsListParams"></a>

`UserAssignmentsListParams(*args, **kwargs)`
:   Parameters for user_assignments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="UserAssignmentsLtCondition"></a>

`UserAssignmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsLteCondition"></a>

`UserAssignmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsNeqCondition"></a>

`UserAssignmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSearchFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition`
    :   The type of the None singleton.

<a id="UserAssignmentsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition]`
    :   The type of the None singleton.

<a id="UserAssignmentsSearchFilter"></a>

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

<a id="UserAssignmentsSearchQuery"></a>

`UserAssignmentsSearchQuery(*args, **kwargs)`
:   Search query for user_assignments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsGteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLtCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsLteCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsInCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsNotCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAndCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsOrCondition | airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsSortFilter]`
    :   The type of the None singleton.

<a id="UserAssignmentsSortFilter"></a>

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

<a id="UserAssignmentsStartswithCondition"></a>

`UserAssignmentsStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.UserAssignmentsStringFilter`
    :   The type of the None singleton.

<a id="UserAssignmentsStringFilter"></a>

`UserAssignmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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

    `and: list[airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.harvest.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

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

<a id="UsersArrayContainsCondition"></a>

`UsersArrayContainsCondition(*args, **kwargs)`
:   Exact membership test on an array field. Example: \{"array_contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `array_contains: airbyte_agent_sdk.connectors.harvest.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Case-insensitive substring match on a scalar field. Example: \{"contains": \{"subject": "billing"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.harvest.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEndswithCondition"></a>

`UsersEndswithCondition(*args, **kwargs)`
:   Literal case-insensitive suffix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `endswith: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.harvest.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

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

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.harvest.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

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

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.harvest.types.UsersEqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNeqCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersGteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLtCondition | airbyte_agent_sdk.connectors.harvest.types.UsersLteCondition | airbyte_agent_sdk.connectors.harvest.types.UsersInCondition | airbyte_agent_sdk.connectors.harvest.types.UsersStartswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersEndswithCondition | airbyte_agent_sdk.connectors.harvest.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.harvest.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.harvest.types.UsersContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersArrayContainsCondition | airbyte_agent_sdk.connectors.harvest.types.UsersNotCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAndCondition | airbyte_agent_sdk.connectors.harvest.types.UsersOrCondition | airbyte_agent_sdk.connectors.harvest.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.harvest.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

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

<a id="UsersStartswithCondition"></a>

`UsersStartswithCondition(*args, **kwargs)`
:   Literal case-insensitive prefix match.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `startswith: airbyte_agent_sdk.connectors.harvest.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (startswith, endswith, fuzzy, keyword).

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