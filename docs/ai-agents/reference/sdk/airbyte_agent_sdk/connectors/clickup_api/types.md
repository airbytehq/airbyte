---
id: airbyte_agent_sdk-connectors-clickup_api-types
title: airbyte_agent_sdk.connectors.clickup_api.types
---

Module airbyte_agent_sdk.connectors.clickup_api.types
=====================================================
Type definitions for clickup-api connector.

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

<a id="CommentsAndCondition"></a>

`CommentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.CommentsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAnyCondition]`
    :   The type of the None singleton.

<a id="CommentsAnyCondition"></a>

`CommentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.clickup_api.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsAnyValueFilter"></a>

`CommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_text: Any`
    :   Plain-text content of the comment

    `date: Any`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: Any`
    :   Unique identifier for the comment

    `reply_count: Any`
    :   Number of replies on the comment

<a id="CommentsContainsCondition"></a>

`CommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsCreateParams"></a>

`CommentsCreateParams(*args, **kwargs)`
:   Parameters for comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: int`
    :   The type of the None singleton.

    `comment_text: str`
    :   The type of the None singleton.

    `notify_all: bool`
    :   The type of the None singleton.

    `task_id: str`
    :   The type of the None singleton.

<a id="CommentsEqCondition"></a>

`CommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsFuzzyCondition"></a>

`CommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsGetParams"></a>

`CommentsGetParams(*args, **kwargs)`
:   Parameters for comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

<a id="CommentsGtCondition"></a>

`CommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsGteCondition"></a>

`CommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsInCondition"></a>

`CommentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.clickup_api.types.CommentsInFilter`
    :   The type of the None singleton.

<a id="CommentsInFilter"></a>

`CommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_text: list[str]`
    :   Plain-text content of the comment

    `date: list[str]`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: list[str]`
    :   Unique identifier for the comment

    `reply_count: list[float]`
    :   Number of replies on the comment

<a id="CommentsKeywordCondition"></a>

`CommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsLikeCondition"></a>

`CommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsListParams"></a>

`CommentsListParams(*args, **kwargs)`
:   Parameters for comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_id: str`
    :   The type of the None singleton.

<a id="CommentsLtCondition"></a>

`CommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsLteCondition"></a>

`CommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsNeqCondition"></a>

`CommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsNotCondition"></a>

`CommentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.clickup_api.types.CommentsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAnyCondition`
    :   The type of the None singleton.

<a id="CommentsOrCondition"></a>

`CommentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.CommentsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAnyCondition]`
    :   The type of the None singleton.

<a id="CommentsSearchFilter"></a>

`CommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_text: str | None`
    :   Plain-text content of the comment

    `date: str | None`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the comment

    `reply_count: float | None`
    :   Number of replies on the comment

<a id="CommentsSearchQuery"></a>

`CommentsSearchQuery(*args, **kwargs)`
:   Search query for comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.CommentsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.CommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.CommentsSortFilter]`
    :   The type of the None singleton.

<a id="CommentsSortFilter"></a>

`CommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_text: Literal['asc', 'desc']`
    :   Plain-text content of the comment

    `date: Literal['asc', 'desc']`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the comment

    `reply_count: Literal['asc', 'desc']`
    :   Number of replies on the comment

<a id="CommentsStringFilter"></a>

`CommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_text: str`
    :   Plain-text content of the comment

    `date: str`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the comment

    `reply_count: str`
    :   Number of replies on the comment

<a id="CommentsUpdateParams"></a>

`CommentsUpdateParams(*args, **kwargs)`
:   Parameters for comments.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: int`
    :   The type of the None singleton.

    `comment_id: str`
    :   The type of the None singleton.

    `comment_text: str`
    :   The type of the None singleton.

    `resolved: bool`
    :   The type of the None singleton.

<a id="DocsGetParams"></a>

`DocsGetParams(*args, **kwargs)`
:   Parameters for docs.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `doc_id: str`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.

<a id="DocsListParams"></a>

`DocsListParams(*args, **kwargs)`
:   Parameters for docs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `workspace_id: str`
    :   The type of the None singleton.

<a id="FoldersAndCondition"></a>

`FoldersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.FoldersEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersInCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAnyCondition]`
    :   The type of the None singleton.

<a id="FoldersAnyCondition"></a>

`FoldersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.clickup_api.types.FoldersAnyValueFilter`
    :   The type of the None singleton.

<a id="FoldersAnyValueFilter"></a>

`FoldersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hidden: Any`
    :   Whether the folder is hidden from the sidebar

    `id: Any`
    :   Unique identifier for the folder

    `name: Any`
    :   Name of the folder

    `task_count: Any`
    :   Number of tasks contained in the folder

<a id="FoldersContainsCondition"></a>

`FoldersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.FoldersAnyValueFilter`
    :   The type of the None singleton.

<a id="FoldersEqCondition"></a>

`FoldersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.FoldersSearchFilter`
    :   The type of the None singleton.

<a id="FoldersFuzzyCondition"></a>

`FoldersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.FoldersStringFilter`
    :   The type of the None singleton.

<a id="FoldersGetParams"></a>

`FoldersGetParams(*args, **kwargs)`
:   Parameters for folders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `folder_id: str`
    :   The type of the None singleton.

<a id="FoldersGtCondition"></a>

`FoldersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.FoldersSearchFilter`
    :   The type of the None singleton.

<a id="FoldersGteCondition"></a>

`FoldersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.FoldersSearchFilter`
    :   The type of the None singleton.

<a id="FoldersInCondition"></a>

`FoldersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.clickup_api.types.FoldersInFilter`
    :   The type of the None singleton.

<a id="FoldersInFilter"></a>

`FoldersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hidden: list[bool]`
    :   Whether the folder is hidden from the sidebar

    `id: list[str]`
    :   Unique identifier for the folder

    `name: list[str]`
    :   Name of the folder

    `task_count: list[str]`
    :   Number of tasks contained in the folder

<a id="FoldersKeywordCondition"></a>

`FoldersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.FoldersStringFilter`
    :   The type of the None singleton.

<a id="FoldersLikeCondition"></a>

`FoldersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.FoldersStringFilter`
    :   The type of the None singleton.

<a id="FoldersListParams"></a>

`FoldersListParams(*args, **kwargs)`
:   Parameters for folders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `space_id: str`
    :   The type of the None singleton.

<a id="FoldersLtCondition"></a>

`FoldersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.FoldersSearchFilter`
    :   The type of the None singleton.

<a id="FoldersLteCondition"></a>

`FoldersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.FoldersSearchFilter`
    :   The type of the None singleton.

<a id="FoldersNeqCondition"></a>

`FoldersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.FoldersSearchFilter`
    :   The type of the None singleton.

<a id="FoldersNotCondition"></a>

`FoldersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.clickup_api.types.FoldersEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersInCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAnyCondition`
    :   The type of the None singleton.

<a id="FoldersOrCondition"></a>

`FoldersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.FoldersEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersInCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAnyCondition]`
    :   The type of the None singleton.

<a id="FoldersSearchFilter"></a>

`FoldersSearchFilter(*args, **kwargs)`
:   Available fields for filtering folders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hidden: bool | None`
    :   Whether the folder is hidden from the sidebar

    `id: str | None`
    :   Unique identifier for the folder

    `name: str | None`
    :   Name of the folder

    `task_count: str | None`
    :   Number of tasks contained in the folder

<a id="FoldersSearchQuery"></a>

`FoldersSearchQuery(*args, **kwargs)`
:   Search query for folders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.FoldersEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersInCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.FoldersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.FoldersSortFilter]`
    :   The type of the None singleton.

<a id="FoldersSortFilter"></a>

`FoldersSortFilter(*args, **kwargs)`
:   Available fields for sorting folders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hidden: Literal['asc', 'desc']`
    :   Whether the folder is hidden from the sidebar

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the folder

    `name: Literal['asc', 'desc']`
    :   Name of the folder

    `task_count: Literal['asc', 'desc']`
    :   Number of tasks contained in the folder

<a id="FoldersStringFilter"></a>

`FoldersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hidden: str`
    :   Whether the folder is hidden from the sidebar

    `id: str`
    :   Unique identifier for the folder

    `name: str`
    :   Name of the folder

    `task_count: str`
    :   Number of tasks contained in the folder

<a id="GoalsAndCondition"></a>

`GoalsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.GoalsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAnyCondition]`
    :   The type of the None singleton.

<a id="GoalsAnyCondition"></a>

`GoalsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.clickup_api.types.GoalsAnyValueFilter`
    :   The type of the None singleton.

<a id="GoalsAnyValueFilter"></a>

`GoalsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Whether the goal has been archived

    `date_created: Any`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: Any`
    :   Description of the goal

    `due_date: Any`
    :   Due date for the goal, in ClickUp timestamp format

    `id: Any`
    :   Unique identifier for the goal

    `name: Any`
    :   Name of the goal

    `percent_completed: Any`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: Any`
    :   Whether the goal is pinned to the top of the list

    `private: Any`
    :   Whether the goal is private to its owners

    `team_id: Any`
    :   Identifier of the team that owns the goal

<a id="GoalsContainsCondition"></a>

`GoalsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.GoalsAnyValueFilter`
    :   The type of the None singleton.

<a id="GoalsEqCondition"></a>

`GoalsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.GoalsSearchFilter`
    :   The type of the None singleton.

<a id="GoalsFuzzyCondition"></a>

`GoalsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.GoalsStringFilter`
    :   The type of the None singleton.

<a id="GoalsGetParams"></a>

`GoalsGetParams(*args, **kwargs)`
:   Parameters for goals.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `goal_id: str`
    :   The type of the None singleton.

<a id="GoalsGtCondition"></a>

`GoalsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.GoalsSearchFilter`
    :   The type of the None singleton.

<a id="GoalsGteCondition"></a>

`GoalsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.GoalsSearchFilter`
    :   The type of the None singleton.

<a id="GoalsInCondition"></a>

`GoalsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.clickup_api.types.GoalsInFilter`
    :   The type of the None singleton.

<a id="GoalsInFilter"></a>

`GoalsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Whether the goal has been archived

    `date_created: list[str]`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: list[str]`
    :   Description of the goal

    `due_date: list[str]`
    :   Due date for the goal, in ClickUp timestamp format

    `id: list[str]`
    :   Unique identifier for the goal

    `name: list[str]`
    :   Name of the goal

    `percent_completed: list[float]`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: list[bool]`
    :   Whether the goal is pinned to the top of the list

    `private: list[bool]`
    :   Whether the goal is private to its owners

    `team_id: list[str]`
    :   Identifier of the team that owns the goal

<a id="GoalsKeywordCondition"></a>

`GoalsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.GoalsStringFilter`
    :   The type of the None singleton.

<a id="GoalsLikeCondition"></a>

`GoalsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.GoalsStringFilter`
    :   The type of the None singleton.

<a id="GoalsListParams"></a>

`GoalsListParams(*args, **kwargs)`
:   Parameters for goals.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.

<a id="GoalsLtCondition"></a>

`GoalsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.GoalsSearchFilter`
    :   The type of the None singleton.

<a id="GoalsLteCondition"></a>

`GoalsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.GoalsSearchFilter`
    :   The type of the None singleton.

<a id="GoalsNeqCondition"></a>

`GoalsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.GoalsSearchFilter`
    :   The type of the None singleton.

<a id="GoalsNotCondition"></a>

`GoalsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.clickup_api.types.GoalsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAnyCondition`
    :   The type of the None singleton.

<a id="GoalsOrCondition"></a>

`GoalsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.GoalsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAnyCondition]`
    :   The type of the None singleton.

<a id="GoalsSearchFilter"></a>

`GoalsSearchFilter(*args, **kwargs)`
:   Available fields for filtering goals search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Whether the goal has been archived

    `date_created: str | None`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: str | None`
    :   Description of the goal

    `due_date: str | None`
    :   Due date for the goal, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the goal

    `name: str | None`
    :   Name of the goal

    `percent_completed: float | None`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: bool | None`
    :   Whether the goal is pinned to the top of the list

    `private: bool | None`
    :   Whether the goal is private to its owners

    `team_id: str | None`
    :   Identifier of the team that owns the goal

<a id="GoalsSearchQuery"></a>

`GoalsSearchQuery(*args, **kwargs)`
:   Search query for goals entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.GoalsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.GoalsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.GoalsSortFilter]`
    :   The type of the None singleton.

<a id="GoalsSortFilter"></a>

`GoalsSortFilter(*args, **kwargs)`
:   Available fields for sorting goals search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Whether the goal has been archived

    `date_created: Literal['asc', 'desc']`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: Literal['asc', 'desc']`
    :   Description of the goal

    `due_date: Literal['asc', 'desc']`
    :   Due date for the goal, in ClickUp timestamp format

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the goal

    `name: Literal['asc', 'desc']`
    :   Name of the goal

    `percent_completed: Literal['asc', 'desc']`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: Literal['asc', 'desc']`
    :   Whether the goal is pinned to the top of the list

    `private: Literal['asc', 'desc']`
    :   Whether the goal is private to its owners

    `team_id: Literal['asc', 'desc']`
    :   Identifier of the team that owns the goal

<a id="GoalsStringFilter"></a>

`GoalsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Whether the goal has been archived

    `date_created: str`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: str`
    :   Description of the goal

    `due_date: str`
    :   Due date for the goal, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the goal

    `name: str`
    :   Name of the goal

    `percent_completed: str`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: str`
    :   Whether the goal is pinned to the top of the list

    `private: str`
    :   Whether the goal is private to its owners

    `team_id: str`
    :   Identifier of the team that owns the goal

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

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.ListsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.clickup_api.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsAnyValueFilter"></a>

`ListsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Whether the list has been archived

    `due_date: Any`
    :   Due date for the list, in ClickUp timestamp format

    `id: Any`
    :   Unique identifier for the list

    `name: Any`
    :   Name of the list

    `priority: Any`
    :   Priority assigned to the list

    `start_date: Any`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: Any`
    :   Number of tasks contained in the list

<a id="ListsContainsCondition"></a>

`ListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsEqCondition"></a>

`ListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsFuzzyCondition"></a>

`ListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsGetParams"></a>

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

<a id="ListsGtCondition"></a>

`ListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsGteCondition"></a>

`ListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.ListsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.clickup_api.types.ListsInFilter`
    :   The type of the None singleton.

<a id="ListsInFilter"></a>

`ListsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Whether the list has been archived

    `due_date: list[str]`
    :   Due date for the list, in ClickUp timestamp format

    `id: list[str]`
    :   Unique identifier for the list

    `name: list[str]`
    :   Name of the list

    `priority: list[str]`
    :   Priority assigned to the list

    `start_date: list[str]`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: list[int]`
    :   Number of tasks contained in the list

<a id="ListsKeywordCondition"></a>

`ListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsLikeCondition"></a>

`ListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsListParams"></a>

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `folder_id: str`
    :   The type of the None singleton.

<a id="ListsLtCondition"></a>

`ListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsLteCondition"></a>

`ListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNeqCondition"></a>

`ListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.ListsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.clickup_api.types.ListsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.ListsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAnyCondition]`
    :   The type of the None singleton.

<a id="ListsSearchFilter"></a>

`ListsSearchFilter(*args, **kwargs)`
:   Available fields for filtering lists search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool | None`
    :   Whether the list has been archived

    `due_date: str | None`
    :   Due date for the list, in ClickUp timestamp format

    `id: str | None`
    :   Unique identifier for the list

    `name: str | None`
    :   Name of the list

    `priority: str | None`
    :   Priority assigned to the list

    `start_date: str | None`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: int | None`
    :   Number of tasks contained in the list

<a id="ListsSearchQuery"></a>

`ListsSearchQuery(*args, **kwargs)`
:   Search query for lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.ListsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.ListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.ListsSortFilter]`
    :   The type of the None singleton.

<a id="ListsSortFilter"></a>

`ListsSortFilter(*args, **kwargs)`
:   Available fields for sorting lists search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Whether the list has been archived

    `due_date: Literal['asc', 'desc']`
    :   Due date for the list, in ClickUp timestamp format

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the list

    `name: Literal['asc', 'desc']`
    :   Name of the list

    `priority: Literal['asc', 'desc']`
    :   Priority assigned to the list

    `start_date: Literal['asc', 'desc']`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: Literal['asc', 'desc']`
    :   Number of tasks contained in the list

<a id="ListsStringFilter"></a>

`ListsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Whether the list has been archived

    `due_date: str`
    :   Due date for the list, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the list

    `name: str`
    :   Name of the list

    `priority: str`
    :   Priority assigned to the list

    `start_date: str`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: str`
    :   Number of tasks contained in the list

<a id="MembersListParams"></a>

`MembersListParams(*args, **kwargs)`
:   Parameters for members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `task_id: str`
    :   The type of the None singleton.

<a id="SpacesAndCondition"></a>

`SpacesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.SpacesEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesInCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAnyCondition]`
    :   The type of the None singleton.

<a id="SpacesAnyCondition"></a>

`SpacesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.clickup_api.types.SpacesAnyValueFilter`
    :   The type of the None singleton.

<a id="SpacesAnyValueFilter"></a>

`SpacesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the space

    `name: Any`
    :   Name of the space

    `private: Any`
    :   Whether the space is private

<a id="SpacesContainsCondition"></a>

`SpacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.SpacesAnyValueFilter`
    :   The type of the None singleton.

<a id="SpacesEqCondition"></a>

`SpacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesFuzzyCondition"></a>

`SpacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.SpacesStringFilter`
    :   The type of the None singleton.

<a id="SpacesGetParams"></a>

`SpacesGetParams(*args, **kwargs)`
:   Parameters for spaces.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `space_id: str`
    :   The type of the None singleton.

<a id="SpacesGtCondition"></a>

`SpacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesGteCondition"></a>

`SpacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesInCondition"></a>

`SpacesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.clickup_api.types.SpacesInFilter`
    :   The type of the None singleton.

<a id="SpacesInFilter"></a>

`SpacesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the space

    `name: list[str]`
    :   Name of the space

    `private: list[bool]`
    :   Whether the space is private

<a id="SpacesKeywordCondition"></a>

`SpacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.SpacesStringFilter`
    :   The type of the None singleton.

<a id="SpacesLikeCondition"></a>

`SpacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.SpacesStringFilter`
    :   The type of the None singleton.

<a id="SpacesListParams"></a>

`SpacesListParams(*args, **kwargs)`
:   Parameters for spaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.

<a id="SpacesLtCondition"></a>

`SpacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesLteCondition"></a>

`SpacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesNeqCondition"></a>

`SpacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesNotCondition"></a>

`SpacesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.clickup_api.types.SpacesEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesInCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAnyCondition`
    :   The type of the None singleton.

<a id="SpacesOrCondition"></a>

`SpacesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.SpacesEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesInCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAnyCondition]`
    :   The type of the None singleton.

<a id="SpacesSearchFilter"></a>

`SpacesSearchFilter(*args, **kwargs)`
:   Available fields for filtering spaces search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str | None`
    :   Unique identifier for the space

    `name: str | None`
    :   Name of the space

    `private: bool | None`
    :   Whether the space is private

<a id="SpacesSearchQuery"></a>

`SpacesSearchQuery(*args, **kwargs)`
:   Search query for spaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.SpacesEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesInCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.SpacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.SpacesSortFilter]`
    :   The type of the None singleton.

<a id="SpacesSortFilter"></a>

`SpacesSortFilter(*args, **kwargs)`
:   Available fields for sorting spaces search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the space

    `name: Literal['asc', 'desc']`
    :   Name of the space

    `private: Literal['asc', 'desc']`
    :   Whether the space is private

<a id="SpacesStringFilter"></a>

`SpacesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the space

    `name: str`
    :   Name of the space

    `private: str`
    :   Whether the space is private

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

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.TasksEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.clickup_api.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksAnyValueFilter"></a>

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_closed: Any`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: Any`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: Any`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: Any`
    :   Due date for the task, in ClickUp timestamp format

    `id: Any`
    :   Unique identifier for the task

    `name: Any`
    :   Name of the task

    `parent: Any`
    :   ID of the parent task, if this task is a subtask

    `start_date: Any`
    :   Start date for the task, in ClickUp timestamp format

    `url: Any`
    :   Permalink URL to view the task in ClickUp

<a id="TasksApiSearchParams"></a>

`TasksApiSearchParams(*args, **kwargs)`
:   Parameters for tasks.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignees: list[str]`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `date_created_gt: int`
    :   The type of the None singleton.

    `date_created_lt: int`
    :   The type of the None singleton.

    `date_updated_gt: int`
    :   The type of the None singleton.

    `date_updated_lt: int`
    :   The type of the None singleton.

    `due_date_gt: int`
    :   The type of the None singleton.

    `due_date_lt: int`
    :   The type of the None singleton.

    `include_closed: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `priority: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `statuses: list[str]`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

<a id="TasksContainsCondition"></a>

`TasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.TasksAnyValueFilter`
    :   The type of the None singleton.

<a id="TasksEqCondition"></a>

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksFuzzyCondition"></a>

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksGetParams"></a>

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_task_ids: bool`
    :   The type of the None singleton.

    `include_subtasks: bool`
    :   The type of the None singleton.

    `task_id: str`
    :   The type of the None singleton.

<a id="TasksGtCondition"></a>

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksGteCondition"></a>

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.TasksSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.clickup_api.types.TasksInFilter`
    :   The type of the None singleton.

<a id="TasksInFilter"></a>

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_closed: list[str]`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: list[str]`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: list[str]`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: list[str]`
    :   Due date for the task, in ClickUp timestamp format

    `id: list[str]`
    :   Unique identifier for the task

    `name: list[str]`
    :   Name of the task

    `parent: list[str]`
    :   ID of the parent task, if this task is a subtask

    `start_date: list[str]`
    :   Start date for the task, in ClickUp timestamp format

    `url: list[str]`
    :   Permalink URL to view the task in ClickUp

<a id="TasksKeywordCondition"></a>

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksLikeCondition"></a>

`TasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.TasksStringFilter`
    :   The type of the None singleton.

<a id="TasksListParams"></a>

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

<a id="TasksLtCondition"></a>

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksLteCondition"></a>

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.TasksSearchFilter`
    :   The type of the None singleton.

<a id="TasksNeqCondition"></a>

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.TasksSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.clickup_api.types.TasksEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.TasksEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAnyCondition]`
    :   The type of the None singleton.

<a id="TasksSearchFilter"></a>

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_closed: str | None`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: str | None`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: str | None`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: str | None`
    :   Due date for the task, in ClickUp timestamp format

    `id: str | None`
    :   Unique identifier for the task

    `name: str | None`
    :   Name of the task

    `parent: str | None`
    :   ID of the parent task, if this task is a subtask

    `start_date: str | None`
    :   Start date for the task, in ClickUp timestamp format

    `url: str | None`
    :   Permalink URL to view the task in ClickUp

<a id="TasksSearchQuery"></a>

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.TasksEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.TasksSortFilter]`
    :   The type of the None singleton.

<a id="TasksSortFilter"></a>

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_closed: Literal['asc', 'desc']`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: Literal['asc', 'desc']`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: Literal['asc', 'desc']`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: Literal['asc', 'desc']`
    :   Due date for the task, in ClickUp timestamp format

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the task

    `name: Literal['asc', 'desc']`
    :   Name of the task

    `parent: Literal['asc', 'desc']`
    :   ID of the parent task, if this task is a subtask

    `start_date: Literal['asc', 'desc']`
    :   Start date for the task, in ClickUp timestamp format

    `url: Literal['asc', 'desc']`
    :   Permalink URL to view the task in ClickUp

<a id="TasksStringFilter"></a>

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `date_closed: str`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: str`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: str`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: str`
    :   Due date for the task, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the task

    `name: str`
    :   Name of the task

    `parent: str`
    :   ID of the parent task, if this task is a subtask

    `start_date: str`
    :   Start date for the task, in ClickUp timestamp format

    `url: str`
    :   Permalink URL to view the task in ClickUp

<a id="TeamsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.TeamsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAnyCondition]`
    :   The type of the None singleton.

<a id="TeamsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.clickup_api.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsAnyValueFilter"></a>

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the team (workspace)

    `name: Any`
    :   Name of the team

<a id="TeamsContainsCondition"></a>

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsEqCondition"></a>

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsFuzzyCondition"></a>

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsGtCondition"></a>

`TeamsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsGteCondition"></a>

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.clickup_api.types.TeamsInFilter`
    :   The type of the None singleton.

<a id="TeamsInFilter"></a>

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the team (workspace)

    `name: list[str]`
    :   Name of the team

<a id="TeamsKeywordCondition"></a>

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsLikeCondition"></a>

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsListParams"></a>

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="TeamsLtCondition"></a>

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsLteCondition"></a>

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsNeqCondition"></a>

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.clickup_api.types.TeamsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAnyCondition`
    :   The type of the None singleton.

<a id="TeamsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.TeamsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAnyCondition]`
    :   The type of the None singleton.

<a id="TeamsSearchFilter"></a>

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str | None`
    :   Unique identifier for the team (workspace)

    `name: str | None`
    :   Name of the team

<a id="TeamsSearchQuery"></a>

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.TeamsEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.TeamsSortFilter]`
    :   The type of the None singleton.

<a id="TeamsSortFilter"></a>

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the team (workspace)

    `name: Literal['asc', 'desc']`
    :   Name of the team

<a id="TeamsStringFilter"></a>

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the team (workspace)

    `name: str`
    :   Name of the team

<a id="TimeTrackingAndCondition"></a>

`TimeTrackingAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAnyCondition]`
    :   The type of the None singleton.

<a id="TimeTrackingAnyCondition"></a>

`TimeTrackingAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeTrackingAnyValueFilter"></a>

`TimeTrackingAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `time: Any`
    :   Total tracked time in milliseconds

    `user: Any`
    :   User who tracked the time

<a id="TimeTrackingContainsCondition"></a>

`TimeTrackingContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAnyValueFilter`
    :   The type of the None singleton.

<a id="TimeTrackingEqCondition"></a>

`TimeTrackingEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSearchFilter`
    :   The type of the None singleton.

<a id="TimeTrackingFuzzyCondition"></a>

`TimeTrackingFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingStringFilter`
    :   The type of the None singleton.

<a id="TimeTrackingGetParams"></a>

`TimeTrackingGetParams(*args, **kwargs)`
:   Parameters for time_tracking.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.

    `time_entry_id: str`
    :   The type of the None singleton.

<a id="TimeTrackingGtCondition"></a>

`TimeTrackingGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSearchFilter`
    :   The type of the None singleton.

<a id="TimeTrackingGteCondition"></a>

`TimeTrackingGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSearchFilter`
    :   The type of the None singleton.

<a id="TimeTrackingInCondition"></a>

`TimeTrackingInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingInFilter`
    :   The type of the None singleton.

<a id="TimeTrackingInFilter"></a>

`TimeTrackingInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `time: list[float]`
    :   Total tracked time in milliseconds

    `user: list[dict[str, typing.Any]]`
    :   User who tracked the time

<a id="TimeTrackingKeywordCondition"></a>

`TimeTrackingKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingStringFilter`
    :   The type of the None singleton.

<a id="TimeTrackingLikeCondition"></a>

`TimeTrackingLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingStringFilter`
    :   The type of the None singleton.

<a id="TimeTrackingListParams"></a>

`TimeTrackingListParams(*args, **kwargs)`
:   Parameters for time_tracking.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   The type of the None singleton.

    `end_date: int`
    :   The type of the None singleton.

    `start_date: int`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

<a id="TimeTrackingLtCondition"></a>

`TimeTrackingLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSearchFilter`
    :   The type of the None singleton.

<a id="TimeTrackingLteCondition"></a>

`TimeTrackingLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSearchFilter`
    :   The type of the None singleton.

<a id="TimeTrackingNeqCondition"></a>

`TimeTrackingNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSearchFilter`
    :   The type of the None singleton.

<a id="TimeTrackingNotCondition"></a>

`TimeTrackingNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAnyCondition`
    :   The type of the None singleton.

<a id="TimeTrackingOrCondition"></a>

`TimeTrackingOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAnyCondition]`
    :   The type of the None singleton.

<a id="TimeTrackingSearchFilter"></a>

`TimeTrackingSearchFilter(*args, **kwargs)`
:   Available fields for filtering time_tracking search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `time: float | None`
    :   Total tracked time in milliseconds

    `user: dict[str, typing.Any] | None`
    :   User who tracked the time

<a id="TimeTrackingSearchQuery"></a>

`TimeTrackingSearchQuery(*args, **kwargs)`
:   Search query for time_tracking entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingInCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.TimeTrackingSortFilter]`
    :   The type of the None singleton.

<a id="TimeTrackingSortFilter"></a>

`TimeTrackingSortFilter(*args, **kwargs)`
:   Available fields for sorting time_tracking search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `time: Literal['asc', 'desc']`
    :   Total tracked time in milliseconds

    `user: Literal['asc', 'desc']`
    :   User who tracked the time

<a id="TimeTrackingStringFilter"></a>

`TimeTrackingStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `time: str`
    :   Total tracked time in milliseconds

    `user: str`
    :   User who tracked the time

<a id="UserAndCondition"></a>

`UserAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.clickup_api.types.UserEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserInCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAnyCondition]`
    :   The type of the None singleton.

<a id="UserAnyCondition"></a>

`UserAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.clickup_api.types.UserAnyValueFilter`
    :   The type of the None singleton.

<a id="UserAnyValueFilter"></a>

`UserAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the user

    `username: Any`
    :   Display name of the user

<a id="UserContainsCondition"></a>

`UserContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.clickup_api.types.UserAnyValueFilter`
    :   The type of the None singleton.

<a id="UserEqCondition"></a>

`UserEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.clickup_api.types.UserSearchFilter`
    :   The type of the None singleton.

<a id="UserFuzzyCondition"></a>

`UserFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.clickup_api.types.UserStringFilter`
    :   The type of the None singleton.

<a id="UserGetParams"></a>

`UserGetParams(*args, **kwargs)`
:   Parameters for user.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="UserGtCondition"></a>

`UserGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.clickup_api.types.UserSearchFilter`
    :   The type of the None singleton.

<a id="UserGteCondition"></a>

`UserGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.clickup_api.types.UserSearchFilter`
    :   The type of the None singleton.

<a id="UserInCondition"></a>

`UserInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.clickup_api.types.UserInFilter`
    :   The type of the None singleton.

<a id="UserInFilter"></a>

`UserInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[int]`
    :   Unique identifier for the user

    `username: list[str]`
    :   Display name of the user

<a id="UserKeywordCondition"></a>

`UserKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.clickup_api.types.UserStringFilter`
    :   The type of the None singleton.

<a id="UserLikeCondition"></a>

`UserLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.clickup_api.types.UserStringFilter`
    :   The type of the None singleton.

<a id="UserLtCondition"></a>

`UserLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.clickup_api.types.UserSearchFilter`
    :   The type of the None singleton.

<a id="UserLteCondition"></a>

`UserLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.clickup_api.types.UserSearchFilter`
    :   The type of the None singleton.

<a id="UserNeqCondition"></a>

`UserNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.clickup_api.types.UserSearchFilter`
    :   The type of the None singleton.

<a id="UserNotCondition"></a>

`UserNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.clickup_api.types.UserEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserInCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAnyCondition`
    :   The type of the None singleton.

<a id="UserOrCondition"></a>

`UserOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.clickup_api.types.UserEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserInCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAnyCondition]`
    :   The type of the None singleton.

<a id="UserSearchFilter"></a>

`UserSearchFilter(*args, **kwargs)`
:   Available fields for filtering user search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int | None`
    :   Unique identifier for the user

    `username: str | None`
    :   Display name of the user

<a id="UserSearchQuery"></a>

`UserSearchQuery(*args, **kwargs)`
:   Search query for user entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.clickup_api.types.UserEqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNeqCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserGteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLtCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLteCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserInCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserLikeCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserFuzzyCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserKeywordCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserContainsCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserNotCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAndCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserOrCondition | airbyte_agent_sdk.connectors.clickup_api.types.UserAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.clickup_api.types.UserSortFilter]`
    :   The type of the None singleton.

<a id="UserSortFilter"></a>

`UserSortFilter(*args, **kwargs)`
:   Available fields for sorting user search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user

    `username: Literal['asc', 'desc']`
    :   Display name of the user

<a id="UserStringFilter"></a>

`UserStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the user

    `username: str`
    :   Display name of the user

<a id="ViewTasksListParams"></a>

`ViewTasksListParams(*args, **kwargs)`
:   Parameters for view_tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `view_id: str`
    :   The type of the None singleton.

<a id="ViewsGetParams"></a>

`ViewsGetParams(*args, **kwargs)`
:   Parameters for views.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `view_id: str`
    :   The type of the None singleton.

<a id="ViewsListParams"></a>

`ViewsListParams(*args, **kwargs)`
:   Parameters for views.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `team_id: str`
    :   The type of the None singleton.