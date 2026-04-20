---
id: airbyte_agent_sdk-connectors-monday-types
title: airbyte_agent_sdk.connectors.monday.types
---

Module airbyte_agent_sdk.connectors.monday.types
================================================
Type definitions for monday connector.

Classes
-------

`ActivityLogsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.ActivityLogsEqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsInCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNotCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAndCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsOrCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAnyCondition]`
    :   The type of the None singleton.

`ActivityLogsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.ActivityLogsAnyValueFilter`
    :   The type of the None singleton.

`ActivityLogsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: Any`
    :   Board ID the activity belongs to

    `created_at: Any`
    :   When the activity occurred

    `created_at_int: Any`
    :   When the activity occurred (Unix timestamp)

    `data: Any`
    :   Event data (JSON string)

    `entity: Any`
    :   Entity type that was affected

    `event: Any`
    :   Event type

    `id: Any`
    :   Unique activity log identifier

    `pulse_id: Any`
    :   Item (pulse) ID the activity belongs to

    `user_id: Any`
    :   ID of the user who performed the action

`ActivityLogsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.ActivityLogsAnyValueFilter`
    :   The type of the None singleton.

`ActivityLogsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.ActivityLogsSearchFilter`
    :   The type of the None singleton.

`ActivityLogsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.ActivityLogsStringFilter`
    :   The type of the None singleton.

`ActivityLogsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.ActivityLogsSearchFilter`
    :   The type of the None singleton.

`ActivityLogsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.ActivityLogsSearchFilter`
    :   The type of the None singleton.

`ActivityLogsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.ActivityLogsInFilter`
    :   The type of the None singleton.

`ActivityLogsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: list[int]`
    :   Board ID the activity belongs to

    `created_at: list[str]`
    :   When the activity occurred

    `created_at_int: list[int]`
    :   When the activity occurred (Unix timestamp)

    `data: list[str]`
    :   Event data (JSON string)

    `entity: list[str]`
    :   Entity type that was affected

    `event: list[str]`
    :   Event type

    `id: list[str]`
    :   Unique activity log identifier

    `pulse_id: list[int]`
    :   Item (pulse) ID the activity belongs to

    `user_id: list[str]`
    :   ID of the user who performed the action

`ActivityLogsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.ActivityLogsStringFilter`
    :   The type of the None singleton.

`ActivityLogsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.ActivityLogsStringFilter`
    :   The type of the None singleton.

`ActivityLogsListParams(*args, **kwargs)`
:   Parameters for activity_logs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: str`
    :   The type of the None singleton.

`ActivityLogsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.ActivityLogsSearchFilter`
    :   The type of the None singleton.

`ActivityLogsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.ActivityLogsSearchFilter`
    :   The type of the None singleton.

`ActivityLogsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.ActivityLogsSearchFilter`
    :   The type of the None singleton.

`ActivityLogsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.ActivityLogsEqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsInCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNotCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAndCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsOrCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAnyCondition`
    :   The type of the None singleton.

`ActivityLogsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.ActivityLogsEqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsInCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNotCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAndCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsOrCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAnyCondition]`
    :   The type of the None singleton.

`ActivityLogsSearchFilter(*args, **kwargs)`
:   Available fields for filtering activity_logs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: int | None`
    :   Board ID the activity belongs to

    `created_at: str | None`
    :   When the activity occurred

    `created_at_int: int | None`
    :   When the activity occurred (Unix timestamp)

    `data: str | None`
    :   Event data (JSON string)

    `entity: str | None`
    :   Entity type that was affected

    `event: str | None`
    :   Event type

    `id: str | None`
    :   Unique activity log identifier

    `pulse_id: int | None`
    :   Item (pulse) ID the activity belongs to

    `user_id: str | None`
    :   ID of the user who performed the action

`ActivityLogsSearchQuery(*args, **kwargs)`
:   Search query for activity_logs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.ActivityLogsEqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsGteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLtCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLteCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsInCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsNotCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAndCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsOrCondition | airbyte_agent_sdk.connectors.monday.types.ActivityLogsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.ActivityLogsSortFilter]`
    :   The type of the None singleton.

`ActivityLogsSortFilter(*args, **kwargs)`
:   Available fields for sorting activity_logs search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: Literal['asc', 'desc']`
    :   Board ID the activity belongs to

    `created_at: Literal['asc', 'desc']`
    :   When the activity occurred

    `created_at_int: Literal['asc', 'desc']`
    :   When the activity occurred (Unix timestamp)

    `data: Literal['asc', 'desc']`
    :   Event data (JSON string)

    `entity: Literal['asc', 'desc']`
    :   Entity type that was affected

    `event: Literal['asc', 'desc']`
    :   Event type

    `id: Literal['asc', 'desc']`
    :   Unique activity log identifier

    `pulse_id: Literal['asc', 'desc']`
    :   Item (pulse) ID the activity belongs to

    `user_id: Literal['asc', 'desc']`
    :   ID of the user who performed the action

`ActivityLogsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: str`
    :   Board ID the activity belongs to

    `created_at: str`
    :   When the activity occurred

    `created_at_int: str`
    :   When the activity occurred (Unix timestamp)

    `data: str`
    :   Event data (JSON string)

    `entity: str`
    :   Entity type that was affected

    `event: str`
    :   Event type

    `id: str`
    :   Unique activity log identifier

    `pulse_id: str`
    :   Item (pulse) ID the activity belongs to

    `user_id: str`
    :   ID of the user who performed the action

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

`BoardsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.BoardsEqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsInCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.monday.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNotCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAndCondition | airbyte_agent_sdk.connectors.monday.types.BoardsOrCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAnyCondition]`
    :   The type of the None singleton.

`BoardsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.BoardsAnyValueFilter`
    :   The type of the None singleton.

`BoardsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_kind: Any`
    :   Board kind (public, private, share)

    `columns: Any`
    :   Board columns

    `communication: Any`
    :   Board communication value

    `creator: Any`
    :   Board creator

    `description: Any`
    :   Board description

    `groups: Any`
    :   Board groups

    `id: Any`
    :   Unique board identifier

    `name: Any`
    :   Board name

    `owners: Any`
    :   Board owners

    `permissions: Any`
    :   Board permissions

    `state: Any`
    :   Board state (active, archived, deleted)

    `subscribers: Any`
    :   Board subscribers

    `tags: Any`
    :   Board tags

    `top_group: Any`
    :   Top group on the board

    `type_: Any`
    :   Board type

    `updated_at: Any`
    :   When the board was last updated

    `updated_at_int: Any`
    :   When the board was last updated (Unix timestamp)

    `updates: Any`
    :   Board updates

    `views: Any`
    :   Board views

    `workspace: Any`
    :   Workspace the board belongs to

`BoardsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.BoardsAnyValueFilter`
    :   The type of the None singleton.

`BoardsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.BoardsStringFilter`
    :   The type of the None singleton.

`BoardsGetParams(*args, **kwargs)`
:   Parameters for boards.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`BoardsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.BoardsInFilter`
    :   The type of the None singleton.

`BoardsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_kind: list[str]`
    :   Board kind (public, private, share)

    `columns: list[list[typing.Any]]`
    :   Board columns

    `communication: list[str]`
    :   Board communication value

    `creator: list[dict[str, typing.Any]]`
    :   Board creator

    `description: list[str]`
    :   Board description

    `groups: list[list[typing.Any]]`
    :   Board groups

    `id: list[str]`
    :   Unique board identifier

    `name: list[str]`
    :   Board name

    `owners: list[list[typing.Any]]`
    :   Board owners

    `permissions: list[str]`
    :   Board permissions

    `state: list[str]`
    :   Board state (active, archived, deleted)

    `subscribers: list[list[typing.Any]]`
    :   Board subscribers

    `tags: list[list[typing.Any]]`
    :   Board tags

    `top_group: list[dict[str, typing.Any]]`
    :   Top group on the board

    `type_: list[str]`
    :   Board type

    `updated_at: list[str]`
    :   When the board was last updated

    `updated_at_int: list[int]`
    :   When the board was last updated (Unix timestamp)

    `updates: list[list[typing.Any]]`
    :   Board updates

    `views: list[list[typing.Any]]`
    :   Board views

    `workspace: list[dict[str, typing.Any]]`
    :   Workspace the board belongs to

`BoardsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.BoardsStringFilter`
    :   The type of the None singleton.

`BoardsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.BoardsStringFilter`
    :   The type of the None singleton.

`BoardsListParams(*args, **kwargs)`
:   Parameters for boards.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`BoardsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.BoardsSearchFilter`
    :   The type of the None singleton.

`BoardsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.BoardsEqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsInCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.monday.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNotCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAndCondition | airbyte_agent_sdk.connectors.monday.types.BoardsOrCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAnyCondition`
    :   The type of the None singleton.

`BoardsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.BoardsEqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsInCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.monday.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNotCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAndCondition | airbyte_agent_sdk.connectors.monday.types.BoardsOrCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAnyCondition]`
    :   The type of the None singleton.

`BoardsSearchFilter(*args, **kwargs)`
:   Available fields for filtering boards search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_kind: str | None`
    :   Board kind (public, private, share)

    `columns: list[typing.Any] | None`
    :   Board columns

    `communication: str | None`
    :   Board communication value

    `creator: dict[str, typing.Any] | None`
    :   Board creator

    `description: str | None`
    :   Board description

    `groups: list[typing.Any] | None`
    :   Board groups

    `id: str | None`
    :   Unique board identifier

    `name: str | None`
    :   Board name

    `owners: list[typing.Any] | None`
    :   Board owners

    `permissions: str | None`
    :   Board permissions

    `state: str | None`
    :   Board state (active, archived, deleted)

    `subscribers: list[typing.Any] | None`
    :   Board subscribers

    `tags: list[typing.Any] | None`
    :   Board tags

    `top_group: dict[str, typing.Any] | None`
    :   Top group on the board

    `type_: str | None`
    :   Board type

    `updated_at: str | None`
    :   When the board was last updated

    `updated_at_int: int | None`
    :   When the board was last updated (Unix timestamp)

    `updates: list[typing.Any] | None`
    :   Board updates

    `views: list[typing.Any] | None`
    :   Board views

    `workspace: dict[str, typing.Any] | None`
    :   Workspace the board belongs to

`BoardsSearchQuery(*args, **kwargs)`
:   Search query for boards entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.BoardsEqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNeqCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsGteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLtCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLteCondition | airbyte_agent_sdk.connectors.monday.types.BoardsInCondition | airbyte_agent_sdk.connectors.monday.types.BoardsLikeCondition | airbyte_agent_sdk.connectors.monday.types.BoardsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.BoardsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.BoardsContainsCondition | airbyte_agent_sdk.connectors.monday.types.BoardsNotCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAndCondition | airbyte_agent_sdk.connectors.monday.types.BoardsOrCondition | airbyte_agent_sdk.connectors.monday.types.BoardsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.BoardsSortFilter]`
    :   The type of the None singleton.

`BoardsSortFilter(*args, **kwargs)`
:   Available fields for sorting boards search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_kind: Literal['asc', 'desc']`
    :   Board kind (public, private, share)

    `columns: Literal['asc', 'desc']`
    :   Board columns

    `communication: Literal['asc', 'desc']`
    :   Board communication value

    `creator: Literal['asc', 'desc']`
    :   Board creator

    `description: Literal['asc', 'desc']`
    :   Board description

    `groups: Literal['asc', 'desc']`
    :   Board groups

    `id: Literal['asc', 'desc']`
    :   Unique board identifier

    `name: Literal['asc', 'desc']`
    :   Board name

    `owners: Literal['asc', 'desc']`
    :   Board owners

    `permissions: Literal['asc', 'desc']`
    :   Board permissions

    `state: Literal['asc', 'desc']`
    :   Board state (active, archived, deleted)

    `subscribers: Literal['asc', 'desc']`
    :   Board subscribers

    `tags: Literal['asc', 'desc']`
    :   Board tags

    `top_group: Literal['asc', 'desc']`
    :   Top group on the board

    `type_: Literal['asc', 'desc']`
    :   Board type

    `updated_at: Literal['asc', 'desc']`
    :   When the board was last updated

    `updated_at_int: Literal['asc', 'desc']`
    :   When the board was last updated (Unix timestamp)

    `updates: Literal['asc', 'desc']`
    :   Board updates

    `views: Literal['asc', 'desc']`
    :   Board views

    `workspace: Literal['asc', 'desc']`
    :   Workspace the board belongs to

`BoardsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_kind: str`
    :   Board kind (public, private, share)

    `columns: str`
    :   Board columns

    `communication: str`
    :   Board communication value

    `creator: str`
    :   Board creator

    `description: str`
    :   Board description

    `groups: str`
    :   Board groups

    `id: str`
    :   Unique board identifier

    `name: str`
    :   Board name

    `owners: str`
    :   Board owners

    `permissions: str`
    :   Board permissions

    `state: str`
    :   Board state (active, archived, deleted)

    `subscribers: str`
    :   Board subscribers

    `tags: str`
    :   Board tags

    `top_group: str`
    :   Top group on the board

    `type_: str`
    :   Board type

    `updated_at: str`
    :   When the board was last updated

    `updated_at_int: str`
    :   When the board was last updated (Unix timestamp)

    `updates: str`
    :   Board updates

    `views: str`
    :   Board views

    `workspace: str`
    :   Workspace the board belongs to

`ItemsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.ItemsEqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsInCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ItemsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ItemsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ItemsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNotCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAndCondition | airbyte_agent_sdk.connectors.monday.types.ItemsOrCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAnyCondition]`
    :   The type of the None singleton.

`ItemsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.ItemsAnyValueFilter`
    :   The type of the None singleton.

`ItemsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: Any`
    :   Files attached to the item

    `board: Any`
    :   Board the item belongs to

    `column_values: Any`
    :   Item column values

    `created_at: Any`
    :   When the item was created

    `creator_id: Any`
    :   ID of the user who created the item

    `group: Any`
    :   Group the item belongs to

    `id: Any`
    :   Unique item identifier

    `name: Any`
    :   Item name

    `parent_item: Any`
    :   Parent item (for subitems)

    `state: Any`
    :   Item state (active, archived, deleted)

    `subscribers: Any`
    :   Item subscribers

    `updated_at: Any`
    :   When the item was last updated

    `updated_at_int: Any`
    :   When the item was last updated (Unix timestamp)

    `updates: Any`
    :   Item updates

`ItemsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.ItemsAnyValueFilter`
    :   The type of the None singleton.

`ItemsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.ItemsSearchFilter`
    :   The type of the None singleton.

`ItemsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.ItemsStringFilter`
    :   The type of the None singleton.

`ItemsGetParams(*args, **kwargs)`
:   Parameters for items.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`ItemsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.ItemsSearchFilter`
    :   The type of the None singleton.

`ItemsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.ItemsSearchFilter`
    :   The type of the None singleton.

`ItemsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.ItemsInFilter`
    :   The type of the None singleton.

`ItemsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: list[list[typing.Any]]`
    :   Files attached to the item

    `board: list[dict[str, typing.Any]]`
    :   Board the item belongs to

    `column_values: list[list[typing.Any]]`
    :   Item column values

    `created_at: list[str]`
    :   When the item was created

    `creator_id: list[str]`
    :   ID of the user who created the item

    `group: list[dict[str, typing.Any]]`
    :   Group the item belongs to

    `id: list[str]`
    :   Unique item identifier

    `name: list[str]`
    :   Item name

    `parent_item: list[dict[str, typing.Any]]`
    :   Parent item (for subitems)

    `state: list[str]`
    :   Item state (active, archived, deleted)

    `subscribers: list[list[typing.Any]]`
    :   Item subscribers

    `updated_at: list[str]`
    :   When the item was last updated

    `updated_at_int: list[int]`
    :   When the item was last updated (Unix timestamp)

    `updates: list[list[typing.Any]]`
    :   Item updates

`ItemsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.ItemsStringFilter`
    :   The type of the None singleton.

`ItemsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.ItemsStringFilter`
    :   The type of the None singleton.

`ItemsListParams(*args, **kwargs)`
:   Parameters for items.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `board_id: str`
    :   The type of the None singleton.

`ItemsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.ItemsSearchFilter`
    :   The type of the None singleton.

`ItemsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.ItemsSearchFilter`
    :   The type of the None singleton.

`ItemsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.ItemsSearchFilter`
    :   The type of the None singleton.

`ItemsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.ItemsEqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsInCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ItemsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ItemsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ItemsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNotCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAndCondition | airbyte_agent_sdk.connectors.monday.types.ItemsOrCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAnyCondition`
    :   The type of the None singleton.

`ItemsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.ItemsEqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsInCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ItemsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ItemsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ItemsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNotCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAndCondition | airbyte_agent_sdk.connectors.monday.types.ItemsOrCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAnyCondition]`
    :   The type of the None singleton.

`ItemsSearchFilter(*args, **kwargs)`
:   Available fields for filtering items search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: list[typing.Any] | None`
    :   Files attached to the item

    `board: dict[str, typing.Any] | None`
    :   Board the item belongs to

    `column_values: list[typing.Any] | None`
    :   Item column values

    `created_at: str | None`
    :   When the item was created

    `creator_id: str | None`
    :   ID of the user who created the item

    `group: dict[str, typing.Any] | None`
    :   Group the item belongs to

    `id: str | None`
    :   Unique item identifier

    `name: str | None`
    :   Item name

    `parent_item: dict[str, typing.Any] | None`
    :   Parent item (for subitems)

    `state: str | None`
    :   Item state (active, archived, deleted)

    `subscribers: list[typing.Any] | None`
    :   Item subscribers

    `updated_at: str | None`
    :   When the item was last updated

    `updated_at_int: int | None`
    :   When the item was last updated (Unix timestamp)

    `updates: list[typing.Any] | None`
    :   Item updates

`ItemsSearchQuery(*args, **kwargs)`
:   Search query for items entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.ItemsEqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNeqCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsGteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLtCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLteCondition | airbyte_agent_sdk.connectors.monday.types.ItemsInCondition | airbyte_agent_sdk.connectors.monday.types.ItemsLikeCondition | airbyte_agent_sdk.connectors.monday.types.ItemsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.ItemsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.ItemsContainsCondition | airbyte_agent_sdk.connectors.monday.types.ItemsNotCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAndCondition | airbyte_agent_sdk.connectors.monday.types.ItemsOrCondition | airbyte_agent_sdk.connectors.monday.types.ItemsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.ItemsSortFilter]`
    :   The type of the None singleton.

`ItemsSortFilter(*args, **kwargs)`
:   Available fields for sorting items search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: Literal['asc', 'desc']`
    :   Files attached to the item

    `board: Literal['asc', 'desc']`
    :   Board the item belongs to

    `column_values: Literal['asc', 'desc']`
    :   Item column values

    `created_at: Literal['asc', 'desc']`
    :   When the item was created

    `creator_id: Literal['asc', 'desc']`
    :   ID of the user who created the item

    `group: Literal['asc', 'desc']`
    :   Group the item belongs to

    `id: Literal['asc', 'desc']`
    :   Unique item identifier

    `name: Literal['asc', 'desc']`
    :   Item name

    `parent_item: Literal['asc', 'desc']`
    :   Parent item (for subitems)

    `state: Literal['asc', 'desc']`
    :   Item state (active, archived, deleted)

    `subscribers: Literal['asc', 'desc']`
    :   Item subscribers

    `updated_at: Literal['asc', 'desc']`
    :   When the item was last updated

    `updated_at_int: Literal['asc', 'desc']`
    :   When the item was last updated (Unix timestamp)

    `updates: Literal['asc', 'desc']`
    :   Item updates

`ItemsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: str`
    :   Files attached to the item

    `board: str`
    :   Board the item belongs to

    `column_values: str`
    :   Item column values

    `created_at: str`
    :   When the item was created

    `creator_id: str`
    :   ID of the user who created the item

    `group: str`
    :   Group the item belongs to

    `id: str`
    :   Unique item identifier

    `name: str`
    :   Item name

    `parent_item: str`
    :   Parent item (for subitems)

    `state: str`
    :   Item state (active, archived, deleted)

    `subscribers: str`
    :   Item subscribers

    `updated_at: str`
    :   When the item was last updated

    `updated_at_int: str`
    :   When the item was last updated (Unix timestamp)

    `updates: str`
    :   Item updates

`TagsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.TagsEqCondition | airbyte_agent_sdk.connectors.monday.types.TagsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TagsGtCondition | airbyte_agent_sdk.connectors.monday.types.TagsGteCondition | airbyte_agent_sdk.connectors.monday.types.TagsLtCondition | airbyte_agent_sdk.connectors.monday.types.TagsLteCondition | airbyte_agent_sdk.connectors.monday.types.TagsInCondition | airbyte_agent_sdk.connectors.monday.types.TagsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TagsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TagsNotCondition | airbyte_agent_sdk.connectors.monday.types.TagsAndCondition | airbyte_agent_sdk.connectors.monday.types.TagsOrCondition | airbyte_agent_sdk.connectors.monday.types.TagsAnyCondition]`
    :   The type of the None singleton.

`TagsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.TagsAnyValueFilter`
    :   The type of the None singleton.

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Any`
    :   Tag color

    `id: Any`
    :   Unique tag identifier

    `name: Any`
    :   Tag name

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.TagsAnyValueFilter`
    :   The type of the None singleton.

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.TagsInFilter`
    :   The type of the None singleton.

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: list[str]`
    :   Tag color

    `id: list[str]`
    :   Unique tag identifier

    `name: list[str]`
    :   Tag name

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.TagsEqCondition | airbyte_agent_sdk.connectors.monday.types.TagsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TagsGtCondition | airbyte_agent_sdk.connectors.monday.types.TagsGteCondition | airbyte_agent_sdk.connectors.monday.types.TagsLtCondition | airbyte_agent_sdk.connectors.monday.types.TagsLteCondition | airbyte_agent_sdk.connectors.monday.types.TagsInCondition | airbyte_agent_sdk.connectors.monday.types.TagsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TagsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TagsNotCondition | airbyte_agent_sdk.connectors.monday.types.TagsAndCondition | airbyte_agent_sdk.connectors.monday.types.TagsOrCondition | airbyte_agent_sdk.connectors.monday.types.TagsAnyCondition`
    :   The type of the None singleton.

`TagsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.TagsEqCondition | airbyte_agent_sdk.connectors.monday.types.TagsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TagsGtCondition | airbyte_agent_sdk.connectors.monday.types.TagsGteCondition | airbyte_agent_sdk.connectors.monday.types.TagsLtCondition | airbyte_agent_sdk.connectors.monday.types.TagsLteCondition | airbyte_agent_sdk.connectors.monday.types.TagsInCondition | airbyte_agent_sdk.connectors.monday.types.TagsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TagsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TagsNotCondition | airbyte_agent_sdk.connectors.monday.types.TagsAndCondition | airbyte_agent_sdk.connectors.monday.types.TagsOrCondition | airbyte_agent_sdk.connectors.monday.types.TagsAnyCondition]`
    :   The type of the None singleton.

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str | None`
    :   Tag color

    `id: str | None`
    :   Unique tag identifier

    `name: str | None`
    :   Tag name

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.TagsEqCondition | airbyte_agent_sdk.connectors.monday.types.TagsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TagsGtCondition | airbyte_agent_sdk.connectors.monday.types.TagsGteCondition | airbyte_agent_sdk.connectors.monday.types.TagsLtCondition | airbyte_agent_sdk.connectors.monday.types.TagsLteCondition | airbyte_agent_sdk.connectors.monday.types.TagsInCondition | airbyte_agent_sdk.connectors.monday.types.TagsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TagsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TagsNotCondition | airbyte_agent_sdk.connectors.monday.types.TagsAndCondition | airbyte_agent_sdk.connectors.monday.types.TagsOrCondition | airbyte_agent_sdk.connectors.monday.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.TagsSortFilter]`
    :   The type of the None singleton.

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Literal['asc', 'desc']`
    :   Tag color

    `id: Literal['asc', 'desc']`
    :   Unique tag identifier

    `name: Literal['asc', 'desc']`
    :   Tag name

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   Tag color

    `id: str`
    :   Unique tag identifier

    `name: str`
    :   Tag name

`TeamsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.TeamsEqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsInCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNotCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAndCondition | airbyte_agent_sdk.connectors.monday.types.TeamsOrCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAnyCondition]`
    :   The type of the None singleton.

`TeamsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique team identifier

    `name: Any`
    :   Team name

    `picture_url: Any`
    :   Team picture URL

    `users: Any`
    :   Team members

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsGetParams(*args, **kwargs)`
:   Parameters for teams.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`TeamsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.TeamsInFilter`
    :   The type of the None singleton.

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[int]`
    :   Unique team identifier

    `name: list[str]`
    :   Team name

    `picture_url: list[str]`
    :   Team picture URL

    `users: list[list[typing.Any]]`
    :   Team members

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.TeamsEqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsInCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNotCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAndCondition | airbyte_agent_sdk.connectors.monday.types.TeamsOrCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAnyCondition`
    :   The type of the None singleton.

`TeamsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.TeamsEqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsInCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNotCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAndCondition | airbyte_agent_sdk.connectors.monday.types.TeamsOrCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAnyCondition]`
    :   The type of the None singleton.

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int | None`
    :   Unique team identifier

    `name: str | None`
    :   Team name

    `picture_url: str | None`
    :   Team picture URL

    `users: list[typing.Any] | None`
    :   Team members

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.TeamsEqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsGteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLtCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLteCondition | airbyte_agent_sdk.connectors.monday.types.TeamsInCondition | airbyte_agent_sdk.connectors.monday.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.monday.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.monday.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.monday.types.TeamsNotCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAndCondition | airbyte_agent_sdk.connectors.monday.types.TeamsOrCondition | airbyte_agent_sdk.connectors.monday.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.TeamsSortFilter]`
    :   The type of the None singleton.

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique team identifier

    `name: Literal['asc', 'desc']`
    :   Team name

    `picture_url: Literal['asc', 'desc']`
    :   Team picture URL

    `users: Literal['asc', 'desc']`
    :   Team members

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique team identifier

    `name: str`
    :   Team name

    `picture_url: str`
    :   Team picture URL

    `users: str`
    :   Team members

`UpdatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.UpdatesEqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNeqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesInCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLikeCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesContainsCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNotCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAndCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesOrCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAnyCondition]`
    :   The type of the None singleton.

`UpdatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.UpdatesAnyValueFilter`
    :   The type of the None singleton.

`UpdatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: Any`
    :   Files attached to this update

    `body: Any`
    :   Update body (HTML)

    `created_at: Any`
    :   When the update was created

    `creator_id: Any`
    :   ID of the user who created the update

    `id: Any`
    :   Unique update identifier

    `item_id: Any`
    :   ID of the item this update belongs to

    `replies: Any`
    :   Replies to this update

    `text_body: Any`
    :   Update body (plain text)

    `updated_at: Any`
    :   When the update was last modified

`UpdatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.UpdatesAnyValueFilter`
    :   The type of the None singleton.

`UpdatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.UpdatesSearchFilter`
    :   The type of the None singleton.

`UpdatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.UpdatesStringFilter`
    :   The type of the None singleton.

`UpdatesGetParams(*args, **kwargs)`
:   Parameters for updates.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`UpdatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.UpdatesSearchFilter`
    :   The type of the None singleton.

`UpdatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.UpdatesSearchFilter`
    :   The type of the None singleton.

`UpdatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.UpdatesInFilter`
    :   The type of the None singleton.

`UpdatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: list[list[typing.Any]]`
    :   Files attached to this update

    `body: list[str]`
    :   Update body (HTML)

    `created_at: list[str]`
    :   When the update was created

    `creator_id: list[str]`
    :   ID of the user who created the update

    `id: list[str]`
    :   Unique update identifier

    `item_id: list[str]`
    :   ID of the item this update belongs to

    `replies: list[list[typing.Any]]`
    :   Replies to this update

    `text_body: list[str]`
    :   Update body (plain text)

    `updated_at: list[str]`
    :   When the update was last modified

`UpdatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.UpdatesStringFilter`
    :   The type of the None singleton.

`UpdatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.UpdatesStringFilter`
    :   The type of the None singleton.

`UpdatesListParams(*args, **kwargs)`
:   Parameters for updates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

`UpdatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.UpdatesSearchFilter`
    :   The type of the None singleton.

`UpdatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.UpdatesSearchFilter`
    :   The type of the None singleton.

`UpdatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.UpdatesSearchFilter`
    :   The type of the None singleton.

`UpdatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.UpdatesEqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNeqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesInCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLikeCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesContainsCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNotCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAndCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesOrCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAnyCondition`
    :   The type of the None singleton.

`UpdatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.UpdatesEqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNeqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesInCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLikeCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesContainsCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNotCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAndCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesOrCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAnyCondition]`
    :   The type of the None singleton.

`UpdatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering updates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: list[typing.Any] | None`
    :   Files attached to this update

    `body: str | None`
    :   Update body (HTML)

    `created_at: str | None`
    :   When the update was created

    `creator_id: str | None`
    :   ID of the user who created the update

    `id: str | None`
    :   Unique update identifier

    `item_id: str | None`
    :   ID of the item this update belongs to

    `replies: list[typing.Any] | None`
    :   Replies to this update

    `text_body: str | None`
    :   Update body (plain text)

    `updated_at: str | None`
    :   When the update was last modified

`UpdatesSearchQuery(*args, **kwargs)`
:   Search query for updates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.UpdatesEqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNeqCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesGteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLtCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLteCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesInCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesLikeCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesContainsCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesNotCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAndCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesOrCondition | airbyte_agent_sdk.connectors.monday.types.UpdatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.UpdatesSortFilter]`
    :   The type of the None singleton.

`UpdatesSortFilter(*args, **kwargs)`
:   Available fields for sorting updates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: Literal['asc', 'desc']`
    :   Files attached to this update

    `body: Literal['asc', 'desc']`
    :   Update body (HTML)

    `created_at: Literal['asc', 'desc']`
    :   When the update was created

    `creator_id: Literal['asc', 'desc']`
    :   ID of the user who created the update

    `id: Literal['asc', 'desc']`
    :   Unique update identifier

    `item_id: Literal['asc', 'desc']`
    :   ID of the item this update belongs to

    `replies: Literal['asc', 'desc']`
    :   Replies to this update

    `text_body: Literal['asc', 'desc']`
    :   Update body (plain text)

    `updated_at: Literal['asc', 'desc']`
    :   When the update was last modified

`UpdatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: str`
    :   Files attached to this update

    `body: str`
    :   Update body (HTML)

    `created_at: str`
    :   When the update was created

    `creator_id: str`
    :   ID of the user who created the update

    `id: str`
    :   Unique update identifier

    `item_id: str`
    :   ID of the item this update belongs to

    `replies: str`
    :   Replies to this update

    `text_body: str`
    :   Update body (plain text)

    `updated_at: str`
    :   When the update was last modified

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

    `and: list[airbyte_agent_sdk.connectors.monday.types.UsersEqCondition | airbyte_agent_sdk.connectors.monday.types.UsersNeqCondition | airbyte_agent_sdk.connectors.monday.types.UsersGtCondition | airbyte_agent_sdk.connectors.monday.types.UsersGteCondition | airbyte_agent_sdk.connectors.monday.types.UsersLtCondition | airbyte_agent_sdk.connectors.monday.types.UsersLteCondition | airbyte_agent_sdk.connectors.monday.types.UsersInCondition | airbyte_agent_sdk.connectors.monday.types.UsersLikeCondition | airbyte_agent_sdk.connectors.monday.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UsersContainsCondition | airbyte_agent_sdk.connectors.monday.types.UsersNotCondition | airbyte_agent_sdk.connectors.monday.types.UsersAndCondition | airbyte_agent_sdk.connectors.monday.types.UsersOrCondition | airbyte_agent_sdk.connectors.monday.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.monday.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `birthday: Any`
    :   User's birthday

    `country_code: Any`
    :   User's country code

    `created_at: Any`
    :   When the user was created

    `email: Any`
    :   User's email address

    `enabled: Any`
    :   Whether the user account is enabled

    `id: Any`
    :   Unique user identifier

    `is_admin: Any`
    :   Whether the user is an admin

    `is_guest: Any`
    :   Whether the user is a guest

    `is_pending: Any`
    :   Whether the user is pending

    `is_verified: Any`
    :   Whether the user is verified

    `is_view_only: Any`
    :   Whether the user is view-only

    `join_date: Any`
    :   When the user joined

    `location: Any`
    :   User's location

    `mobile_phone: Any`
    :   User's mobile phone number

    `name: Any`
    :   User's display name

    `phone: Any`
    :   User's phone number

    `photo_original: Any`
    :   URL to original size photo

    `photo_small: Any`
    :   URL to small photo

    `photo_thumb: Any`
    :   URL to thumbnail photo

    `photo_thumb_small: Any`
    :   URL to small thumbnail photo

    `photo_tiny: Any`
    :   URL to tiny photo

    `time_zone_identifier: Any`
    :   User's timezone identifier

    `title: Any`
    :   User's job title

    `url: Any`
    :   User's Monday.com profile URL

    `utc_hours_diff: Any`
    :   UTC hours difference for the user's timezone

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.UsersStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.monday.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.monday.types.UsersInFilter`
    :   The type of the None singleton.

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `birthday: list[str]`
    :   User's birthday

    `country_code: list[str]`
    :   User's country code

    `created_at: list[str]`
    :   When the user was created

    `email: list[str]`
    :   User's email address

    `enabled: list[bool]`
    :   Whether the user account is enabled

    `id: list[str]`
    :   Unique user identifier

    `is_admin: list[bool]`
    :   Whether the user is an admin

    `is_guest: list[bool]`
    :   Whether the user is a guest

    `is_pending: list[bool]`
    :   Whether the user is pending

    `is_verified: list[bool]`
    :   Whether the user is verified

    `is_view_only: list[bool]`
    :   Whether the user is view-only

    `join_date: list[str]`
    :   When the user joined

    `location: list[str]`
    :   User's location

    `mobile_phone: list[str]`
    :   User's mobile phone number

    `name: list[str]`
    :   User's display name

    `phone: list[str]`
    :   User's phone number

    `photo_original: list[str]`
    :   URL to original size photo

    `photo_small: list[str]`
    :   URL to small photo

    `photo_thumb: list[str]`
    :   URL to thumbnail photo

    `photo_thumb_small: list[str]`
    :   URL to small thumbnail photo

    `photo_tiny: list[str]`
    :   URL to tiny photo

    `time_zone_identifier: list[str]`
    :   User's timezone identifier

    `title: list[str]`
    :   User's job title

    `url: list[str]`
    :   User's Monday.com profile URL

    `utc_hours_diff: list[int]`
    :   UTC hours difference for the user's timezone

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.monday.types.UsersEqCondition | airbyte_agent_sdk.connectors.monday.types.UsersNeqCondition | airbyte_agent_sdk.connectors.monday.types.UsersGtCondition | airbyte_agent_sdk.connectors.monday.types.UsersGteCondition | airbyte_agent_sdk.connectors.monday.types.UsersLtCondition | airbyte_agent_sdk.connectors.monday.types.UsersLteCondition | airbyte_agent_sdk.connectors.monday.types.UsersInCondition | airbyte_agent_sdk.connectors.monday.types.UsersLikeCondition | airbyte_agent_sdk.connectors.monday.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UsersContainsCondition | airbyte_agent_sdk.connectors.monday.types.UsersNotCondition | airbyte_agent_sdk.connectors.monday.types.UsersAndCondition | airbyte_agent_sdk.connectors.monday.types.UsersOrCondition | airbyte_agent_sdk.connectors.monday.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.monday.types.UsersEqCondition | airbyte_agent_sdk.connectors.monday.types.UsersNeqCondition | airbyte_agent_sdk.connectors.monday.types.UsersGtCondition | airbyte_agent_sdk.connectors.monday.types.UsersGteCondition | airbyte_agent_sdk.connectors.monday.types.UsersLtCondition | airbyte_agent_sdk.connectors.monday.types.UsersLteCondition | airbyte_agent_sdk.connectors.monday.types.UsersInCondition | airbyte_agent_sdk.connectors.monday.types.UsersLikeCondition | airbyte_agent_sdk.connectors.monday.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UsersContainsCondition | airbyte_agent_sdk.connectors.monday.types.UsersNotCondition | airbyte_agent_sdk.connectors.monday.types.UsersAndCondition | airbyte_agent_sdk.connectors.monday.types.UsersOrCondition | airbyte_agent_sdk.connectors.monday.types.UsersAnyCondition]`
    :   The type of the None singleton.

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `birthday: str | None`
    :   User's birthday

    `country_code: str | None`
    :   User's country code

    `created_at: str | None`
    :   When the user was created

    `email: str | None`
    :   User's email address

    `enabled: bool | None`
    :   Whether the user account is enabled

    `id: str | None`
    :   Unique user identifier

    `is_admin: bool | None`
    :   Whether the user is an admin

    `is_guest: bool | None`
    :   Whether the user is a guest

    `is_pending: bool | None`
    :   Whether the user is pending

    `is_verified: bool | None`
    :   Whether the user is verified

    `is_view_only: bool | None`
    :   Whether the user is view-only

    `join_date: str | None`
    :   When the user joined

    `location: str | None`
    :   User's location

    `mobile_phone: str | None`
    :   User's mobile phone number

    `name: str | None`
    :   User's display name

    `phone: str | None`
    :   User's phone number

    `photo_original: str | None`
    :   URL to original size photo

    `photo_small: str | None`
    :   URL to small photo

    `photo_thumb: str | None`
    :   URL to thumbnail photo

    `photo_thumb_small: str | None`
    :   URL to small thumbnail photo

    `photo_tiny: str | None`
    :   URL to tiny photo

    `time_zone_identifier: str | None`
    :   User's timezone identifier

    `title: str | None`
    :   User's job title

    `url: str | None`
    :   User's Monday.com profile URL

    `utc_hours_diff: int | None`
    :   UTC hours difference for the user's timezone

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.UsersEqCondition | airbyte_agent_sdk.connectors.monday.types.UsersNeqCondition | airbyte_agent_sdk.connectors.monday.types.UsersGtCondition | airbyte_agent_sdk.connectors.monday.types.UsersGteCondition | airbyte_agent_sdk.connectors.monday.types.UsersLtCondition | airbyte_agent_sdk.connectors.monday.types.UsersLteCondition | airbyte_agent_sdk.connectors.monday.types.UsersInCondition | airbyte_agent_sdk.connectors.monday.types.UsersLikeCondition | airbyte_agent_sdk.connectors.monday.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.monday.types.UsersContainsCondition | airbyte_agent_sdk.connectors.monday.types.UsersNotCondition | airbyte_agent_sdk.connectors.monday.types.UsersAndCondition | airbyte_agent_sdk.connectors.monday.types.UsersOrCondition | airbyte_agent_sdk.connectors.monday.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.UsersSortFilter]`
    :   The type of the None singleton.

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `birthday: Literal['asc', 'desc']`
    :   User's birthday

    `country_code: Literal['asc', 'desc']`
    :   User's country code

    `created_at: Literal['asc', 'desc']`
    :   When the user was created

    `email: Literal['asc', 'desc']`
    :   User's email address

    `enabled: Literal['asc', 'desc']`
    :   Whether the user account is enabled

    `id: Literal['asc', 'desc']`
    :   Unique user identifier

    `is_admin: Literal['asc', 'desc']`
    :   Whether the user is an admin

    `is_guest: Literal['asc', 'desc']`
    :   Whether the user is a guest

    `is_pending: Literal['asc', 'desc']`
    :   Whether the user is pending

    `is_verified: Literal['asc', 'desc']`
    :   Whether the user is verified

    `is_view_only: Literal['asc', 'desc']`
    :   Whether the user is view-only

    `join_date: Literal['asc', 'desc']`
    :   When the user joined

    `location: Literal['asc', 'desc']`
    :   User's location

    `mobile_phone: Literal['asc', 'desc']`
    :   User's mobile phone number

    `name: Literal['asc', 'desc']`
    :   User's display name

    `phone: Literal['asc', 'desc']`
    :   User's phone number

    `photo_original: Literal['asc', 'desc']`
    :   URL to original size photo

    `photo_small: Literal['asc', 'desc']`
    :   URL to small photo

    `photo_thumb: Literal['asc', 'desc']`
    :   URL to thumbnail photo

    `photo_thumb_small: Literal['asc', 'desc']`
    :   URL to small thumbnail photo

    `photo_tiny: Literal['asc', 'desc']`
    :   URL to tiny photo

    `time_zone_identifier: Literal['asc', 'desc']`
    :   User's timezone identifier

    `title: Literal['asc', 'desc']`
    :   User's job title

    `url: Literal['asc', 'desc']`
    :   User's Monday.com profile URL

    `utc_hours_diff: Literal['asc', 'desc']`
    :   UTC hours difference for the user's timezone

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `birthday: str`
    :   User's birthday

    `country_code: str`
    :   User's country code

    `created_at: str`
    :   When the user was created

    `email: str`
    :   User's email address

    `enabled: str`
    :   Whether the user account is enabled

    `id: str`
    :   Unique user identifier

    `is_admin: str`
    :   Whether the user is an admin

    `is_guest: str`
    :   Whether the user is a guest

    `is_pending: str`
    :   Whether the user is pending

    `is_verified: str`
    :   Whether the user is verified

    `is_view_only: str`
    :   Whether the user is view-only

    `join_date: str`
    :   When the user joined

    `location: str`
    :   User's location

    `mobile_phone: str`
    :   User's mobile phone number

    `name: str`
    :   User's display name

    `phone: str`
    :   User's phone number

    `photo_original: str`
    :   URL to original size photo

    `photo_small: str`
    :   URL to small photo

    `photo_thumb: str`
    :   URL to thumbnail photo

    `photo_thumb_small: str`
    :   URL to small thumbnail photo

    `photo_tiny: str`
    :   URL to tiny photo

    `time_zone_identifier: str`
    :   User's timezone identifier

    `title: str`
    :   User's job title

    `url: str`
    :   User's Monday.com profile URL

    `utc_hours_diff: str`
    :   UTC hours difference for the user's timezone

`WorkspacesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.monday.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAnyCondition]`
    :   The type of the None singleton.

`WorkspacesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.monday.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

`WorkspacesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_product: Any`
    :   Account product info

    `created_at: Any`
    :   When the workspace was created

    `description: Any`
    :   Workspace description

    `id: Any`
    :   Unique workspace identifier

    `kind: Any`
    :   Workspace kind (open, closed)

    `name: Any`
    :   Workspace name

    `owners_subscribers: Any`
    :   Owner subscribers

    `settings: Any`
    :   Workspace settings

    `state: Any`
    :   Workspace state

    `team_owners_subscribers: Any`
    :   Team owner subscribers

    `teams_subscribers: Any`
    :   Team subscribers

    `users_subscribers: Any`
    :   User subscribers

`WorkspacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.monday.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

`WorkspacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.monday.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.monday.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesGetParams(*args, **kwargs)`
:   Parameters for workspaces.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

`WorkspacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.monday.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.monday.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.monday.types.WorkspacesInFilter`
    :   The type of the None singleton.

`WorkspacesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_product: list[dict[str, typing.Any]]`
    :   Account product info

    `created_at: list[str]`
    :   When the workspace was created

    `description: list[str]`
    :   Workspace description

    `id: list[str]`
    :   Unique workspace identifier

    `kind: list[str]`
    :   Workspace kind (open, closed)

    `name: list[str]`
    :   Workspace name

    `owners_subscribers: list[list[typing.Any]]`
    :   Owner subscribers

    `settings: list[dict[str, typing.Any]]`
    :   Workspace settings

    `state: list[str]`
    :   Workspace state

    `team_owners_subscribers: list[list[typing.Any]]`
    :   Team owner subscribers

    `teams_subscribers: list[list[typing.Any]]`
    :   Team subscribers

    `users_subscribers: list[list[typing.Any]]`
    :   User subscribers

`WorkspacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.monday.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.monday.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesListParams(*args, **kwargs)`
:   Parameters for workspaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`WorkspacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.monday.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.monday.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.monday.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.monday.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

`WorkspacesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.monday.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAnyCondition]`
    :   The type of the None singleton.

`WorkspacesSearchFilter(*args, **kwargs)`
:   Available fields for filtering workspaces search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_product: dict[str, typing.Any] | None`
    :   Account product info

    `created_at: str | None`
    :   When the workspace was created

    `description: str | None`
    :   Workspace description

    `id: str | None`
    :   Unique workspace identifier

    `kind: str | None`
    :   Workspace kind (open, closed)

    `name: str | None`
    :   Workspace name

    `owners_subscribers: list[typing.Any] | None`
    :   Owner subscribers

    `settings: dict[str, typing.Any] | None`
    :   Workspace settings

    `state: str | None`
    :   Workspace state

    `team_owners_subscribers: list[typing.Any] | None`
    :   Team owner subscribers

    `teams_subscribers: list[typing.Any] | None`
    :   Team subscribers

    `users_subscribers: list[typing.Any] | None`
    :   User subscribers

`WorkspacesSearchQuery(*args, **kwargs)`
:   Search query for workspaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.monday.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.monday.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.monday.types.WorkspacesSortFilter]`
    :   The type of the None singleton.

`WorkspacesSortFilter(*args, **kwargs)`
:   Available fields for sorting workspaces search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_product: Literal['asc', 'desc']`
    :   Account product info

    `created_at: Literal['asc', 'desc']`
    :   When the workspace was created

    `description: Literal['asc', 'desc']`
    :   Workspace description

    `id: Literal['asc', 'desc']`
    :   Unique workspace identifier

    `kind: Literal['asc', 'desc']`
    :   Workspace kind (open, closed)

    `name: Literal['asc', 'desc']`
    :   Workspace name

    `owners_subscribers: Literal['asc', 'desc']`
    :   Owner subscribers

    `settings: Literal['asc', 'desc']`
    :   Workspace settings

    `state: Literal['asc', 'desc']`
    :   Workspace state

    `team_owners_subscribers: Literal['asc', 'desc']`
    :   Team owner subscribers

    `teams_subscribers: Literal['asc', 'desc']`
    :   Team subscribers

    `users_subscribers: Literal['asc', 'desc']`
    :   User subscribers

`WorkspacesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_product: str`
    :   Account product info

    `created_at: str`
    :   When the workspace was created

    `description: str`
    :   Workspace description

    `id: str`
    :   Unique workspace identifier

    `kind: str`
    :   Workspace kind (open, closed)

    `name: str`
    :   Workspace name

    `owners_subscribers: str`
    :   Owner subscribers

    `settings: str`
    :   Workspace settings

    `state: str`
    :   Workspace state

    `team_owners_subscribers: str`
    :   Team owner subscribers

    `teams_subscribers: str`
    :   Team subscribers

    `users_subscribers: str`
    :   User subscribers