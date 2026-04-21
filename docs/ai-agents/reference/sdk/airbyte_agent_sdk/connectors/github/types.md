---
id: airbyte_agent_sdk-connectors-github-types
title: airbyte_agent_sdk.connectors.github.types
---

Module airbyte_agent_sdk.connectors.github.types
================================================
Type definitions for github connector.

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

`BranchesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`BranchesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.BranchesAnyValueFilter`
    :   The type of the None singleton.

`BranchesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

`BranchesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.BranchesStringFilter`
    :   The type of the None singleton.

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

`BranchesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

`BranchesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

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

`BranchesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`BranchesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.BranchesStringFilter`
    :   The type of the None singleton.

`BranchesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.BranchesStringFilter`
    :   The type of the None singleton.

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

`BranchesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

`BranchesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

`BranchesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.BranchesSearchFilter`
    :   The type of the None singleton.

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

`BranchesSearchFilter(*args, **kwargs)`
:   Available fields for filtering branches search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`BranchesSearchQuery(*args, **kwargs)`
:   Search query for branches entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.BranchesEqCondition | airbyte_agent_sdk.connectors.github.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.github.types.BranchesGtCondition | airbyte_agent_sdk.connectors.github.types.BranchesGteCondition | airbyte_agent_sdk.connectors.github.types.BranchesLtCondition | airbyte_agent_sdk.connectors.github.types.BranchesLteCondition | airbyte_agent_sdk.connectors.github.types.BranchesInCondition | airbyte_agent_sdk.connectors.github.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.github.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.github.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.github.types.BranchesNotCondition | airbyte_agent_sdk.connectors.github.types.BranchesAndCondition | airbyte_agent_sdk.connectors.github.types.BranchesOrCondition | airbyte_agent_sdk.connectors.github.types.BranchesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.BranchesSortFilter]`
    :   The type of the None singleton.

`BranchesSortFilter(*args, **kwargs)`
:   Available fields for sorting branches search results.

    ### Ancestors (in MRO)

    * builtins.dict

`BranchesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`CommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`CommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

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

`CommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

`CommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.CommentsStringFilter`
    :   The type of the None singleton.

`CommentsGetParams(*args, **kwargs)`
:   Parameters for comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`CommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

`CommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

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

`CommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`CommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.CommentsStringFilter`
    :   The type of the None singleton.

`CommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.CommentsStringFilter`
    :   The type of the None singleton.

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

`CommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

`CommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

`CommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.CommentsSearchFilter`
    :   The type of the None singleton.

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

`CommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`CommentsSearchQuery(*args, **kwargs)`
:   Search query for comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.CommentsEqCondition | airbyte_agent_sdk.connectors.github.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.github.types.CommentsGtCondition | airbyte_agent_sdk.connectors.github.types.CommentsGteCondition | airbyte_agent_sdk.connectors.github.types.CommentsLtCondition | airbyte_agent_sdk.connectors.github.types.CommentsLteCondition | airbyte_agent_sdk.connectors.github.types.CommentsInCondition | airbyte_agent_sdk.connectors.github.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.github.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.github.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.github.types.CommentsNotCondition | airbyte_agent_sdk.connectors.github.types.CommentsAndCondition | airbyte_agent_sdk.connectors.github.types.CommentsOrCondition | airbyte_agent_sdk.connectors.github.types.CommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.CommentsSortFilter]`
    :   The type of the None singleton.

`CommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

`CommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

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

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

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

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.IssuesStringFilter`
    :   The type of the None singleton.

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

`IssuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

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

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.IssuesStringFilter`
    :   The type of the None singleton.

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.IssuesStringFilter`
    :   The type of the None singleton.

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

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.IssuesSearchFilter`
    :   The type of the None singleton.

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

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.IssuesEqCondition | airbyte_agent_sdk.connectors.github.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.github.types.IssuesGtCondition | airbyte_agent_sdk.connectors.github.types.IssuesGteCondition | airbyte_agent_sdk.connectors.github.types.IssuesLtCondition | airbyte_agent_sdk.connectors.github.types.IssuesLteCondition | airbyte_agent_sdk.connectors.github.types.IssuesInCondition | airbyte_agent_sdk.connectors.github.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.github.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.github.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.github.types.IssuesNotCondition | airbyte_agent_sdk.connectors.github.types.IssuesAndCondition | airbyte_agent_sdk.connectors.github.types.IssuesOrCondition | airbyte_agent_sdk.connectors.github.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.IssuesSortFilter]`
    :   The type of the None singleton.

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`OrganizationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`OrganizationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

`OrganizationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.OrganizationsStringFilter`
    :   The type of the None singleton.

`OrganizationsGetParams(*args, **kwargs)`
:   Parameters for organizations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `org: str`
    :   The type of the None singleton.

`OrganizationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

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

`OrganizationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`OrganizationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.OrganizationsStringFilter`
    :   The type of the None singleton.

`OrganizationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.OrganizationsStringFilter`
    :   The type of the None singleton.

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

`OrganizationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

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

`OrganizationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering organizations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`OrganizationsSearchQuery(*args, **kwargs)`
:   Search query for organizations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.github.types.OrganizationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.OrganizationsSortFilter]`
    :   The type of the None singleton.

`OrganizationsSortFilter(*args, **kwargs)`
:   Available fields for sorting organizations search results.

    ### Ancestors (in MRO)

    * builtins.dict

`OrganizationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`PrCommentsGetParams(*args, **kwargs)`
:   Parameters for pr_comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

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

`PullRequestsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

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

`PullRequestsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.PullRequestsAnyValueFilter`
    :   The type of the None singleton.

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

`PullRequestsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

`PullRequestsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.PullRequestsStringFilter`
    :   The type of the None singleton.

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

`PullRequestsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

`PullRequestsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

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

`PullRequestsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`PullRequestsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.PullRequestsStringFilter`
    :   The type of the None singleton.

`PullRequestsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.PullRequestsStringFilter`
    :   The type of the None singleton.

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

`PullRequestsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

`PullRequestsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

`PullRequestsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.PullRequestsSearchFilter`
    :   The type of the None singleton.

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

`PullRequestsSearchFilter(*args, **kwargs)`
:   Available fields for filtering pull_requests search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`PullRequestsSearchQuery(*args, **kwargs)`
:   Search query for pull_requests entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.PullRequestsEqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNeqCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsGteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLtCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLteCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsInCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsLikeCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsKeywordCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsContainsCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsNotCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAndCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsOrCondition | airbyte_agent_sdk.connectors.github.types.PullRequestsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.PullRequestsSortFilter]`
    :   The type of the None singleton.

`PullRequestsSortFilter(*args, **kwargs)`
:   Available fields for sorting pull_requests search results.

    ### Ancestors (in MRO)

    * builtins.dict

`PullRequestsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`RepositoriesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

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

`RepositoriesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.RepositoriesAnyValueFilter`
    :   The type of the None singleton.

`RepositoriesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

`RepositoriesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.RepositoriesStringFilter`
    :   The type of the None singleton.

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

`RepositoriesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

`RepositoriesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

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

`RepositoriesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`RepositoriesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.RepositoriesStringFilter`
    :   The type of the None singleton.

`RepositoriesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.RepositoriesStringFilter`
    :   The type of the None singleton.

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

`RepositoriesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

`RepositoriesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

`RepositoriesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.RepositoriesSearchFilter`
    :   The type of the None singleton.

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

`RepositoriesSearchFilter(*args, **kwargs)`
:   Available fields for filtering repositories search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`RepositoriesSearchQuery(*args, **kwargs)`
:   Search query for repositories entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.RepositoriesEqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNeqCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesGteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLtCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLteCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesInCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesLikeCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesFuzzyCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesKeywordCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesContainsCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesNotCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAndCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesOrCondition | airbyte_agent_sdk.connectors.github.types.RepositoriesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.RepositoriesSortFilter]`
    :   The type of the None singleton.

`RepositoriesSortFilter(*args, **kwargs)`
:   Available fields for sorting repositories search results.

    ### Ancestors (in MRO)

    * builtins.dict

`RepositoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`StargazersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`StargazersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.StargazersAnyValueFilter`
    :   The type of the None singleton.

`StargazersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

`StargazersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.StargazersStringFilter`
    :   The type of the None singleton.

`StargazersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

`StargazersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

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

`StargazersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`StargazersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.StargazersStringFilter`
    :   The type of the None singleton.

`StargazersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.StargazersStringFilter`
    :   The type of the None singleton.

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

`StargazersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

`StargazersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

`StargazersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.StargazersSearchFilter`
    :   The type of the None singleton.

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

`StargazersSearchFilter(*args, **kwargs)`
:   Available fields for filtering stargazers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`StargazersSearchQuery(*args, **kwargs)`
:   Search query for stargazers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.StargazersEqCondition | airbyte_agent_sdk.connectors.github.types.StargazersNeqCondition | airbyte_agent_sdk.connectors.github.types.StargazersGtCondition | airbyte_agent_sdk.connectors.github.types.StargazersGteCondition | airbyte_agent_sdk.connectors.github.types.StargazersLtCondition | airbyte_agent_sdk.connectors.github.types.StargazersLteCondition | airbyte_agent_sdk.connectors.github.types.StargazersInCondition | airbyte_agent_sdk.connectors.github.types.StargazersLikeCondition | airbyte_agent_sdk.connectors.github.types.StargazersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.StargazersKeywordCondition | airbyte_agent_sdk.connectors.github.types.StargazersContainsCondition | airbyte_agent_sdk.connectors.github.types.StargazersNotCondition | airbyte_agent_sdk.connectors.github.types.StargazersAndCondition | airbyte_agent_sdk.connectors.github.types.StargazersOrCondition | airbyte_agent_sdk.connectors.github.types.StargazersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.StargazersSortFilter]`
    :   The type of the None singleton.

`StargazersSortFilter(*args, **kwargs)`
:   Available fields for sorting stargazers search results.

    ### Ancestors (in MRO)

    * builtins.dict

`StargazersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.TagsAnyValueFilter`
    :   The type of the None singleton.

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.TagsStringFilter`
    :   The type of the None singleton.

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

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.TagsInFilter`
    :   The type of the None singleton.

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.TagsStringFilter`
    :   The type of the None singleton.

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

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.TagsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition]`
    :   The type of the None singleton.

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.TagsEqCondition | airbyte_agent_sdk.connectors.github.types.TagsNeqCondition | airbyte_agent_sdk.connectors.github.types.TagsGtCondition | airbyte_agent_sdk.connectors.github.types.TagsGteCondition | airbyte_agent_sdk.connectors.github.types.TagsLtCondition | airbyte_agent_sdk.connectors.github.types.TagsLteCondition | airbyte_agent_sdk.connectors.github.types.TagsInCondition | airbyte_agent_sdk.connectors.github.types.TagsLikeCondition | airbyte_agent_sdk.connectors.github.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TagsContainsCondition | airbyte_agent_sdk.connectors.github.types.TagsNotCondition | airbyte_agent_sdk.connectors.github.types.TagsAndCondition | airbyte_agent_sdk.connectors.github.types.TagsOrCondition | airbyte_agent_sdk.connectors.github.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.TagsSortFilter]`
    :   The type of the None singleton.

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.TeamsStringFilter`
    :   The type of the None singleton.

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

`TeamsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.TeamsInFilter`
    :   The type of the None singleton.

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.TeamsStringFilter`
    :   The type of the None singleton.

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.TeamsStringFilter`
    :   The type of the None singleton.

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

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
    :   The type of the None singleton.

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.TeamsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition]`
    :   The type of the None singleton.

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.TeamsEqCondition | airbyte_agent_sdk.connectors.github.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.github.types.TeamsGtCondition | airbyte_agent_sdk.connectors.github.types.TeamsGteCondition | airbyte_agent_sdk.connectors.github.types.TeamsLtCondition | airbyte_agent_sdk.connectors.github.types.TeamsLteCondition | airbyte_agent_sdk.connectors.github.types.TeamsInCondition | airbyte_agent_sdk.connectors.github.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.github.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.github.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.github.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.github.types.TeamsNotCondition | airbyte_agent_sdk.connectors.github.types.TeamsAndCondition | airbyte_agent_sdk.connectors.github.types.TeamsOrCondition | airbyte_agent_sdk.connectors.github.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.TeamsSortFilter]`
    :   The type of the None singleton.

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

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

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.github.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.github.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

    `username: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.github.types.UsersInFilter`
    :   The type of the None singleton.

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.github.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.github.types.UsersStringFilter`
    :   The type of the None singleton.

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

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.github.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition]`
    :   The type of the None singleton.

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.github.types.UsersEqCondition | airbyte_agent_sdk.connectors.github.types.UsersNeqCondition | airbyte_agent_sdk.connectors.github.types.UsersGtCondition | airbyte_agent_sdk.connectors.github.types.UsersGteCondition | airbyte_agent_sdk.connectors.github.types.UsersLtCondition | airbyte_agent_sdk.connectors.github.types.UsersLteCondition | airbyte_agent_sdk.connectors.github.types.UsersInCondition | airbyte_agent_sdk.connectors.github.types.UsersLikeCondition | airbyte_agent_sdk.connectors.github.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.github.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.github.types.UsersContainsCondition | airbyte_agent_sdk.connectors.github.types.UsersNotCondition | airbyte_agent_sdk.connectors.github.types.UsersAndCondition | airbyte_agent_sdk.connectors.github.types.UsersOrCondition | airbyte_agent_sdk.connectors.github.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.github.types.UsersSortFilter]`
    :   The type of the None singleton.

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

`ViewerGetParams(*args, **kwargs)`
:   Parameters for viewer.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
    :   The type of the None singleton.

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