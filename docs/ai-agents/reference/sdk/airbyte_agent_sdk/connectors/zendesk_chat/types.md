---
id: airbyte_agent_sdk-connectors-zendesk_chat-types
title: airbyte_agent_sdk.connectors.zendesk_chat.types
---

Module airbyte_agent_sdk.connectors.zendesk_chat.types
======================================================
Type definitions for zendesk-chat connector.

Classes
-------

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

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

`AgentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyValueFilter`
    :   The type of the None singleton.

`AgentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

`AgentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsStringFilter`
    :   The type of the None singleton.

`AgentsGetParams(*args, **kwargs)`
:   Parameters for agents.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_id: str`
    :   The type of the None singleton.

`AgentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

`AgentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

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

`AgentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsStringFilter`
    :   The type of the None singleton.

`AgentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsStringFilter`
    :   The type of the None singleton.

`AgentsListParams(*args, **kwargs)`
:   Parameters for agents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

`AgentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

`AgentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

`AgentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSearchFilter`
    :   The type of the None singleton.

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

`AgentsSearchQuery(*args, **kwargs)`
:   Search query for agents entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.AgentsSortFilter]`
    :   The type of the None singleton.

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

`BansGetParams(*args, **kwargs)`
:   Parameters for bans.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ban_id: str`
    :   The type of the None singleton.

`BansListParams(*args, **kwargs)`
:   Parameters for bans.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `since_id: int`
    :   The type of the None singleton.

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

`ChatsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyValueFilter`
    :   The type of the None singleton.

`ChatsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

`ChatsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsStringFilter`
    :   The type of the None singleton.

`ChatsGetParams(*args, **kwargs)`
:   Parameters for chats.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `chat_id: str`
    :   The type of the None singleton.

`ChatsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

`ChatsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

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

`ChatsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsStringFilter`
    :   The type of the None singleton.

`ChatsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsStringFilter`
    :   The type of the None singleton.

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

`ChatsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

`ChatsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

`ChatsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSearchFilter`
    :   The type of the None singleton.

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

`ChatsSearchQuery(*args, **kwargs)`
:   Search query for chats entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ChatsSortFilter]`
    :   The type of the None singleton.

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

`DepartmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyValueFilter`
    :   The type of the None singleton.

`DepartmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

`DepartmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsStringFilter`
    :   The type of the None singleton.

`DepartmentsGetParams(*args, **kwargs)`
:   Parameters for departments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `department_id: str`
    :   The type of the None singleton.

`DepartmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

`DepartmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

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

`DepartmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsStringFilter`
    :   The type of the None singleton.

`DepartmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsStringFilter`
    :   The type of the None singleton.

`DepartmentsListParams(*args, **kwargs)`
:   Parameters for departments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`DepartmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

`DepartmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

`DepartmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSearchFilter`
    :   The type of the None singleton.

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

`DepartmentsSearchQuery(*args, **kwargs)`
:   Search query for departments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.DepartmentsSortFilter]`
    :   The type of the None singleton.

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

`GoalsGetParams(*args, **kwargs)`
:   Parameters for goals.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `goal_id: str`
    :   The type of the None singleton.

`GoalsListParams(*args, **kwargs)`
:   Parameters for goals.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`RolesGetParams(*args, **kwargs)`
:   Parameters for roles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `role_id: str`
    :   The type of the None singleton.

`RolesListParams(*args, **kwargs)`
:   Parameters for roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`RoutingSettingsGetParams(*args, **kwargs)`
:   Parameters for routing_settings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

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

`ShortcutsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyValueFilter`
    :   The type of the None singleton.

`ShortcutsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

`ShortcutsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsStringFilter`
    :   The type of the None singleton.

`ShortcutsGetParams(*args, **kwargs)`
:   Parameters for shortcuts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `shortcut_id: str`
    :   The type of the None singleton.

`ShortcutsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

`ShortcutsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

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

`ShortcutsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsStringFilter`
    :   The type of the None singleton.

`ShortcutsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsStringFilter`
    :   The type of the None singleton.

`ShortcutsListParams(*args, **kwargs)`
:   Parameters for shortcuts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`ShortcutsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

`ShortcutsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

`ShortcutsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSearchFilter`
    :   The type of the None singleton.

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

`ShortcutsSearchQuery(*args, **kwargs)`
:   Search query for shortcuts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.ShortcutsSortFilter]`
    :   The type of the None singleton.

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

`SkillsGetParams(*args, **kwargs)`
:   Parameters for skills.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `skill_id: str`
    :   The type of the None singleton.

`SkillsListParams(*args, **kwargs)`
:   Parameters for skills.list operation

    ### Ancestors (in MRO)

    * builtins.dict

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

`TriggersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyValueFilter`
    :   The type of the None singleton.

`TriggersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

`TriggersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersStringFilter`
    :   The type of the None singleton.

`TriggersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

`TriggersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

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

`TriggersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersStringFilter`
    :   The type of the None singleton.

`TriggersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersStringFilter`
    :   The type of the None singleton.

`TriggersListParams(*args, **kwargs)`
:   Parameters for triggers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`TriggersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

`TriggersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

`TriggersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSearchFilter`
    :   The type of the None singleton.

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

`TriggersSearchQuery(*args, **kwargs)`
:   Search query for triggers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_chat.types.TriggersSortFilter]`
    :   The type of the None singleton.

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