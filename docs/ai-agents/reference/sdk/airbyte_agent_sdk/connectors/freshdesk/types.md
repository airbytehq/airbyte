---
id: airbyte_agent_sdk-connectors-freshdesk-types
title: airbyte_agent_sdk.connectors.freshdesk.types
---

Module airbyte_agent_sdk.connectors.freshdesk.types
===================================================
Type definitions for freshdesk connector.

Classes
-------

<a id="AgentsAndCondition"></a>

`AgentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.AgentsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsAnyCondition"></a>

`AgentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.AgentsAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsAnyValueFilter"></a>

`AgentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: Any`
    :   Whether the agent is available

    `available_since: Any`
    :   Timestamp since the agent has been available

    `contact: Any`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: Any`
    :   Agent creation timestamp

    `id: Any`
    :   Unique agent ID

    `last_active_at: Any`
    :   Timestamp of last agent activity

    `occasional: Any`
    :   Whether the agent is an occasional agent

    `signature: Any`
    :   Signature of the agent (HTML)

    `ticket_scope: Any`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: Any`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: Any`
    :   Agent last update timestamp

<a id="AgentsContainsCondition"></a>

`AgentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.AgentsAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsEqCondition"></a>

`AgentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsFuzzyCondition"></a>

`AgentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.AgentsStringFilter`
    :   The type of the None singleton.

<a id="AgentsGetParams"></a>

`AgentsGetParams(*args, **kwargs)`
:   Parameters for agents.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AgentsGtCondition"></a>

`AgentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsGteCondition"></a>

`AgentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsInCondition"></a>

`AgentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.AgentsInFilter`
    :   The type of the None singleton.

<a id="AgentsInFilter"></a>

`AgentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: list[bool]`
    :   Whether the agent is available

    `available_since: list[str]`
    :   Timestamp since the agent has been available

    `contact: list[dict[str, typing.Any]]`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: list[str]`
    :   Agent creation timestamp

    `id: list[int]`
    :   Unique agent ID

    `last_active_at: list[str]`
    :   Timestamp of last agent activity

    `occasional: list[bool]`
    :   Whether the agent is an occasional agent

    `signature: list[str]`
    :   Signature of the agent (HTML)

    `ticket_scope: list[int]`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: list[str]`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: list[str]`
    :   Agent last update timestamp

<a id="AgentsKeywordCondition"></a>

`AgentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.AgentsStringFilter`
    :   The type of the None singleton.

<a id="AgentsLikeCondition"></a>

`AgentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.AgentsStringFilter`
    :   The type of the None singleton.

<a id="AgentsListParams"></a>

`AgentsListParams(*args, **kwargs)`
:   Parameters for agents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="AgentsLtCondition"></a>

`AgentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsLteCondition"></a>

`AgentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsNeqCondition"></a>

`AgentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsNotCondition"></a>

`AgentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.AgentsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAnyCondition`
    :   The type of the None singleton.

<a id="AgentsOrCondition"></a>

`AgentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.AgentsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsSearchFilter"></a>

`AgentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering agents search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: bool | None`
    :   Whether the agent is available

    `available_since: str | None`
    :   Timestamp since the agent has been available

    `contact: dict[str, typing.Any] | None`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: str | None`
    :   Agent creation timestamp

    `id: int | None`
    :   Unique agent ID

    `last_active_at: str | None`
    :   Timestamp of last agent activity

    `occasional: bool | None`
    :   Whether the agent is an occasional agent

    `signature: str | None`
    :   Signature of the agent (HTML)

    `ticket_scope: int | None`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: str | None`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: str | None`
    :   Agent last update timestamp

<a id="AgentsSearchQuery"></a>

`AgentsSearchQuery(*args, **kwargs)`
:   Search query for agents entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.AgentsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.AgentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.AgentsSortFilter]`
    :   The type of the None singleton.

<a id="AgentsSortFilter"></a>

`AgentsSortFilter(*args, **kwargs)`
:   Available fields for sorting agents search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: Literal['asc', 'desc']`
    :   Whether the agent is available

    `available_since: Literal['asc', 'desc']`
    :   Timestamp since the agent has been available

    `contact: Literal['asc', 'desc']`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: Literal['asc', 'desc']`
    :   Agent creation timestamp

    `id: Literal['asc', 'desc']`
    :   Unique agent ID

    `last_active_at: Literal['asc', 'desc']`
    :   Timestamp of last agent activity

    `occasional: Literal['asc', 'desc']`
    :   Whether the agent is an occasional agent

    `signature: Literal['asc', 'desc']`
    :   Signature of the agent (HTML)

    `ticket_scope: Literal['asc', 'desc']`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: Literal['asc', 'desc']`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: Literal['asc', 'desc']`
    :   Agent last update timestamp

<a id="AgentsStringFilter"></a>

`AgentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `available: str`
    :   Whether the agent is available

    `available_since: str`
    :   Timestamp since the agent has been available

    `contact: str`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: str`
    :   Agent creation timestamp

    `id: str`
    :   Unique agent ID

    `last_active_at: str`
    :   Timestamp of last agent activity

    `occasional: str`
    :   Whether the agent is an occasional agent

    `signature: str`
    :   Signature of the agent (HTML)

    `ticket_scope: str`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: str`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: str`
    :   Agent last update timestamp

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

<a id="CompaniesAndCondition"></a>

`CompaniesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAnyCondition]`
    :   The type of the None singleton.

<a id="CompaniesAnyCondition"></a>

`CompaniesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

<a id="CompaniesAnyValueFilter"></a>

`CompaniesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tier: Any`
    :   Account tier of the company

    `created_at: Any`
    :   Company creation timestamp

    `custom_fields: Any`
    :   Custom fields associated with the company

    `description: Any`
    :   Description of the company

    `domains: Any`
    :   Email domains associated with the company

    `health_score: Any`
    :   Health score of the company

    `id: Any`
    :   Unique company ID

    `industry: Any`
    :   Industry of the company

    `name: Any`
    :   Name of the company

    `note: Any`
    :   Notes about the company

    `renewal_date: Any`
    :   Renewal date

    `updated_at: Any`
    :   Company last update timestamp

<a id="CompaniesContainsCondition"></a>

`CompaniesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

<a id="CompaniesEqCondition"></a>

`CompaniesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesFuzzyCondition"></a>

`CompaniesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesGetParams"></a>

`CompaniesGetParams(*args, **kwargs)`
:   Parameters for companies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CompaniesGtCondition"></a>

`CompaniesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesGteCondition"></a>

`CompaniesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesInCondition"></a>

`CompaniesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesInFilter`
    :   The type of the None singleton.

<a id="CompaniesInFilter"></a>

`CompaniesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tier: list[str]`
    :   Account tier of the company

    `created_at: list[str]`
    :   Company creation timestamp

    `custom_fields: list[dict[str, typing.Any]]`
    :   Custom fields associated with the company

    `description: list[str]`
    :   Description of the company

    `domains: list[list[typing.Any]]`
    :   Email domains associated with the company

    `health_score: list[str]`
    :   Health score of the company

    `id: list[int]`
    :   Unique company ID

    `industry: list[str]`
    :   Industry of the company

    `name: list[str]`
    :   Name of the company

    `note: list[str]`
    :   Notes about the company

    `renewal_date: list[str]`
    :   Renewal date

    `updated_at: list[str]`
    :   Company last update timestamp

<a id="CompaniesKeywordCondition"></a>

`CompaniesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesLikeCondition"></a>

`CompaniesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesListParams"></a>

`CompaniesListParams(*args, **kwargs)`
:   Parameters for companies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="CompaniesLtCondition"></a>

`CompaniesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesLteCondition"></a>

`CompaniesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesNeqCondition"></a>

`CompaniesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesNotCondition"></a>

`CompaniesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAnyCondition`
    :   The type of the None singleton.

<a id="CompaniesOrCondition"></a>

`CompaniesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAnyCondition]`
    :   The type of the None singleton.

<a id="CompaniesSearchFilter"></a>

`CompaniesSearchFilter(*args, **kwargs)`
:   Available fields for filtering companies search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tier: str | None`
    :   Account tier of the company

    `created_at: str | None`
    :   Company creation timestamp

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the company

    `description: str | None`
    :   Description of the company

    `domains: list[typing.Any] | None`
    :   Email domains associated with the company

    `health_score: str | None`
    :   Health score of the company

    `id: int | None`
    :   Unique company ID

    `industry: str | None`
    :   Industry of the company

    `name: str | None`
    :   Name of the company

    `note: str | None`
    :   Notes about the company

    `renewal_date: str | None`
    :   Renewal date

    `updated_at: str | None`
    :   Company last update timestamp

<a id="CompaniesSearchQuery"></a>

`CompaniesSearchQuery(*args, **kwargs)`
:   Search query for companies entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.CompaniesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.CompaniesSortFilter]`
    :   The type of the None singleton.

<a id="CompaniesSortFilter"></a>

`CompaniesSortFilter(*args, **kwargs)`
:   Available fields for sorting companies search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tier: Literal['asc', 'desc']`
    :   Account tier of the company

    `created_at: Literal['asc', 'desc']`
    :   Company creation timestamp

    `custom_fields: Literal['asc', 'desc']`
    :   Custom fields associated with the company

    `description: Literal['asc', 'desc']`
    :   Description of the company

    `domains: Literal['asc', 'desc']`
    :   Email domains associated with the company

    `health_score: Literal['asc', 'desc']`
    :   Health score of the company

    `id: Literal['asc', 'desc']`
    :   Unique company ID

    `industry: Literal['asc', 'desc']`
    :   Industry of the company

    `name: Literal['asc', 'desc']`
    :   Name of the company

    `note: Literal['asc', 'desc']`
    :   Notes about the company

    `renewal_date: Literal['asc', 'desc']`
    :   Renewal date

    `updated_at: Literal['asc', 'desc']`
    :   Company last update timestamp

<a id="CompaniesStringFilter"></a>

`CompaniesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tier: str`
    :   Account tier of the company

    `created_at: str`
    :   Company creation timestamp

    `custom_fields: str`
    :   Custom fields associated with the company

    `description: str`
    :   Description of the company

    `domains: str`
    :   Email domains associated with the company

    `health_score: str`
    :   Health score of the company

    `id: str`
    :   Unique company ID

    `industry: str`
    :   Industry of the company

    `name: str`
    :   Name of the company

    `note: str`
    :   Notes about the company

    `renewal_date: str`
    :   Renewal date

    `updated_at: str`
    :   Company last update timestamp

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

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.ContactsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.freshdesk.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsAnyValueFilter"></a>

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Whether the contact has been verified

    `address: Any`
    :   Address of the contact

    `company_id: Any`
    :   ID of the primary company

    `created_at: Any`
    :   Contact creation timestamp

    `csat_rating: Any`
    :   CSAT rating of the contact

    `custom_fields: Any`
    :   Custom fields associated with the contact

    `description: Any`
    :   Description of the contact

    `email: Any`
    :   Primary email address

    `facebook_id: Any`
    :   Facebook ID of the contact

    `id: Any`
    :   Unique contact ID

    `job_title: Any`
    :   Job title of the contact

    `language: Any`
    :   Language of the contact

    `mobile: Any`
    :   Mobile number

    `name: Any`
    :   Name of the contact

    `phone: Any`
    :   Phone number

    `preferred_source: Any`
    :   Preferred contact source

    `time_zone: Any`
    :   Time zone of the contact

    `twitter_id: Any`
    :   Twitter ID

    `unique_external_id: Any`
    :   External ID of the contact

    `updated_at: Any`
    :   Contact last update timestamp

<a id="ContactsContainsCondition"></a>

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsEqCondition"></a>

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsFuzzyCondition"></a>

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.ContactsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsGteCondition"></a>

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.ContactsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.freshdesk.types.ContactsInFilter`
    :   The type of the None singleton.

<a id="ContactsInFilter"></a>

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Whether the contact has been verified

    `address: list[str]`
    :   Address of the contact

    `company_id: list[int]`
    :   ID of the primary company

    `created_at: list[str]`
    :   Contact creation timestamp

    `csat_rating: list[int]`
    :   CSAT rating of the contact

    `custom_fields: list[dict[str, typing.Any]]`
    :   Custom fields associated with the contact

    `description: list[str]`
    :   Description of the contact

    `email: list[str]`
    :   Primary email address

    `facebook_id: list[str]`
    :   Facebook ID of the contact

    `id: list[int]`
    :   Unique contact ID

    `job_title: list[str]`
    :   Job title of the contact

    `language: list[str]`
    :   Language of the contact

    `mobile: list[str]`
    :   Mobile number

    `name: list[str]`
    :   Name of the contact

    `phone: list[str]`
    :   Phone number

    `preferred_source: list[str]`
    :   Preferred contact source

    `time_zone: list[str]`
    :   Time zone of the contact

    `twitter_id: list[str]`
    :   Twitter ID

    `unique_external_id: list[str]`
    :   External ID of the contact

    `updated_at: list[str]`
    :   Contact last update timestamp

<a id="ContactsKeywordCondition"></a>

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsLikeCondition"></a>

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_since: str`
    :   The type of the None singleton.

<a id="ContactsLtCondition"></a>

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsLteCondition"></a>

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNeqCondition"></a>

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.ContactsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.freshdesk.types.ContactsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.ContactsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsSearchFilter"></a>

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   Whether the contact has been verified

    `address: str | None`
    :   Address of the contact

    `company_id: int | None`
    :   ID of the primary company

    `created_at: str | None`
    :   Contact creation timestamp

    `csat_rating: int | None`
    :   CSAT rating of the contact

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the contact

    `description: str | None`
    :   Description of the contact

    `email: str | None`
    :   Primary email address

    `facebook_id: str | None`
    :   Facebook ID of the contact

    `id: int | None`
    :   Unique contact ID

    `job_title: str | None`
    :   Job title of the contact

    `language: str | None`
    :   Language of the contact

    `mobile: str | None`
    :   Mobile number

    `name: str | None`
    :   Name of the contact

    `phone: str | None`
    :   Phone number

    `preferred_source: str | None`
    :   Preferred contact source

    `time_zone: str | None`
    :   Time zone of the contact

    `twitter_id: str | None`
    :   Twitter ID

    `unique_external_id: str | None`
    :   External ID of the contact

    `updated_at: str | None`
    :   Contact last update timestamp

<a id="ContactsSearchQuery"></a>

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.ContactsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.ContactsSortFilter]`
    :   The type of the None singleton.

<a id="ContactsSortFilter"></a>

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Whether the contact has been verified

    `address: Literal['asc', 'desc']`
    :   Address of the contact

    `company_id: Literal['asc', 'desc']`
    :   ID of the primary company

    `created_at: Literal['asc', 'desc']`
    :   Contact creation timestamp

    `csat_rating: Literal['asc', 'desc']`
    :   CSAT rating of the contact

    `custom_fields: Literal['asc', 'desc']`
    :   Custom fields associated with the contact

    `description: Literal['asc', 'desc']`
    :   Description of the contact

    `email: Literal['asc', 'desc']`
    :   Primary email address

    `facebook_id: Literal['asc', 'desc']`
    :   Facebook ID of the contact

    `id: Literal['asc', 'desc']`
    :   Unique contact ID

    `job_title: Literal['asc', 'desc']`
    :   Job title of the contact

    `language: Literal['asc', 'desc']`
    :   Language of the contact

    `mobile: Literal['asc', 'desc']`
    :   Mobile number

    `name: Literal['asc', 'desc']`
    :   Name of the contact

    `phone: Literal['asc', 'desc']`
    :   Phone number

    `preferred_source: Literal['asc', 'desc']`
    :   Preferred contact source

    `time_zone: Literal['asc', 'desc']`
    :   Time zone of the contact

    `twitter_id: Literal['asc', 'desc']`
    :   Twitter ID

    `unique_external_id: Literal['asc', 'desc']`
    :   External ID of the contact

    `updated_at: Literal['asc', 'desc']`
    :   Contact last update timestamp

<a id="ContactsStringFilter"></a>

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Whether the contact has been verified

    `address: str`
    :   Address of the contact

    `company_id: str`
    :   ID of the primary company

    `created_at: str`
    :   Contact creation timestamp

    `csat_rating: str`
    :   CSAT rating of the contact

    `custom_fields: str`
    :   Custom fields associated with the contact

    `description: str`
    :   Description of the contact

    `email: str`
    :   Primary email address

    `facebook_id: str`
    :   Facebook ID of the contact

    `id: str`
    :   Unique contact ID

    `job_title: str`
    :   Job title of the contact

    `language: str`
    :   Language of the contact

    `mobile: str`
    :   Mobile number

    `name: str`
    :   Name of the contact

    `phone: str`
    :   Phone number

    `preferred_source: str`
    :   Preferred contact source

    `time_zone: str`
    :   Time zone of the contact

    `twitter_id: str`
    :   Twitter ID

    `unique_external_id: str`
    :   External ID of the contact

    `updated_at: str`
    :   Contact last update timestamp

<a id="GroupsAndCondition"></a>

`GroupsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.GroupsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupsAnyCondition"></a>

`GroupsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsAnyValueFilter"></a>

`GroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_ticket_assign: Any`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: Any`
    :   ID of the associated business hour

    `created_at: Any`
    :   Group creation timestamp

    `description: Any`
    :   Description of the group

    `escalate_to: Any`
    :   User ID for escalation

    `group_type: Any`
    :   Type of the group (e.g., support_agent_group)

    `id: Any`
    :   Unique group ID

    `name: Any`
    :   Name of the group

    `unassigned_for: Any`
    :   Time after which escalation triggers

    `updated_at: Any`
    :   Group last update timestamp

<a id="GroupsContainsCondition"></a>

`GroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsEqCondition"></a>

`GroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsFuzzyCondition"></a>

`GroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsGetParams"></a>

`GroupsGetParams(*args, **kwargs)`
:   Parameters for groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="GroupsGtCondition"></a>

`GroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsGteCondition"></a>

`GroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsInCondition"></a>

`GroupsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.GroupsInFilter`
    :   The type of the None singleton.

<a id="GroupsInFilter"></a>

`GroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_ticket_assign: list[int]`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: list[int]`
    :   ID of the associated business hour

    `created_at: list[str]`
    :   Group creation timestamp

    `description: list[str]`
    :   Description of the group

    `escalate_to: list[int]`
    :   User ID for escalation

    `group_type: list[str]`
    :   Type of the group (e.g., support_agent_group)

    `id: list[int]`
    :   Unique group ID

    `name: list[str]`
    :   Name of the group

    `unassigned_for: list[str]`
    :   Time after which escalation triggers

    `updated_at: list[str]`
    :   Group last update timestamp

<a id="GroupsKeywordCondition"></a>

`GroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsLikeCondition"></a>

`GroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsListParams"></a>

`GroupsListParams(*args, **kwargs)`
:   Parameters for groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="GroupsLtCondition"></a>

`GroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsLteCondition"></a>

`GroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsNeqCondition"></a>

`GroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsNotCondition"></a>

`GroupsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.GroupsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAnyCondition`
    :   The type of the None singleton.

<a id="GroupsOrCondition"></a>

`GroupsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.GroupsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupsSearchFilter"></a>

`GroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_ticket_assign: int | None`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: int | None`
    :   ID of the associated business hour

    `created_at: str | None`
    :   Group creation timestamp

    `description: str | None`
    :   Description of the group

    `escalate_to: int | None`
    :   User ID for escalation

    `group_type: str | None`
    :   Type of the group (e.g., support_agent_group)

    `id: int | None`
    :   Unique group ID

    `name: str | None`
    :   Name of the group

    `unassigned_for: str | None`
    :   Time after which escalation triggers

    `updated_at: str | None`
    :   Group last update timestamp

<a id="GroupsSearchQuery"></a>

`GroupsSearchQuery(*args, **kwargs)`
:   Search query for groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.GroupsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.GroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.GroupsSortFilter]`
    :   The type of the None singleton.

<a id="GroupsSortFilter"></a>

`GroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_ticket_assign: Literal['asc', 'desc']`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: Literal['asc', 'desc']`
    :   ID of the associated business hour

    `created_at: Literal['asc', 'desc']`
    :   Group creation timestamp

    `description: Literal['asc', 'desc']`
    :   Description of the group

    `escalate_to: Literal['asc', 'desc']`
    :   User ID for escalation

    `group_type: Literal['asc', 'desc']`
    :   Type of the group (e.g., support_agent_group)

    `id: Literal['asc', 'desc']`
    :   Unique group ID

    `name: Literal['asc', 'desc']`
    :   Name of the group

    `unassigned_for: Literal['asc', 'desc']`
    :   Time after which escalation triggers

    `updated_at: Literal['asc', 'desc']`
    :   Group last update timestamp

<a id="GroupsStringFilter"></a>

`GroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_ticket_assign: str`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: str`
    :   ID of the associated business hour

    `created_at: str`
    :   Group creation timestamp

    `description: str`
    :   Description of the group

    `escalate_to: str`
    :   User ID for escalation

    `group_type: str`
    :   Type of the group (e.g., support_agent_group)

    `id: str`
    :   Unique group ID

    `name: str`
    :   Name of the group

    `unassigned_for: str`
    :   Time after which escalation triggers

    `updated_at: str`
    :   Group last update timestamp

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

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.RolesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.freshdesk.types.RolesAnyValueFilter`
    :   The type of the None singleton.

<a id="RolesAnyValueFilter"></a>

`RolesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Role creation timestamp

    `default: Any`
    :   Whether this is a default role

    `description: Any`
    :   Description of the role

    `id: Any`
    :   Unique role ID

    `name: Any`
    :   Name of the role

    `updated_at: Any`
    :   Role last update timestamp

<a id="RolesContainsCondition"></a>

`RolesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.RolesAnyValueFilter`
    :   The type of the None singleton.

<a id="RolesEqCondition"></a>

`RolesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesFuzzyCondition"></a>

`RolesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.RolesStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesGteCondition"></a>

`RolesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.RolesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.freshdesk.types.RolesInFilter`
    :   The type of the None singleton.

<a id="RolesInFilter"></a>

`RolesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Role creation timestamp

    `default: list[bool]`
    :   Whether this is a default role

    `description: list[str]`
    :   Description of the role

    `id: list[int]`
    :   Unique role ID

    `name: list[str]`
    :   Name of the role

    `updated_at: list[str]`
    :   Role last update timestamp

<a id="RolesKeywordCondition"></a>

`RolesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.RolesStringFilter`
    :   The type of the None singleton.

<a id="RolesLikeCondition"></a>

`RolesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.RolesStringFilter`
    :   The type of the None singleton.

<a id="RolesListParams"></a>

`RolesListParams(*args, **kwargs)`
:   Parameters for roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="RolesLtCondition"></a>

`RolesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesLteCondition"></a>

`RolesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.RolesSearchFilter`
    :   The type of the None singleton.

<a id="RolesNeqCondition"></a>

`RolesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.RolesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.freshdesk.types.RolesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.RolesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAnyCondition]`
    :   The type of the None singleton.

<a id="RolesSearchFilter"></a>

`RolesSearchFilter(*args, **kwargs)`
:   Available fields for filtering roles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Role creation timestamp

    `default: bool | None`
    :   Whether this is a default role

    `description: str | None`
    :   Description of the role

    `id: int | None`
    :   Unique role ID

    `name: str | None`
    :   Name of the role

    `updated_at: str | None`
    :   Role last update timestamp

<a id="RolesSearchQuery"></a>

`RolesSearchQuery(*args, **kwargs)`
:   Search query for roles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.RolesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.RolesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.RolesSortFilter]`
    :   The type of the None singleton.

<a id="RolesSortFilter"></a>

`RolesSortFilter(*args, **kwargs)`
:   Available fields for sorting roles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Role creation timestamp

    `default: Literal['asc', 'desc']`
    :   Whether this is a default role

    `description: Literal['asc', 'desc']`
    :   Description of the role

    `id: Literal['asc', 'desc']`
    :   Unique role ID

    `name: Literal['asc', 'desc']`
    :   Name of the role

    `updated_at: Literal['asc', 'desc']`
    :   Role last update timestamp

<a id="RolesStringFilter"></a>

`RolesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Role creation timestamp

    `default: str`
    :   Whether this is a default role

    `description: str`
    :   Description of the role

    `id: str`
    :   Unique role ID

    `name: str`
    :   Name of the role

    `updated_at: str`
    :   Role last update timestamp

<a id="SatisfactionRatingsAndCondition"></a>

`SatisfactionRatingsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAnyCondition]`
    :   The type of the None singleton.

<a id="SatisfactionRatingsAnyCondition"></a>

`SatisfactionRatingsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAnyValueFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsAnyValueFilter"></a>

`SatisfactionRatingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Any`
    :   ID of the agent

    `created_at: Any`
    :   Rating creation timestamp

    `feedback: Any`
    :   Feedback text

    `group_id: Any`
    :   ID of the group

    `id: Any`
    :   Unique satisfaction rating ID

    `ratings: Any`
    :   Rating values (question_id to rating mapping)

    `survey_id: Any`
    :   ID of the survey

    `ticket_id: Any`
    :   ID of the ticket

    `updated_at: Any`
    :   Rating last update timestamp

    `user_id: Any`
    :   ID of the user (requester)

<a id="SatisfactionRatingsContainsCondition"></a>

`SatisfactionRatingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAnyValueFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsEqCondition"></a>

`SatisfactionRatingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsFuzzyCondition"></a>

`SatisfactionRatingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsGtCondition"></a>

`SatisfactionRatingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsGteCondition"></a>

`SatisfactionRatingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsInCondition"></a>

`SatisfactionRatingsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsInFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsInFilter"></a>

`SatisfactionRatingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: list[int]`
    :   ID of the agent

    `created_at: list[str]`
    :   Rating creation timestamp

    `feedback: list[str]`
    :   Feedback text

    `group_id: list[int]`
    :   ID of the group

    `id: list[int]`
    :   Unique satisfaction rating ID

    `ratings: list[dict[str, typing.Any]]`
    :   Rating values (question_id to rating mapping)

    `survey_id: list[int]`
    :   ID of the survey

    `ticket_id: list[int]`
    :   ID of the ticket

    `updated_at: list[str]`
    :   Rating last update timestamp

    `user_id: list[int]`
    :   ID of the user (requester)

<a id="SatisfactionRatingsKeywordCondition"></a>

`SatisfactionRatingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsLikeCondition"></a>

`SatisfactionRatingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsListParams"></a>

`SatisfactionRatingsListParams(*args, **kwargs)`
:   Parameters for satisfaction_ratings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_since: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="SatisfactionRatingsLtCondition"></a>

`SatisfactionRatingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsLteCondition"></a>

`SatisfactionRatingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsNeqCondition"></a>

`SatisfactionRatingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsNotCondition"></a>

`SatisfactionRatingsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAnyCondition`
    :   The type of the None singleton.

<a id="SatisfactionRatingsOrCondition"></a>

`SatisfactionRatingsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAnyCondition]`
    :   The type of the None singleton.

<a id="SatisfactionRatingsSearchFilter"></a>

`SatisfactionRatingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering satisfaction_ratings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: int | None`
    :   ID of the agent

    `created_at: str | None`
    :   Rating creation timestamp

    `feedback: str | None`
    :   Feedback text

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   Unique satisfaction rating ID

    `ratings: dict[str, typing.Any] | None`
    :   Rating values (question_id to rating mapping)

    `survey_id: int | None`
    :   ID of the survey

    `ticket_id: int | None`
    :   ID of the ticket

    `updated_at: str | None`
    :   Rating last update timestamp

    `user_id: int | None`
    :   ID of the user (requester)

<a id="SatisfactionRatingsSearchQuery"></a>

`SatisfactionRatingsSearchQuery(*args, **kwargs)`
:   Search query for satisfaction_ratings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.SatisfactionRatingsSortFilter]`
    :   The type of the None singleton.

<a id="SatisfactionRatingsSortFilter"></a>

`SatisfactionRatingsSortFilter(*args, **kwargs)`
:   Available fields for sorting satisfaction_ratings search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Literal['asc', 'desc']`
    :   ID of the agent

    `created_at: Literal['asc', 'desc']`
    :   Rating creation timestamp

    `feedback: Literal['asc', 'desc']`
    :   Feedback text

    `group_id: Literal['asc', 'desc']`
    :   ID of the group

    `id: Literal['asc', 'desc']`
    :   Unique satisfaction rating ID

    `ratings: Literal['asc', 'desc']`
    :   Rating values (question_id to rating mapping)

    `survey_id: Literal['asc', 'desc']`
    :   ID of the survey

    `ticket_id: Literal['asc', 'desc']`
    :   ID of the ticket

    `updated_at: Literal['asc', 'desc']`
    :   Rating last update timestamp

    `user_id: Literal['asc', 'desc']`
    :   ID of the user (requester)

<a id="SatisfactionRatingsStringFilter"></a>

`SatisfactionRatingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: str`
    :   ID of the agent

    `created_at: str`
    :   Rating creation timestamp

    `feedback: str`
    :   Feedback text

    `group_id: str`
    :   ID of the group

    `id: str`
    :   Unique satisfaction rating ID

    `ratings: str`
    :   Rating values (question_id to rating mapping)

    `survey_id: str`
    :   ID of the survey

    `ticket_id: str`
    :   ID of the ticket

    `updated_at: str`
    :   Rating last update timestamp

    `user_id: str`
    :   ID of the user (requester)

<a id="SurveysAndCondition"></a>

`SurveysAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.SurveysEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAnyCondition]`
    :   The type of the None singleton.

<a id="SurveysAnyCondition"></a>

`SurveysAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.SurveysAnyValueFilter`
    :   The type of the None singleton.

<a id="SurveysAnyValueFilter"></a>

`SurveysAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Whether the survey is active

    `created_at: Any`
    :   Survey creation timestamp

    `id: Any`
    :   Unique survey ID

    `questions: Any`
    :   Survey questions

    `title: Any`
    :   Title of the survey

    `updated_at: Any`
    :   Survey last update timestamp

<a id="SurveysContainsCondition"></a>

`SurveysContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.SurveysAnyValueFilter`
    :   The type of the None singleton.

<a id="SurveysEqCondition"></a>

`SurveysEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.SurveysSearchFilter`
    :   The type of the None singleton.

<a id="SurveysFuzzyCondition"></a>

`SurveysFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.SurveysStringFilter`
    :   The type of the None singleton.

<a id="SurveysGtCondition"></a>

`SurveysGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.SurveysSearchFilter`
    :   The type of the None singleton.

<a id="SurveysGteCondition"></a>

`SurveysGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.SurveysSearchFilter`
    :   The type of the None singleton.

<a id="SurveysInCondition"></a>

`SurveysInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.SurveysInFilter`
    :   The type of the None singleton.

<a id="SurveysInFilter"></a>

`SurveysInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Whether the survey is active

    `created_at: list[str]`
    :   Survey creation timestamp

    `id: list[int]`
    :   Unique survey ID

    `questions: list[list[typing.Any]]`
    :   Survey questions

    `title: list[str]`
    :   Title of the survey

    `updated_at: list[str]`
    :   Survey last update timestamp

<a id="SurveysKeywordCondition"></a>

`SurveysKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.SurveysStringFilter`
    :   The type of the None singleton.

<a id="SurveysLikeCondition"></a>

`SurveysLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.SurveysStringFilter`
    :   The type of the None singleton.

<a id="SurveysListParams"></a>

`SurveysListParams(*args, **kwargs)`
:   Parameters for surveys.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="SurveysLtCondition"></a>

`SurveysLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.SurveysSearchFilter`
    :   The type of the None singleton.

<a id="SurveysLteCondition"></a>

`SurveysLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.SurveysSearchFilter`
    :   The type of the None singleton.

<a id="SurveysNeqCondition"></a>

`SurveysNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.SurveysSearchFilter`
    :   The type of the None singleton.

<a id="SurveysNotCondition"></a>

`SurveysNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.SurveysEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAnyCondition`
    :   The type of the None singleton.

<a id="SurveysOrCondition"></a>

`SurveysOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.SurveysEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAnyCondition]`
    :   The type of the None singleton.

<a id="SurveysSearchFilter"></a>

`SurveysSearchFilter(*args, **kwargs)`
:   Available fields for filtering surveys search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   Whether the survey is active

    `created_at: str | None`
    :   Survey creation timestamp

    `id: int | None`
    :   Unique survey ID

    `questions: list[typing.Any] | None`
    :   Survey questions

    `title: str | None`
    :   Title of the survey

    `updated_at: str | None`
    :   Survey last update timestamp

<a id="SurveysSearchQuery"></a>

`SurveysSearchQuery(*args, **kwargs)`
:   Search query for surveys entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.SurveysEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysInCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.SurveysAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.SurveysSortFilter]`
    :   The type of the None singleton.

<a id="SurveysSortFilter"></a>

`SurveysSortFilter(*args, **kwargs)`
:   Available fields for sorting surveys search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Whether the survey is active

    `created_at: Literal['asc', 'desc']`
    :   Survey creation timestamp

    `id: Literal['asc', 'desc']`
    :   Unique survey ID

    `questions: Literal['asc', 'desc']`
    :   Survey questions

    `title: Literal['asc', 'desc']`
    :   Title of the survey

    `updated_at: Literal['asc', 'desc']`
    :   Survey last update timestamp

<a id="SurveysStringFilter"></a>

`SurveysStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Whether the survey is active

    `created_at: str`
    :   Survey creation timestamp

    `id: str`
    :   Unique survey ID

    `questions: str`
    :   Survey questions

    `title: str`
    :   Title of the survey

    `updated_at: str`
    :   Survey last update timestamp

<a id="TicketFieldsAndCondition"></a>

`TicketFieldsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFieldsAnyCondition"></a>

`TicketFieldsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFieldsAnyValueFilter"></a>

`TicketFieldsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `choices: Any`
    :   Available choices for dropdown fields

    `created_at: Any`
    :   Field creation timestamp

    `customers_can_edit: Any`
    :   Whether customers can edit this field

    `default: Any`
    :   Whether this is a default (non-custom) field

    `description: Any`
    :   Description of the field

    `displayed_to_customers: Any`
    :   Whether the field is displayed to customers

    `id: Any`
    :   Unique ticket field ID

    `label: Any`
    :   Display label for agents

    `label_for_customers: Any`
    :   Display label in the customer portal

    `name: Any`
    :   Name of the field

    `portal_cc: Any`
    :   Whether CC is enabled in the portal

    `portal_cc_to: Any`
    :   CC recipients scope (all or company)

    `position: Any`
    :   Position of the field in the form

    `required_for_agents: Any`
    :   Whether the field is required for agents

    `required_for_closure: Any`
    :   Whether the field is required for ticket closure

    `required_for_customers: Any`
    :   Whether the field is required for customers

    `type_: Any`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: Any`
    :   Field last update timestamp

<a id="TicketFieldsContainsCondition"></a>

`TicketFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFieldsEqCondition"></a>

`TicketFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsFuzzyCondition"></a>

`TicketFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

<a id="TicketFieldsGtCondition"></a>

`TicketFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsGteCondition"></a>

`TicketFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsInCondition"></a>

`TicketFieldsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsInFilter`
    :   The type of the None singleton.

<a id="TicketFieldsInFilter"></a>

`TicketFieldsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `choices: list[dict[str, typing.Any]]`
    :   Available choices for dropdown fields

    `created_at: list[str]`
    :   Field creation timestamp

    `customers_can_edit: list[bool]`
    :   Whether customers can edit this field

    `default: list[bool]`
    :   Whether this is a default (non-custom) field

    `description: list[str]`
    :   Description of the field

    `displayed_to_customers: list[bool]`
    :   Whether the field is displayed to customers

    `id: list[int]`
    :   Unique ticket field ID

    `label: list[str]`
    :   Display label for agents

    `label_for_customers: list[str]`
    :   Display label in the customer portal

    `name: list[str]`
    :   Name of the field

    `portal_cc: list[bool]`
    :   Whether CC is enabled in the portal

    `portal_cc_to: list[str]`
    :   CC recipients scope (all or company)

    `position: list[int]`
    :   Position of the field in the form

    `required_for_agents: list[bool]`
    :   Whether the field is required for agents

    `required_for_closure: list[bool]`
    :   Whether the field is required for ticket closure

    `required_for_customers: list[bool]`
    :   Whether the field is required for customers

    `type_: list[str]`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: list[str]`
    :   Field last update timestamp

<a id="TicketFieldsKeywordCondition"></a>

`TicketFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

<a id="TicketFieldsLikeCondition"></a>

`TicketFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

<a id="TicketFieldsListParams"></a>

`TicketFieldsListParams(*args, **kwargs)`
:   Parameters for ticket_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TicketFieldsLtCondition"></a>

`TicketFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsLteCondition"></a>

`TicketFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsNeqCondition"></a>

`TicketFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsNotCondition"></a>

`TicketFieldsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAnyCondition`
    :   The type of the None singleton.

<a id="TicketFieldsOrCondition"></a>

`TicketFieldsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFieldsSearchFilter"></a>

`TicketFieldsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_fields search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `choices: dict[str, typing.Any] | None`
    :   Available choices for dropdown fields

    `created_at: str | None`
    :   Field creation timestamp

    `customers_can_edit: bool | None`
    :   Whether customers can edit this field

    `default: bool | None`
    :   Whether this is a default (non-custom) field

    `description: str | None`
    :   Description of the field

    `displayed_to_customers: bool | None`
    :   Whether the field is displayed to customers

    `id: int | None`
    :   Unique ticket field ID

    `label: str | None`
    :   Display label for agents

    `label_for_customers: str | None`
    :   Display label in the customer portal

    `name: str | None`
    :   Name of the field

    `portal_cc: bool | None`
    :   Whether CC is enabled in the portal

    `portal_cc_to: str | None`
    :   CC recipients scope (all or company)

    `position: int | None`
    :   Position of the field in the form

    `required_for_agents: bool | None`
    :   Whether the field is required for agents

    `required_for_closure: bool | None`
    :   Whether the field is required for ticket closure

    `required_for_customers: bool | None`
    :   Whether the field is required for customers

    `type_: str | None`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: str | None`
    :   Field last update timestamp

<a id="TicketFieldsSearchQuery"></a>

`TicketFieldsSearchQuery(*args, **kwargs)`
:   Search query for ticket_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.TicketFieldsSortFilter]`
    :   The type of the None singleton.

<a id="TicketFieldsSortFilter"></a>

`TicketFieldsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_fields search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `choices: Literal['asc', 'desc']`
    :   Available choices for dropdown fields

    `created_at: Literal['asc', 'desc']`
    :   Field creation timestamp

    `customers_can_edit: Literal['asc', 'desc']`
    :   Whether customers can edit this field

    `default: Literal['asc', 'desc']`
    :   Whether this is a default (non-custom) field

    `description: Literal['asc', 'desc']`
    :   Description of the field

    `displayed_to_customers: Literal['asc', 'desc']`
    :   Whether the field is displayed to customers

    `id: Literal['asc', 'desc']`
    :   Unique ticket field ID

    `label: Literal['asc', 'desc']`
    :   Display label for agents

    `label_for_customers: Literal['asc', 'desc']`
    :   Display label in the customer portal

    `name: Literal['asc', 'desc']`
    :   Name of the field

    `portal_cc: Literal['asc', 'desc']`
    :   Whether CC is enabled in the portal

    `portal_cc_to: Literal['asc', 'desc']`
    :   CC recipients scope (all or company)

    `position: Literal['asc', 'desc']`
    :   Position of the field in the form

    `required_for_agents: Literal['asc', 'desc']`
    :   Whether the field is required for agents

    `required_for_closure: Literal['asc', 'desc']`
    :   Whether the field is required for ticket closure

    `required_for_customers: Literal['asc', 'desc']`
    :   Whether the field is required for customers

    `type_: Literal['asc', 'desc']`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: Literal['asc', 'desc']`
    :   Field last update timestamp

<a id="TicketFieldsStringFilter"></a>

`TicketFieldsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `choices: str`
    :   Available choices for dropdown fields

    `created_at: str`
    :   Field creation timestamp

    `customers_can_edit: str`
    :   Whether customers can edit this field

    `default: str`
    :   Whether this is a default (non-custom) field

    `description: str`
    :   Description of the field

    `displayed_to_customers: str`
    :   Whether the field is displayed to customers

    `id: str`
    :   Unique ticket field ID

    `label: str`
    :   Display label for agents

    `label_for_customers: str`
    :   Display label in the customer portal

    `name: str`
    :   Name of the field

    `portal_cc: str`
    :   Whether CC is enabled in the portal

    `portal_cc_to: str`
    :   CC recipients scope (all or company)

    `position: str`
    :   Position of the field in the form

    `required_for_agents: str`
    :   Whether the field is required for agents

    `required_for_closure: str`
    :   Whether the field is required for ticket closure

    `required_for_customers: str`
    :   Whether the field is required for customers

    `type_: str`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: str`
    :   Field last update timestamp

<a id="TicketsAndCondition"></a>

`TicketsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.TicketsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketsAnyCondition"></a>

`TicketsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.freshdesk.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketsAnyValueFilter"></a>

`TicketsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_tickets_count: Any`
    :   Number of associated tickets

    `association_type: Any`
    :   Association type for parent/child tickets

    `cc_emails: Any`
    :   CC email addresses

    `company_id: Any`
    :   Company ID of the requester

    `created_at: Any`
    :   Ticket creation timestamp

    `custom_fields: Any`
    :   Custom fields associated with the ticket

    `description: Any`
    :   HTML content of the ticket

    `description_text: Any`
    :   Plain text content of the ticket

    `due_by: Any`
    :   Resolution due by timestamp

    `email_config_id: Any`
    :   ID of the email config used for the ticket

    `fr_due_by: Any`
    :   First response due by timestamp

    `fr_escalated: Any`
    :   Whether the first response time was breached

    `fwd_emails: Any`
    :   Forwarded email addresses

    `group_id: Any`
    :   ID of the group to which the ticket is assigned

    `id: Any`
    :   Unique ticket ID

    `is_escalated: Any`
    :   Whether the ticket is escalated

    `nr_due_by: Any`
    :   Next response due by timestamp

    `nr_escalated: Any`
    :   Whether the next response time was breached

    `priority: Any`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: Any`
    :   ID of the product associated with the ticket

    `reply_cc_emails: Any`
    :   Reply CC email addresses

    `requester: Any`
    :   Requester details including name, email, and contact info

    `requester_id: Any`
    :   ID of the requester

    `responder_id: Any`
    :   ID of the agent to whom the ticket is assigned

    `source: Any`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: Any`
    :   Whether the ticket is marked as spam

    `stats: Any`
    :   Ticket statistics including response and resolution times

    `status: Any`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: Any`
    :   Subject of the ticket

    `tags: Any`
    :   Tags associated with the ticket

    `ticket_cc_emails: Any`
    :   Ticket CC email addresses

    `to_emails: Any`
    :   To email addresses

    `type_: Any`
    :   Ticket type

    `updated_at: Any`
    :   Ticket last update timestamp

<a id="TicketsContainsCondition"></a>

`TicketsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketsEqCondition"></a>

`TicketsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsFuzzyCondition"></a>

`TicketsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsGetParams"></a>

`TicketsGetParams(*args, **kwargs)`
:   Parameters for tickets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TicketsGtCondition"></a>

`TicketsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsGteCondition"></a>

`TicketsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsInCondition"></a>

`TicketsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.freshdesk.types.TicketsInFilter`
    :   The type of the None singleton.

<a id="TicketsInFilter"></a>

`TicketsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_tickets_count: list[int]`
    :   Number of associated tickets

    `association_type: list[int]`
    :   Association type for parent/child tickets

    `cc_emails: list[list[typing.Any]]`
    :   CC email addresses

    `company_id: list[int]`
    :   Company ID of the requester

    `created_at: list[str]`
    :   Ticket creation timestamp

    `custom_fields: list[dict[str, typing.Any]]`
    :   Custom fields associated with the ticket

    `description: list[str]`
    :   HTML content of the ticket

    `description_text: list[str]`
    :   Plain text content of the ticket

    `due_by: list[str]`
    :   Resolution due by timestamp

    `email_config_id: list[int]`
    :   ID of the email config used for the ticket

    `fr_due_by: list[str]`
    :   First response due by timestamp

    `fr_escalated: list[bool]`
    :   Whether the first response time was breached

    `fwd_emails: list[list[typing.Any]]`
    :   Forwarded email addresses

    `group_id: list[int]`
    :   ID of the group to which the ticket is assigned

    `id: list[int]`
    :   Unique ticket ID

    `is_escalated: list[bool]`
    :   Whether the ticket is escalated

    `nr_due_by: list[str]`
    :   Next response due by timestamp

    `nr_escalated: list[bool]`
    :   Whether the next response time was breached

    `priority: list[int]`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: list[int]`
    :   ID of the product associated with the ticket

    `reply_cc_emails: list[list[typing.Any]]`
    :   Reply CC email addresses

    `requester: list[dict[str, typing.Any]]`
    :   Requester details including name, email, and contact info

    `requester_id: list[int]`
    :   ID of the requester

    `responder_id: list[int]`
    :   ID of the agent to whom the ticket is assigned

    `source: list[int]`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: list[bool]`
    :   Whether the ticket is marked as spam

    `stats: list[dict[str, typing.Any]]`
    :   Ticket statistics including response and resolution times

    `status: list[int]`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: list[str]`
    :   Subject of the ticket

    `tags: list[list[typing.Any]]`
    :   Tags associated with the ticket

    `ticket_cc_emails: list[list[typing.Any]]`
    :   Ticket CC email addresses

    `to_emails: list[list[typing.Any]]`
    :   To email addresses

    `type_: list[str]`
    :   Ticket type

    `updated_at: list[str]`
    :   Ticket last update timestamp

<a id="TicketsKeywordCondition"></a>

`TicketsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsLikeCondition"></a>

`TicketsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsListParams"></a>

`TicketsListParams(*args, **kwargs)`
:   Parameters for tickets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_by: str`
    :   The type of the None singleton.

    `order_type: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `updated_since: str`
    :   The type of the None singleton.

<a id="TicketsLtCondition"></a>

`TicketsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsLteCondition"></a>

`TicketsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsNeqCondition"></a>

`TicketsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsNotCondition"></a>

`TicketsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.freshdesk.types.TicketsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAnyCondition`
    :   The type of the None singleton.

<a id="TicketsOrCondition"></a>

`TicketsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.TicketsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketsSearchFilter"></a>

`TicketsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tickets search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_tickets_count: int | None`
    :   Number of associated tickets

    `association_type: int | None`
    :   Association type for parent/child tickets

    `cc_emails: list[typing.Any] | None`
    :   CC email addresses

    `company_id: int | None`
    :   Company ID of the requester

    `created_at: str | None`
    :   Ticket creation timestamp

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the ticket

    `description: str | None`
    :   HTML content of the ticket

    `description_text: str | None`
    :   Plain text content of the ticket

    `due_by: str | None`
    :   Resolution due by timestamp

    `email_config_id: int | None`
    :   ID of the email config used for the ticket

    `fr_due_by: str | None`
    :   First response due by timestamp

    `fr_escalated: bool | None`
    :   Whether the first response time was breached

    `fwd_emails: list[typing.Any] | None`
    :   Forwarded email addresses

    `group_id: int | None`
    :   ID of the group to which the ticket is assigned

    `id: int | None`
    :   Unique ticket ID

    `is_escalated: bool | None`
    :   Whether the ticket is escalated

    `nr_due_by: str | None`
    :   Next response due by timestamp

    `nr_escalated: bool | None`
    :   Whether the next response time was breached

    `priority: int | None`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: int | None`
    :   ID of the product associated with the ticket

    `reply_cc_emails: list[typing.Any] | None`
    :   Reply CC email addresses

    `requester: dict[str, typing.Any] | None`
    :   Requester details including name, email, and contact info

    `requester_id: int | None`
    :   ID of the requester

    `responder_id: int | None`
    :   ID of the agent to whom the ticket is assigned

    `source: int | None`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: bool | None`
    :   Whether the ticket is marked as spam

    `stats: dict[str, typing.Any] | None`
    :   Ticket statistics including response and resolution times

    `status: int | None`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: str | None`
    :   Subject of the ticket

    `tags: list[typing.Any] | None`
    :   Tags associated with the ticket

    `ticket_cc_emails: list[typing.Any] | None`
    :   Ticket CC email addresses

    `to_emails: list[typing.Any] | None`
    :   To email addresses

    `type_: str | None`
    :   Ticket type

    `updated_at: str | None`
    :   Ticket last update timestamp

<a id="TicketsSearchQuery"></a>

`TicketsSearchQuery(*args, **kwargs)`
:   Search query for tickets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.TicketsEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TicketsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.TicketsSortFilter]`
    :   The type of the None singleton.

<a id="TicketsSortFilter"></a>

`TicketsSortFilter(*args, **kwargs)`
:   Available fields for sorting tickets search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_tickets_count: Literal['asc', 'desc']`
    :   Number of associated tickets

    `association_type: Literal['asc', 'desc']`
    :   Association type for parent/child tickets

    `cc_emails: Literal['asc', 'desc']`
    :   CC email addresses

    `company_id: Literal['asc', 'desc']`
    :   Company ID of the requester

    `created_at: Literal['asc', 'desc']`
    :   Ticket creation timestamp

    `custom_fields: Literal['asc', 'desc']`
    :   Custom fields associated with the ticket

    `description: Literal['asc', 'desc']`
    :   HTML content of the ticket

    `description_text: Literal['asc', 'desc']`
    :   Plain text content of the ticket

    `due_by: Literal['asc', 'desc']`
    :   Resolution due by timestamp

    `email_config_id: Literal['asc', 'desc']`
    :   ID of the email config used for the ticket

    `fr_due_by: Literal['asc', 'desc']`
    :   First response due by timestamp

    `fr_escalated: Literal['asc', 'desc']`
    :   Whether the first response time was breached

    `fwd_emails: Literal['asc', 'desc']`
    :   Forwarded email addresses

    `group_id: Literal['asc', 'desc']`
    :   ID of the group to which the ticket is assigned

    `id: Literal['asc', 'desc']`
    :   Unique ticket ID

    `is_escalated: Literal['asc', 'desc']`
    :   Whether the ticket is escalated

    `nr_due_by: Literal['asc', 'desc']`
    :   Next response due by timestamp

    `nr_escalated: Literal['asc', 'desc']`
    :   Whether the next response time was breached

    `priority: Literal['asc', 'desc']`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: Literal['asc', 'desc']`
    :   ID of the product associated with the ticket

    `reply_cc_emails: Literal['asc', 'desc']`
    :   Reply CC email addresses

    `requester: Literal['asc', 'desc']`
    :   Requester details including name, email, and contact info

    `requester_id: Literal['asc', 'desc']`
    :   ID of the requester

    `responder_id: Literal['asc', 'desc']`
    :   ID of the agent to whom the ticket is assigned

    `source: Literal['asc', 'desc']`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: Literal['asc', 'desc']`
    :   Whether the ticket is marked as spam

    `stats: Literal['asc', 'desc']`
    :   Ticket statistics including response and resolution times

    `status: Literal['asc', 'desc']`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: Literal['asc', 'desc']`
    :   Subject of the ticket

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the ticket

    `ticket_cc_emails: Literal['asc', 'desc']`
    :   Ticket CC email addresses

    `to_emails: Literal['asc', 'desc']`
    :   To email addresses

    `type_: Literal['asc', 'desc']`
    :   Ticket type

    `updated_at: Literal['asc', 'desc']`
    :   Ticket last update timestamp

<a id="TicketsStringFilter"></a>

`TicketsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `associated_tickets_count: str`
    :   Number of associated tickets

    `association_type: str`
    :   Association type for parent/child tickets

    `cc_emails: str`
    :   CC email addresses

    `company_id: str`
    :   Company ID of the requester

    `created_at: str`
    :   Ticket creation timestamp

    `custom_fields: str`
    :   Custom fields associated with the ticket

    `description: str`
    :   HTML content of the ticket

    `description_text: str`
    :   Plain text content of the ticket

    `due_by: str`
    :   Resolution due by timestamp

    `email_config_id: str`
    :   ID of the email config used for the ticket

    `fr_due_by: str`
    :   First response due by timestamp

    `fr_escalated: str`
    :   Whether the first response time was breached

    `fwd_emails: str`
    :   Forwarded email addresses

    `group_id: str`
    :   ID of the group to which the ticket is assigned

    `id: str`
    :   Unique ticket ID

    `is_escalated: str`
    :   Whether the ticket is escalated

    `nr_due_by: str`
    :   Next response due by timestamp

    `nr_escalated: str`
    :   Whether the next response time was breached

    `priority: str`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: str`
    :   ID of the product associated with the ticket

    `reply_cc_emails: str`
    :   Reply CC email addresses

    `requester: str`
    :   Requester details including name, email, and contact info

    `requester_id: str`
    :   ID of the requester

    `responder_id: str`
    :   ID of the agent to whom the ticket is assigned

    `source: str`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: str`
    :   Whether the ticket is marked as spam

    `stats: str`
    :   Ticket statistics including response and resolution times

    `status: str`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: str`
    :   Subject of the ticket

    `tags: str`
    :   Tags associated with the ticket

    `ticket_cc_emails: str`
    :   Ticket CC email addresses

    `to_emails: str`
    :   To email addresses

    `type_: str`
    :   Ticket type

    `updated_at: str`
    :   Ticket last update timestamp

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

    `and: list[airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeEntriesAnyValueFilter"></a>

`TimeEntriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Any`
    :   ID of the agent

    `billable: Any`
    :   Whether the time entry is billable

    `company_id: Any`
    :   ID of the associated company

    `created_at: Any`
    :   Time entry creation timestamp

    `executed_at: Any`
    :   Execution timestamp

    `id: Any`
    :   Unique time entry ID

    `note: Any`
    :   Description of the time entry

    `start_time: Any`
    :   Start time of the timer

    `ticket_id: Any`
    :   ID of the associated ticket

    `time_spent: Any`
    :   Time spent in hh:mm format

    `timer_running: Any`
    :   Whether the timer is running

    `updated_at: Any`
    :   Time entry last update timestamp

<a id="TimeEntriesContainsCondition"></a>

`TimeEntriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeEntriesEqCondition"></a>

`TimeEntriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesFuzzyCondition"></a>

`TimeEntriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesGtCondition"></a>

`TimeEntriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesGteCondition"></a>

`TimeEntriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesInFilter`
    :   The type of the None singleton.

<a id="TimeEntriesInFilter"></a>

`TimeEntriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: list[int]`
    :   ID of the agent

    `billable: list[bool]`
    :   Whether the time entry is billable

    `company_id: list[int]`
    :   ID of the associated company

    `created_at: list[str]`
    :   Time entry creation timestamp

    `executed_at: list[str]`
    :   Execution timestamp

    `id: list[int]`
    :   Unique time entry ID

    `note: list[str]`
    :   Description of the time entry

    `start_time: list[str]`
    :   Start time of the timer

    `ticket_id: list[int]`
    :   ID of the associated ticket

    `time_spent: list[str]`
    :   Time spent in hh:mm format

    `timer_running: list[bool]`
    :   Whether the timer is running

    `updated_at: list[str]`
    :   Time entry last update timestamp

<a id="TimeEntriesKeywordCondition"></a>

`TimeEntriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesLikeCondition"></a>

`TimeEntriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesStringFilter`
    :   The type of the None singleton.

<a id="TimeEntriesListParams"></a>

`TimeEntriesListParams(*args, **kwargs)`
:   Parameters for time_entries.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TimeEntriesLtCondition"></a>

`TimeEntriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesLteCondition"></a>

`TimeEntriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSearchFilter`
    :   The type of the None singleton.

<a id="TimeEntriesNeqCondition"></a>

`TimeEntriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAnyCondition]`
    :   The type of the None singleton.

<a id="TimeEntriesSearchFilter"></a>

`TimeEntriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering time_entries search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: int | None`
    :   ID of the agent

    `billable: bool | None`
    :   Whether the time entry is billable

    `company_id: int | None`
    :   ID of the associated company

    `created_at: str | None`
    :   Time entry creation timestamp

    `executed_at: str | None`
    :   Execution timestamp

    `id: int | None`
    :   Unique time entry ID

    `note: str | None`
    :   Description of the time entry

    `start_time: str | None`
    :   Start time of the timer

    `ticket_id: int | None`
    :   ID of the associated ticket

    `time_spent: str | None`
    :   Time spent in hh:mm format

    `timer_running: bool | None`
    :   Whether the timer is running

    `updated_at: str | None`
    :   Time entry last update timestamp

<a id="TimeEntriesSearchQuery"></a>

`TimeEntriesSearchQuery(*args, **kwargs)`
:   Search query for time_entries entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesEqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNeqCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesGteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLtCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLteCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesInCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesLikeCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesFuzzyCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesKeywordCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesContainsCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesNotCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAndCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesOrCondition | airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.freshdesk.types.TimeEntriesSortFilter]`
    :   The type of the None singleton.

<a id="TimeEntriesSortFilter"></a>

`TimeEntriesSortFilter(*args, **kwargs)`
:   Available fields for sorting time_entries search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: Literal['asc', 'desc']`
    :   ID of the agent

    `billable: Literal['asc', 'desc']`
    :   Whether the time entry is billable

    `company_id: Literal['asc', 'desc']`
    :   ID of the associated company

    `created_at: Literal['asc', 'desc']`
    :   Time entry creation timestamp

    `executed_at: Literal['asc', 'desc']`
    :   Execution timestamp

    `id: Literal['asc', 'desc']`
    :   Unique time entry ID

    `note: Literal['asc', 'desc']`
    :   Description of the time entry

    `start_time: Literal['asc', 'desc']`
    :   Start time of the timer

    `ticket_id: Literal['asc', 'desc']`
    :   ID of the associated ticket

    `time_spent: Literal['asc', 'desc']`
    :   Time spent in hh:mm format

    `timer_running: Literal['asc', 'desc']`
    :   Whether the timer is running

    `updated_at: Literal['asc', 'desc']`
    :   Time entry last update timestamp

<a id="TimeEntriesStringFilter"></a>

`TimeEntriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: str`
    :   ID of the agent

    `billable: str`
    :   Whether the time entry is billable

    `company_id: str`
    :   ID of the associated company

    `created_at: str`
    :   Time entry creation timestamp

    `executed_at: str`
    :   Execution timestamp

    `id: str`
    :   Unique time entry ID

    `note: str`
    :   Description of the time entry

    `start_time: str`
    :   Start time of the timer

    `ticket_id: str`
    :   ID of the associated ticket

    `time_spent: str`
    :   Time spent in hh:mm format

    `timer_running: str`
    :   Whether the timer is running

    `updated_at: str`
    :   Time entry last update timestamp