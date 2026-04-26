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

<a id="CompaniesGetParams"></a>

`CompaniesGetParams(*args, **kwargs)`
:   Parameters for companies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

<a id="ContactsGetParams"></a>

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

<a id="RolesGetParams"></a>

`RolesGetParams(*args, **kwargs)`
:   Parameters for roles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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