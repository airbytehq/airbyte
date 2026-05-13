---
id: airbyte_agent_sdk-connectors-github-types
title: airbyte_agent_sdk.connectors.github.types
---

Module airbyte_agent_sdk.connectors.github.types
================================================
Type definitions for github connector.

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

<a id="BranchesAndCondition"></a>

`BranchesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.BranchesEqCondition | airbyte_agent_sdk.connectors.github.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.github.types.BranchesGtCondition | airbyte_agent_sdk.connectors.github.types.BranchesGteCondition | airbyte_agent_sdk.connectors.github.types.BranchesLtCondition | airbyte_agent_sdk.connectors.github.types.BranchesLteCondition | airbyte_agent_sdk.connectors.github.types.BranchesInCondition | airbyte_agent_sdk.connectors.github.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.github.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.github.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.github.types.BranchesNotCondition | airbyte_agent_sdk.connectors.github.types.BranchesAndCondition | airbyte_agent_sdk.connectors.github.types.BranchesOrCondition | airbyte_agent_sdk.connectors.github.types.BranchesAnyCondition]`
    :   The type of the None singleton.

<a id="BranchesAnyCondition"></a>

`BranchesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.BranchesAnyValueFilter`
    :   The type of the None singleton.

<a id="BranchesAnyValueFilter"></a>

`BranchesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: Any`
    :   Branch name (e.g. `main`, `feature/foo`)

    `prefix: Any`
    :   Git ref prefix for the branch (typically `refs/heads/`)

<a id="BranchesContainsCondition"></a>

`BranchesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.BranchesAnyValueFilter`
    :   The type of the None singleton.

<a id="BranchesEqCondition"></a>

`BranchesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesFuzzyCondition"></a>

`BranchesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.BranchesStringFilter`
    :   The type of the None singleton.

<a id="BranchesGetParams"></a>

`BranchesGetParams(*args, **kwargs)`
:   Parameters for branches.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `branch: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="BranchesGtCondition"></a>

`BranchesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesGteCondition"></a>

`BranchesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesInCondition"></a>

`BranchesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.BranchesInFilter`
    :   The type of the None singleton.

<a id="BranchesInFilter"></a>

`BranchesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: list[str]`
    :   Branch name (e.g. `main`, `feature/foo`)

    `prefix: list[str]`
    :   Git ref prefix for the branch (typically `refs/heads/`)

<a id="BranchesKeywordCondition"></a>

`BranchesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.BranchesStringFilter`
    :   The type of the None singleton.

<a id="BranchesLikeCondition"></a>

`BranchesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.BranchesStringFilter`
    :   The type of the None singleton.

<a id="BranchesListParams"></a>

`BranchesListParams(*args, **kwargs)`
:   Parameters for branches.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="BranchesLtCondition"></a>

`BranchesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesLteCondition"></a>

`BranchesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesNeqCondition"></a>

`BranchesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesNotCondition"></a>

`BranchesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.BranchesEqCondition | airbyte_agent_sdk.connectors.github.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.github.types.BranchesGtCondition | airbyte_agent_sdk.connectors.github.types.BranchesGteCondition | airbyte_agent_sdk.connectors.github.types.BranchesLtCondition | airbyte_agent_sdk.connectors.github.types.BranchesLteCondition | airbyte_agent_sdk.connectors.github.types.BranchesInCondition | airbyte_agent_sdk.connectors.github.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.github.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.github.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.github.types.BranchesNotCondition | airbyte_agent_sdk.connectors.github.types.BranchesAndCondition | airbyte_agent_sdk.connectors.github.types.BranchesOrCondition | airbyte_agent_sdk.connectors.github.types.BranchesAnyCondition`
    :   The type of the None singleton.

<a id="BranchesOrCondition"></a>

`BranchesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.BranchesEqCondition | airbyte_agent_sdk.connectors.github.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.github.types.BranchesGtCondition | airbyte_agent_sdk.connectors.github.types.BranchesGteCondition | airbyte_agent_sdk.connectors.github.types.BranchesLtCondition | airbyte_agent_sdk.connectors.github.types.BranchesLteCondition | airbyte_agent_sdk.connectors.github.types.BranchesInCondition | airbyte_agent_sdk.connectors.github.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.github.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.github.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.github.types.BranchesNotCondition | airbyte_agent_sdk.connectors.github.types.BranchesAndCondition | airbyte_agent_sdk.connectors.github.types.BranchesOrCondition | airbyte_agent_sdk.connectors.github.types.BranchesAnyCondition]`
    :   The type of the None singleton.

<a id="BranchesSearchFilter"></a>

`BranchesSearchFilter(*args, **kwargs)`
:   Available fields for filtering branches search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str | None`
    :   Branch name (e.g. `main`, `feature/foo`)

    `prefix: str | None`
    :   Git ref prefix for the branch (typically `refs/heads/`)

<a id="BranchesSearchQuery"></a>

`BranchesSearchQuery(*args, **kwargs)`
:   Search query for branches entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.BranchesEqCondition | airbyte_agent_sdk.connectors.github.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.github.types.BranchesGtCondition | airbyte_agent_sdk.connectors.github.types.BranchesGteCondition | airbyte_agent_sdk.connectors.github.types.BranchesLtCondition | airbyte_agent_sdk.connectors.github.types.BranchesLteCondition | airbyte_agent_sdk.connectors.github.types.BranchesInCondition | airbyte_agent_sdk.connectors.github.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.github.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.github.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.github.types.BranchesNotCondition | airbyte_agent_sdk.connectors.github.types.BranchesAndCondition | airbyte_agent_sdk.connectors.github.types.BranchesOrCondition | airbyte_agent_sdk.connectors.github.types.BranchesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.BranchesSortFilter]`
    :   The type of the None singleton.

<a id="BranchesSortFilter"></a>

`BranchesSortFilter(*args, **kwargs)`
:   Available fields for sorting branches search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: Literal['asc', 'desc']`
    :   Branch name (e.g. `main`, `feature/foo`)

    `prefix: Literal['asc', 'desc']`
    :   Git ref prefix for the branch (typically `refs/heads/`)

<a id="BranchesStringFilter"></a>

`BranchesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   Branch name (e.g. `main`, `feature/foo`)

    `prefix: str`
    :   Git ref prefix for the branch (typically `refs/heads/`)

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

    `and: list[airbyte_agent_sdk.connectors.github.types.CommentsEqCondition | airbyte_agent_sdk.connectors.github.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommentsGtCondition | airbyte_agent_sdk.connectors.github.types.CommentsGteCondition | airbyte_agent_sdk.connectors.github.types.CommentsLtCondition | airbyte_agent_sdk.connectors.github.types.CommentsLteCondition | airbyte_agent_sdk.connectors.github.types.CommentsInCondition | airbyte_agent_sdk.connectors.github.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommentsNotCondition | airbyte_agent_sdk.connectors.github.types.CommentsAndCondition | airbyte_agent_sdk.connectors.github.types.CommentsOrCondition | airbyte_agent_sdk.connectors.github.types.CommentsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.github.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsAnyValueFilter"></a>

`CommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: Any`
    :   Markdown body of the comment

    `created_at: Any`
    :   ISO 8601 timestamp when the comment was created

    `database_id: Any`
    :   REST API numeric identifier for the comment

    `id: Any`
    :   GraphQL node ID of the comment

    `is_minimized: Any`
    :   Whether the comment has been hidden/collapsed

    `updated_at: Any`
    :   ISO 8601 timestamp when the comment was last updated

    `url: Any`
    :   Permalink to the comment on GitHub

<a id="CommentsContainsCondition"></a>

`CommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsCreateParams"></a>

`CommentsCreateParams(*args, **kwargs)`
:   Parameters for comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   The type of the None singleton.

    `issue_number: str`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="CommentsEqCondition"></a>

`CommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsFuzzyCondition"></a>

`CommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsGetParams"></a>

`CommentsGetParams(*args, **kwargs)`
:   Parameters for comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="CommentsGtCondition"></a>

`CommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsGteCondition"></a>

`CommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.CommentsInFilter`
    :   The type of the None singleton.

<a id="CommentsInFilter"></a>

`CommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: list[str]`
    :   Markdown body of the comment

    `created_at: list[str]`
    :   ISO 8601 timestamp when the comment was created

    `database_id: list[int]`
    :   REST API numeric identifier for the comment

    `id: list[str]`
    :   GraphQL node ID of the comment

    `is_minimized: list[bool]`
    :   Whether the comment has been hidden/collapsed

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the comment was last updated

    `url: list[str]`
    :   Permalink to the comment on GitHub

<a id="CommentsKeywordCondition"></a>

`CommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsLikeCondition"></a>

`CommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsListParams"></a>

`CommentsListParams(*args, **kwargs)`
:   Parameters for comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="CommentsLtCondition"></a>

`CommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsLteCondition"></a>

`CommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsNeqCondition"></a>

`CommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.CommentsEqCondition | airbyte_agent_sdk.connectors.github.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommentsGtCondition | airbyte_agent_sdk.connectors.github.types.CommentsGteCondition | airbyte_agent_sdk.connectors.github.types.CommentsLtCondition | airbyte_agent_sdk.connectors.github.types.CommentsLteCondition | airbyte_agent_sdk.connectors.github.types.CommentsInCondition | airbyte_agent_sdk.connectors.github.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommentsNotCondition | airbyte_agent_sdk.connectors.github.types.CommentsAndCondition | airbyte_agent_sdk.connectors.github.types.CommentsOrCondition | airbyte_agent_sdk.connectors.github.types.CommentsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.CommentsEqCondition | airbyte_agent_sdk.connectors.github.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommentsGtCondition | airbyte_agent_sdk.connectors.github.types.CommentsGteCondition | airbyte_agent_sdk.connectors.github.types.CommentsLtCondition | airbyte_agent_sdk.connectors.github.types.CommentsLteCondition | airbyte_agent_sdk.connectors.github.types.CommentsInCondition | airbyte_agent_sdk.connectors.github.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommentsNotCondition | airbyte_agent_sdk.connectors.github.types.CommentsAndCondition | airbyte_agent_sdk.connectors.github.types.CommentsOrCondition | airbyte_agent_sdk.connectors.github.types.CommentsAnyCondition]`
    :   The type of the None singleton.

<a id="CommentsSearchFilter"></a>

`CommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str | None`
    :   Markdown body of the comment

    `created_at: str | None`
    :   ISO 8601 timestamp when the comment was created

    `database_id: int | None`
    :   REST API numeric identifier for the comment

    `id: str | None`
    :   GraphQL node ID of the comment

    `is_minimized: bool | None`
    :   Whether the comment has been hidden/collapsed

    `updated_at: str | None`
    :   ISO 8601 timestamp when the comment was last updated

    `url: str | None`
    :   Permalink to the comment on GitHub

<a id="CommentsSearchQuery"></a>

`CommentsSearchQuery(*args, **kwargs)`
:   Search query for comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.CommentsEqCondition | airbyte_agent_sdk.connectors.github.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommentsGtCondition | airbyte_agent_sdk.connectors.github.types.CommentsGteCondition | airbyte_agent_sdk.connectors.github.types.CommentsLtCondition | airbyte_agent_sdk.connectors.github.types.CommentsLteCondition | airbyte_agent_sdk.connectors.github.types.CommentsInCondition | airbyte_agent_sdk.connectors.github.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommentsNotCondition | airbyte_agent_sdk.connectors.github.types.CommentsAndCondition | airbyte_agent_sdk.connectors.github.types.CommentsOrCondition | airbyte_agent_sdk.connectors.github.types.CommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.CommentsSortFilter]`
    :   The type of the None singleton.

<a id="CommentsSortFilter"></a>

`CommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: Literal['asc', 'desc']`
    :   Markdown body of the comment

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the comment was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the comment

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the comment

    `is_minimized: Literal['asc', 'desc']`
    :   Whether the comment has been hidden/collapsed

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the comment was last updated

    `url: Literal['asc', 'desc']`
    :   Permalink to the comment on GitHub

<a id="CommentsStringFilter"></a>

`CommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   Markdown body of the comment

    `created_at: str`
    :   ISO 8601 timestamp when the comment was created

    `database_id: str`
    :   REST API numeric identifier for the comment

    `id: str`
    :   GraphQL node ID of the comment

    `is_minimized: str`
    :   Whether the comment has been hidden/collapsed

    `updated_at: str`
    :   ISO 8601 timestamp when the comment was last updated

    `url: str`
    :   Permalink to the comment on GitHub

<a id="CommitsAndCondition"></a>

`CommitsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.CommitsEqCondition | airbyte_agent_sdk.connectors.github.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommitsGtCondition | airbyte_agent_sdk.connectors.github.types.CommitsGteCondition | airbyte_agent_sdk.connectors.github.types.CommitsLtCondition | airbyte_agent_sdk.connectors.github.types.CommitsLteCondition | airbyte_agent_sdk.connectors.github.types.CommitsInCondition | airbyte_agent_sdk.connectors.github.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommitsNotCondition | airbyte_agent_sdk.connectors.github.types.CommitsAndCondition | airbyte_agent_sdk.connectors.github.types.CommitsOrCondition | airbyte_agent_sdk.connectors.github.types.CommitsAnyCondition]`
    :   The type of the None singleton.

<a id="CommitsAnyCondition"></a>

`CommitsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.CommitsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommitsAnyValueFilter"></a>

`CommitsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `abbreviated_oid: Any`
    :   Abbreviated Git commit SHA (typically 7 characters)

    `additions: Any`
    :   Number of lines added across all files in the commit

    `authored_date: Any`
    :   ISO 8601 timestamp when the commit was originally authored

    `changed_files: Any`
    :   Number of files changed in the commit

    `committed_date: Any`
    :   ISO 8601 timestamp when the commit was applied to its tree

    `deletions: Any`
    :   Number of lines deleted across all files in the commit

    `message: Any`
    :   Full commit message

    `message_headline: Any`
    :   First line of the commit message

    `oid: Any`
    :   Full Git commit SHA

    `url: Any`
    :   Permalink to the commit on GitHub

<a id="CommitsContainsCondition"></a>

`CommitsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.CommitsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommitsEqCondition"></a>

`CommitsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsFuzzyCondition"></a>

`CommitsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.CommitsStringFilter`
    :   The type of the None singleton.

<a id="CommitsGetParams"></a>

`CommitsGetParams(*args, **kwargs)`
:   Parameters for commits.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `sha: str`
    :   The type of the None singleton.

<a id="CommitsGtCondition"></a>

`CommitsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsGteCondition"></a>

`CommitsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsInCondition"></a>

`CommitsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.CommitsInFilter`
    :   The type of the None singleton.

<a id="CommitsInFilter"></a>

`CommitsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `abbreviated_oid: list[str]`
    :   Abbreviated Git commit SHA (typically 7 characters)

    `additions: list[int]`
    :   Number of lines added across all files in the commit

    `authored_date: list[str]`
    :   ISO 8601 timestamp when the commit was originally authored

    `changed_files: list[int]`
    :   Number of files changed in the commit

    `committed_date: list[str]`
    :   ISO 8601 timestamp when the commit was applied to its tree

    `deletions: list[int]`
    :   Number of lines deleted across all files in the commit

    `message: list[str]`
    :   Full commit message

    `message_headline: list[str]`
    :   First line of the commit message

    `oid: list[str]`
    :   Full Git commit SHA

    `url: list[str]`
    :   Permalink to the commit on GitHub

<a id="CommitsKeywordCondition"></a>

`CommitsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.CommitsStringFilter`
    :   The type of the None singleton.

<a id="CommitsLikeCondition"></a>

`CommitsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.CommitsStringFilter`
    :   The type of the None singleton.

<a id="CommitsListParams"></a>

`CommitsListParams(*args, **kwargs)`
:   Parameters for commits.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `path: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="CommitsLtCondition"></a>

`CommitsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsLteCondition"></a>

`CommitsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsNeqCondition"></a>

`CommitsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsNotCondition"></a>

`CommitsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.CommitsEqCondition | airbyte_agent_sdk.connectors.github.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommitsGtCondition | airbyte_agent_sdk.connectors.github.types.CommitsGteCondition | airbyte_agent_sdk.connectors.github.types.CommitsLtCondition | airbyte_agent_sdk.connectors.github.types.CommitsLteCondition | airbyte_agent_sdk.connectors.github.types.CommitsInCondition | airbyte_agent_sdk.connectors.github.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommitsNotCondition | airbyte_agent_sdk.connectors.github.types.CommitsAndCondition | airbyte_agent_sdk.connectors.github.types.CommitsOrCondition | airbyte_agent_sdk.connectors.github.types.CommitsAnyCondition`
    :   The type of the None singleton.

<a id="CommitsOrCondition"></a>

`CommitsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.CommitsEqCondition | airbyte_agent_sdk.connectors.github.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommitsGtCondition | airbyte_agent_sdk.connectors.github.types.CommitsGteCondition | airbyte_agent_sdk.connectors.github.types.CommitsLtCondition | airbyte_agent_sdk.connectors.github.types.CommitsLteCondition | airbyte_agent_sdk.connectors.github.types.CommitsInCondition | airbyte_agent_sdk.connectors.github.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommitsNotCondition | airbyte_agent_sdk.connectors.github.types.CommitsAndCondition | airbyte_agent_sdk.connectors.github.types.CommitsOrCondition | airbyte_agent_sdk.connectors.github.types.CommitsAnyCondition]`
    :   The type of the None singleton.

<a id="CommitsSearchFilter"></a>

`CommitsSearchFilter(*args, **kwargs)`
:   Available fields for filtering commits search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `abbreviated_oid: str | None`
    :   Abbreviated Git commit SHA (typically 7 characters)

    `additions: int | None`
    :   Number of lines added across all files in the commit

    `authored_date: str | None`
    :   ISO 8601 timestamp when the commit was originally authored

    `changed_files: int | None`
    :   Number of files changed in the commit

    `committed_date: str | None`
    :   ISO 8601 timestamp when the commit was applied to its tree

    `deletions: int | None`
    :   Number of lines deleted across all files in the commit

    `message: str | None`
    :   Full commit message

    `message_headline: str | None`
    :   First line of the commit message

    `oid: str | None`
    :   Full Git commit SHA

    `url: str | None`
    :   Permalink to the commit on GitHub

<a id="CommitsSearchQuery"></a>

`CommitsSearchQuery(*args, **kwargs)`
:   Search query for commits entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.CommitsEqCondition | airbyte_agent_sdk.connectors.github.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommitsGtCondition | airbyte_agent_sdk.connectors.github.types.CommitsGteCondition | airbyte_agent_sdk.connectors.github.types.CommitsLtCondition | airbyte_agent_sdk.connectors.github.types.CommitsLteCondition | airbyte_agent_sdk.connectors.github.types.CommitsInCondition | airbyte_agent_sdk.connectors.github.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommitsNotCondition | airbyte_agent_sdk.connectors.github.types.CommitsAndCondition | airbyte_agent_sdk.connectors.github.types.CommitsOrCondition | airbyte_agent_sdk.connectors.github.types.CommitsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.CommitsSortFilter]`
    :   The type of the None singleton.

<a id="CommitsSortFilter"></a>

`CommitsSortFilter(*args, **kwargs)`
:   Available fields for sorting commits search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `abbreviated_oid: Literal['asc', 'desc']`
    :   Abbreviated Git commit SHA (typically 7 characters)

    `additions: Literal['asc', 'desc']`
    :   Number of lines added across all files in the commit

    `authored_date: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the commit was originally authored

    `changed_files: Literal['asc', 'desc']`
    :   Number of files changed in the commit

    `committed_date: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the commit was applied to its tree

    `deletions: Literal['asc', 'desc']`
    :   Number of lines deleted across all files in the commit

    `message: Literal['asc', 'desc']`
    :   Full commit message

    `message_headline: Literal['asc', 'desc']`
    :   First line of the commit message

    `oid: Literal['asc', 'desc']`
    :   Full Git commit SHA

    `url: Literal['asc', 'desc']`
    :   Permalink to the commit on GitHub

<a id="CommitsStringFilter"></a>

`CommitsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `abbreviated_oid: str`
    :   Abbreviated Git commit SHA (typically 7 characters)

    `additions: str`
    :   Number of lines added across all files in the commit

    `authored_date: str`
    :   ISO 8601 timestamp when the commit was originally authored

    `changed_files: str`
    :   Number of files changed in the commit

    `committed_date: str`
    :   ISO 8601 timestamp when the commit was applied to its tree

    `deletions: str`
    :   Number of lines deleted across all files in the commit

    `message: str`
    :   Full commit message

    `message_headline: str`
    :   First line of the commit message

    `oid: str`
    :   Full Git commit SHA

    `url: str`
    :   Permalink to the commit on GitHub

<a id="DirectoryContentAndCondition"></a>

`DirectoryContentAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.DirectoryContentEqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNeqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentInCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLikeCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentContainsCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNotCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAndCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentOrCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAnyCondition]`
    :   The type of the None singleton.

<a id="DirectoryContentAnyCondition"></a>

`DirectoryContentAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.DirectoryContentAnyValueFilter`
    :   The type of the None singleton.

<a id="DirectoryContentAnyValueFilter"></a>

`DirectoryContentAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DirectoryContentContainsCondition"></a>

`DirectoryContentContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.DirectoryContentAnyValueFilter`
    :   The type of the None singleton.

<a id="DirectoryContentEqCondition"></a>

`DirectoryContentEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.DirectoryContentSearchFilter`
    :   The type of the None singleton.

<a id="DirectoryContentFuzzyCondition"></a>

`DirectoryContentFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.DirectoryContentStringFilter`
    :   The type of the None singleton.

<a id="DirectoryContentGtCondition"></a>

`DirectoryContentGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.DirectoryContentSearchFilter`
    :   The type of the None singleton.

<a id="DirectoryContentGteCondition"></a>

`DirectoryContentGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.DirectoryContentSearchFilter`
    :   The type of the None singleton.

<a id="DirectoryContentInCondition"></a>

`DirectoryContentInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.DirectoryContentInFilter`
    :   The type of the None singleton.

<a id="DirectoryContentInFilter"></a>

`DirectoryContentInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DirectoryContentKeywordCondition"></a>

`DirectoryContentKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.DirectoryContentStringFilter`
    :   The type of the None singleton.

<a id="DirectoryContentLikeCondition"></a>

`DirectoryContentLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.DirectoryContentStringFilter`
    :   The type of the None singleton.

<a id="DirectoryContentListParams"></a>

`DirectoryContentListParams(*args, **kwargs)`
:   Parameters for directory_content.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `path: str`
    :   The type of the None singleton.

    `ref: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="DirectoryContentLtCondition"></a>

`DirectoryContentLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.DirectoryContentSearchFilter`
    :   The type of the None singleton.

<a id="DirectoryContentLteCondition"></a>

`DirectoryContentLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.DirectoryContentSearchFilter`
    :   The type of the None singleton.

<a id="DirectoryContentNeqCondition"></a>

`DirectoryContentNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.DirectoryContentSearchFilter`
    :   The type of the None singleton.

<a id="DirectoryContentNotCondition"></a>

`DirectoryContentNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.DirectoryContentEqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNeqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentInCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLikeCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentContainsCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNotCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAndCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentOrCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAnyCondition`
    :   The type of the None singleton.

<a id="DirectoryContentOrCondition"></a>

`DirectoryContentOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.DirectoryContentEqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNeqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentInCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLikeCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentContainsCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNotCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAndCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentOrCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAnyCondition]`
    :   The type of the None singleton.

<a id="DirectoryContentSearchFilter"></a>

`DirectoryContentSearchFilter(*args, **kwargs)`
:   Available fields for filtering directory_content search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DirectoryContentSearchQuery"></a>

`DirectoryContentSearchQuery(*args, **kwargs)`
:   Search query for directory_content entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.DirectoryContentEqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNeqCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentGteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLtCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLteCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentInCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentLikeCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentContainsCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentNotCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAndCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentOrCondition | airbyte_agent_sdk.connectors.github.types.DirectoryContentAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.DirectoryContentSortFilter]`
    :   The type of the None singleton.

<a id="DirectoryContentSortFilter"></a>

`DirectoryContentSortFilter(*args, **kwargs)`
:   Available fields for sorting directory_content search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DirectoryContentStringFilter"></a>

`DirectoryContentStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DiscussionsAndCondition"></a>

`DiscussionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.DiscussionsEqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNeqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsInCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLikeCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsKeywordCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsContainsCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNotCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAndCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsOrCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAnyCondition]`
    :   The type of the None singleton.

<a id="DiscussionsAnyCondition"></a>

`DiscussionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.DiscussionsAnyValueFilter`
    :   The type of the None singleton.

<a id="DiscussionsAnyValueFilter"></a>

`DiscussionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DiscussionsApiSearchParams"></a>

`DiscussionsApiSearchParams(*args, **kwargs)`
:   Parameters for discussions.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="DiscussionsContainsCondition"></a>

`DiscussionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.DiscussionsAnyValueFilter`
    :   The type of the None singleton.

<a id="DiscussionsEqCondition"></a>

`DiscussionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.DiscussionsSearchFilter`
    :   The type of the None singleton.

<a id="DiscussionsFuzzyCondition"></a>

`DiscussionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.DiscussionsStringFilter`
    :   The type of the None singleton.

<a id="DiscussionsGetParams"></a>

`DiscussionsGetParams(*args, **kwargs)`
:   Parameters for discussions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="DiscussionsGtCondition"></a>

`DiscussionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.DiscussionsSearchFilter`
    :   The type of the None singleton.

<a id="DiscussionsGteCondition"></a>

`DiscussionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.DiscussionsSearchFilter`
    :   The type of the None singleton.

<a id="DiscussionsInCondition"></a>

`DiscussionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.DiscussionsInFilter`
    :   The type of the None singleton.

<a id="DiscussionsInFilter"></a>

`DiscussionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DiscussionsKeywordCondition"></a>

`DiscussionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.DiscussionsStringFilter`
    :   The type of the None singleton.

<a id="DiscussionsLikeCondition"></a>

`DiscussionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.DiscussionsStringFilter`
    :   The type of the None singleton.

<a id="DiscussionsListParams"></a>

`DiscussionsListParams(*args, **kwargs)`
:   Parameters for discussions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `answered: bool`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `states: list[str]`
    :   The type of the None singleton.

<a id="DiscussionsLtCondition"></a>

`DiscussionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.DiscussionsSearchFilter`
    :   The type of the None singleton.

<a id="DiscussionsLteCondition"></a>

`DiscussionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.DiscussionsSearchFilter`
    :   The type of the None singleton.

<a id="DiscussionsNeqCondition"></a>

`DiscussionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.DiscussionsSearchFilter`
    :   The type of the None singleton.

<a id="DiscussionsNotCondition"></a>

`DiscussionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.DiscussionsEqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNeqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsInCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLikeCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsKeywordCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsContainsCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNotCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAndCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsOrCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAnyCondition`
    :   The type of the None singleton.

<a id="DiscussionsOrCondition"></a>

`DiscussionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.DiscussionsEqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNeqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsInCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLikeCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsKeywordCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsContainsCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNotCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAndCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsOrCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAnyCondition]`
    :   The type of the None singleton.

<a id="DiscussionsSearchFilter"></a>

`DiscussionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering discussions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DiscussionsSearchQuery"></a>

`DiscussionsSearchQuery(*args, **kwargs)`
:   Search query for discussions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.DiscussionsEqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNeqCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsGteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLtCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLteCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsInCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsLikeCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsKeywordCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsContainsCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsNotCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAndCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsOrCondition | airbyte_agent_sdk.connectors.github.types.DiscussionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.DiscussionsSortFilter]`
    :   The type of the None singleton.

<a id="DiscussionsSortFilter"></a>

`DiscussionsSortFilter(*args, **kwargs)`
:   Available fields for sorting discussions search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="DiscussionsStringFilter"></a>

`DiscussionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="FileContentAndCondition"></a>

`FileContentAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.FileContentEqCondition | airbyte_agent_sdk.connectors.github.types.FileContentNeqCondition | airbyte_agent_sdk.connectors.github.types.FileContentGtCondition | airbyte_agent_sdk.connectors.github.types.FileContentGteCondition | airbyte_agent_sdk.connectors.github.types.FileContentLtCondition | airbyte_agent_sdk.connectors.github.types.FileContentLteCondition | airbyte_agent_sdk.connectors.github.types.FileContentInCondition | airbyte_agent_sdk.connectors.github.types.FileContentLikeCondition | airbyte_agent_sdk.connectors.github.types.FileContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.FileContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.FileContentContainsCondition | airbyte_agent_sdk.connectors.github.types.FileContentNotCondition | airbyte_agent_sdk.connectors.github.types.FileContentAndCondition | airbyte_agent_sdk.connectors.github.types.FileContentOrCondition | airbyte_agent_sdk.connectors.github.types.FileContentAnyCondition]`
    :   The type of the None singleton.

<a id="FileContentAnyCondition"></a>

`FileContentAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.FileContentAnyValueFilter`
    :   The type of the None singleton.

<a id="FileContentAnyValueFilter"></a>

`FileContentAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="FileContentContainsCondition"></a>

`FileContentContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.FileContentAnyValueFilter`
    :   The type of the None singleton.

<a id="FileContentEqCondition"></a>

`FileContentEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.FileContentSearchFilter`
    :   The type of the None singleton.

<a id="FileContentFuzzyCondition"></a>

`FileContentFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.FileContentStringFilter`
    :   The type of the None singleton.

<a id="FileContentGetParams"></a>

`FileContentGetParams(*args, **kwargs)`
:   Parameters for file_content.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `path: str`
    :   The type of the None singleton.

    `ref: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="FileContentGtCondition"></a>

`FileContentGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.FileContentSearchFilter`
    :   The type of the None singleton.

<a id="FileContentGteCondition"></a>

`FileContentGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.FileContentSearchFilter`
    :   The type of the None singleton.

<a id="FileContentInCondition"></a>

`FileContentInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.FileContentInFilter`
    :   The type of the None singleton.

<a id="FileContentInFilter"></a>

`FileContentInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="FileContentKeywordCondition"></a>

`FileContentKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.FileContentStringFilter`
    :   The type of the None singleton.

<a id="FileContentLikeCondition"></a>

`FileContentLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.FileContentStringFilter`
    :   The type of the None singleton.

<a id="FileContentLtCondition"></a>

`FileContentLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.FileContentSearchFilter`
    :   The type of the None singleton.

<a id="FileContentLteCondition"></a>

`FileContentLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.FileContentSearchFilter`
    :   The type of the None singleton.

<a id="FileContentNeqCondition"></a>

`FileContentNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.FileContentSearchFilter`
    :   The type of the None singleton.

<a id="FileContentNotCondition"></a>

`FileContentNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.FileContentEqCondition | airbyte_agent_sdk.connectors.github.types.FileContentNeqCondition | airbyte_agent_sdk.connectors.github.types.FileContentGtCondition | airbyte_agent_sdk.connectors.github.types.FileContentGteCondition | airbyte_agent_sdk.connectors.github.types.FileContentLtCondition | airbyte_agent_sdk.connectors.github.types.FileContentLteCondition | airbyte_agent_sdk.connectors.github.types.FileContentInCondition | airbyte_agent_sdk.connectors.github.types.FileContentLikeCondition | airbyte_agent_sdk.connectors.github.types.FileContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.FileContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.FileContentContainsCondition | airbyte_agent_sdk.connectors.github.types.FileContentNotCondition | airbyte_agent_sdk.connectors.github.types.FileContentAndCondition | airbyte_agent_sdk.connectors.github.types.FileContentOrCondition | airbyte_agent_sdk.connectors.github.types.FileContentAnyCondition`
    :   The type of the None singleton.

<a id="FileContentOrCondition"></a>

`FileContentOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.FileContentEqCondition | airbyte_agent_sdk.connectors.github.types.FileContentNeqCondition | airbyte_agent_sdk.connectors.github.types.FileContentGtCondition | airbyte_agent_sdk.connectors.github.types.FileContentGteCondition | airbyte_agent_sdk.connectors.github.types.FileContentLtCondition | airbyte_agent_sdk.connectors.github.types.FileContentLteCondition | airbyte_agent_sdk.connectors.github.types.FileContentInCondition | airbyte_agent_sdk.connectors.github.types.FileContentLikeCondition | airbyte_agent_sdk.connectors.github.types.FileContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.FileContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.FileContentContainsCondition | airbyte_agent_sdk.connectors.github.types.FileContentNotCondition | airbyte_agent_sdk.connectors.github.types.FileContentAndCondition | airbyte_agent_sdk.connectors.github.types.FileContentOrCondition | airbyte_agent_sdk.connectors.github.types.FileContentAnyCondition]`
    :   The type of the None singleton.

<a id="FileContentSearchFilter"></a>

`FileContentSearchFilter(*args, **kwargs)`
:   Available fields for filtering file_content search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="FileContentSearchQuery"></a>

`FileContentSearchQuery(*args, **kwargs)`
:   Search query for file_content entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.FileContentEqCondition | airbyte_agent_sdk.connectors.github.types.FileContentNeqCondition | airbyte_agent_sdk.connectors.github.types.FileContentGtCondition | airbyte_agent_sdk.connectors.github.types.FileContentGteCondition | airbyte_agent_sdk.connectors.github.types.FileContentLtCondition | airbyte_agent_sdk.connectors.github.types.FileContentLteCondition | airbyte_agent_sdk.connectors.github.types.FileContentInCondition | airbyte_agent_sdk.connectors.github.types.FileContentLikeCondition | airbyte_agent_sdk.connectors.github.types.FileContentFuzzyCondition | airbyte_agent_sdk.connectors.github.types.FileContentKeywordCondition | airbyte_agent_sdk.connectors.github.types.FileContentContainsCondition | airbyte_agent_sdk.connectors.github.types.FileContentNotCondition | airbyte_agent_sdk.connectors.github.types.FileContentAndCondition | airbyte_agent_sdk.connectors.github.types.FileContentOrCondition | airbyte_agent_sdk.connectors.github.types.FileContentAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.FileContentSortFilter]`
    :   The type of the None singleton.

<a id="FileContentSortFilter"></a>

`FileContentSortFilter(*args, **kwargs)`
:   Available fields for sorting file_content search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="FileContentStringFilter"></a>

`FileContentStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="IssuesAndCondition"></a>

`IssuesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.IssuesEqCondition | airbyte_agent_sdk.connectors.github.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.github.types.IssuesGtCondition | airbyte_agent_sdk.connectors.github.types.IssuesGteCondition | airbyte_agent_sdk.connectors.github.types.IssuesLtCondition | airbyte_agent_sdk.connectors.github.types.IssuesLteCondition | airbyte_agent_sdk.connectors.github.types.IssuesInCondition | airbyte_agent_sdk.connectors.github.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.github.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.github.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.github.types.IssuesNotCondition | airbyte_agent_sdk.connectors.github.types.IssuesAndCondition | airbyte_agent_sdk.connectors.github.types.IssuesOrCondition | airbyte_agent_sdk.connectors.github.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesAnyCondition"></a>

`IssuesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesAnyValueFilter"></a>

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: Any`
    :   ISO 8601 timestamp when the issue was closed, if applicable

    `created_at: Any`
    :   ISO 8601 timestamp when the issue was created

    `database_id: Any`
    :   REST API numeric identifier for the issue

    `id: Any`
    :   GraphQL node ID of the issue

    `locked: Any`
    :   Whether the conversation on the issue is locked

    `number: Any`
    :   Repository-scoped issue number

    `state: Any`
    :   Issue state: `OPEN` or `CLOSED`

    `state_reason: Any`
    :   Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)

    `title: Any`
    :   Issue title

    `updated_at: Any`
    :   ISO 8601 timestamp when the issue was last updated

    `url: Any`
    :   Permalink to the issue on GitHub

<a id="IssuesApiSearchParams"></a>

`IssuesApiSearchParams(*args, **kwargs)`
:   Parameters for issues.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="IssuesContainsCondition"></a>

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesCreateParams"></a>

`IssuesCreateParams(*args, **kwargs)`
:   Parameters for issues.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignees: list[str]`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `labels: list[str]`
    :   The type of the None singleton.

    `milestone: int | None`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="IssuesEqCondition"></a>

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesFuzzyCondition"></a>

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesGetParams"></a>

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="IssuesGtCondition"></a>

`IssuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesGteCondition"></a>

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesInCondition"></a>

`IssuesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.IssuesInFilter`
    :   The type of the None singleton.

<a id="IssuesInFilter"></a>

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: list[str]`
    :   ISO 8601 timestamp when the issue was closed, if applicable

    `created_at: list[str]`
    :   ISO 8601 timestamp when the issue was created

    `database_id: list[int]`
    :   REST API numeric identifier for the issue

    `id: list[str]`
    :   GraphQL node ID of the issue

    `locked: list[bool]`
    :   Whether the conversation on the issue is locked

    `number: list[int]`
    :   Repository-scoped issue number

    `state: list[str]`
    :   Issue state: `OPEN` or `CLOSED`

    `state_reason: list[str]`
    :   Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)

    `title: list[str]`
    :   Issue title

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the issue was last updated

    `url: list[str]`
    :   Permalink to the issue on GitHub

<a id="IssuesKeywordCondition"></a>

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLikeCondition"></a>

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesListParams"></a>

`IssuesListParams(*args, **kwargs)`
:   Parameters for issues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `states: list[str]`
    :   The type of the None singleton.

<a id="IssuesLtCondition"></a>

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesLteCondition"></a>

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNeqCondition"></a>

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNotCondition"></a>

`IssuesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.IssuesEqCondition | airbyte_agent_sdk.connectors.github.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.github.types.IssuesGtCondition | airbyte_agent_sdk.connectors.github.types.IssuesGteCondition | airbyte_agent_sdk.connectors.github.types.IssuesLtCondition | airbyte_agent_sdk.connectors.github.types.IssuesLteCondition | airbyte_agent_sdk.connectors.github.types.IssuesInCondition | airbyte_agent_sdk.connectors.github.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.github.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.github.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.github.types.IssuesNotCondition | airbyte_agent_sdk.connectors.github.types.IssuesAndCondition | airbyte_agent_sdk.connectors.github.types.IssuesOrCondition | airbyte_agent_sdk.connectors.github.types.IssuesAnyCondition`
    :   The type of the None singleton.

<a id="IssuesOrCondition"></a>

`IssuesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.IssuesEqCondition | airbyte_agent_sdk.connectors.github.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.github.types.IssuesGtCondition | airbyte_agent_sdk.connectors.github.types.IssuesGteCondition | airbyte_agent_sdk.connectors.github.types.IssuesLtCondition | airbyte_agent_sdk.connectors.github.types.IssuesLteCondition | airbyte_agent_sdk.connectors.github.types.IssuesInCondition | airbyte_agent_sdk.connectors.github.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.github.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.github.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.github.types.IssuesNotCondition | airbyte_agent_sdk.connectors.github.types.IssuesAndCondition | airbyte_agent_sdk.connectors.github.types.IssuesOrCondition | airbyte_agent_sdk.connectors.github.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesSearchFilter"></a>

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: str | None`
    :   ISO 8601 timestamp when the issue was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the issue was created

    `database_id: int | None`
    :   REST API numeric identifier for the issue

    `id: str | None`
    :   GraphQL node ID of the issue

    `locked: bool | None`
    :   Whether the conversation on the issue is locked

    `number: int | None`
    :   Repository-scoped issue number

    `state: str | None`
    :   Issue state: `OPEN` or `CLOSED`

    `state_reason: str | None`
    :   Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)

    `title: str | None`
    :   Issue title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the issue was last updated

    `url: str | None`
    :   Permalink to the issue on GitHub

<a id="IssuesSearchQuery"></a>

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.IssuesEqCondition | airbyte_agent_sdk.connectors.github.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.github.types.IssuesGtCondition | airbyte_agent_sdk.connectors.github.types.IssuesGteCondition | airbyte_agent_sdk.connectors.github.types.IssuesLtCondition | airbyte_agent_sdk.connectors.github.types.IssuesLteCondition | airbyte_agent_sdk.connectors.github.types.IssuesInCondition | airbyte_agent_sdk.connectors.github.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.github.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.github.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.github.types.IssuesNotCondition | airbyte_agent_sdk.connectors.github.types.IssuesAndCondition | airbyte_agent_sdk.connectors.github.types.IssuesOrCondition | airbyte_agent_sdk.connectors.github.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.IssuesSortFilter]`
    :   The type of the None singleton.

<a id="IssuesSortFilter"></a>

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the issue was closed, if applicable

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the issue was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the issue

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the issue

    `locked: Literal['asc', 'desc']`
    :   Whether the conversation on the issue is locked

    `number: Literal['asc', 'desc']`
    :   Repository-scoped issue number

    `state: Literal['asc', 'desc']`
    :   Issue state: `OPEN` or `CLOSED`

    `state_reason: Literal['asc', 'desc']`
    :   Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)

    `title: Literal['asc', 'desc']`
    :   Issue title

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the issue was last updated

    `url: Literal['asc', 'desc']`
    :   Permalink to the issue on GitHub

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: str`
    :   ISO 8601 timestamp when the issue was closed, if applicable

    `created_at: str`
    :   ISO 8601 timestamp when the issue was created

    `database_id: str`
    :   REST API numeric identifier for the issue

    `id: str`
    :   GraphQL node ID of the issue

    `locked: str`
    :   Whether the conversation on the issue is locked

    `number: str`
    :   Repository-scoped issue number

    `state: str`
    :   Issue state: `OPEN` or `CLOSED`

    `state_reason: str`
    :   Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)

    `title: str`
    :   Issue title

    `updated_at: str`
    :   ISO 8601 timestamp when the issue was last updated

    `url: str`
    :   Permalink to the issue on GitHub

<a id="IssuesUpdateParams"></a>

`IssuesUpdateParams(*args, **kwargs)`
:   Parameters for issues.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignees: list[str]`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `issue_number: str`
    :   The type of the None singleton.

    `labels: list[str]`
    :   The type of the None singleton.

    `milestone: int | None`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `state_reason: str | None`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="LabelsAndCondition"></a>

`LabelsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.LabelsEqCondition | airbyte_agent_sdk.connectors.github.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.github.types.LabelsGtCondition | airbyte_agent_sdk.connectors.github.types.LabelsGteCondition | airbyte_agent_sdk.connectors.github.types.LabelsLtCondition | airbyte_agent_sdk.connectors.github.types.LabelsLteCondition | airbyte_agent_sdk.connectors.github.types.LabelsInCondition | airbyte_agent_sdk.connectors.github.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.github.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.github.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.github.types.LabelsNotCondition | airbyte_agent_sdk.connectors.github.types.LabelsAndCondition | airbyte_agent_sdk.connectors.github.types.LabelsOrCondition | airbyte_agent_sdk.connectors.github.types.LabelsAnyCondition]`
    :   The type of the None singleton.

<a id="LabelsAnyCondition"></a>

`LabelsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.LabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="LabelsAnyValueFilter"></a>

`LabelsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Any`
    :   Label color as a 6-character hex string without a leading `#`

    `created_at: Any`
    :   ISO 8601 timestamp when the label was created

    `description: Any`
    :   Short description of what the label is used for

    `id: Any`
    :   GraphQL node ID of the label

    `name: Any`
    :   Label name

    `url: Any`
    :   Permalink to the label on GitHub

<a id="LabelsContainsCondition"></a>

`LabelsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.LabelsAnyValueFilter`
    :   The type of the None singleton.

<a id="LabelsEqCondition"></a>

`LabelsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsFuzzyCondition"></a>

`LabelsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.LabelsStringFilter`
    :   The type of the None singleton.

<a id="LabelsGetParams"></a>

`LabelsGetParams(*args, **kwargs)`
:   Parameters for labels.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="LabelsGtCondition"></a>

`LabelsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsGteCondition"></a>

`LabelsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsInCondition"></a>

`LabelsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.LabelsInFilter`
    :   The type of the None singleton.

<a id="LabelsInFilter"></a>

`LabelsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: list[str]`
    :   Label color as a 6-character hex string without a leading `#`

    `created_at: list[str]`
    :   ISO 8601 timestamp when the label was created

    `description: list[str]`
    :   Short description of what the label is used for

    `id: list[str]`
    :   GraphQL node ID of the label

    `name: list[str]`
    :   Label name

    `url: list[str]`
    :   Permalink to the label on GitHub

<a id="LabelsKeywordCondition"></a>

`LabelsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.LabelsStringFilter`
    :   The type of the None singleton.

<a id="LabelsLikeCondition"></a>

`LabelsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.LabelsStringFilter`
    :   The type of the None singleton.

<a id="LabelsListParams"></a>

`LabelsListParams(*args, **kwargs)`
:   Parameters for labels.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="LabelsLtCondition"></a>

`LabelsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsLteCondition"></a>

`LabelsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsNeqCondition"></a>

`LabelsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.LabelsSearchFilter`
    :   The type of the None singleton.

<a id="LabelsNotCondition"></a>

`LabelsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.LabelsEqCondition | airbyte_agent_sdk.connectors.github.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.github.types.LabelsGtCondition | airbyte_agent_sdk.connectors.github.types.LabelsGteCondition | airbyte_agent_sdk.connectors.github.types.LabelsLtCondition | airbyte_agent_sdk.connectors.github.types.LabelsLteCondition | airbyte_agent_sdk.connectors.github.types.LabelsInCondition | airbyte_agent_sdk.connectors.github.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.github.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.github.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.github.types.LabelsNotCondition | airbyte_agent_sdk.connectors.github.types.LabelsAndCondition | airbyte_agent_sdk.connectors.github.types.LabelsOrCondition | airbyte_agent_sdk.connectors.github.types.LabelsAnyCondition`
    :   The type of the None singleton.

<a id="LabelsOrCondition"></a>

`LabelsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.LabelsEqCondition | airbyte_agent_sdk.connectors.github.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.github.types.LabelsGtCondition | airbyte_agent_sdk.connectors.github.types.LabelsGteCondition | airbyte_agent_sdk.connectors.github.types.LabelsLtCondition | airbyte_agent_sdk.connectors.github.types.LabelsLteCondition | airbyte_agent_sdk.connectors.github.types.LabelsInCondition | airbyte_agent_sdk.connectors.github.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.github.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.github.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.github.types.LabelsNotCondition | airbyte_agent_sdk.connectors.github.types.LabelsAndCondition | airbyte_agent_sdk.connectors.github.types.LabelsOrCondition | airbyte_agent_sdk.connectors.github.types.LabelsAnyCondition]`
    :   The type of the None singleton.

<a id="LabelsSearchFilter"></a>

`LabelsSearchFilter(*args, **kwargs)`
:   Available fields for filtering labels search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str | None`
    :   Label color as a 6-character hex string without a leading `#`

    `created_at: str | None`
    :   ISO 8601 timestamp when the label was created

    `description: str | None`
    :   Short description of what the label is used for

    `id: str | None`
    :   GraphQL node ID of the label

    `name: str | None`
    :   Label name

    `url: str | None`
    :   Permalink to the label on GitHub

<a id="LabelsSearchQuery"></a>

`LabelsSearchQuery(*args, **kwargs)`
:   Search query for labels entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.LabelsEqCondition | airbyte_agent_sdk.connectors.github.types.LabelsNeqCondition | airbyte_agent_sdk.connectors.github.types.LabelsGtCondition | airbyte_agent_sdk.connectors.github.types.LabelsGteCondition | airbyte_agent_sdk.connectors.github.types.LabelsLtCondition | airbyte_agent_sdk.connectors.github.types.LabelsLteCondition | airbyte_agent_sdk.connectors.github.types.LabelsInCondition | airbyte_agent_sdk.connectors.github.types.LabelsLikeCondition | airbyte_agent_sdk.connectors.github.types.LabelsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.LabelsKeywordCondition | airbyte_agent_sdk.connectors.github.types.LabelsContainsCondition | airbyte_agent_sdk.connectors.github.types.LabelsNotCondition | airbyte_agent_sdk.connectors.github.types.LabelsAndCondition | airbyte_agent_sdk.connectors.github.types.LabelsOrCondition | airbyte_agent_sdk.connectors.github.types.LabelsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.LabelsSortFilter]`
    :   The type of the None singleton.

<a id="LabelsSortFilter"></a>

`LabelsSortFilter(*args, **kwargs)`
:   Available fields for sorting labels search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Literal['asc', 'desc']`
    :   Label color as a 6-character hex string without a leading `#`

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the label was created

    `description: Literal['asc', 'desc']`
    :   Short description of what the label is used for

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the label

    `name: Literal['asc', 'desc']`
    :   Label name

    `url: Literal['asc', 'desc']`
    :   Permalink to the label on GitHub

<a id="LabelsStringFilter"></a>

`LabelsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   Label color as a 6-character hex string without a leading `#`

    `created_at: str`
    :   ISO 8601 timestamp when the label was created

    `description: str`
    :   Short description of what the label is used for

    `id: str`
    :   GraphQL node ID of the label

    `name: str`
    :   Label name

    `url: str`
    :   Permalink to the label on GitHub

<a id="MilestonesAndCondition"></a>

`MilestonesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.MilestonesEqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNeqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesInCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLikeCondition | airbyte_agent_sdk.connectors.github.types.MilestonesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.MilestonesKeywordCondition | airbyte_agent_sdk.connectors.github.types.MilestonesContainsCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNotCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAndCondition | airbyte_agent_sdk.connectors.github.types.MilestonesOrCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAnyCondition]`
    :   The type of the None singleton.

<a id="MilestonesAnyCondition"></a>

`MilestonesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.MilestonesAnyValueFilter`
    :   The type of the None singleton.

<a id="MilestonesAnyValueFilter"></a>

`MilestonesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: Any`
    :   ISO 8601 timestamp when the milestone was closed, if applicable

    `created_at: Any`
    :   ISO 8601 timestamp when the milestone was created

    `description: Any`
    :   Milestone description

    `due_on: Any`
    :   ISO 8601 timestamp for the milestone's due date, if set

    `id: Any`
    :   GraphQL node ID of the milestone

    `number: Any`
    :   Repository-scoped milestone number

    `progress_percentage: Any`
    :   Percentage of associated issues/PRs that are closed

    `state: Any`
    :   Milestone state: `OPEN` or `CLOSED`

    `title: Any`
    :   Milestone title

    `updated_at: Any`
    :   ISO 8601 timestamp when the milestone was last updated

<a id="MilestonesContainsCondition"></a>

`MilestonesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.MilestonesAnyValueFilter`
    :   The type of the None singleton.

<a id="MilestonesEqCondition"></a>

`MilestonesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.MilestonesSearchFilter`
    :   The type of the None singleton.

<a id="MilestonesFuzzyCondition"></a>

`MilestonesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.MilestonesStringFilter`
    :   The type of the None singleton.

<a id="MilestonesGetParams"></a>

`MilestonesGetParams(*args, **kwargs)`
:   Parameters for milestones.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="MilestonesGtCondition"></a>

`MilestonesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.MilestonesSearchFilter`
    :   The type of the None singleton.

<a id="MilestonesGteCondition"></a>

`MilestonesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.MilestonesSearchFilter`
    :   The type of the None singleton.

<a id="MilestonesInCondition"></a>

`MilestonesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.MilestonesInFilter`
    :   The type of the None singleton.

<a id="MilestonesInFilter"></a>

`MilestonesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: list[str]`
    :   ISO 8601 timestamp when the milestone was closed, if applicable

    `created_at: list[str]`
    :   ISO 8601 timestamp when the milestone was created

    `description: list[str]`
    :   Milestone description

    `due_on: list[str]`
    :   ISO 8601 timestamp for the milestone's due date, if set

    `id: list[str]`
    :   GraphQL node ID of the milestone

    `number: list[int]`
    :   Repository-scoped milestone number

    `progress_percentage: list[float]`
    :   Percentage of associated issues/PRs that are closed

    `state: list[str]`
    :   Milestone state: `OPEN` or `CLOSED`

    `title: list[str]`
    :   Milestone title

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the milestone was last updated

<a id="MilestonesKeywordCondition"></a>

`MilestonesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.MilestonesStringFilter`
    :   The type of the None singleton.

<a id="MilestonesLikeCondition"></a>

`MilestonesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.MilestonesStringFilter`
    :   The type of the None singleton.

<a id="MilestonesListParams"></a>

`MilestonesListParams(*args, **kwargs)`
:   Parameters for milestones.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `states: list[str]`
    :   The type of the None singleton.

<a id="MilestonesLtCondition"></a>

`MilestonesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.MilestonesSearchFilter`
    :   The type of the None singleton.

<a id="MilestonesLteCondition"></a>

`MilestonesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.MilestonesSearchFilter`
    :   The type of the None singleton.

<a id="MilestonesNeqCondition"></a>

`MilestonesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.MilestonesSearchFilter`
    :   The type of the None singleton.

<a id="MilestonesNotCondition"></a>

`MilestonesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.MilestonesEqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNeqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesInCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLikeCondition | airbyte_agent_sdk.connectors.github.types.MilestonesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.MilestonesKeywordCondition | airbyte_agent_sdk.connectors.github.types.MilestonesContainsCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNotCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAndCondition | airbyte_agent_sdk.connectors.github.types.MilestonesOrCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAnyCondition`
    :   The type of the None singleton.

<a id="MilestonesOrCondition"></a>

`MilestonesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.MilestonesEqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNeqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesInCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLikeCondition | airbyte_agent_sdk.connectors.github.types.MilestonesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.MilestonesKeywordCondition | airbyte_agent_sdk.connectors.github.types.MilestonesContainsCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNotCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAndCondition | airbyte_agent_sdk.connectors.github.types.MilestonesOrCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAnyCondition]`
    :   The type of the None singleton.

<a id="MilestonesSearchFilter"></a>

`MilestonesSearchFilter(*args, **kwargs)`
:   Available fields for filtering milestones search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: str | None`
    :   ISO 8601 timestamp when the milestone was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the milestone was created

    `description: str | None`
    :   Milestone description

    `due_on: str | None`
    :   ISO 8601 timestamp for the milestone's due date, if set

    `id: str | None`
    :   GraphQL node ID of the milestone

    `number: int | None`
    :   Repository-scoped milestone number

    `progress_percentage: float | None`
    :   Percentage of associated issues/PRs that are closed

    `state: str | None`
    :   Milestone state: `OPEN` or `CLOSED`

    `title: str | None`
    :   Milestone title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the milestone was last updated

<a id="MilestonesSearchQuery"></a>

`MilestonesSearchQuery(*args, **kwargs)`
:   Search query for milestones entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.MilestonesEqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNeqCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesGteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLtCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLteCondition | airbyte_agent_sdk.connectors.github.types.MilestonesInCondition | airbyte_agent_sdk.connectors.github.types.MilestonesLikeCondition | airbyte_agent_sdk.connectors.github.types.MilestonesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.MilestonesKeywordCondition | airbyte_agent_sdk.connectors.github.types.MilestonesContainsCondition | airbyte_agent_sdk.connectors.github.types.MilestonesNotCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAndCondition | airbyte_agent_sdk.connectors.github.types.MilestonesOrCondition | airbyte_agent_sdk.connectors.github.types.MilestonesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.MilestonesSortFilter]`
    :   The type of the None singleton.

<a id="MilestonesSortFilter"></a>

`MilestonesSortFilter(*args, **kwargs)`
:   Available fields for sorting milestones search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the milestone was closed, if applicable

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the milestone was created

    `description: Literal['asc', 'desc']`
    :   Milestone description

    `due_on: Literal['asc', 'desc']`
    :   ISO 8601 timestamp for the milestone's due date, if set

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the milestone

    `number: Literal['asc', 'desc']`
    :   Repository-scoped milestone number

    `progress_percentage: Literal['asc', 'desc']`
    :   Percentage of associated issues/PRs that are closed

    `state: Literal['asc', 'desc']`
    :   Milestone state: `OPEN` or `CLOSED`

    `title: Literal['asc', 'desc']`
    :   Milestone title

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the milestone was last updated

<a id="MilestonesStringFilter"></a>

`MilestonesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed_at: str`
    :   ISO 8601 timestamp when the milestone was closed, if applicable

    `created_at: str`
    :   ISO 8601 timestamp when the milestone was created

    `description: str`
    :   Milestone description

    `due_on: str`
    :   ISO 8601 timestamp for the milestone's due date, if set

    `id: str`
    :   GraphQL node ID of the milestone

    `number: str`
    :   Repository-scoped milestone number

    `progress_percentage: str`
    :   Percentage of associated issues/PRs that are closed

    `state: str`
    :   Milestone state: `OPEN` or `CLOSED`

    `title: str`
    :   Milestone title

    `updated_at: str`
    :   ISO 8601 timestamp when the milestone was last updated

<a id="OrgRepositoriesAndCondition"></a>

`OrgRepositoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.OrgRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAnyCondition]`
    :   The type of the None singleton.

<a id="OrgRepositoriesAnyCondition"></a>

`OrgRepositoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesAnyValueFilter"></a>

`OrgRepositoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="OrgRepositoriesContainsCondition"></a>

`OrgRepositoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesEqCondition"></a>

`OrgRepositoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesFuzzyCondition"></a>

`OrgRepositoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesStringFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesGtCondition"></a>

`OrgRepositoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesGteCondition"></a>

`OrgRepositoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesInCondition"></a>

`OrgRepositoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesInFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesInFilter"></a>

`OrgRepositoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="OrgRepositoriesKeywordCondition"></a>

`OrgRepositoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesStringFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesLikeCondition"></a>

`OrgRepositoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesStringFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesListParams"></a>

`OrgRepositoriesListParams(*args, **kwargs)`
:   Parameters for org_repositories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="OrgRepositoriesLtCondition"></a>

`OrgRepositoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesLteCondition"></a>

`OrgRepositoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesNeqCondition"></a>

`OrgRepositoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="OrgRepositoriesNotCondition"></a>

`OrgRepositoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAnyCondition`
    :   The type of the None singleton.

<a id="OrgRepositoriesOrCondition"></a>

`OrgRepositoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.OrgRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAnyCondition]`
    :   The type of the None singleton.

<a id="OrgRepositoriesSearchFilter"></a>

`OrgRepositoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering org_repositories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="OrgRepositoriesSearchQuery"></a>

`OrgRepositoriesSearchQuery(*args, **kwargs)`
:   Search query for org_repositories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.OrgRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.OrgRepositoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.OrgRepositoriesSortFilter]`
    :   The type of the None singleton.

<a id="OrgRepositoriesSortFilter"></a>

`OrgRepositoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting org_repositories search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="OrgRepositoriesStringFilter"></a>

`OrgRepositoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="OrganizationsAndCondition"></a>

`OrganizationsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAnyCondition]`
    :   The type of the None singleton.

<a id="OrganizationsAnyCondition"></a>

`OrganizationsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationsAnyValueFilter"></a>

`OrganizationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the organization was created

    `database_id: Any`
    :   REST API numeric identifier for the organization

    `description: Any`
    :   Short public description of the organization

    `email: Any`
    :   Public contact email for the organization, if set

    `id: Any`
    :   GraphQL node ID of the organization

    `is_verified: Any`
    :   Whether the organization has a verified domain

    `location: Any`
    :   Public location of the organization, if set

    `login: Any`
    :   Organization login/handle (unique URL slug)

    `name: Any`
    :   Display name of the organization

<a id="OrganizationsContainsCondition"></a>

`OrganizationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationsEqCondition"></a>

`OrganizationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsFuzzyCondition"></a>

`OrganizationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsGetParams"></a>

`OrganizationsGetParams(*args, **kwargs)`
:   Parameters for organizations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

<a id="OrganizationsGtCondition"></a>

`OrganizationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsGteCondition"></a>

`OrganizationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsInCondition"></a>

`OrganizationsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.OrganizationsInFilter`
    :   The type of the None singleton.

<a id="OrganizationsInFilter"></a>

`OrganizationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the organization was created

    `database_id: list[int]`
    :   REST API numeric identifier for the organization

    `description: list[str]`
    :   Short public description of the organization

    `email: list[str]`
    :   Public contact email for the organization, if set

    `id: list[str]`
    :   GraphQL node ID of the organization

    `is_verified: list[bool]`
    :   Whether the organization has a verified domain

    `location: list[str]`
    :   Public location of the organization, if set

    `login: list[str]`
    :   Organization login/handle (unique URL slug)

    `name: list[str]`
    :   Display name of the organization

<a id="OrganizationsKeywordCondition"></a>

`OrganizationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsLikeCondition"></a>

`OrganizationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsListParams"></a>

`OrganizationsListParams(*args, **kwargs)`
:   Parameters for organizations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `username: str`
    :   The type of the None singleton.

<a id="OrganizationsLtCondition"></a>

`OrganizationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsLteCondition"></a>

`OrganizationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsNeqCondition"></a>

`OrganizationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsNotCondition"></a>

`OrganizationsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAnyCondition`
    :   The type of the None singleton.

<a id="OrganizationsOrCondition"></a>

`OrganizationsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAnyCondition]`
    :   The type of the None singleton.

<a id="OrganizationsSearchFilter"></a>

`OrganizationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering organizations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the organization was created

    `database_id: int | None`
    :   REST API numeric identifier for the organization

    `description: str | None`
    :   Short public description of the organization

    `email: str | None`
    :   Public contact email for the organization, if set

    `id: str | None`
    :   GraphQL node ID of the organization

    `is_verified: bool | None`
    :   Whether the organization has a verified domain

    `location: str | None`
    :   Public location of the organization, if set

    `login: str | None`
    :   Organization login/handle (unique URL slug)

    `name: str | None`
    :   Display name of the organization

<a id="OrganizationsSearchQuery"></a>

`OrganizationsSearchQuery(*args, **kwargs)`
:   Search query for organizations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.OrganizationsSortFilter]`
    :   The type of the None singleton.

<a id="OrganizationsSortFilter"></a>

`OrganizationsSortFilter(*args, **kwargs)`
:   Available fields for sorting organizations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the organization was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the organization

    `description: Literal['asc', 'desc']`
    :   Short public description of the organization

    `email: Literal['asc', 'desc']`
    :   Public contact email for the organization, if set

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the organization

    `is_verified: Literal['asc', 'desc']`
    :   Whether the organization has a verified domain

    `location: Literal['asc', 'desc']`
    :   Public location of the organization, if set

    `login: Literal['asc', 'desc']`
    :   Organization login/handle (unique URL slug)

    `name: Literal['asc', 'desc']`
    :   Display name of the organization

<a id="OrganizationsStringFilter"></a>

`OrganizationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the organization was created

    `database_id: str`
    :   REST API numeric identifier for the organization

    `description: str`
    :   Short public description of the organization

    `email: str`
    :   Public contact email for the organization, if set

    `id: str`
    :   GraphQL node ID of the organization

    `is_verified: str`
    :   Whether the organization has a verified domain

    `location: str`
    :   Public location of the organization, if set

    `login: str`
    :   Organization login/handle (unique URL slug)

    `name: str`
    :   Display name of the organization

<a id="PrCommentsAndCondition"></a>

`PrCommentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.PrCommentsEqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsInCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNotCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAndCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsOrCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAnyCondition]`
    :   The type of the None singleton.

<a id="PrCommentsAnyCondition"></a>

`PrCommentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.PrCommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="PrCommentsAnyValueFilter"></a>

`PrCommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="PrCommentsContainsCondition"></a>

`PrCommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.PrCommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="PrCommentsEqCondition"></a>

`PrCommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.PrCommentsSearchFilter`
    :   The type of the None singleton.

<a id="PrCommentsFuzzyCondition"></a>

`PrCommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.PrCommentsStringFilter`
    :   The type of the None singleton.

<a id="PrCommentsGetParams"></a>

`PrCommentsGetParams(*args, **kwargs)`
:   Parameters for pr_comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="PrCommentsGtCondition"></a>

`PrCommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.PrCommentsSearchFilter`
    :   The type of the None singleton.

<a id="PrCommentsGteCondition"></a>

`PrCommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.PrCommentsSearchFilter`
    :   The type of the None singleton.

<a id="PrCommentsInCondition"></a>

`PrCommentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.PrCommentsInFilter`
    :   The type of the None singleton.

<a id="PrCommentsInFilter"></a>

`PrCommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="PrCommentsKeywordCondition"></a>

`PrCommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.PrCommentsStringFilter`
    :   The type of the None singleton.

<a id="PrCommentsLikeCondition"></a>

`PrCommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.PrCommentsStringFilter`
    :   The type of the None singleton.

<a id="PrCommentsListParams"></a>

`PrCommentsListParams(*args, **kwargs)`
:   Parameters for pr_comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="PrCommentsLtCondition"></a>

`PrCommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.PrCommentsSearchFilter`
    :   The type of the None singleton.

<a id="PrCommentsLteCondition"></a>

`PrCommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.PrCommentsSearchFilter`
    :   The type of the None singleton.

<a id="PrCommentsNeqCondition"></a>

`PrCommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.PrCommentsSearchFilter`
    :   The type of the None singleton.

<a id="PrCommentsNotCondition"></a>

`PrCommentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.PrCommentsEqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsInCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNotCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAndCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsOrCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAnyCondition`
    :   The type of the None singleton.

<a id="PrCommentsOrCondition"></a>

`PrCommentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.PrCommentsEqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsInCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNotCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAndCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsOrCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAnyCondition]`
    :   The type of the None singleton.

<a id="PrCommentsSearchFilter"></a>

`PrCommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering pr_comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="PrCommentsSearchQuery"></a>

`PrCommentsSearchQuery(*args, **kwargs)`
:   Search query for pr_comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.PrCommentsEqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsGteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLtCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLteCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsInCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsNotCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAndCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsOrCondition | airbyte_agent_sdk.connectors.github.types.PrCommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.PrCommentsSortFilter]`
    :   The type of the None singleton.

<a id="PrCommentsSortFilter"></a>

`PrCommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting pr_comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="PrCommentsStringFilter"></a>

`PrCommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProjectItemsAndCondition"></a>

`ProjectItemsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.ProjectItemsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectItemsAnyCondition"></a>

`ProjectItemsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.ProjectItemsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectItemsAnyValueFilter"></a>

`ProjectItemsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProjectItemsContainsCondition"></a>

`ProjectItemsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.ProjectItemsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectItemsEqCondition"></a>

`ProjectItemsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.ProjectItemsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectItemsFuzzyCondition"></a>

`ProjectItemsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.ProjectItemsStringFilter`
    :   The type of the None singleton.

<a id="ProjectItemsGtCondition"></a>

`ProjectItemsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.ProjectItemsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectItemsGteCondition"></a>

`ProjectItemsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.ProjectItemsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectItemsInCondition"></a>

`ProjectItemsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.ProjectItemsInFilter`
    :   The type of the None singleton.

<a id="ProjectItemsInFilter"></a>

`ProjectItemsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProjectItemsKeywordCondition"></a>

`ProjectItemsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.ProjectItemsStringFilter`
    :   The type of the None singleton.

<a id="ProjectItemsLikeCondition"></a>

`ProjectItemsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.ProjectItemsStringFilter`
    :   The type of the None singleton.

<a id="ProjectItemsListParams"></a>

`ProjectItemsListParams(*args, **kwargs)`
:   Parameters for project_items.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_number: int`
    :   The type of the None singleton.

<a id="ProjectItemsLtCondition"></a>

`ProjectItemsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.ProjectItemsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectItemsLteCondition"></a>

`ProjectItemsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.ProjectItemsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectItemsNeqCondition"></a>

`ProjectItemsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.ProjectItemsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectItemsNotCondition"></a>

`ProjectItemsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.ProjectItemsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAnyCondition`
    :   The type of the None singleton.

<a id="ProjectItemsOrCondition"></a>

`ProjectItemsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.ProjectItemsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectItemsSearchFilter"></a>

`ProjectItemsSearchFilter(*args, **kwargs)`
:   Available fields for filtering project_items search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProjectItemsSearchQuery"></a>

`ProjectItemsSearchQuery(*args, **kwargs)`
:   Search query for project_items entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.ProjectItemsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectItemsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.ProjectItemsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectItemsSortFilter"></a>

`ProjectItemsSortFilter(*args, **kwargs)`
:   Available fields for sorting project_items search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProjectItemsStringFilter"></a>

`ProjectItemsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

    `and: list[airbyte_agent_sdk.connectors.github.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.github.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsAnyValueFilter"></a>

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed: Any`
    :   Whether the project has been closed

    `created_at: Any`
    :   ISO 8601 timestamp when the project was created

    `id: Any`
    :   GraphQL node ID of the project

    `number: Any`
    :   Organization- or user-scoped project number

    `public: Any`
    :   Whether the project is publicly visible

    `short_description: Any`
    :   Short description displayed on the project summary

    `title: Any`
    :   Project title

    `updated_at: Any`
    :   ISO 8601 timestamp when the project was last updated

    `url: Any`
    :   Permalink to the project on GitHub

<a id="ProjectsContainsCondition"></a>

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsEqCondition"></a>

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsFuzzyCondition"></a>

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsGetParams"></a>

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `project_number: int`
    :   The type of the None singleton.

<a id="ProjectsGtCondition"></a>

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsGteCondition"></a>

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.ProjectsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.ProjectsInFilter`
    :   The type of the None singleton.

<a id="ProjectsInFilter"></a>

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed: list[bool]`
    :   Whether the project has been closed

    `created_at: list[str]`
    :   ISO 8601 timestamp when the project was created

    `id: list[str]`
    :   GraphQL node ID of the project

    `number: list[int]`
    :   Organization- or user-scoped project number

    `public: list[bool]`
    :   Whether the project is publicly visible

    `short_description: list[str]`
    :   Short description displayed on the project summary

    `title: list[str]`
    :   Project title

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the project was last updated

    `url: list[str]`
    :   Permalink to the project on GitHub

<a id="ProjectsKeywordCondition"></a>

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsLikeCondition"></a>

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsListParams"></a>

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="ProjectsLtCondition"></a>

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsLteCondition"></a>

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNeqCondition"></a>

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.ProjectsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsSearchFilter"></a>

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed: bool | None`
    :   Whether the project has been closed

    `created_at: str | None`
    :   ISO 8601 timestamp when the project was created

    `id: str | None`
    :   GraphQL node ID of the project

    `number: int | None`
    :   Organization- or user-scoped project number

    `public: bool | None`
    :   Whether the project is publicly visible

    `short_description: str | None`
    :   Short description displayed on the project summary

    `title: str | None`
    :   Project title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the project was last updated

    `url: str | None`
    :   Permalink to the project on GitHub

<a id="ProjectsSearchQuery"></a>

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.github.types.ProjectsInCondition | airbyte_agent_sdk.connectors.github.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.github.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.github.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.github.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.github.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.ProjectsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectsSortFilter"></a>

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed: Literal['asc', 'desc']`
    :   Whether the project has been closed

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the project was created

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the project

    `number: Literal['asc', 'desc']`
    :   Organization- or user-scoped project number

    `public: Literal['asc', 'desc']`
    :   Whether the project is publicly visible

    `short_description: Literal['asc', 'desc']`
    :   Short description displayed on the project summary

    `title: Literal['asc', 'desc']`
    :   Project title

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the project was last updated

    `url: Literal['asc', 'desc']`
    :   Permalink to the project on GitHub

<a id="ProjectsStringFilter"></a>

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `closed: str`
    :   Whether the project has been closed

    `created_at: str`
    :   ISO 8601 timestamp when the project was created

    `id: str`
    :   GraphQL node ID of the project

    `number: str`
    :   Organization- or user-scoped project number

    `public: str`
    :   Whether the project is publicly visible

    `short_description: str`
    :   Short description displayed on the project summary

    `title: str`
    :   Project title

    `updated_at: str`
    :   ISO 8601 timestamp when the project was last updated

    `url: str`
    :   Permalink to the project on GitHub

<a id="PullRequestsAndCondition"></a>

`PullRequestsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.PullRequestsEqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNeqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsInCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLikeCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsContainsCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNotCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAndCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsOrCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAnyCondition]`
    :   The type of the None singleton.

<a id="PullRequestsAnyCondition"></a>

`PullRequestsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.PullRequestsAnyValueFilter`
    :   The type of the None singleton.

<a id="PullRequestsAnyValueFilter"></a>

`PullRequestsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_ref_name: Any`
    :   Name of the branch being merged into

    `closed_at: Any`
    :   ISO 8601 timestamp when the pull request was closed, if applicable

    `created_at: Any`
    :   ISO 8601 timestamp when the pull request was created

    `database_id: Any`
    :   REST API numeric identifier for the pull request

    `head_ref_name: Any`
    :   Name of the branch with the proposed changes

    `id: Any`
    :   GraphQL node ID of the pull request

    `is_draft: Any`
    :   Whether the pull request is still a draft

    `merged: Any`
    :   Whether the pull request has been merged

    `merged_at: Any`
    :   ISO 8601 timestamp when the pull request was merged, if applicable

    `number: Any`
    :   Repository-scoped pull request number

    `state: Any`
    :   Pull request state: `OPEN`, `CLOSED`, or `MERGED`

    `title: Any`
    :   Pull request title

    `updated_at: Any`
    :   ISO 8601 timestamp when the pull request was last updated

    `url: Any`
    :   Permalink to the pull request on GitHub

<a id="PullRequestsApiSearchParams"></a>

`PullRequestsApiSearchParams(*args, **kwargs)`
:   Parameters for pull_requests.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="PullRequestsContainsCondition"></a>

`PullRequestsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.PullRequestsAnyValueFilter`
    :   The type of the None singleton.

<a id="PullRequestsCreateParams"></a>

`PullRequestsCreateParams(*args, **kwargs)`
:   Parameters for pull_requests.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base: str`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `draft: bool`
    :   The type of the None singleton.

    `head: str`
    :   The type of the None singleton.

    `maintainer_can_modify: bool`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="PullRequestsEqCondition"></a>

`PullRequestsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

<a id="PullRequestsFuzzyCondition"></a>

`PullRequestsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.PullRequestsStringFilter`
    :   The type of the None singleton.

<a id="PullRequestsGetParams"></a>

`PullRequestsGetParams(*args, **kwargs)`
:   Parameters for pull_requests.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="PullRequestsGtCondition"></a>

`PullRequestsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

<a id="PullRequestsGteCondition"></a>

`PullRequestsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

<a id="PullRequestsInCondition"></a>

`PullRequestsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.PullRequestsInFilter`
    :   The type of the None singleton.

<a id="PullRequestsInFilter"></a>

`PullRequestsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_ref_name: list[str]`
    :   Name of the branch being merged into

    `closed_at: list[str]`
    :   ISO 8601 timestamp when the pull request was closed, if applicable

    `created_at: list[str]`
    :   ISO 8601 timestamp when the pull request was created

    `database_id: list[int]`
    :   REST API numeric identifier for the pull request

    `head_ref_name: list[str]`
    :   Name of the branch with the proposed changes

    `id: list[str]`
    :   GraphQL node ID of the pull request

    `is_draft: list[bool]`
    :   Whether the pull request is still a draft

    `merged: list[bool]`
    :   Whether the pull request has been merged

    `merged_at: list[str]`
    :   ISO 8601 timestamp when the pull request was merged, if applicable

    `number: list[int]`
    :   Repository-scoped pull request number

    `state: list[str]`
    :   Pull request state: `OPEN`, `CLOSED`, or `MERGED`

    `title: list[str]`
    :   Pull request title

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the pull request was last updated

    `url: list[str]`
    :   Permalink to the pull request on GitHub

<a id="PullRequestsKeywordCondition"></a>

`PullRequestsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.PullRequestsStringFilter`
    :   The type of the None singleton.

<a id="PullRequestsLikeCondition"></a>

`PullRequestsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.PullRequestsStringFilter`
    :   The type of the None singleton.

<a id="PullRequestsListParams"></a>

`PullRequestsListParams(*args, **kwargs)`
:   Parameters for pull_requests.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `states: list[str]`
    :   The type of the None singleton.

<a id="PullRequestsLtCondition"></a>

`PullRequestsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

<a id="PullRequestsLteCondition"></a>

`PullRequestsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

<a id="PullRequestsNeqCondition"></a>

`PullRequestsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

<a id="PullRequestsNotCondition"></a>

`PullRequestsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.PullRequestsEqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNeqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsInCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLikeCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsContainsCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNotCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAndCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsOrCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAnyCondition`
    :   The type of the None singleton.

<a id="PullRequestsOrCondition"></a>

`PullRequestsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.PullRequestsEqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNeqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsInCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLikeCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsContainsCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNotCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAndCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsOrCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAnyCondition]`
    :   The type of the None singleton.

<a id="PullRequestsSearchFilter"></a>

`PullRequestsSearchFilter(*args, **kwargs)`
:   Available fields for filtering pull_requests search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_ref_name: str | None`
    :   Name of the branch being merged into

    `closed_at: str | None`
    :   ISO 8601 timestamp when the pull request was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the pull request was created

    `database_id: int | None`
    :   REST API numeric identifier for the pull request

    `head_ref_name: str | None`
    :   Name of the branch with the proposed changes

    `id: str | None`
    :   GraphQL node ID of the pull request

    `is_draft: bool | None`
    :   Whether the pull request is still a draft

    `merged: bool | None`
    :   Whether the pull request has been merged

    `merged_at: str | None`
    :   ISO 8601 timestamp when the pull request was merged, if applicable

    `number: int | None`
    :   Repository-scoped pull request number

    `state: str | None`
    :   Pull request state: `OPEN`, `CLOSED`, or `MERGED`

    `title: str | None`
    :   Pull request title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the pull request was last updated

    `url: str | None`
    :   Permalink to the pull request on GitHub

<a id="PullRequestsSearchQuery"></a>

`PullRequestsSearchQuery(*args, **kwargs)`
:   Search query for pull_requests entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.PullRequestsEqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNeqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsInCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLikeCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsContainsCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNotCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAndCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsOrCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.PullRequestsSortFilter]`
    :   The type of the None singleton.

<a id="PullRequestsSortFilter"></a>

`PullRequestsSortFilter(*args, **kwargs)`
:   Available fields for sorting pull_requests search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_ref_name: Literal['asc', 'desc']`
    :   Name of the branch being merged into

    `closed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the pull request was closed, if applicable

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the pull request was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the pull request

    `head_ref_name: Literal['asc', 'desc']`
    :   Name of the branch with the proposed changes

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the pull request

    `is_draft: Literal['asc', 'desc']`
    :   Whether the pull request is still a draft

    `merged: Literal['asc', 'desc']`
    :   Whether the pull request has been merged

    `merged_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the pull request was merged, if applicable

    `number: Literal['asc', 'desc']`
    :   Repository-scoped pull request number

    `state: Literal['asc', 'desc']`
    :   Pull request state: `OPEN`, `CLOSED`, or `MERGED`

    `title: Literal['asc', 'desc']`
    :   Pull request title

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the pull request was last updated

    `url: Literal['asc', 'desc']`
    :   Permalink to the pull request on GitHub

<a id="PullRequestsStringFilter"></a>

`PullRequestsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_ref_name: str`
    :   Name of the branch being merged into

    `closed_at: str`
    :   ISO 8601 timestamp when the pull request was closed, if applicable

    `created_at: str`
    :   ISO 8601 timestamp when the pull request was created

    `database_id: str`
    :   REST API numeric identifier for the pull request

    `head_ref_name: str`
    :   Name of the branch with the proposed changes

    `id: str`
    :   GraphQL node ID of the pull request

    `is_draft: str`
    :   Whether the pull request is still a draft

    `merged: str`
    :   Whether the pull request has been merged

    `merged_at: str`
    :   ISO 8601 timestamp when the pull request was merged, if applicable

    `number: str`
    :   Repository-scoped pull request number

    `state: str`
    :   Pull request state: `OPEN`, `CLOSED`, or `MERGED`

    `title: str`
    :   Pull request title

    `updated_at: str`
    :   ISO 8601 timestamp when the pull request was last updated

    `url: str`
    :   Permalink to the pull request on GitHub

<a id="ReleasesAndCondition"></a>

`ReleasesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesInCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.github.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.github.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAnyCondition]`
    :   The type of the None singleton.

<a id="ReleasesAnyCondition"></a>

`ReleasesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.ReleasesAnyValueFilter`
    :   The type of the None singleton.

<a id="ReleasesAnyValueFilter"></a>

`ReleasesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the release was created

    `database_id: Any`
    :   REST API numeric identifier for the release

    `description: Any`
    :   Markdown body / release notes

    `id: Any`
    :   GraphQL node ID of the release

    `is_draft: Any`
    :   Whether the release is still a draft and not published

    `is_prerelease: Any`
    :   Whether the release is marked as a pre-release

    `name: Any`
    :   Display name of the release

    `published_at: Any`
    :   ISO 8601 timestamp when the release was published

    `tag_name: Any`
    :   Git tag the release points at (e.g. `v1.2.3`)

    `url: Any`
    :   Permalink to the release on GitHub

<a id="ReleasesContainsCondition"></a>

`ReleasesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.ReleasesAnyValueFilter`
    :   The type of the None singleton.

<a id="ReleasesEqCondition"></a>

`ReleasesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesFuzzyCondition"></a>

`ReleasesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesGetParams"></a>

`ReleasesGetParams(*args, **kwargs)`
:   Parameters for releases.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `tag: str`
    :   The type of the None singleton.

<a id="ReleasesGtCondition"></a>

`ReleasesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesGteCondition"></a>

`ReleasesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesInCondition"></a>

`ReleasesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.ReleasesInFilter`
    :   The type of the None singleton.

<a id="ReleasesInFilter"></a>

`ReleasesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the release was created

    `database_id: list[int]`
    :   REST API numeric identifier for the release

    `description: list[str]`
    :   Markdown body / release notes

    `id: list[str]`
    :   GraphQL node ID of the release

    `is_draft: list[bool]`
    :   Whether the release is still a draft and not published

    `is_prerelease: list[bool]`
    :   Whether the release is marked as a pre-release

    `name: list[str]`
    :   Display name of the release

    `published_at: list[str]`
    :   ISO 8601 timestamp when the release was published

    `tag_name: list[str]`
    :   Git tag the release points at (e.g. `v1.2.3`)

    `url: list[str]`
    :   Permalink to the release on GitHub

<a id="ReleasesKeywordCondition"></a>

`ReleasesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesLikeCondition"></a>

`ReleasesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesListParams"></a>

`ReleasesListParams(*args, **kwargs)`
:   Parameters for releases.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="ReleasesLtCondition"></a>

`ReleasesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesLteCondition"></a>

`ReleasesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesNeqCondition"></a>

`ReleasesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesNotCondition"></a>

`ReleasesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesInCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.github.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.github.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAnyCondition`
    :   The type of the None singleton.

<a id="ReleasesOrCondition"></a>

`ReleasesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesInCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.github.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.github.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAnyCondition]`
    :   The type of the None singleton.

<a id="ReleasesSearchFilter"></a>

`ReleasesSearchFilter(*args, **kwargs)`
:   Available fields for filtering releases search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the release was created

    `database_id: int | None`
    :   REST API numeric identifier for the release

    `description: str | None`
    :   Markdown body / release notes

    `id: str | None`
    :   GraphQL node ID of the release

    `is_draft: bool | None`
    :   Whether the release is still a draft and not published

    `is_prerelease: bool | None`
    :   Whether the release is marked as a pre-release

    `name: str | None`
    :   Display name of the release

    `published_at: str | None`
    :   ISO 8601 timestamp when the release was published

    `tag_name: str | None`
    :   Git tag the release points at (e.g. `v1.2.3`)

    `url: str | None`
    :   Permalink to the release on GitHub

<a id="ReleasesSearchQuery"></a>

`ReleasesSearchQuery(*args, **kwargs)`
:   Search query for releases entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.github.types.ReleasesInCondition | airbyte_agent_sdk.connectors.github.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.github.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.github.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.github.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.github.types.ReleasesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.ReleasesSortFilter]`
    :   The type of the None singleton.

<a id="ReleasesSortFilter"></a>

`ReleasesSortFilter(*args, **kwargs)`
:   Available fields for sorting releases search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the release was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the release

    `description: Literal['asc', 'desc']`
    :   Markdown body / release notes

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the release

    `is_draft: Literal['asc', 'desc']`
    :   Whether the release is still a draft and not published

    `is_prerelease: Literal['asc', 'desc']`
    :   Whether the release is marked as a pre-release

    `name: Literal['asc', 'desc']`
    :   Display name of the release

    `published_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the release was published

    `tag_name: Literal['asc', 'desc']`
    :   Git tag the release points at (e.g. `v1.2.3`)

    `url: Literal['asc', 'desc']`
    :   Permalink to the release on GitHub

<a id="ReleasesStringFilter"></a>

`ReleasesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the release was created

    `database_id: str`
    :   REST API numeric identifier for the release

    `description: str`
    :   Markdown body / release notes

    `id: str`
    :   GraphQL node ID of the release

    `is_draft: str`
    :   Whether the release is still a draft and not published

    `is_prerelease: str`
    :   Whether the release is marked as a pre-release

    `name: str`
    :   Display name of the release

    `published_at: str`
    :   ISO 8601 timestamp when the release was published

    `tag_name: str`
    :   Git tag the release points at (e.g. `v1.2.3`)

    `url: str`
    :   Permalink to the release on GitHub

<a id="RepositoriesAndCondition"></a>

`RepositoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.RepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAnyCondition]`
    :   The type of the None singleton.

<a id="RepositoriesAnyCondition"></a>

`RepositoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.RepositoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="RepositoriesAnyValueFilter"></a>

`RepositoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the repository was created

    `description: Any`
    :   Short description of the repository

    `fork_count: Any`
    :   Number of forks of the repository

    `id: Any`
    :   GraphQL node ID of the repository

    `is_archived: Any`
    :   Whether the repository has been archived

    `is_fork: Any`
    :   Whether the repository is a fork of another repository

    `is_private: Any`
    :   Whether the repository is private

    `name: Any`
    :   Short repository name (without owner)

    `name_with_owner: Any`
    :   Fully-qualified `owner/name` identifier for the repository

    `pushed_at: Any`
    :   ISO 8601 timestamp of the most recent push to the repository

    `stargazer_count: Any`
    :   Number of users who have starred the repository

    `updated_at: Any`
    :   ISO 8601 timestamp when the repository was last updated

    `url: Any`
    :   Canonical GitHub URL for the repository

<a id="RepositoriesApiSearchParams"></a>

`RepositoriesApiSearchParams(*args, **kwargs)`
:   Parameters for repositories.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="RepositoriesContainsCondition"></a>

`RepositoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.RepositoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="RepositoriesEqCondition"></a>

`RepositoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="RepositoriesFuzzyCondition"></a>

`RepositoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.RepositoriesStringFilter`
    :   The type of the None singleton.

<a id="RepositoriesGetParams"></a>

`RepositoriesGetParams(*args, **kwargs)`
:   Parameters for repositories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="RepositoriesGtCondition"></a>

`RepositoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="RepositoriesGteCondition"></a>

`RepositoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="RepositoriesInCondition"></a>

`RepositoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.RepositoriesInFilter`
    :   The type of the None singleton.

<a id="RepositoriesInFilter"></a>

`RepositoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the repository was created

    `description: list[str]`
    :   Short description of the repository

    `fork_count: list[int]`
    :   Number of forks of the repository

    `id: list[str]`
    :   GraphQL node ID of the repository

    `is_archived: list[bool]`
    :   Whether the repository has been archived

    `is_fork: list[bool]`
    :   Whether the repository is a fork of another repository

    `is_private: list[bool]`
    :   Whether the repository is private

    `name: list[str]`
    :   Short repository name (without owner)

    `name_with_owner: list[str]`
    :   Fully-qualified `owner/name` identifier for the repository

    `pushed_at: list[str]`
    :   ISO 8601 timestamp of the most recent push to the repository

    `stargazer_count: list[int]`
    :   Number of users who have starred the repository

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the repository was last updated

    `url: list[str]`
    :   Canonical GitHub URL for the repository

<a id="RepositoriesKeywordCondition"></a>

`RepositoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.RepositoriesStringFilter`
    :   The type of the None singleton.

<a id="RepositoriesLikeCondition"></a>

`RepositoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.RepositoriesStringFilter`
    :   The type of the None singleton.

<a id="RepositoriesListParams"></a>

`RepositoriesListParams(*args, **kwargs)`
:   Parameters for repositories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `username: str`
    :   The type of the None singleton.

<a id="RepositoriesLtCondition"></a>

`RepositoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="RepositoriesLteCondition"></a>

`RepositoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="RepositoriesNeqCondition"></a>

`RepositoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="RepositoriesNotCondition"></a>

`RepositoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.RepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAnyCondition`
    :   The type of the None singleton.

<a id="RepositoriesOrCondition"></a>

`RepositoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.RepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAnyCondition]`
    :   The type of the None singleton.

<a id="RepositoriesSearchFilter"></a>

`RepositoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering repositories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the repository was created

    `description: str | None`
    :   Short description of the repository

    `fork_count: int | None`
    :   Number of forks of the repository

    `id: str | None`
    :   GraphQL node ID of the repository

    `is_archived: bool | None`
    :   Whether the repository has been archived

    `is_fork: bool | None`
    :   Whether the repository is a fork of another repository

    `is_private: bool | None`
    :   Whether the repository is private

    `name: str | None`
    :   Short repository name (without owner)

    `name_with_owner: str | None`
    :   Fully-qualified `owner/name` identifier for the repository

    `pushed_at: str | None`
    :   ISO 8601 timestamp of the most recent push to the repository

    `stargazer_count: int | None`
    :   Number of users who have starred the repository

    `updated_at: str | None`
    :   ISO 8601 timestamp when the repository was last updated

    `url: str | None`
    :   Canonical GitHub URL for the repository

<a id="RepositoriesSearchQuery"></a>

`RepositoriesSearchQuery(*args, **kwargs)`
:   Search query for repositories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.RepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.RepositoriesSortFilter]`
    :   The type of the None singleton.

<a id="RepositoriesSortFilter"></a>

`RepositoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting repositories search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the repository was created

    `description: Literal['asc', 'desc']`
    :   Short description of the repository

    `fork_count: Literal['asc', 'desc']`
    :   Number of forks of the repository

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the repository

    `is_archived: Literal['asc', 'desc']`
    :   Whether the repository has been archived

    `is_fork: Literal['asc', 'desc']`
    :   Whether the repository is a fork of another repository

    `is_private: Literal['asc', 'desc']`
    :   Whether the repository is private

    `name: Literal['asc', 'desc']`
    :   Short repository name (without owner)

    `name_with_owner: Literal['asc', 'desc']`
    :   Fully-qualified `owner/name` identifier for the repository

    `pushed_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp of the most recent push to the repository

    `stargazer_count: Literal['asc', 'desc']`
    :   Number of users who have starred the repository

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the repository was last updated

    `url: Literal['asc', 'desc']`
    :   Canonical GitHub URL for the repository

<a id="RepositoriesStringFilter"></a>

`RepositoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the repository was created

    `description: str`
    :   Short description of the repository

    `fork_count: str`
    :   Number of forks of the repository

    `id: str`
    :   GraphQL node ID of the repository

    `is_archived: str`
    :   Whether the repository has been archived

    `is_fork: str`
    :   Whether the repository is a fork of another repository

    `is_private: str`
    :   Whether the repository is private

    `name: str`
    :   Short repository name (without owner)

    `name_with_owner: str`
    :   Fully-qualified `owner/name` identifier for the repository

    `pushed_at: str`
    :   ISO 8601 timestamp of the most recent push to the repository

    `stargazer_count: str`
    :   Number of users who have starred the repository

    `updated_at: str`
    :   ISO 8601 timestamp when the repository was last updated

    `url: str`
    :   Canonical GitHub URL for the repository

<a id="ReviewsAndCondition"></a>

`ReviewsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.ReviewsEqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNeqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsInCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLikeCondition | airbyte_agent_sdk.connectors.github.types.ReviewsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReviewsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReviewsContainsCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNotCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAndCondition | airbyte_agent_sdk.connectors.github.types.ReviewsOrCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAnyCondition]`
    :   The type of the None singleton.

<a id="ReviewsAnyCondition"></a>

`ReviewsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.ReviewsAnyValueFilter`
    :   The type of the None singleton.

<a id="ReviewsAnyValueFilter"></a>

`ReviewsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: Any`
    :   Review body text

    `created_at: Any`
    :   ISO 8601 timestamp when the review was created

    `database_id: Any`
    :   REST API numeric identifier for the review

    `id: Any`
    :   GraphQL node ID of the review

    `state: Any`
    :   Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`

    `submitted_at: Any`
    :   ISO 8601 timestamp when the review was submitted

    `updated_at: Any`
    :   ISO 8601 timestamp when the review was last updated

    `url: Any`
    :   Permalink to the review on GitHub

<a id="ReviewsContainsCondition"></a>

`ReviewsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.ReviewsAnyValueFilter`
    :   The type of the None singleton.

<a id="ReviewsEqCondition"></a>

`ReviewsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.ReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ReviewsFuzzyCondition"></a>

`ReviewsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.ReviewsStringFilter`
    :   The type of the None singleton.

<a id="ReviewsGtCondition"></a>

`ReviewsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.ReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ReviewsGteCondition"></a>

`ReviewsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.ReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ReviewsInCondition"></a>

`ReviewsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.ReviewsInFilter`
    :   The type of the None singleton.

<a id="ReviewsInFilter"></a>

`ReviewsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: list[str]`
    :   Review body text

    `created_at: list[str]`
    :   ISO 8601 timestamp when the review was created

    `database_id: list[int]`
    :   REST API numeric identifier for the review

    `id: list[str]`
    :   GraphQL node ID of the review

    `state: list[str]`
    :   Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`

    `submitted_at: list[str]`
    :   ISO 8601 timestamp when the review was submitted

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the review was last updated

    `url: list[str]`
    :   Permalink to the review on GitHub

<a id="ReviewsKeywordCondition"></a>

`ReviewsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.ReviewsStringFilter`
    :   The type of the None singleton.

<a id="ReviewsLikeCondition"></a>

`ReviewsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.ReviewsStringFilter`
    :   The type of the None singleton.

<a id="ReviewsListParams"></a>

`ReviewsListParams(*args, **kwargs)`
:   Parameters for reviews.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `number: int`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="ReviewsLtCondition"></a>

`ReviewsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.ReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ReviewsLteCondition"></a>

`ReviewsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.ReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ReviewsNeqCondition"></a>

`ReviewsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.ReviewsSearchFilter`
    :   The type of the None singleton.

<a id="ReviewsNotCondition"></a>

`ReviewsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.ReviewsEqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNeqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsInCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLikeCondition | airbyte_agent_sdk.connectors.github.types.ReviewsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReviewsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReviewsContainsCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNotCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAndCondition | airbyte_agent_sdk.connectors.github.types.ReviewsOrCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAnyCondition`
    :   The type of the None singleton.

<a id="ReviewsOrCondition"></a>

`ReviewsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.ReviewsEqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNeqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsInCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLikeCondition | airbyte_agent_sdk.connectors.github.types.ReviewsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReviewsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReviewsContainsCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNotCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAndCondition | airbyte_agent_sdk.connectors.github.types.ReviewsOrCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAnyCondition]`
    :   The type of the None singleton.

<a id="ReviewsSearchFilter"></a>

`ReviewsSearchFilter(*args, **kwargs)`
:   Available fields for filtering reviews search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str | None`
    :   Review body text

    `created_at: str | None`
    :   ISO 8601 timestamp when the review was created

    `database_id: int | None`
    :   REST API numeric identifier for the review

    `id: str | None`
    :   GraphQL node ID of the review

    `state: str | None`
    :   Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`

    `submitted_at: str | None`
    :   ISO 8601 timestamp when the review was submitted

    `updated_at: str | None`
    :   ISO 8601 timestamp when the review was last updated

    `url: str | None`
    :   Permalink to the review on GitHub

<a id="ReviewsSearchQuery"></a>

`ReviewsSearchQuery(*args, **kwargs)`
:   Search query for reviews entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.ReviewsEqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNeqCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsGteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLtCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLteCondition | airbyte_agent_sdk.connectors.github.types.ReviewsInCondition | airbyte_agent_sdk.connectors.github.types.ReviewsLikeCondition | airbyte_agent_sdk.connectors.github.types.ReviewsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ReviewsKeywordCondition | airbyte_agent_sdk.connectors.github.types.ReviewsContainsCondition | airbyte_agent_sdk.connectors.github.types.ReviewsNotCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAndCondition | airbyte_agent_sdk.connectors.github.types.ReviewsOrCondition | airbyte_agent_sdk.connectors.github.types.ReviewsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.ReviewsSortFilter]`
    :   The type of the None singleton.

<a id="ReviewsSortFilter"></a>

`ReviewsSortFilter(*args, **kwargs)`
:   Available fields for sorting reviews search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: Literal['asc', 'desc']`
    :   Review body text

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the review was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the review

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the review

    `state: Literal['asc', 'desc']`
    :   Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`

    `submitted_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the review was submitted

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the review was last updated

    `url: Literal['asc', 'desc']`
    :   Permalink to the review on GitHub

<a id="ReviewsStringFilter"></a>

`ReviewsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   Review body text

    `created_at: str`
    :   ISO 8601 timestamp when the review was created

    `database_id: str`
    :   REST API numeric identifier for the review

    `id: str`
    :   GraphQL node ID of the review

    `state: str`
    :   Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`

    `submitted_at: str`
    :   ISO 8601 timestamp when the review was submitted

    `updated_at: str`
    :   ISO 8601 timestamp when the review was last updated

    `url: str`
    :   Permalink to the review on GitHub

<a id="StargazersAndCondition"></a>

`StargazersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.StargazersEqCondition | airbyte_agent_sdk.connectors.github.types.StargazersNeqCondition | airbyte_agent_sdk.connectors.github.types.StargazersGtCondition | airbyte_agent_sdk.connectors.github.types.StargazersGteCondition | airbyte_agent_sdk.connectors.github.types.StargazersLtCondition | airbyte_agent_sdk.connectors.github.types.StargazersLteCondition | airbyte_agent_sdk.connectors.github.types.StargazersInCondition | airbyte_agent_sdk.connectors.github.types.StargazersLikeCondition | airbyte_agent_sdk.connectors.github.types.StargazersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.StargazersKeywordCondition | airbyte_agent_sdk.connectors.github.types.StargazersContainsCondition | airbyte_agent_sdk.connectors.github.types.StargazersNotCondition | airbyte_agent_sdk.connectors.github.types.StargazersAndCondition | airbyte_agent_sdk.connectors.github.types.StargazersOrCondition | airbyte_agent_sdk.connectors.github.types.StargazersAnyCondition]`
    :   The type of the None singleton.

<a id="StargazersAnyCondition"></a>

`StargazersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.StargazersAnyValueFilter`
    :   The type of the None singleton.

<a id="StargazersAnyValueFilter"></a>

`StargazersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `starred_at: Any`
    :   ISO 8601 timestamp when the user starred the repository

<a id="StargazersContainsCondition"></a>

`StargazersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.StargazersAnyValueFilter`
    :   The type of the None singleton.

<a id="StargazersEqCondition"></a>

`StargazersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

<a id="StargazersFuzzyCondition"></a>

`StargazersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.StargazersStringFilter`
    :   The type of the None singleton.

<a id="StargazersGtCondition"></a>

`StargazersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

<a id="StargazersGteCondition"></a>

`StargazersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

<a id="StargazersInCondition"></a>

`StargazersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.StargazersInFilter`
    :   The type of the None singleton.

<a id="StargazersInFilter"></a>

`StargazersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `starred_at: list[str]`
    :   ISO 8601 timestamp when the user starred the repository

<a id="StargazersKeywordCondition"></a>

`StargazersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.StargazersStringFilter`
    :   The type of the None singleton.

<a id="StargazersLikeCondition"></a>

`StargazersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.StargazersStringFilter`
    :   The type of the None singleton.

<a id="StargazersListParams"></a>

`StargazersListParams(*args, **kwargs)`
:   Parameters for stargazers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="StargazersLtCondition"></a>

`StargazersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

<a id="StargazersLteCondition"></a>

`StargazersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

<a id="StargazersNeqCondition"></a>

`StargazersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

<a id="StargazersNotCondition"></a>

`StargazersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.StargazersEqCondition | airbyte_agent_sdk.connectors.github.types.StargazersNeqCondition | airbyte_agent_sdk.connectors.github.types.StargazersGtCondition | airbyte_agent_sdk.connectors.github.types.StargazersGteCondition | airbyte_agent_sdk.connectors.github.types.StargazersLtCondition | airbyte_agent_sdk.connectors.github.types.StargazersLteCondition | airbyte_agent_sdk.connectors.github.types.StargazersInCondition | airbyte_agent_sdk.connectors.github.types.StargazersLikeCondition | airbyte_agent_sdk.connectors.github.types.StargazersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.StargazersKeywordCondition | airbyte_agent_sdk.connectors.github.types.StargazersContainsCondition | airbyte_agent_sdk.connectors.github.types.StargazersNotCondition | airbyte_agent_sdk.connectors.github.types.StargazersAndCondition | airbyte_agent_sdk.connectors.github.types.StargazersOrCondition | airbyte_agent_sdk.connectors.github.types.StargazersAnyCondition`
    :   The type of the None singleton.

<a id="StargazersOrCondition"></a>

`StargazersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.StargazersEqCondition | airbyte_agent_sdk.connectors.github.types.StargazersNeqCondition | airbyte_agent_sdk.connectors.github.types.StargazersGtCondition | airbyte_agent_sdk.connectors.github.types.StargazersGteCondition | airbyte_agent_sdk.connectors.github.types.StargazersLtCondition | airbyte_agent_sdk.connectors.github.types.StargazersLteCondition | airbyte_agent_sdk.connectors.github.types.StargazersInCondition | airbyte_agent_sdk.connectors.github.types.StargazersLikeCondition | airbyte_agent_sdk.connectors.github.types.StargazersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.StargazersKeywordCondition | airbyte_agent_sdk.connectors.github.types.StargazersContainsCondition | airbyte_agent_sdk.connectors.github.types.StargazersNotCondition | airbyte_agent_sdk.connectors.github.types.StargazersAndCondition | airbyte_agent_sdk.connectors.github.types.StargazersOrCondition | airbyte_agent_sdk.connectors.github.types.StargazersAnyCondition]`
    :   The type of the None singleton.

<a id="StargazersSearchFilter"></a>

`StargazersSearchFilter(*args, **kwargs)`
:   Available fields for filtering stargazers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `starred_at: str | None`
    :   ISO 8601 timestamp when the user starred the repository

<a id="StargazersSearchQuery"></a>

`StargazersSearchQuery(*args, **kwargs)`
:   Search query for stargazers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.StargazersEqCondition | airbyte_agent_sdk.connectors.github.types.StargazersNeqCondition | airbyte_agent_sdk.connectors.github.types.StargazersGtCondition | airbyte_agent_sdk.connectors.github.types.StargazersGteCondition | airbyte_agent_sdk.connectors.github.types.StargazersLtCondition | airbyte_agent_sdk.connectors.github.types.StargazersLteCondition | airbyte_agent_sdk.connectors.github.types.StargazersInCondition | airbyte_agent_sdk.connectors.github.types.StargazersLikeCondition | airbyte_agent_sdk.connectors.github.types.StargazersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.StargazersKeywordCondition | airbyte_agent_sdk.connectors.github.types.StargazersContainsCondition | airbyte_agent_sdk.connectors.github.types.StargazersNotCondition | airbyte_agent_sdk.connectors.github.types.StargazersAndCondition | airbyte_agent_sdk.connectors.github.types.StargazersOrCondition | airbyte_agent_sdk.connectors.github.types.StargazersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.StargazersSortFilter]`
    :   The type of the None singleton.

<a id="StargazersSortFilter"></a>

`StargazersSortFilter(*args, **kwargs)`
:   Available fields for sorting stargazers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `starred_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the user starred the repository

<a id="StargazersStringFilter"></a>

`StargazersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `starred_at: str`
    :   ISO 8601 timestamp when the user starred the repository

<a id="TagsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition]`
    :   The type of the None singleton.

<a id="TagsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.github.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsAnyValueFilter"></a>

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: Any`
    :   Tag name (e.g. `v1.2.3`)

    `prefix: Any`
    :   Git ref prefix for the tag (typically `refs/tags/`)

<a id="TagsContainsCondition"></a>

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsEqCondition"></a>

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsFuzzyCondition"></a>

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsGetParams"></a>

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

    `tag: str`
    :   The type of the None singleton.

<a id="TagsGtCondition"></a>

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsGteCondition"></a>

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.github.types.TagsInFilter`
    :   The type of the None singleton.

<a id="TagsInFilter"></a>

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: list[str]`
    :   Tag name (e.g. `v1.2.3`)

    `prefix: list[str]`
    :   Git ref prefix for the tag (typically `refs/tags/`)

<a id="TagsKeywordCondition"></a>

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsLikeCondition"></a>

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `owner: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `repo: str`
    :   The type of the None singleton.

<a id="TagsLtCondition"></a>

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsLteCondition"></a>

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsNeqCondition"></a>

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition`
    :   The type of the None singleton.

<a id="TagsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition]`
    :   The type of the None singleton.

<a id="TagsSearchFilter"></a>

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str | None`
    :   Tag name (e.g. `v1.2.3`)

    `prefix: str | None`
    :   Git ref prefix for the tag (typically `refs/tags/`)

<a id="TagsSearchQuery"></a>

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.TagsSortFilter]`
    :   The type of the None singleton.

<a id="TagsSortFilter"></a>

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: Literal['asc', 'desc']`
    :   Tag name (e.g. `v1.2.3`)

    `prefix: Literal['asc', 'desc']`
    :   Git ref prefix for the tag (typically `refs/tags/`)

<a id="TagsStringFilter"></a>

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   Tag name (e.g. `v1.2.3`)

    `prefix: str`
    :   Git ref prefix for the tag (typically `refs/tags/`)

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

    `and: list[airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.github.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsAnyValueFilter"></a>

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   ISO 8601 timestamp when the team was created

    `database_id: Any`
    :   REST API numeric identifier for the team

    `description: Any`
    :   Short description of the team

    `id: Any`
    :   GraphQL node ID of the team

    `name: Any`
    :   Display name of the team

    `privacy: Any`
    :   Team visibility: `SECRET` or `VISIBLE`

    `slug: Any`
    :   URL-friendly slug for the team within its organization

    `updated_at: Any`
    :   ISO 8601 timestamp when the team was last updated

    `url: Any`
    :   Permalink to the team on GitHub

<a id="TeamsContainsCondition"></a>

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsEqCondition"></a>

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsFuzzyCondition"></a>

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsGetParams"></a>

`TeamsGetParams(*args, **kwargs)`
:   Parameters for teams.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `team_slug: str`
    :   The type of the None singleton.

<a id="TeamsGtCondition"></a>

`TeamsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsGteCondition"></a>

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.TeamsInFilter`
    :   The type of the None singleton.

<a id="TeamsInFilter"></a>

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   ISO 8601 timestamp when the team was created

    `database_id: list[int]`
    :   REST API numeric identifier for the team

    `description: list[str]`
    :   Short description of the team

    `id: list[str]`
    :   GraphQL node ID of the team

    `name: list[str]`
    :   Display name of the team

    `privacy: list[str]`
    :   Team visibility: `SECRET` or `VISIBLE`

    `slug: list[str]`
    :   URL-friendly slug for the team within its organization

    `updated_at: list[str]`
    :   ISO 8601 timestamp when the team was last updated

    `url: list[str]`
    :   Permalink to the team on GitHub

<a id="TeamsKeywordCondition"></a>

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsLikeCondition"></a>

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsListParams"></a>

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TeamsLtCondition"></a>

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsLteCondition"></a>

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsNeqCondition"></a>

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition]`
    :   The type of the None singleton.

<a id="TeamsSearchFilter"></a>

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   ISO 8601 timestamp when the team was created

    `database_id: int | None`
    :   REST API numeric identifier for the team

    `description: str | None`
    :   Short description of the team

    `id: str | None`
    :   GraphQL node ID of the team

    `name: str | None`
    :   Display name of the team

    `privacy: str | None`
    :   Team visibility: `SECRET` or `VISIBLE`

    `slug: str | None`
    :   URL-friendly slug for the team within its organization

    `updated_at: str | None`
    :   ISO 8601 timestamp when the team was last updated

    `url: str | None`
    :   Permalink to the team on GitHub

<a id="TeamsSearchQuery"></a>

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.TeamsSortFilter]`
    :   The type of the None singleton.

<a id="TeamsSortFilter"></a>

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the team was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the team

    `description: Literal['asc', 'desc']`
    :   Short description of the team

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the team

    `name: Literal['asc', 'desc']`
    :   Display name of the team

    `privacy: Literal['asc', 'desc']`
    :   Team visibility: `SECRET` or `VISIBLE`

    `slug: Literal['asc', 'desc']`
    :   URL-friendly slug for the team within its organization

    `updated_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the team was last updated

    `url: Literal['asc', 'desc']`
    :   Permalink to the team on GitHub

<a id="TeamsStringFilter"></a>

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   ISO 8601 timestamp when the team was created

    `database_id: str`
    :   REST API numeric identifier for the team

    `description: str`
    :   Short description of the team

    `id: str`
    :   GraphQL node ID of the team

    `name: str`
    :   Display name of the team

    `privacy: str`
    :   Team visibility: `SECRET` or `VISIBLE`

    `slug: str`
    :   URL-friendly slug for the team within its organization

    `updated_at: str`
    :   ISO 8601 timestamp when the team was last updated

    `url: str`
    :   Permalink to the team on GitHub

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

    `and: list[airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.github.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: Any`
    :   Public company affiliation of the user, if set

    `created_at: Any`
    :   ISO 8601 timestamp when the user account was created

    `database_id: Any`
    :   REST API numeric identifier for the user

    `email: Any`
    :   Public email address of the user, if set

    `id: Any`
    :   GraphQL node ID of the user

    `is_hireable: Any`
    :   Whether the user has marked themselves as available for hire

    `location: Any`
    :   Public location of the user, if set

    `login: Any`
    :   User login/handle

    `name: Any`
    :   Public display name of the user, if set

    `twitter_username: Any`
    :   Public Twitter/X username of the user, if set

    `url: Any`
    :   Permalink to the user's profile on GitHub

<a id="UsersApiSearchParams"></a>

`UsersApiSearchParams(*args, **kwargs)`
:   Parameters for users.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `username: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: list[str]`
    :   Public company affiliation of the user, if set

    `created_at: list[str]`
    :   ISO 8601 timestamp when the user account was created

    `database_id: list[int]`
    :   REST API numeric identifier for the user

    `email: list[str]`
    :   Public email address of the user, if set

    `id: list[str]`
    :   GraphQL node ID of the user

    `is_hireable: list[bool]`
    :   Whether the user has marked themselves as available for hire

    `location: list[str]`
    :   Public location of the user, if set

    `login: list[str]`
    :   User login/handle

    `name: list[str]`
    :   Public display name of the user, if set

    `twitter_username: list[str]`
    :   Public Twitter/X username of the user, if set

    `url: list[str]`
    :   Permalink to the user's profile on GitHub

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: str | None`
    :   Public company affiliation of the user, if set

    `created_at: str | None`
    :   ISO 8601 timestamp when the user account was created

    `database_id: int | None`
    :   REST API numeric identifier for the user

    `email: str | None`
    :   Public email address of the user, if set

    `id: str | None`
    :   GraphQL node ID of the user

    `is_hireable: bool | None`
    :   Whether the user has marked themselves as available for hire

    `location: str | None`
    :   Public location of the user, if set

    `login: str | None`
    :   User login/handle

    `name: str | None`
    :   Public display name of the user, if set

    `twitter_username: str | None`
    :   Public Twitter/X username of the user, if set

    `url: str | None`
    :   Permalink to the user's profile on GitHub

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: Literal['asc', 'desc']`
    :   Public company affiliation of the user, if set

    `created_at: Literal['asc', 'desc']`
    :   ISO 8601 timestamp when the user account was created

    `database_id: Literal['asc', 'desc']`
    :   REST API numeric identifier for the user

    `email: Literal['asc', 'desc']`
    :   Public email address of the user, if set

    `id: Literal['asc', 'desc']`
    :   GraphQL node ID of the user

    `is_hireable: Literal['asc', 'desc']`
    :   Whether the user has marked themselves as available for hire

    `location: Literal['asc', 'desc']`
    :   Public location of the user, if set

    `login: Literal['asc', 'desc']`
    :   User login/handle

    `name: Literal['asc', 'desc']`
    :   Public display name of the user, if set

    `twitter_username: Literal['asc', 'desc']`
    :   Public Twitter/X username of the user, if set

    `url: Literal['asc', 'desc']`
    :   Permalink to the user's profile on GitHub

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company: str`
    :   Public company affiliation of the user, if set

    `created_at: str`
    :   ISO 8601 timestamp when the user account was created

    `database_id: str`
    :   REST API numeric identifier for the user

    `email: str`
    :   Public email address of the user, if set

    `id: str`
    :   GraphQL node ID of the user

    `is_hireable: str`
    :   Whether the user has marked themselves as available for hire

    `location: str`
    :   Public location of the user, if set

    `login: str`
    :   User login/handle

    `name: str`
    :   Public display name of the user, if set

    `twitter_username: str`
    :   Public Twitter/X username of the user, if set

    `url: str`
    :   Permalink to the user's profile on GitHub

<a id="ViewerAndCondition"></a>

`ViewerAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.ViewerEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerInCondition | airbyte_agent_sdk.connectors.github.types.ViewerLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerAnyCondition]`
    :   The type of the None singleton.

<a id="ViewerAnyCondition"></a>

`ViewerAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.ViewerAnyValueFilter`
    :   The type of the None singleton.

<a id="ViewerAnyValueFilter"></a>

`ViewerAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerContainsCondition"></a>

`ViewerContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.ViewerAnyValueFilter`
    :   The type of the None singleton.

<a id="ViewerEqCondition"></a>

`ViewerEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.ViewerSearchFilter`
    :   The type of the None singleton.

<a id="ViewerFuzzyCondition"></a>

`ViewerFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.ViewerStringFilter`
    :   The type of the None singleton.

<a id="ViewerGetParams"></a>

`ViewerGetParams(*args, **kwargs)`
:   Parameters for viewer.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

<a id="ViewerGtCondition"></a>

`ViewerGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.ViewerSearchFilter`
    :   The type of the None singleton.

<a id="ViewerGteCondition"></a>

`ViewerGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.ViewerSearchFilter`
    :   The type of the None singleton.

<a id="ViewerInCondition"></a>

`ViewerInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.ViewerInFilter`
    :   The type of the None singleton.

<a id="ViewerInFilter"></a>

`ViewerInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerKeywordCondition"></a>

`ViewerKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.ViewerStringFilter`
    :   The type of the None singleton.

<a id="ViewerLikeCondition"></a>

`ViewerLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.ViewerStringFilter`
    :   The type of the None singleton.

<a id="ViewerLtCondition"></a>

`ViewerLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.ViewerSearchFilter`
    :   The type of the None singleton.

<a id="ViewerLteCondition"></a>

`ViewerLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.ViewerSearchFilter`
    :   The type of the None singleton.

<a id="ViewerNeqCondition"></a>

`ViewerNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.ViewerSearchFilter`
    :   The type of the None singleton.

<a id="ViewerNotCondition"></a>

`ViewerNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.ViewerEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerInCondition | airbyte_agent_sdk.connectors.github.types.ViewerLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerAnyCondition`
    :   The type of the None singleton.

<a id="ViewerOrCondition"></a>

`ViewerOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.ViewerEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerInCondition | airbyte_agent_sdk.connectors.github.types.ViewerLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerAnyCondition]`
    :   The type of the None singleton.

<a id="ViewerRepositoriesAndCondition"></a>

`ViewerRepositoriesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAnyCondition]`
    :   The type of the None singleton.

<a id="ViewerRepositoriesAnyCondition"></a>

`ViewerRepositoriesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesAnyValueFilter"></a>

`ViewerRepositoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerRepositoriesContainsCondition"></a>

`ViewerRepositoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAnyValueFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesEqCondition"></a>

`ViewerRepositoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesFuzzyCondition"></a>

`ViewerRepositoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesStringFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesGtCondition"></a>

`ViewerRepositoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesGteCondition"></a>

`ViewerRepositoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesInCondition"></a>

`ViewerRepositoriesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesInFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesInFilter"></a>

`ViewerRepositoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerRepositoriesKeywordCondition"></a>

`ViewerRepositoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesStringFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesLikeCondition"></a>

`ViewerRepositoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesStringFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesListParams"></a>

`ViewerRepositoriesListParams(*args, **kwargs)`
:   Parameters for viewer_repositories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `fields: list[str]`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="ViewerRepositoriesLtCondition"></a>

`ViewerRepositoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesLteCondition"></a>

`ViewerRepositoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesNeqCondition"></a>

`ViewerRepositoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSearchFilter`
    :   The type of the None singleton.

<a id="ViewerRepositoriesNotCondition"></a>

`ViewerRepositoriesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAnyCondition`
    :   The type of the None singleton.

<a id="ViewerRepositoriesOrCondition"></a>

`ViewerRepositoriesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAnyCondition]`
    :   The type of the None singleton.

<a id="ViewerRepositoriesSearchFilter"></a>

`ViewerRepositoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering viewer_repositories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerRepositoriesSearchQuery"></a>

`ViewerRepositoriesSearchQuery(*args, **kwargs)`
:   Search query for viewer_repositories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.ViewerRepositoriesSortFilter]`
    :   The type of the None singleton.

<a id="ViewerRepositoriesSortFilter"></a>

`ViewerRepositoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting viewer_repositories search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerRepositoriesStringFilter"></a>

`ViewerRepositoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerSearchFilter"></a>

`ViewerSearchFilter(*args, **kwargs)`
:   Available fields for filtering viewer search queries.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerSearchQuery"></a>

`ViewerSearchQuery(*args, **kwargs)`
:   Search query for viewer entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.ViewerEqCondition | airbyte_agent_sdk.connectors.github.types.ViewerNeqCondition | airbyte_agent_sdk.connectors.github.types.ViewerGtCondition | airbyte_agent_sdk.connectors.github.types.ViewerGteCondition | airbyte_agent_sdk.connectors.github.types.ViewerLtCondition | airbyte_agent_sdk.connectors.github.types.ViewerLteCondition | airbyte_agent_sdk.connectors.github.types.ViewerInCondition | airbyte_agent_sdk.connectors.github.types.ViewerLikeCondition | airbyte_agent_sdk.connectors.github.types.ViewerFuzzyCondition | airbyte_agent_sdk.connectors.github.types.ViewerKeywordCondition | airbyte_agent_sdk.connectors.github.types.ViewerContainsCondition | airbyte_agent_sdk.connectors.github.types.ViewerNotCondition | airbyte_agent_sdk.connectors.github.types.ViewerAndCondition | airbyte_agent_sdk.connectors.github.types.ViewerOrCondition | airbyte_agent_sdk.connectors.github.types.ViewerAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.ViewerSortFilter]`
    :   The type of the None singleton.

<a id="ViewerSortFilter"></a>

`ViewerSortFilter(*args, **kwargs)`
:   Available fields for sorting viewer search results.

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerStringFilter"></a>

`ViewerStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict