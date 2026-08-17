---
id: airbyte_agent_sdk-connectors-zendesk_chat-types
title: airbyte_agent_sdk.connectors.zendesk_chat.types
---

Module airbyte_agent_sdk.connectors.zendesk_chat.types
======================================================
Type definitions for zendesk-chat connector.

Classes
-------

<a id="AccountsGetParams"></a>

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="AgentTimelineListParams"></a>

`AgentTimelineListParams(*args, **kwargs)`
:   Parameters for agent_timeline.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `start_time: int`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsAnyValueFilter"></a>

`AgentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_date: Any`
    :   When agent was created

    `departments: Any`
    :   Department IDs agent belongs to

    `display_name: Any`
    :   Agent display name

    `email: Any`
    :   Agent email address

    `enabled: Any`
    :   Whether agent is enabled

    `first_name: Any`
    :   Agent first name

    `id: Any`
    :   Unique agent identifier

    `last_name: Any`
    :   Agent last name

    `role_id: Any`
    :   Agent role ID

<a id="AgentsContainsCondition"></a>

`AgentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyValueFilter`
    :   The type of the None singleton.

<a id="AgentsEqCondition"></a>

`AgentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsFuzzyCondition"></a>

`AgentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsStringFilter`
    :   The type of the None singleton.

<a id="AgentsGetParams"></a>

`AgentsGetParams(*args, **kwargs)`
:   Parameters for agents.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: str`
    :   The type of the None singleton.

<a id="AgentsGtCondition"></a>

`AgentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsGteCondition"></a>

`AgentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsInFilter`
    :   The type of the None singleton.

<a id="AgentsInFilter"></a>

`AgentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_date: list[str]`
    :   When agent was created

    `departments: list[list[typing.Any]]`
    :   Department IDs agent belongs to

    `display_name: list[str]`
    :   Agent display name

    `email: list[str]`
    :   Agent email address

    `enabled: list[bool]`
    :   Whether agent is enabled

    `first_name: list[str]`
    :   Agent first name

    `id: list[int]`
    :   Unique agent identifier

    `last_name: list[str]`
    :   Agent last name

    `role_id: list[int]`
    :   Agent role ID

<a id="AgentsKeywordCondition"></a>

`AgentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsStringFilter`
    :   The type of the None singleton.

<a id="AgentsLikeCondition"></a>

`AgentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsStringFilter`
    :   The type of the None singleton.

<a id="AgentsListParams"></a>

`AgentsListParams(*args, **kwargs)`
:   Parameters for agents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="AgentsLtCondition"></a>

`AgentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsLteCondition"></a>

`AgentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

<a id="AgentsNeqCondition"></a>

`AgentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyCondition]`
    :   The type of the None singleton.

<a id="AgentsSearchFilter"></a>

`AgentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering agents search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_date: str | None`
    :   When agent was created

    `departments: list[typing.Any] | None`
    :   Department IDs agent belongs to

    `display_name: str | None`
    :   Agent display name

    `email: str | None`
    :   Agent email address

    `enabled: bool | None`
    :   Whether agent is enabled

    `first_name: str | None`
    :   Agent first name

    `id: int`
    :   Unique agent identifier

    `last_name: str | None`
    :   Agent last name

    `role_id: int | None`
    :   Agent role ID

<a id="AgentsSearchQuery"></a>

`AgentsSearchQuery(*args, **kwargs)`
:   Search query for agents entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSortFilter]`
    :   The type of the None singleton.

<a id="AgentsSortFilter"></a>

`AgentsSortFilter(*args, **kwargs)`
:   Available fields for sorting agents search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_date: Literal['asc', 'desc']`
    :   When agent was created

    `departments: Literal['asc', 'desc']`
    :   Department IDs agent belongs to

    `display_name: Literal['asc', 'desc']`
    :   Agent display name

    `email: Literal['asc', 'desc']`
    :   Agent email address

    `enabled: Literal['asc', 'desc']`
    :   Whether agent is enabled

    `first_name: Literal['asc', 'desc']`
    :   Agent first name

    `id: Literal['asc', 'desc']`
    :   Unique agent identifier

    `last_name: Literal['asc', 'desc']`
    :   Agent last name

    `role_id: Literal['asc', 'desc']`
    :   Agent role ID

<a id="AgentsStringFilter"></a>

`AgentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_date: str`
    :   When agent was created

    `departments: str`
    :   Department IDs agent belongs to

    `display_name: str`
    :   Agent display name

    `email: str`
    :   Agent email address

    `enabled: str`
    :   Whether agent is enabled

    `first_name: str`
    :   Agent first name

    `id: str`
    :   Unique agent identifier

    `last_name: str`
    :   Agent last name

    `role_id: str`
    :   Agent role ID

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

<a id="BansGetParams"></a>

`BansGetParams(*args, **kwargs)`
:   Parameters for bans.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ban_id: str`
    :   The type of the None singleton.

<a id="BansListParams"></a>

`BansListParams(*args, **kwargs)`
:   Parameters for bans.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

<a id="ChatsAndCondition"></a>

`ChatsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyCondition]`
    :   The type of the None singleton.

<a id="ChatsAnyCondition"></a>

`ChatsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyValueFilter`
    :   The type of the None singleton.

<a id="ChatsAnyValueFilter"></a>

`ChatsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_ids: Any`
    :   IDs of agents in chat

    `department_id: Any`
    :   Department ID

    `department_name: Any`
    :   Department name

    `duration: Any`
    :   Chat duration in seconds

    `id: Any`
    :   Unique chat identifier

    `missed: Any`
    :   Whether chat was missed

    `rating: Any`
    :   Satisfaction rating

    `timestamp: Any`
    :   Chat start timestamp

    `update_timestamp: Any`
    :   Last update timestamp

<a id="ChatsContainsCondition"></a>

`ChatsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyValueFilter`
    :   The type of the None singleton.

<a id="ChatsEqCondition"></a>

`ChatsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

<a id="ChatsFuzzyCondition"></a>

`ChatsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsStringFilter`
    :   The type of the None singleton.

<a id="ChatsGetParams"></a>

`ChatsGetParams(*args, **kwargs)`
:   Parameters for chats.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `chat_id: str`
    :   The type of the None singleton.

<a id="ChatsGtCondition"></a>

`ChatsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

<a id="ChatsGteCondition"></a>

`ChatsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

<a id="ChatsInCondition"></a>

`ChatsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsInFilter`
    :   The type of the None singleton.

<a id="ChatsInFilter"></a>

`ChatsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_ids: list[list[typing.Any]]`
    :   IDs of agents in chat

    `department_id: list[int]`
    :   Department ID

    `department_name: list[str]`
    :   Department name

    `duration: list[int]`
    :   Chat duration in seconds

    `id: list[str]`
    :   Unique chat identifier

    `missed: list[bool]`
    :   Whether chat was missed

    `rating: list[str]`
    :   Satisfaction rating

    `timestamp: list[str]`
    :   Chat start timestamp

    `update_timestamp: list[str]`
    :   Last update timestamp

<a id="ChatsKeywordCondition"></a>

`ChatsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsStringFilter`
    :   The type of the None singleton.

<a id="ChatsLikeCondition"></a>

`ChatsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsStringFilter`
    :   The type of the None singleton.

<a id="ChatsListParams"></a>

`ChatsListParams(*args, **kwargs)`
:   Parameters for chats.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `start_time: int`
    :   The type of the None singleton.

<a id="ChatsLtCondition"></a>

`ChatsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

<a id="ChatsLteCondition"></a>

`ChatsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

<a id="ChatsNeqCondition"></a>

`ChatsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

<a id="ChatsNotCondition"></a>

`ChatsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyCondition`
    :   The type of the None singleton.

<a id="ChatsOrCondition"></a>

`ChatsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyCondition]`
    :   The type of the None singleton.

<a id="ChatsSearchFilter"></a>

`ChatsSearchFilter(*args, **kwargs)`
:   Available fields for filtering chats search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_ids: list[typing.Any] | None`
    :   IDs of agents in chat

    `department_id: int | None`
    :   Department ID

    `department_name: str | None`
    :   Department name

    `duration: int | None`
    :   Chat duration in seconds

    `id: str`
    :   Unique chat identifier

    `missed: bool | None`
    :   Whether chat was missed

    `rating: str | None`
    :   Satisfaction rating

    `timestamp: str | None`
    :   Chat start timestamp

    `update_timestamp: str | None`
    :   Last update timestamp

<a id="ChatsSearchQuery"></a>

`ChatsSearchQuery(*args, **kwargs)`
:   Search query for chats entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSortFilter]`
    :   The type of the None singleton.

<a id="ChatsSortFilter"></a>

`ChatsSortFilter(*args, **kwargs)`
:   Available fields for sorting chats search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_ids: Literal['asc', 'desc']`
    :   IDs of agents in chat

    `department_id: Literal['asc', 'desc']`
    :   Department ID

    `department_name: Literal['asc', 'desc']`
    :   Department name

    `duration: Literal['asc', 'desc']`
    :   Chat duration in seconds

    `id: Literal['asc', 'desc']`
    :   Unique chat identifier

    `missed: Literal['asc', 'desc']`
    :   Whether chat was missed

    `rating: Literal['asc', 'desc']`
    :   Satisfaction rating

    `timestamp: Literal['asc', 'desc']`
    :   Chat start timestamp

    `update_timestamp: Literal['asc', 'desc']`
    :   Last update timestamp

<a id="ChatsStringFilter"></a>

`ChatsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_ids: str`
    :   IDs of agents in chat

    `department_id: str`
    :   Department ID

    `department_name: str`
    :   Department name

    `duration: str`
    :   Chat duration in seconds

    `id: str`
    :   Unique chat identifier

    `missed: str`
    :   Whether chat was missed

    `rating: str`
    :   Satisfaction rating

    `timestamp: str`
    :   Chat start timestamp

    `update_timestamp: str`
    :   Last update timestamp

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

    `and: list[airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="DepartmentsAnyValueFilter"></a>

`DepartmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: Any`
    :   Whether department is enabled

    `id: Any`
    :   Department ID

    `members: Any`
    :   Agent IDs in department

    `name: Any`
    :   Department name

<a id="DepartmentsContainsCondition"></a>

`DepartmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="DepartmentsEqCondition"></a>

`DepartmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsFuzzyCondition"></a>

`DepartmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsGetParams"></a>

`DepartmentsGetParams(*args, **kwargs)`
:   Parameters for departments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `department_id: str`
    :   The type of the None singleton.

<a id="DepartmentsGtCondition"></a>

`DepartmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsGteCondition"></a>

`DepartmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsInFilter`
    :   The type of the None singleton.

<a id="DepartmentsInFilter"></a>

`DepartmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: list[bool]`
    :   Whether department is enabled

    `id: list[int]`
    :   Department ID

    `members: list[list[typing.Any]]`
    :   Agent IDs in department

    `name: list[str]`
    :   Department name

<a id="DepartmentsKeywordCondition"></a>

`DepartmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsLikeCondition"></a>

`DepartmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsStringFilter`
    :   The type of the None singleton.

<a id="DepartmentsListParams"></a>

`DepartmentsListParams(*args, **kwargs)`
:   Parameters for departments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DepartmentsLtCondition"></a>

`DepartmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsLteCondition"></a>

`DepartmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

<a id="DepartmentsNeqCondition"></a>

`DepartmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyCondition]`
    :   The type of the None singleton.

<a id="DepartmentsSearchFilter"></a>

`DepartmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering departments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: bool | None`
    :   Whether department is enabled

    `id: int`
    :   Department ID

    `members: list[typing.Any] | None`
    :   Agent IDs in department

    `name: str | None`
    :   Department name

<a id="DepartmentsSearchQuery"></a>

`DepartmentsSearchQuery(*args, **kwargs)`
:   Search query for departments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSortFilter]`
    :   The type of the None singleton.

<a id="DepartmentsSortFilter"></a>

`DepartmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting departments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: Literal['asc', 'desc']`
    :   Whether department is enabled

    `id: Literal['asc', 'desc']`
    :   Department ID

    `members: Literal['asc', 'desc']`
    :   Agent IDs in department

    `name: Literal['asc', 'desc']`
    :   Department name

<a id="DepartmentsStringFilter"></a>

`DepartmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: str`
    :   Whether department is enabled

    `id: str`
    :   Department ID

    `members: str`
    :   Agent IDs in department

    `name: str`
    :   Department name

<a id="GoalsGetParams"></a>

`GoalsGetParams(*args, **kwargs)`
:   Parameters for goals.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `goal_id: str`
    :   The type of the None singleton.

<a id="GoalsListParams"></a>

`GoalsListParams(*args, **kwargs)`
:   Parameters for goals.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="RolesGetParams"></a>

`RolesGetParams(*args, **kwargs)`
:   Parameters for roles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `role_id: str`
    :   The type of the None singleton.

<a id="RolesListParams"></a>

`RolesListParams(*args, **kwargs)`
:   Parameters for roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="RoutingSettingsGetParams"></a>

`RoutingSettingsGetParams(*args, **kwargs)`
:   Parameters for routing_settings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ShortcutsAndCondition"></a>

`ShortcutsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyCondition]`
    :   The type of the None singleton.

<a id="ShortcutsAnyCondition"></a>

`ShortcutsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyValueFilter`
    :   The type of the None singleton.

<a id="ShortcutsAnyValueFilter"></a>

`ShortcutsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Shortcut ID

    `message: Any`
    :   Shortcut message content

    `name: Any`
    :   Shortcut name/trigger

    `tags: Any`
    :   Tags applied when shortcut is used

<a id="ShortcutsContainsCondition"></a>

`ShortcutsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyValueFilter`
    :   The type of the None singleton.

<a id="ShortcutsEqCondition"></a>

`ShortcutsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

<a id="ShortcutsFuzzyCondition"></a>

`ShortcutsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsStringFilter`
    :   The type of the None singleton.

<a id="ShortcutsGetParams"></a>

`ShortcutsGetParams(*args, **kwargs)`
:   Parameters for shortcuts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `shortcut_id: str`
    :   The type of the None singleton.

<a id="ShortcutsGtCondition"></a>

`ShortcutsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

<a id="ShortcutsGteCondition"></a>

`ShortcutsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

<a id="ShortcutsInCondition"></a>

`ShortcutsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsInFilter`
    :   The type of the None singleton.

<a id="ShortcutsInFilter"></a>

`ShortcutsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[int]`
    :   Shortcut ID

    `message: list[str]`
    :   Shortcut message content

    `name: list[str]`
    :   Shortcut name/trigger

    `tags: list[list[typing.Any]]`
    :   Tags applied when shortcut is used

<a id="ShortcutsKeywordCondition"></a>

`ShortcutsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsStringFilter`
    :   The type of the None singleton.

<a id="ShortcutsLikeCondition"></a>

`ShortcutsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsStringFilter`
    :   The type of the None singleton.

<a id="ShortcutsListParams"></a>

`ShortcutsListParams(*args, **kwargs)`
:   Parameters for shortcuts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ShortcutsLtCondition"></a>

`ShortcutsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

<a id="ShortcutsLteCondition"></a>

`ShortcutsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

<a id="ShortcutsNeqCondition"></a>

`ShortcutsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

<a id="ShortcutsNotCondition"></a>

`ShortcutsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyCondition`
    :   The type of the None singleton.

<a id="ShortcutsOrCondition"></a>

`ShortcutsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyCondition]`
    :   The type of the None singleton.

<a id="ShortcutsSearchFilter"></a>

`ShortcutsSearchFilter(*args, **kwargs)`
:   Available fields for filtering shortcuts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int`
    :   Shortcut ID

    `message: str | None`
    :   Shortcut message content

    `name: str | None`
    :   Shortcut name/trigger

    `tags: list[typing.Any] | None`
    :   Tags applied when shortcut is used

<a id="ShortcutsSearchQuery"></a>

`ShortcutsSearchQuery(*args, **kwargs)`
:   Search query for shortcuts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSortFilter]`
    :   The type of the None singleton.

<a id="ShortcutsSortFilter"></a>

`ShortcutsSortFilter(*args, **kwargs)`
:   Available fields for sorting shortcuts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Shortcut ID

    `message: Literal['asc', 'desc']`
    :   Shortcut message content

    `name: Literal['asc', 'desc']`
    :   Shortcut name/trigger

    `tags: Literal['asc', 'desc']`
    :   Tags applied when shortcut is used

<a id="ShortcutsStringFilter"></a>

`ShortcutsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Shortcut ID

    `message: str`
    :   Shortcut message content

    `name: str`
    :   Shortcut name/trigger

    `tags: str`
    :   Tags applied when shortcut is used

<a id="SkillsGetParams"></a>

`SkillsGetParams(*args, **kwargs)`
:   Parameters for skills.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `skill_id: str`
    :   The type of the None singleton.

<a id="SkillsListParams"></a>

`SkillsListParams(*args, **kwargs)`
:   Parameters for skills.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="TriggersAndCondition"></a>

`TriggersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyCondition]`
    :   The type of the None singleton.

<a id="TriggersAnyCondition"></a>

`TriggersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyValueFilter`
    :   The type of the None singleton.

<a id="TriggersAnyValueFilter"></a>

`TriggersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: Any`
    :   Whether trigger is enabled

    `id: Any`
    :   Trigger ID

    `name: Any`
    :   Trigger name

<a id="TriggersContainsCondition"></a>

`TriggersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyValueFilter`
    :   The type of the None singleton.

<a id="TriggersEqCondition"></a>

`TriggersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersFuzzyCondition"></a>

`TriggersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersStringFilter`
    :   The type of the None singleton.

<a id="TriggersGtCondition"></a>

`TriggersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersGteCondition"></a>

`TriggersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersInCondition"></a>

`TriggersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersInFilter`
    :   The type of the None singleton.

<a id="TriggersInFilter"></a>

`TriggersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: list[bool]`
    :   Whether trigger is enabled

    `id: list[int]`
    :   Trigger ID

    `name: list[str]`
    :   Trigger name

<a id="TriggersKeywordCondition"></a>

`TriggersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersStringFilter`
    :   The type of the None singleton.

<a id="TriggersLikeCondition"></a>

`TriggersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersStringFilter`
    :   The type of the None singleton.

<a id="TriggersListParams"></a>

`TriggersListParams(*args, **kwargs)`
:   Parameters for triggers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="TriggersLtCondition"></a>

`TriggersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersLteCondition"></a>

`TriggersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersNeqCondition"></a>

`TriggersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersNotCondition"></a>

`TriggersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyCondition`
    :   The type of the None singleton.

<a id="TriggersOrCondition"></a>

`TriggersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyCondition]`
    :   The type of the None singleton.

<a id="TriggersSearchFilter"></a>

`TriggersSearchFilter(*args, **kwargs)`
:   Available fields for filtering triggers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: bool | None`
    :   Whether trigger is enabled

    `id: int`
    :   Trigger ID

    `name: str | None`
    :   Trigger name

<a id="TriggersSearchQuery"></a>

`TriggersSearchQuery(*args, **kwargs)`
:   Search query for triggers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSortFilter]`
    :   The type of the None singleton.

<a id="TriggersSortFilter"></a>

`TriggersSortFilter(*args, **kwargs)`
:   Available fields for sorting triggers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: Literal['asc', 'desc']`
    :   Whether trigger is enabled

    `id: Literal['asc', 'desc']`
    :   Trigger ID

    `name: Literal['asc', 'desc']`
    :   Trigger name

<a id="TriggersStringFilter"></a>

`TriggersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: str`
    :   Whether trigger is enabled

    `id: str`
    :   Trigger ID

    `name: str`
    :   Trigger name