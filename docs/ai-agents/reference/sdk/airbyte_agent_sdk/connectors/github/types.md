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

<a id="BranchesStringFilter"></a>

`BranchesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CommentsStringFilter"></a>

`CommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="OrganizationsStringFilter"></a>

`OrganizationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="PullRequestsStringFilter"></a>

`PullRequestsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="RepositoriesStringFilter"></a>

`RepositoriesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="StargazersStringFilter"></a>

`StargazersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="TagsStringFilter"></a>

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="TeamsStringFilter"></a>

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ViewerGetParams"></a>

`ViewerGetParams(*args, **kwargs)`
:   Parameters for viewer.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: list[str]`
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