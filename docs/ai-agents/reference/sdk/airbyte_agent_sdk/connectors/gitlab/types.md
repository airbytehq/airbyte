---
id: airbyte_agent_sdk-connectors-gitlab-types
title: airbyte_agent_sdk.connectors.gitlab.types
---

Module airbyte_agent_sdk.connectors.gitlab.types
================================================
Type definitions for gitlab connector.

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.BranchesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesInCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.BranchesAnyValueFilter`
    :   The type of the None singleton.

<a id="BranchesAnyValueFilter"></a>

`BranchesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `can_push: Any`
    :   Whether the current user can push

    `commit: Any`
    :   Head commit details

    `commit_id: Any`
    :   SHA of the head commit

    `default: Any`
    :   Whether this is the default branch

    `developers_can_merge: Any`
    :   Whether developers can merge into the branch

    `developers_can_push: Any`
    :   Whether developers can push to the branch

    `merged: Any`
    :   Whether the branch is merged

    `name: Any`
    :   Name of the branch

    `project_id: Any`
    :   ID of the project the branch belongs to

    `protected: Any`
    :   Whether the branch is protected

    `web_url: Any`
    :   Web URL of the branch

<a id="BranchesContainsCondition"></a>

`BranchesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.BranchesAnyValueFilter`
    :   The type of the None singleton.

<a id="BranchesEqCondition"></a>

`BranchesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesFuzzyCondition"></a>

`BranchesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.BranchesStringFilter`
    :   The type of the None singleton.

<a id="BranchesGetParams"></a>

`BranchesGetParams(*args, **kwargs)`
:   Parameters for branches.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `branch: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="BranchesGtCondition"></a>

`BranchesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesGteCondition"></a>

`BranchesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.BranchesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.BranchesInFilter`
    :   The type of the None singleton.

<a id="BranchesInFilter"></a>

`BranchesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `can_push: list[bool]`
    :   Whether the current user can push

    `commit: list[dict[str, typing.Any]]`
    :   Head commit details

    `commit_id: list[str]`
    :   SHA of the head commit

    `default: list[bool]`
    :   Whether this is the default branch

    `developers_can_merge: list[bool]`
    :   Whether developers can merge into the branch

    `developers_can_push: list[bool]`
    :   Whether developers can push to the branch

    `merged: list[bool]`
    :   Whether the branch is merged

    `name: list[str]`
    :   Name of the branch

    `project_id: list[int]`
    :   ID of the project the branch belongs to

    `protected: list[bool]`
    :   Whether the branch is protected

    `web_url: list[str]`
    :   Web URL of the branch

<a id="BranchesKeywordCondition"></a>

`BranchesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.BranchesStringFilter`
    :   The type of the None singleton.

<a id="BranchesLikeCondition"></a>

`BranchesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.BranchesStringFilter`
    :   The type of the None singleton.

<a id="BranchesListParams"></a>

`BranchesListParams(*args, **kwargs)`
:   Parameters for branches.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

<a id="BranchesLtCondition"></a>

`BranchesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesLteCondition"></a>

`BranchesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.BranchesSearchFilter`
    :   The type of the None singleton.

<a id="BranchesNeqCondition"></a>

`BranchesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.BranchesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.BranchesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesInCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.BranchesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesInCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAnyCondition]`
    :   The type of the None singleton.

<a id="BranchesSearchFilter"></a>

`BranchesSearchFilter(*args, **kwargs)`
:   Available fields for filtering branches search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `can_push: bool | None`
    :   Whether the current user can push

    `commit: dict[str, typing.Any] | None`
    :   Head commit details

    `commit_id: str | None`
    :   SHA of the head commit

    `default: bool | None`
    :   Whether this is the default branch

    `developers_can_merge: bool | None`
    :   Whether developers can merge into the branch

    `developers_can_push: bool | None`
    :   Whether developers can push to the branch

    `merged: bool | None`
    :   Whether the branch is merged

    `name: str | None`
    :   Name of the branch

    `project_id: int | None`
    :   ID of the project the branch belongs to

    `protected: bool | None`
    :   Whether the branch is protected

    `web_url: str | None`
    :   Web URL of the branch

<a id="BranchesSearchQuery"></a>

`BranchesSearchQuery(*args, **kwargs)`
:   Search query for branches entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.BranchesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesInCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.BranchesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.BranchesSortFilter]`
    :   The type of the None singleton.

<a id="BranchesSortFilter"></a>

`BranchesSortFilter(*args, **kwargs)`
:   Available fields for sorting branches search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `can_push: Literal['asc', 'desc']`
    :   Whether the current user can push

    `commit: Literal['asc', 'desc']`
    :   Head commit details

    `commit_id: Literal['asc', 'desc']`
    :   SHA of the head commit

    `default: Literal['asc', 'desc']`
    :   Whether this is the default branch

    `developers_can_merge: Literal['asc', 'desc']`
    :   Whether developers can merge into the branch

    `developers_can_push: Literal['asc', 'desc']`
    :   Whether developers can push to the branch

    `merged: Literal['asc', 'desc']`
    :   Whether the branch is merged

    `name: Literal['asc', 'desc']`
    :   Name of the branch

    `project_id: Literal['asc', 'desc']`
    :   ID of the project the branch belongs to

    `protected: Literal['asc', 'desc']`
    :   Whether the branch is protected

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the branch

<a id="BranchesStringFilter"></a>

`BranchesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `can_push: str`
    :   Whether the current user can push

    `commit: str`
    :   Head commit details

    `commit_id: str`
    :   SHA of the head commit

    `default: str`
    :   Whether this is the default branch

    `developers_can_merge: str`
    :   Whether developers can merge into the branch

    `developers_can_push: str`
    :   Whether developers can push to the branch

    `merged: str`
    :   Whether the branch is merged

    `name: str`
    :   Name of the branch

    `project_id: str`
    :   ID of the project the branch belongs to

    `protected: str`
    :   Whether the branch is protected

    `web_url: str`
    :   Web URL of the branch

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.CommitsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsInCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.CommitsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommitsAnyValueFilter"></a>

`CommitsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_email: Any`
    :   Email of the commit author

    `author_name: Any`
    :   Name of the commit author

    `authored_date: Any`
    :   Date the commit was authored

    `committed_date: Any`
    :   Date the commit was committed

    `committer_email: Any`
    :   Email of the committer

    `committer_name: Any`
    :   Name of the committer

    `created_at: Any`
    :   Timestamp when the commit was created

    `id: Any`
    :   SHA of the commit

    `message: Any`
    :   Full commit message

    `parent_ids: Any`
    :   SHAs of parent commits

    `project_id: Any`
    :   ID of the project the commit belongs to

    `short_id: Any`
    :   Short SHA of the commit

    `stats: Any`
    :   Commit statistics

    `title: Any`
    :   Title of the commit

    `trailers: Any`
    :   Git trailers for the commit

    `web_url: Any`
    :   Web URL of the commit

<a id="CommitsContainsCondition"></a>

`CommitsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.CommitsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommitsEqCondition"></a>

`CommitsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsFuzzyCondition"></a>

`CommitsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.CommitsStringFilter`
    :   The type of the None singleton.

<a id="CommitsGetParams"></a>

`CommitsGetParams(*args, **kwargs)`
:   Parameters for commits.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `project_id: str`
    :   The type of the None singleton.

    `sha: str`
    :   The type of the None singleton.

    `stats: bool`
    :   The type of the None singleton.

<a id="CommitsGtCondition"></a>

`CommitsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsGteCondition"></a>

`CommitsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.CommitsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.CommitsInFilter`
    :   The type of the None singleton.

<a id="CommitsInFilter"></a>

`CommitsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_email: list[str]`
    :   Email of the commit author

    `author_name: list[str]`
    :   Name of the commit author

    `authored_date: list[str]`
    :   Date the commit was authored

    `committed_date: list[str]`
    :   Date the commit was committed

    `committer_email: list[str]`
    :   Email of the committer

    `committer_name: list[str]`
    :   Name of the committer

    `created_at: list[str]`
    :   Timestamp when the commit was created

    `id: list[str]`
    :   SHA of the commit

    `message: list[str]`
    :   Full commit message

    `parent_ids: list[list[typing.Any]]`
    :   SHAs of parent commits

    `project_id: list[int]`
    :   ID of the project the commit belongs to

    `short_id: list[str]`
    :   Short SHA of the commit

    `stats: list[dict[str, typing.Any]]`
    :   Commit statistics

    `title: list[str]`
    :   Title of the commit

    `trailers: list[dict[str, typing.Any]]`
    :   Git trailers for the commit

    `web_url: list[str]`
    :   Web URL of the commit

<a id="CommitsKeywordCondition"></a>

`CommitsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.CommitsStringFilter`
    :   The type of the None singleton.

<a id="CommitsLikeCondition"></a>

`CommitsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.CommitsStringFilter`
    :   The type of the None singleton.

<a id="CommitsListParams"></a>

`CommitsListParams(*args, **kwargs)`
:   Parameters for commits.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `ref_name: str`
    :   The type of the None singleton.

    `since: str`
    :   The type of the None singleton.

    `until: str`
    :   The type of the None singleton.

    `with_stats: bool`
    :   The type of the None singleton.

<a id="CommitsLtCondition"></a>

`CommitsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsLteCondition"></a>

`CommitsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.CommitsSearchFilter`
    :   The type of the None singleton.

<a id="CommitsNeqCondition"></a>

`CommitsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.CommitsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.CommitsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsInCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.CommitsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsInCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAnyCondition]`
    :   The type of the None singleton.

<a id="CommitsSearchFilter"></a>

`CommitsSearchFilter(*args, **kwargs)`
:   Available fields for filtering commits search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_email: str | None`
    :   Email of the commit author

    `author_name: str | None`
    :   Name of the commit author

    `authored_date: str | None`
    :   Date the commit was authored

    `committed_date: str | None`
    :   Date the commit was committed

    `committer_email: str | None`
    :   Email of the committer

    `committer_name: str | None`
    :   Name of the committer

    `created_at: str | None`
    :   Timestamp when the commit was created

    `id: str | None`
    :   SHA of the commit

    `message: str | None`
    :   Full commit message

    `parent_ids: list[typing.Any] | None`
    :   SHAs of parent commits

    `project_id: int | None`
    :   ID of the project the commit belongs to

    `short_id: str | None`
    :   Short SHA of the commit

    `stats: dict[str, typing.Any] | None`
    :   Commit statistics

    `title: str | None`
    :   Title of the commit

    `trailers: dict[str, typing.Any] | None`
    :   Git trailers for the commit

    `web_url: str | None`
    :   Web URL of the commit

<a id="CommitsSearchQuery"></a>

`CommitsSearchQuery(*args, **kwargs)`
:   Search query for commits entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.CommitsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsInCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.CommitsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.CommitsSortFilter]`
    :   The type of the None singleton.

<a id="CommitsSortFilter"></a>

`CommitsSortFilter(*args, **kwargs)`
:   Available fields for sorting commits search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_email: Literal['asc', 'desc']`
    :   Email of the commit author

    `author_name: Literal['asc', 'desc']`
    :   Name of the commit author

    `authored_date: Literal['asc', 'desc']`
    :   Date the commit was authored

    `committed_date: Literal['asc', 'desc']`
    :   Date the commit was committed

    `committer_email: Literal['asc', 'desc']`
    :   Email of the committer

    `committer_name: Literal['asc', 'desc']`
    :   Name of the committer

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the commit was created

    `id: Literal['asc', 'desc']`
    :   SHA of the commit

    `message: Literal['asc', 'desc']`
    :   Full commit message

    `parent_ids: Literal['asc', 'desc']`
    :   SHAs of parent commits

    `project_id: Literal['asc', 'desc']`
    :   ID of the project the commit belongs to

    `short_id: Literal['asc', 'desc']`
    :   Short SHA of the commit

    `stats: Literal['asc', 'desc']`
    :   Commit statistics

    `title: Literal['asc', 'desc']`
    :   Title of the commit

    `trailers: Literal['asc', 'desc']`
    :   Git trailers for the commit

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the commit

<a id="CommitsStringFilter"></a>

`CommitsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_email: str`
    :   Email of the commit author

    `author_name: str`
    :   Name of the commit author

    `authored_date: str`
    :   Date the commit was authored

    `committed_date: str`
    :   Date the commit was committed

    `committer_email: str`
    :   Email of the committer

    `committer_name: str`
    :   Name of the committer

    `created_at: str`
    :   Timestamp when the commit was created

    `id: str`
    :   SHA of the commit

    `message: str`
    :   Full commit message

    `parent_ids: str`
    :   SHAs of parent commits

    `project_id: str`
    :   ID of the project the commit belongs to

    `short_id: str`
    :   Short SHA of the commit

    `stats: str`
    :   Commit statistics

    `title: str`
    :   Title of the commit

    `trailers: str`
    :   Git trailers for the commit

    `web_url: str`
    :   Web URL of the commit

<a id="GroupMembersAndCondition"></a>

`GroupMembersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.GroupMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAnyCondition]`
    :   The type of the None singleton.

<a id="GroupMembersAnyCondition"></a>

`GroupMembersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupMembersAnyValueFilter"></a>

`GroupMembersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: Any`
    :   Access level of the member

    `avatar_url: Any`
    :   URL of the member avatar

    `created_at: Any`
    :   Timestamp when the member was added

    `created_by: Any`
    :   User who added the member

    `expires_at: Any`
    :   Expiration date of the membership

    `group_id: Any`
    :   ID of the group

    `id: Any`
    :   ID of the member

    `locked: Any`
    :   Whether the member account is locked

    `membership_state: Any`
    :   State of the membership

    `name: Any`
    :   Full name of the member

    `state: Any`
    :   State of the member account

    `username: Any`
    :   Username of the member

    `web_url: Any`
    :   Web URL of the member profile

<a id="GroupMembersContainsCondition"></a>

`GroupMembersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupMembersEqCondition"></a>

`GroupMembersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembersFuzzyCondition"></a>

`GroupMembersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersStringFilter`
    :   The type of the None singleton.

<a id="GroupMembersGetParams"></a>

`GroupMembersGetParams(*args, **kwargs)`
:   Parameters for group_members.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

    `user_id: str`
    :   The type of the None singleton.

<a id="GroupMembersGtCondition"></a>

`GroupMembersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembersGteCondition"></a>

`GroupMembersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembersInCondition"></a>

`GroupMembersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersInFilter`
    :   The type of the None singleton.

<a id="GroupMembersInFilter"></a>

`GroupMembersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: list[int]`
    :   Access level of the member

    `avatar_url: list[str]`
    :   URL of the member avatar

    `created_at: list[str]`
    :   Timestamp when the member was added

    `created_by: list[dict[str, typing.Any]]`
    :   User who added the member

    `expires_at: list[str]`
    :   Expiration date of the membership

    `group_id: list[int]`
    :   ID of the group

    `id: list[int]`
    :   ID of the member

    `locked: list[bool]`
    :   Whether the member account is locked

    `membership_state: list[str]`
    :   State of the membership

    `name: list[str]`
    :   Full name of the member

    `state: list[str]`
    :   State of the member account

    `username: list[str]`
    :   Username of the member

    `web_url: list[str]`
    :   Web URL of the member profile

<a id="GroupMembersKeywordCondition"></a>

`GroupMembersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersStringFilter`
    :   The type of the None singleton.

<a id="GroupMembersLikeCondition"></a>

`GroupMembersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersStringFilter`
    :   The type of the None singleton.

<a id="GroupMembersListParams"></a>

`GroupMembersListParams(*args, **kwargs)`
:   Parameters for group_members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="GroupMembersLtCondition"></a>

`GroupMembersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembersLteCondition"></a>

`GroupMembersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembersNeqCondition"></a>

`GroupMembersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembersNotCondition"></a>

`GroupMembersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAnyCondition`
    :   The type of the None singleton.

<a id="GroupMembersOrCondition"></a>

`GroupMembersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.GroupMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAnyCondition]`
    :   The type of the None singleton.

<a id="GroupMembersSearchFilter"></a>

`GroupMembersSearchFilter(*args, **kwargs)`
:   Available fields for filtering group_members search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: int | None`
    :   Access level of the member

    `avatar_url: str | None`
    :   URL of the member avatar

    `created_at: str | None`
    :   Timestamp when the member was added

    `created_by: dict[str, typing.Any] | None`
    :   User who added the member

    `expires_at: str | None`
    :   Expiration date of the membership

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   ID of the member

    `locked: bool | None`
    :   Whether the member account is locked

    `membership_state: str | None`
    :   State of the membership

    `name: str | None`
    :   Full name of the member

    `state: str | None`
    :   State of the member account

    `username: str | None`
    :   Username of the member

    `web_url: str | None`
    :   Web URL of the member profile

<a id="GroupMembersSearchQuery"></a>

`GroupMembersSearchQuery(*args, **kwargs)`
:   Search query for group_members entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.GroupMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMembersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.GroupMembersSortFilter]`
    :   The type of the None singleton.

<a id="GroupMembersSortFilter"></a>

`GroupMembersSortFilter(*args, **kwargs)`
:   Available fields for sorting group_members search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: Literal['asc', 'desc']`
    :   Access level of the member

    `avatar_url: Literal['asc', 'desc']`
    :   URL of the member avatar

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the member was added

    `created_by: Literal['asc', 'desc']`
    :   User who added the member

    `expires_at: Literal['asc', 'desc']`
    :   Expiration date of the membership

    `group_id: Literal['asc', 'desc']`
    :   ID of the group

    `id: Literal['asc', 'desc']`
    :   ID of the member

    `locked: Literal['asc', 'desc']`
    :   Whether the member account is locked

    `membership_state: Literal['asc', 'desc']`
    :   State of the membership

    `name: Literal['asc', 'desc']`
    :   Full name of the member

    `state: Literal['asc', 'desc']`
    :   State of the member account

    `username: Literal['asc', 'desc']`
    :   Username of the member

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the member profile

<a id="GroupMembersStringFilter"></a>

`GroupMembersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: str`
    :   Access level of the member

    `avatar_url: str`
    :   URL of the member avatar

    `created_at: str`
    :   Timestamp when the member was added

    `created_by: str`
    :   User who added the member

    `expires_at: str`
    :   Expiration date of the membership

    `group_id: str`
    :   ID of the group

    `id: str`
    :   ID of the member

    `locked: str`
    :   Whether the member account is locked

    `membership_state: str`
    :   State of the membership

    `name: str`
    :   Full name of the member

    `state: str`
    :   State of the member account

    `username: str`
    :   Username of the member

    `web_url: str`
    :   Web URL of the member profile

<a id="GroupMilestonesAndCondition"></a>

`GroupMilestonesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAnyCondition]`
    :   The type of the None singleton.

<a id="GroupMilestonesAnyCondition"></a>

`GroupMilestonesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesAnyValueFilter"></a>

`GroupMilestonesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the milestone was created

    `description: Any`
    :   Description of the milestone

    `due_date: Any`
    :   Due date of the milestone

    `expired: Any`
    :   Whether the milestone is expired

    `group_id: Any`
    :   ID of the group

    `id: Any`
    :   ID of the milestone

    `iid: Any`
    :   Internal ID of the milestone within the group

    `start_date: Any`
    :   Start date of the milestone

    `state: Any`
    :   State of the milestone

    `title: Any`
    :   Title of the milestone

    `updated_at: Any`
    :   Timestamp when the milestone was last updated

    `web_url: Any`
    :   Web URL of the milestone

<a id="GroupMilestonesContainsCondition"></a>

`GroupMilestonesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesEqCondition"></a>

`GroupMilestonesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesFuzzyCondition"></a>

`GroupMilestonesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesStringFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesGetParams"></a>

`GroupMilestonesGetParams(*args, **kwargs)`
:   Parameters for group_milestones.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

    `milestone_id: str`
    :   The type of the None singleton.

<a id="GroupMilestonesGtCondition"></a>

`GroupMilestonesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesGteCondition"></a>

`GroupMilestonesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesInCondition"></a>

`GroupMilestonesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesInFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesInFilter"></a>

`GroupMilestonesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the milestone was created

    `description: list[str]`
    :   Description of the milestone

    `due_date: list[str]`
    :   Due date of the milestone

    `expired: list[bool]`
    :   Whether the milestone is expired

    `group_id: list[int]`
    :   ID of the group

    `id: list[int]`
    :   ID of the milestone

    `iid: list[int]`
    :   Internal ID of the milestone within the group

    `start_date: list[str]`
    :   Start date of the milestone

    `state: list[str]`
    :   State of the milestone

    `title: list[str]`
    :   Title of the milestone

    `updated_at: list[str]`
    :   Timestamp when the milestone was last updated

    `web_url: list[str]`
    :   Web URL of the milestone

<a id="GroupMilestonesKeywordCondition"></a>

`GroupMilestonesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesStringFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesLikeCondition"></a>

`GroupMilestonesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesStringFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesListParams"></a>

`GroupMilestonesListParams(*args, **kwargs)`
:   Parameters for group_milestones.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

<a id="GroupMilestonesLtCondition"></a>

`GroupMilestonesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesLteCondition"></a>

`GroupMilestonesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesNeqCondition"></a>

`GroupMilestonesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="GroupMilestonesNotCondition"></a>

`GroupMilestonesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAnyCondition`
    :   The type of the None singleton.

<a id="GroupMilestonesOrCondition"></a>

`GroupMilestonesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAnyCondition]`
    :   The type of the None singleton.

<a id="GroupMilestonesSearchFilter"></a>

`GroupMilestonesSearchFilter(*args, **kwargs)`
:   Available fields for filtering group_milestones search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the milestone was created

    `description: str | None`
    :   Description of the milestone

    `due_date: str | None`
    :   Due date of the milestone

    `expired: bool | None`
    :   Whether the milestone is expired

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   ID of the milestone

    `iid: int | None`
    :   Internal ID of the milestone within the group

    `start_date: str | None`
    :   Start date of the milestone

    `state: str | None`
    :   State of the milestone

    `title: str | None`
    :   Title of the milestone

    `updated_at: str | None`
    :   Timestamp when the milestone was last updated

    `web_url: str | None`
    :   Web URL of the milestone

<a id="GroupMilestonesSearchQuery"></a>

`GroupMilestonesSearchQuery(*args, **kwargs)`
:   Search query for group_milestones entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.GroupMilestonesSortFilter]`
    :   The type of the None singleton.

<a id="GroupMilestonesSortFilter"></a>

`GroupMilestonesSortFilter(*args, **kwargs)`
:   Available fields for sorting group_milestones search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the milestone was created

    `description: Literal['asc', 'desc']`
    :   Description of the milestone

    `due_date: Literal['asc', 'desc']`
    :   Due date of the milestone

    `expired: Literal['asc', 'desc']`
    :   Whether the milestone is expired

    `group_id: Literal['asc', 'desc']`
    :   ID of the group

    `id: Literal['asc', 'desc']`
    :   ID of the milestone

    `iid: Literal['asc', 'desc']`
    :   Internal ID of the milestone within the group

    `start_date: Literal['asc', 'desc']`
    :   Start date of the milestone

    `state: Literal['asc', 'desc']`
    :   State of the milestone

    `title: Literal['asc', 'desc']`
    :   Title of the milestone

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the milestone was last updated

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the milestone

<a id="GroupMilestonesStringFilter"></a>

`GroupMilestonesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the milestone was created

    `description: str`
    :   Description of the milestone

    `due_date: str`
    :   Due date of the milestone

    `expired: str`
    :   Whether the milestone is expired

    `group_id: str`
    :   ID of the group

    `id: str`
    :   ID of the milestone

    `iid: str`
    :   Internal ID of the milestone within the group

    `start_date: str`
    :   Start date of the milestone

    `state: str`
    :   State of the milestone

    `title: str`
    :   Title of the milestone

    `updated_at: str`
    :   Timestamp when the milestone was last updated

    `web_url: str`
    :   Web URL of the milestone

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.GroupsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsAnyValueFilter"></a>

`GroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_devops_enabled: Any`
    :   Whether Auto DevOps is enabled

    `avatar_url: Any`
    :   URL of the group avatar

    `created_at: Any`
    :   Timestamp when the group was created

    `default_branch_protection: Any`
    :   Default branch protection level

    `description: Any`
    :   Description of the group

    `emails_disabled: Any`
    :   Whether emails are disabled

    `emails_enabled: Any`
    :   Whether emails are enabled

    `full_name: Any`
    :   Full name of the group

    `full_path: Any`
    :   Full path of the group

    `id: Any`
    :   ID of the group

    `lfs_enabled: Any`
    :   Whether Git LFS is enabled

    `mentions_disabled: Any`
    :   Whether mentions are disabled

    `name: Any`
    :   Name of the group

    `parent_id: Any`
    :   ID of the parent group

    `path: Any`
    :   URL path of the group

    `project_creation_level: Any`
    :   Level required to create projects

    `projects: Any`
    :   Projects in the group

    `request_access_enabled: Any`
    :   Whether access requests are enabled

    `require_two_factor_authentication: Any`
    :   Whether two-factor authentication is required

    `share_with_group_lock: Any`
    :   Whether sharing with other groups is locked

    `shared_with_groups: Any`
    :   Groups this group is shared with

    `subgroup_creation_level: Any`
    :   Level required to create subgroups

    `two_factor_grace_period: Any`
    :   Grace period for two-factor authentication

    `visibility: Any`
    :   Visibility level of the group

    `web_url: Any`
    :   Web URL of the group

<a id="GroupsContainsCondition"></a>

`GroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsEqCondition"></a>

`GroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsFuzzyCondition"></a>

`GroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.GroupsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.gitlab.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsGteCondition"></a>

`GroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.GroupsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.GroupsInFilter`
    :   The type of the None singleton.

<a id="GroupsInFilter"></a>

`GroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_devops_enabled: list[bool]`
    :   Whether Auto DevOps is enabled

    `avatar_url: list[str]`
    :   URL of the group avatar

    `created_at: list[str]`
    :   Timestamp when the group was created

    `default_branch_protection: list[int]`
    :   Default branch protection level

    `description: list[str]`
    :   Description of the group

    `emails_disabled: list[bool]`
    :   Whether emails are disabled

    `emails_enabled: list[bool]`
    :   Whether emails are enabled

    `full_name: list[str]`
    :   Full name of the group

    `full_path: list[str]`
    :   Full path of the group

    `id: list[int]`
    :   ID of the group

    `lfs_enabled: list[bool]`
    :   Whether Git LFS is enabled

    `mentions_disabled: list[bool]`
    :   Whether mentions are disabled

    `name: list[str]`
    :   Name of the group

    `parent_id: list[int]`
    :   ID of the parent group

    `path: list[str]`
    :   URL path of the group

    `project_creation_level: list[str]`
    :   Level required to create projects

    `projects: list[list[typing.Any]]`
    :   Projects in the group

    `request_access_enabled: list[bool]`
    :   Whether access requests are enabled

    `require_two_factor_authentication: list[bool]`
    :   Whether two-factor authentication is required

    `share_with_group_lock: list[bool]`
    :   Whether sharing with other groups is locked

    `shared_with_groups: list[list[typing.Any]]`
    :   Groups this group is shared with

    `subgroup_creation_level: list[str]`
    :   Level required to create subgroups

    `two_factor_grace_period: list[int]`
    :   Grace period for two-factor authentication

    `visibility: list[str]`
    :   Visibility level of the group

    `web_url: list[str]`
    :   Web URL of the group

<a id="GroupsKeywordCondition"></a>

`GroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsLikeCondition"></a>

`GroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsListParams"></a>

`GroupsListParams(*args, **kwargs)`
:   Parameters for groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_by: str`
    :   The type of the None singleton.

    `owned: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="GroupsLtCondition"></a>

`GroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsLteCondition"></a>

`GroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsNeqCondition"></a>

`GroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.GroupsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.GroupsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.GroupsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupsSearchFilter"></a>

`GroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_devops_enabled: bool | None`
    :   Whether Auto DevOps is enabled

    `avatar_url: str | None`
    :   URL of the group avatar

    `created_at: str | None`
    :   Timestamp when the group was created

    `default_branch_protection: int | None`
    :   Default branch protection level

    `description: str | None`
    :   Description of the group

    `emails_disabled: bool | None`
    :   Whether emails are disabled

    `emails_enabled: bool | None`
    :   Whether emails are enabled

    `full_name: str | None`
    :   Full name of the group

    `full_path: str | None`
    :   Full path of the group

    `id: int | None`
    :   ID of the group

    `lfs_enabled: bool | None`
    :   Whether Git LFS is enabled

    `mentions_disabled: bool | None`
    :   Whether mentions are disabled

    `name: str | None`
    :   Name of the group

    `parent_id: int | None`
    :   ID of the parent group

    `path: str | None`
    :   URL path of the group

    `project_creation_level: str | None`
    :   Level required to create projects

    `projects: list[typing.Any] | None`
    :   Projects in the group

    `request_access_enabled: bool | None`
    :   Whether access requests are enabled

    `require_two_factor_authentication: bool | None`
    :   Whether two-factor authentication is required

    `share_with_group_lock: bool | None`
    :   Whether sharing with other groups is locked

    `shared_with_groups: list[typing.Any] | None`
    :   Groups this group is shared with

    `subgroup_creation_level: str | None`
    :   Level required to create subgroups

    `two_factor_grace_period: int | None`
    :   Grace period for two-factor authentication

    `visibility: str | None`
    :   Visibility level of the group

    `web_url: str | None`
    :   Web URL of the group

<a id="GroupsSearchQuery"></a>

`GroupsSearchQuery(*args, **kwargs)`
:   Search query for groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.GroupsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsInCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.GroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.GroupsSortFilter]`
    :   The type of the None singleton.

<a id="GroupsSortFilter"></a>

`GroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_devops_enabled: Literal['asc', 'desc']`
    :   Whether Auto DevOps is enabled

    `avatar_url: Literal['asc', 'desc']`
    :   URL of the group avatar

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the group was created

    `default_branch_protection: Literal['asc', 'desc']`
    :   Default branch protection level

    `description: Literal['asc', 'desc']`
    :   Description of the group

    `emails_disabled: Literal['asc', 'desc']`
    :   Whether emails are disabled

    `emails_enabled: Literal['asc', 'desc']`
    :   Whether emails are enabled

    `full_name: Literal['asc', 'desc']`
    :   Full name of the group

    `full_path: Literal['asc', 'desc']`
    :   Full path of the group

    `id: Literal['asc', 'desc']`
    :   ID of the group

    `lfs_enabled: Literal['asc', 'desc']`
    :   Whether Git LFS is enabled

    `mentions_disabled: Literal['asc', 'desc']`
    :   Whether mentions are disabled

    `name: Literal['asc', 'desc']`
    :   Name of the group

    `parent_id: Literal['asc', 'desc']`
    :   ID of the parent group

    `path: Literal['asc', 'desc']`
    :   URL path of the group

    `project_creation_level: Literal['asc', 'desc']`
    :   Level required to create projects

    `projects: Literal['asc', 'desc']`
    :   Projects in the group

    `request_access_enabled: Literal['asc', 'desc']`
    :   Whether access requests are enabled

    `require_two_factor_authentication: Literal['asc', 'desc']`
    :   Whether two-factor authentication is required

    `share_with_group_lock: Literal['asc', 'desc']`
    :   Whether sharing with other groups is locked

    `shared_with_groups: Literal['asc', 'desc']`
    :   Groups this group is shared with

    `subgroup_creation_level: Literal['asc', 'desc']`
    :   Level required to create subgroups

    `two_factor_grace_period: Literal['asc', 'desc']`
    :   Grace period for two-factor authentication

    `visibility: Literal['asc', 'desc']`
    :   Visibility level of the group

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the group

<a id="GroupsStringFilter"></a>

`GroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_devops_enabled: str`
    :   Whether Auto DevOps is enabled

    `avatar_url: str`
    :   URL of the group avatar

    `created_at: str`
    :   Timestamp when the group was created

    `default_branch_protection: str`
    :   Default branch protection level

    `description: str`
    :   Description of the group

    `emails_disabled: str`
    :   Whether emails are disabled

    `emails_enabled: str`
    :   Whether emails are enabled

    `full_name: str`
    :   Full name of the group

    `full_path: str`
    :   Full path of the group

    `id: str`
    :   ID of the group

    `lfs_enabled: str`
    :   Whether Git LFS is enabled

    `mentions_disabled: str`
    :   Whether mentions are disabled

    `name: str`
    :   Name of the group

    `parent_id: str`
    :   ID of the parent group

    `path: str`
    :   URL path of the group

    `project_creation_level: str`
    :   Level required to create projects

    `projects: str`
    :   Projects in the group

    `request_access_enabled: str`
    :   Whether access requests are enabled

    `require_two_factor_authentication: str`
    :   Whether two-factor authentication is required

    `share_with_group_lock: str`
    :   Whether sharing with other groups is locked

    `shared_with_groups: str`
    :   Groups this group is shared with

    `subgroup_creation_level: str`
    :   Level required to create subgroups

    `two_factor_grace_period: str`
    :   Grace period for two-factor authentication

    `visibility: str`
    :   Visibility level of the group

    `web_url: str`
    :   Web URL of the group

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.IssuesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesInCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesAnyValueFilter"></a>

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: Any`
    :   Primary assignee of the issue

    `assignee_id: Any`
    :   ID of the primary assignee

    `assignees: Any`
    :   Users assigned to the issue

    `author: Any`
    :   Author of the issue

    `author_id: Any`
    :   ID of the author

    `blocking_issues_count: Any`
    :   Number of blocking issues

    `closed_at: Any`
    :   Timestamp when the issue was closed

    `closed_by: Any`
    :   User who closed the issue

    `closed_by_id: Any`
    :   ID of the user who closed the issue

    `confidential: Any`
    :   Whether the issue is confidential

    `created_at: Any`
    :   Timestamp when the issue was created

    `description: Any`
    :   Description of the issue

    `discussion_locked: Any`
    :   Whether discussion is locked

    `downvotes: Any`
    :   Number of downvotes

    `due_date: Any`
    :   Due date for the issue

    `has_tasks: Any`
    :   Whether the issue has tasks

    `id: Any`
    :   ID of the issue

    `iid: Any`
    :   Internal ID of the issue within the project

    `issue_type: Any`
    :   Type classification of the issue

    `labels: Any`
    :   Labels assigned to the issue

    `links: Any`
    :   Related resource links

    `merge_requests_count: Any`
    :   Number of related merge requests

    `milestone: Any`
    :   Milestone the issue belongs to

    `milestone_id: Any`
    :   ID of the milestone

    `project_id: Any`
    :   ID of the project the issue belongs to

    `references: Any`
    :   Issue references

    `severity: Any`
    :   Severity level of the issue

    `state: Any`
    :   State of the issue

    `task_completion_status: Any`
    :   Task completion status

    `time_stats: Any`
    :   Time tracking statistics

    `title: Any`
    :   Title of the issue

    `type_: Any`
    :   Type of the issue

    `updated_at: Any`
    :   Timestamp when the issue was last updated

    `upvotes: Any`
    :   Number of upvotes

    `user_notes_count: Any`
    :   Number of user notes on the issue

    `web_url: Any`
    :   Web URL of the issue

    `weight: Any`
    :   Weight of the issue

<a id="IssuesContainsCondition"></a>

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesEqCondition"></a>

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesFuzzyCondition"></a>

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesGetParams"></a>

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `issue_iid: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="IssuesGtCondition"></a>

`IssuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesGteCondition"></a>

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.IssuesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.IssuesInFilter`
    :   The type of the None singleton.

<a id="IssuesInFilter"></a>

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: list[dict[str, typing.Any]]`
    :   Primary assignee of the issue

    `assignee_id: list[int]`
    :   ID of the primary assignee

    `assignees: list[list[typing.Any]]`
    :   Users assigned to the issue

    `author: list[dict[str, typing.Any]]`
    :   Author of the issue

    `author_id: list[int]`
    :   ID of the author

    `blocking_issues_count: list[int]`
    :   Number of blocking issues

    `closed_at: list[str]`
    :   Timestamp when the issue was closed

    `closed_by: list[dict[str, typing.Any]]`
    :   User who closed the issue

    `closed_by_id: list[int]`
    :   ID of the user who closed the issue

    `confidential: list[bool]`
    :   Whether the issue is confidential

    `created_at: list[str]`
    :   Timestamp when the issue was created

    `description: list[str]`
    :   Description of the issue

    `discussion_locked: list[bool]`
    :   Whether discussion is locked

    `downvotes: list[int]`
    :   Number of downvotes

    `due_date: list[str]`
    :   Due date for the issue

    `has_tasks: list[bool]`
    :   Whether the issue has tasks

    `id: list[int]`
    :   ID of the issue

    `iid: list[int]`
    :   Internal ID of the issue within the project

    `issue_type: list[str]`
    :   Type classification of the issue

    `labels: list[list[typing.Any]]`
    :   Labels assigned to the issue

    `links: list[dict[str, typing.Any]]`
    :   Related resource links

    `merge_requests_count: list[int]`
    :   Number of related merge requests

    `milestone: list[dict[str, typing.Any]]`
    :   Milestone the issue belongs to

    `milestone_id: list[int]`
    :   ID of the milestone

    `project_id: list[int]`
    :   ID of the project the issue belongs to

    `references: list[dict[str, typing.Any]]`
    :   Issue references

    `severity: list[str]`
    :   Severity level of the issue

    `state: list[str]`
    :   State of the issue

    `task_completion_status: list[dict[str, typing.Any]]`
    :   Task completion status

    `time_stats: list[dict[str, typing.Any]]`
    :   Time tracking statistics

    `title: list[str]`
    :   Title of the issue

    `type_: list[str]`
    :   Type of the issue

    `updated_at: list[str]`
    :   Timestamp when the issue was last updated

    `upvotes: list[int]`
    :   Number of upvotes

    `user_notes_count: list[int]`
    :   Number of user notes on the issue

    `web_url: list[str]`
    :   Web URL of the issue

    `weight: list[int]`
    :   Weight of the issue

<a id="IssuesKeywordCondition"></a>

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLikeCondition"></a>

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesListParams"></a>

`IssuesListParams(*args, **kwargs)`
:   Parameters for issues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `scope: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `updated_after: str`
    :   The type of the None singleton.

    `updated_before: str`
    :   The type of the None singleton.

<a id="IssuesLtCondition"></a>

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesLteCondition"></a>

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNeqCondition"></a>

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.IssuesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.IssuesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesInCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.IssuesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesInCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesSearchFilter"></a>

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: dict[str, typing.Any] | None`
    :   Primary assignee of the issue

    `assignee_id: int | None`
    :   ID of the primary assignee

    `assignees: list[typing.Any] | None`
    :   Users assigned to the issue

    `author: dict[str, typing.Any] | None`
    :   Author of the issue

    `author_id: int | None`
    :   ID of the author

    `blocking_issues_count: int | None`
    :   Number of blocking issues

    `closed_at: str | None`
    :   Timestamp when the issue was closed

    `closed_by: dict[str, typing.Any] | None`
    :   User who closed the issue

    `closed_by_id: int | None`
    :   ID of the user who closed the issue

    `confidential: bool | None`
    :   Whether the issue is confidential

    `created_at: str | None`
    :   Timestamp when the issue was created

    `description: str | None`
    :   Description of the issue

    `discussion_locked: bool | None`
    :   Whether discussion is locked

    `downvotes: int | None`
    :   Number of downvotes

    `due_date: str | None`
    :   Due date for the issue

    `has_tasks: bool | None`
    :   Whether the issue has tasks

    `id: int | None`
    :   ID of the issue

    `iid: int | None`
    :   Internal ID of the issue within the project

    `issue_type: str | None`
    :   Type classification of the issue

    `labels: list[typing.Any] | None`
    :   Labels assigned to the issue

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `merge_requests_count: int | None`
    :   Number of related merge requests

    `milestone: dict[str, typing.Any] | None`
    :   Milestone the issue belongs to

    `milestone_id: int | None`
    :   ID of the milestone

    `project_id: int | None`
    :   ID of the project the issue belongs to

    `references: dict[str, typing.Any] | None`
    :   Issue references

    `severity: str | None`
    :   Severity level of the issue

    `state: str | None`
    :   State of the issue

    `task_completion_status: dict[str, typing.Any] | None`
    :   Task completion status

    `time_stats: dict[str, typing.Any] | None`
    :   Time tracking statistics

    `title: str | None`
    :   Title of the issue

    `type_: str | None`
    :   Type of the issue

    `updated_at: str | None`
    :   Timestamp when the issue was last updated

    `upvotes: int | None`
    :   Number of upvotes

    `user_notes_count: int | None`
    :   Number of user notes on the issue

    `web_url: str | None`
    :   Web URL of the issue

    `weight: int | None`
    :   Weight of the issue

<a id="IssuesSearchQuery"></a>

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.IssuesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesInCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.IssuesSortFilter]`
    :   The type of the None singleton.

<a id="IssuesSortFilter"></a>

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: Literal['asc', 'desc']`
    :   Primary assignee of the issue

    `assignee_id: Literal['asc', 'desc']`
    :   ID of the primary assignee

    `assignees: Literal['asc', 'desc']`
    :   Users assigned to the issue

    `author: Literal['asc', 'desc']`
    :   Author of the issue

    `author_id: Literal['asc', 'desc']`
    :   ID of the author

    `blocking_issues_count: Literal['asc', 'desc']`
    :   Number of blocking issues

    `closed_at: Literal['asc', 'desc']`
    :   Timestamp when the issue was closed

    `closed_by: Literal['asc', 'desc']`
    :   User who closed the issue

    `closed_by_id: Literal['asc', 'desc']`
    :   ID of the user who closed the issue

    `confidential: Literal['asc', 'desc']`
    :   Whether the issue is confidential

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the issue was created

    `description: Literal['asc', 'desc']`
    :   Description of the issue

    `discussion_locked: Literal['asc', 'desc']`
    :   Whether discussion is locked

    `downvotes: Literal['asc', 'desc']`
    :   Number of downvotes

    `due_date: Literal['asc', 'desc']`
    :   Due date for the issue

    `has_tasks: Literal['asc', 'desc']`
    :   Whether the issue has tasks

    `id: Literal['asc', 'desc']`
    :   ID of the issue

    `iid: Literal['asc', 'desc']`
    :   Internal ID of the issue within the project

    `issue_type: Literal['asc', 'desc']`
    :   Type classification of the issue

    `labels: Literal['asc', 'desc']`
    :   Labels assigned to the issue

    `links: Literal['asc', 'desc']`
    :   Related resource links

    `merge_requests_count: Literal['asc', 'desc']`
    :   Number of related merge requests

    `milestone: Literal['asc', 'desc']`
    :   Milestone the issue belongs to

    `milestone_id: Literal['asc', 'desc']`
    :   ID of the milestone

    `project_id: Literal['asc', 'desc']`
    :   ID of the project the issue belongs to

    `references: Literal['asc', 'desc']`
    :   Issue references

    `severity: Literal['asc', 'desc']`
    :   Severity level of the issue

    `state: Literal['asc', 'desc']`
    :   State of the issue

    `task_completion_status: Literal['asc', 'desc']`
    :   Task completion status

    `time_stats: Literal['asc', 'desc']`
    :   Time tracking statistics

    `title: Literal['asc', 'desc']`
    :   Title of the issue

    `type_: Literal['asc', 'desc']`
    :   Type of the issue

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the issue was last updated

    `upvotes: Literal['asc', 'desc']`
    :   Number of upvotes

    `user_notes_count: Literal['asc', 'desc']`
    :   Number of user notes on the issue

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the issue

    `weight: Literal['asc', 'desc']`
    :   Weight of the issue

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   Primary assignee of the issue

    `assignee_id: str`
    :   ID of the primary assignee

    `assignees: str`
    :   Users assigned to the issue

    `author: str`
    :   Author of the issue

    `author_id: str`
    :   ID of the author

    `blocking_issues_count: str`
    :   Number of blocking issues

    `closed_at: str`
    :   Timestamp when the issue was closed

    `closed_by: str`
    :   User who closed the issue

    `closed_by_id: str`
    :   ID of the user who closed the issue

    `confidential: str`
    :   Whether the issue is confidential

    `created_at: str`
    :   Timestamp when the issue was created

    `description: str`
    :   Description of the issue

    `discussion_locked: str`
    :   Whether discussion is locked

    `downvotes: str`
    :   Number of downvotes

    `due_date: str`
    :   Due date for the issue

    `has_tasks: str`
    :   Whether the issue has tasks

    `id: str`
    :   ID of the issue

    `iid: str`
    :   Internal ID of the issue within the project

    `issue_type: str`
    :   Type classification of the issue

    `labels: str`
    :   Labels assigned to the issue

    `links: str`
    :   Related resource links

    `merge_requests_count: str`
    :   Number of related merge requests

    `milestone: str`
    :   Milestone the issue belongs to

    `milestone_id: str`
    :   ID of the milestone

    `project_id: str`
    :   ID of the project the issue belongs to

    `references: str`
    :   Issue references

    `severity: str`
    :   Severity level of the issue

    `state: str`
    :   State of the issue

    `task_completion_status: str`
    :   Task completion status

    `time_stats: str`
    :   Time tracking statistics

    `title: str`
    :   Title of the issue

    `type_: str`
    :   Type of the issue

    `updated_at: str`
    :   Timestamp when the issue was last updated

    `upvotes: str`
    :   Number of upvotes

    `user_notes_count: str`
    :   Number of user notes on the issue

    `web_url: str`
    :   Web URL of the issue

    `weight: str`
    :   Weight of the issue

<a id="MergeRequestsAndCondition"></a>

`MergeRequestsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsInCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAnyCondition]`
    :   The type of the None singleton.

<a id="MergeRequestsAnyCondition"></a>

`MergeRequestsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAnyValueFilter`
    :   The type of the None singleton.

<a id="MergeRequestsAnyValueFilter"></a>

`MergeRequestsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: Any`
    :   Primary assignee of the merge request

    `assignee_id: Any`
    :   ID of the primary assignee

    `assignees: Any`
    :   Users assigned to the merge request

    `author: Any`
    :   Author of the merge request

    `author_id: Any`
    :   ID of the author

    `blocking_discussions_resolved: Any`
    :   Whether blocking discussions are resolved

    `closed_at: Any`
    :   Timestamp when the merge request was closed

    `closed_by: Any`
    :   User who closed the merge request

    `closed_by_id: Any`
    :   ID of the user who closed it

    `created_at: Any`
    :   Timestamp when the merge request was created

    `description: Any`
    :   Description of the merge request

    `detailed_merge_status: Any`
    :   Detailed merge status

    `discussion_locked: Any`
    :   Whether discussion is locked

    `downvotes: Any`
    :   Number of downvotes

    `draft: Any`
    :   Whether the merge request is a draft

    `force_remove_source_branch: Any`
    :   Whether to force remove source branch

    `has_conflicts: Any`
    :   Whether the merge request has conflicts

    `id: Any`
    :   ID of the merge request

    `iid: Any`
    :   Internal ID of the merge request within the project

    `labels: Any`
    :   Labels assigned to the merge request

    `merge_commit_sha: Any`
    :   SHA of the merge commit

    `merge_status: Any`
    :   Merge status of the merge request

    `merge_user: Any`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: Any`
    :   Whether to merge when pipeline succeeds

    `merged_at: Any`
    :   Timestamp when the merge request was merged

    `merged_by: Any`
    :   User who merged the merge request

    `merged_by_id: Any`
    :   ID of the user who merged it

    `milestone: Any`
    :   Milestone the merge request belongs to

    `milestone_id: Any`
    :   ID of the milestone

    `project_id: Any`
    :   ID of the project

    `reference: Any`
    :   Short reference for the merge request

    `references: Any`
    :   Merge request references

    `reviewers: Any`
    :   Users assigned as reviewers

    `sha: Any`
    :   SHA of the head commit

    `should_remove_source_branch: Any`
    :   Whether source branch should be removed

    `source_branch: Any`
    :   Source branch for the merge request

    `source_project_id: Any`
    :   ID of the source project

    `squash: Any`
    :   Whether to squash commits on merge

    `squash_commit_sha: Any`
    :   SHA of the squash commit

    `state: Any`
    :   State of the merge request

    `target_branch: Any`
    :   Target branch for the merge request

    `target_project_id: Any`
    :   ID of the target project

    `task_completion_status: Any`
    :   Task completion status

    `time_stats: Any`
    :   Time tracking statistics

    `title: Any`
    :   Title of the merge request

    `updated_at: Any`
    :   Timestamp when the merge request was last updated

    `upvotes: Any`
    :   Number of upvotes

    `user_notes_count: Any`
    :   Number of user notes

    `web_url: Any`
    :   Web URL of the merge request

    `work_in_progress: Any`
    :   Whether the merge request is a work in progress

<a id="MergeRequestsContainsCondition"></a>

`MergeRequestsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAnyValueFilter`
    :   The type of the None singleton.

<a id="MergeRequestsEqCondition"></a>

`MergeRequestsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSearchFilter`
    :   The type of the None singleton.

<a id="MergeRequestsFuzzyCondition"></a>

`MergeRequestsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsStringFilter`
    :   The type of the None singleton.

<a id="MergeRequestsGetParams"></a>

`MergeRequestsGetParams(*args, **kwargs)`
:   Parameters for merge_requests.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `merge_request_iid: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="MergeRequestsGtCondition"></a>

`MergeRequestsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSearchFilter`
    :   The type of the None singleton.

<a id="MergeRequestsGteCondition"></a>

`MergeRequestsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSearchFilter`
    :   The type of the None singleton.

<a id="MergeRequestsInCondition"></a>

`MergeRequestsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsInFilter`
    :   The type of the None singleton.

<a id="MergeRequestsInFilter"></a>

`MergeRequestsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: list[dict[str, typing.Any]]`
    :   Primary assignee of the merge request

    `assignee_id: list[int]`
    :   ID of the primary assignee

    `assignees: list[list[typing.Any]]`
    :   Users assigned to the merge request

    `author: list[dict[str, typing.Any]]`
    :   Author of the merge request

    `author_id: list[int]`
    :   ID of the author

    `blocking_discussions_resolved: list[bool]`
    :   Whether blocking discussions are resolved

    `closed_at: list[str]`
    :   Timestamp when the merge request was closed

    `closed_by: list[dict[str, typing.Any]]`
    :   User who closed the merge request

    `closed_by_id: list[int]`
    :   ID of the user who closed it

    `created_at: list[str]`
    :   Timestamp when the merge request was created

    `description: list[str]`
    :   Description of the merge request

    `detailed_merge_status: list[str]`
    :   Detailed merge status

    `discussion_locked: list[bool]`
    :   Whether discussion is locked

    `downvotes: list[int]`
    :   Number of downvotes

    `draft: list[bool]`
    :   Whether the merge request is a draft

    `force_remove_source_branch: list[bool]`
    :   Whether to force remove source branch

    `has_conflicts: list[bool]`
    :   Whether the merge request has conflicts

    `id: list[int]`
    :   ID of the merge request

    `iid: list[int]`
    :   Internal ID of the merge request within the project

    `labels: list[list[typing.Any]]`
    :   Labels assigned to the merge request

    `merge_commit_sha: list[str]`
    :   SHA of the merge commit

    `merge_status: list[str]`
    :   Merge status of the merge request

    `merge_user: list[dict[str, typing.Any]]`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: list[bool]`
    :   Whether to merge when pipeline succeeds

    `merged_at: list[str]`
    :   Timestamp when the merge request was merged

    `merged_by: list[dict[str, typing.Any]]`
    :   User who merged the merge request

    `merged_by_id: list[int]`
    :   ID of the user who merged it

    `milestone: list[dict[str, typing.Any]]`
    :   Milestone the merge request belongs to

    `milestone_id: list[int]`
    :   ID of the milestone

    `project_id: list[int]`
    :   ID of the project

    `reference: list[str]`
    :   Short reference for the merge request

    `references: list[dict[str, typing.Any]]`
    :   Merge request references

    `reviewers: list[list[typing.Any]]`
    :   Users assigned as reviewers

    `sha: list[str]`
    :   SHA of the head commit

    `should_remove_source_branch: list[bool]`
    :   Whether source branch should be removed

    `source_branch: list[str]`
    :   Source branch for the merge request

    `source_project_id: list[int]`
    :   ID of the source project

    `squash: list[bool]`
    :   Whether to squash commits on merge

    `squash_commit_sha: list[str]`
    :   SHA of the squash commit

    `state: list[str]`
    :   State of the merge request

    `target_branch: list[str]`
    :   Target branch for the merge request

    `target_project_id: list[int]`
    :   ID of the target project

    `task_completion_status: list[dict[str, typing.Any]]`
    :   Task completion status

    `time_stats: list[dict[str, typing.Any]]`
    :   Time tracking statistics

    `title: list[str]`
    :   Title of the merge request

    `updated_at: list[str]`
    :   Timestamp when the merge request was last updated

    `upvotes: list[int]`
    :   Number of upvotes

    `user_notes_count: list[int]`
    :   Number of user notes

    `web_url: list[str]`
    :   Web URL of the merge request

    `work_in_progress: list[bool]`
    :   Whether the merge request is a work in progress

<a id="MergeRequestsKeywordCondition"></a>

`MergeRequestsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsStringFilter`
    :   The type of the None singleton.

<a id="MergeRequestsLikeCondition"></a>

`MergeRequestsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsStringFilter`
    :   The type of the None singleton.

<a id="MergeRequestsListParams"></a>

`MergeRequestsListParams(*args, **kwargs)`
:   Parameters for merge_requests.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `scope: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `updated_after: str`
    :   The type of the None singleton.

    `updated_before: str`
    :   The type of the None singleton.

<a id="MergeRequestsLtCondition"></a>

`MergeRequestsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSearchFilter`
    :   The type of the None singleton.

<a id="MergeRequestsLteCondition"></a>

`MergeRequestsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSearchFilter`
    :   The type of the None singleton.

<a id="MergeRequestsNeqCondition"></a>

`MergeRequestsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSearchFilter`
    :   The type of the None singleton.

<a id="MergeRequestsNotCondition"></a>

`MergeRequestsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsInCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAnyCondition`
    :   The type of the None singleton.

<a id="MergeRequestsOrCondition"></a>

`MergeRequestsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsInCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAnyCondition]`
    :   The type of the None singleton.

<a id="MergeRequestsSearchFilter"></a>

`MergeRequestsSearchFilter(*args, **kwargs)`
:   Available fields for filtering merge_requests search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: dict[str, typing.Any] | None`
    :   Primary assignee of the merge request

    `assignee_id: int | None`
    :   ID of the primary assignee

    `assignees: list[typing.Any] | None`
    :   Users assigned to the merge request

    `author: dict[str, typing.Any] | None`
    :   Author of the merge request

    `author_id: int | None`
    :   ID of the author

    `blocking_discussions_resolved: bool | None`
    :   Whether blocking discussions are resolved

    `closed_at: str | None`
    :   Timestamp when the merge request was closed

    `closed_by: dict[str, typing.Any] | None`
    :   User who closed the merge request

    `closed_by_id: int | None`
    :   ID of the user who closed it

    `created_at: str | None`
    :   Timestamp when the merge request was created

    `description: str | None`
    :   Description of the merge request

    `detailed_merge_status: str | None`
    :   Detailed merge status

    `discussion_locked: bool | None`
    :   Whether discussion is locked

    `downvotes: int | None`
    :   Number of downvotes

    `draft: bool | None`
    :   Whether the merge request is a draft

    `force_remove_source_branch: bool | None`
    :   Whether to force remove source branch

    `has_conflicts: bool | None`
    :   Whether the merge request has conflicts

    `id: int | None`
    :   ID of the merge request

    `iid: int | None`
    :   Internal ID of the merge request within the project

    `labels: list[typing.Any] | None`
    :   Labels assigned to the merge request

    `merge_commit_sha: str | None`
    :   SHA of the merge commit

    `merge_status: str | None`
    :   Merge status of the merge request

    `merge_user: dict[str, typing.Any] | None`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: bool | None`
    :   Whether to merge when pipeline succeeds

    `merged_at: str | None`
    :   Timestamp when the merge request was merged

    `merged_by: dict[str, typing.Any] | None`
    :   User who merged the merge request

    `merged_by_id: int | None`
    :   ID of the user who merged it

    `milestone: dict[str, typing.Any] | None`
    :   Milestone the merge request belongs to

    `milestone_id: int | None`
    :   ID of the milestone

    `project_id: int | None`
    :   ID of the project

    `reference: str | None`
    :   Short reference for the merge request

    `references: dict[str, typing.Any] | None`
    :   Merge request references

    `reviewers: list[typing.Any] | None`
    :   Users assigned as reviewers

    `sha: str | None`
    :   SHA of the head commit

    `should_remove_source_branch: bool | None`
    :   Whether source branch should be removed

    `source_branch: str | None`
    :   Source branch for the merge request

    `source_project_id: int | None`
    :   ID of the source project

    `squash: bool | None`
    :   Whether to squash commits on merge

    `squash_commit_sha: str | None`
    :   SHA of the squash commit

    `state: str | None`
    :   State of the merge request

    `target_branch: str | None`
    :   Target branch for the merge request

    `target_project_id: int | None`
    :   ID of the target project

    `task_completion_status: dict[str, typing.Any] | None`
    :   Task completion status

    `time_stats: dict[str, typing.Any] | None`
    :   Time tracking statistics

    `title: str | None`
    :   Title of the merge request

    `updated_at: str | None`
    :   Timestamp when the merge request was last updated

    `upvotes: int | None`
    :   Number of upvotes

    `user_notes_count: int | None`
    :   Number of user notes

    `web_url: str | None`
    :   Web URL of the merge request

    `work_in_progress: bool | None`
    :   Whether the merge request is a work in progress

<a id="MergeRequestsSearchQuery"></a>

`MergeRequestsSearchQuery(*args, **kwargs)`
:   Search query for merge_requests entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsInCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.MergeRequestsSortFilter]`
    :   The type of the None singleton.

<a id="MergeRequestsSortFilter"></a>

`MergeRequestsSortFilter(*args, **kwargs)`
:   Available fields for sorting merge_requests search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: Literal['asc', 'desc']`
    :   Primary assignee of the merge request

    `assignee_id: Literal['asc', 'desc']`
    :   ID of the primary assignee

    `assignees: Literal['asc', 'desc']`
    :   Users assigned to the merge request

    `author: Literal['asc', 'desc']`
    :   Author of the merge request

    `author_id: Literal['asc', 'desc']`
    :   ID of the author

    `blocking_discussions_resolved: Literal['asc', 'desc']`
    :   Whether blocking discussions are resolved

    `closed_at: Literal['asc', 'desc']`
    :   Timestamp when the merge request was closed

    `closed_by: Literal['asc', 'desc']`
    :   User who closed the merge request

    `closed_by_id: Literal['asc', 'desc']`
    :   ID of the user who closed it

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the merge request was created

    `description: Literal['asc', 'desc']`
    :   Description of the merge request

    `detailed_merge_status: Literal['asc', 'desc']`
    :   Detailed merge status

    `discussion_locked: Literal['asc', 'desc']`
    :   Whether discussion is locked

    `downvotes: Literal['asc', 'desc']`
    :   Number of downvotes

    `draft: Literal['asc', 'desc']`
    :   Whether the merge request is a draft

    `force_remove_source_branch: Literal['asc', 'desc']`
    :   Whether to force remove source branch

    `has_conflicts: Literal['asc', 'desc']`
    :   Whether the merge request has conflicts

    `id: Literal['asc', 'desc']`
    :   ID of the merge request

    `iid: Literal['asc', 'desc']`
    :   Internal ID of the merge request within the project

    `labels: Literal['asc', 'desc']`
    :   Labels assigned to the merge request

    `merge_commit_sha: Literal['asc', 'desc']`
    :   SHA of the merge commit

    `merge_status: Literal['asc', 'desc']`
    :   Merge status of the merge request

    `merge_user: Literal['asc', 'desc']`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: Literal['asc', 'desc']`
    :   Whether to merge when pipeline succeeds

    `merged_at: Literal['asc', 'desc']`
    :   Timestamp when the merge request was merged

    `merged_by: Literal['asc', 'desc']`
    :   User who merged the merge request

    `merged_by_id: Literal['asc', 'desc']`
    :   ID of the user who merged it

    `milestone: Literal['asc', 'desc']`
    :   Milestone the merge request belongs to

    `milestone_id: Literal['asc', 'desc']`
    :   ID of the milestone

    `project_id: Literal['asc', 'desc']`
    :   ID of the project

    `reference: Literal['asc', 'desc']`
    :   Short reference for the merge request

    `references: Literal['asc', 'desc']`
    :   Merge request references

    `reviewers: Literal['asc', 'desc']`
    :   Users assigned as reviewers

    `sha: Literal['asc', 'desc']`
    :   SHA of the head commit

    `should_remove_source_branch: Literal['asc', 'desc']`
    :   Whether source branch should be removed

    `source_branch: Literal['asc', 'desc']`
    :   Source branch for the merge request

    `source_project_id: Literal['asc', 'desc']`
    :   ID of the source project

    `squash: Literal['asc', 'desc']`
    :   Whether to squash commits on merge

    `squash_commit_sha: Literal['asc', 'desc']`
    :   SHA of the squash commit

    `state: Literal['asc', 'desc']`
    :   State of the merge request

    `target_branch: Literal['asc', 'desc']`
    :   Target branch for the merge request

    `target_project_id: Literal['asc', 'desc']`
    :   ID of the target project

    `task_completion_status: Literal['asc', 'desc']`
    :   Task completion status

    `time_stats: Literal['asc', 'desc']`
    :   Time tracking statistics

    `title: Literal['asc', 'desc']`
    :   Title of the merge request

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the merge request was last updated

    `upvotes: Literal['asc', 'desc']`
    :   Number of upvotes

    `user_notes_count: Literal['asc', 'desc']`
    :   Number of user notes

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the merge request

    `work_in_progress: Literal['asc', 'desc']`
    :   Whether the merge request is a work in progress

<a id="MergeRequestsStringFilter"></a>

`MergeRequestsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: str`
    :   Primary assignee of the merge request

    `assignee_id: str`
    :   ID of the primary assignee

    `assignees: str`
    :   Users assigned to the merge request

    `author: str`
    :   Author of the merge request

    `author_id: str`
    :   ID of the author

    `blocking_discussions_resolved: str`
    :   Whether blocking discussions are resolved

    `closed_at: str`
    :   Timestamp when the merge request was closed

    `closed_by: str`
    :   User who closed the merge request

    `closed_by_id: str`
    :   ID of the user who closed it

    `created_at: str`
    :   Timestamp when the merge request was created

    `description: str`
    :   Description of the merge request

    `detailed_merge_status: str`
    :   Detailed merge status

    `discussion_locked: str`
    :   Whether discussion is locked

    `downvotes: str`
    :   Number of downvotes

    `draft: str`
    :   Whether the merge request is a draft

    `force_remove_source_branch: str`
    :   Whether to force remove source branch

    `has_conflicts: str`
    :   Whether the merge request has conflicts

    `id: str`
    :   ID of the merge request

    `iid: str`
    :   Internal ID of the merge request within the project

    `labels: str`
    :   Labels assigned to the merge request

    `merge_commit_sha: str`
    :   SHA of the merge commit

    `merge_status: str`
    :   Merge status of the merge request

    `merge_user: str`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: str`
    :   Whether to merge when pipeline succeeds

    `merged_at: str`
    :   Timestamp when the merge request was merged

    `merged_by: str`
    :   User who merged the merge request

    `merged_by_id: str`
    :   ID of the user who merged it

    `milestone: str`
    :   Milestone the merge request belongs to

    `milestone_id: str`
    :   ID of the milestone

    `project_id: str`
    :   ID of the project

    `reference: str`
    :   Short reference for the merge request

    `references: str`
    :   Merge request references

    `reviewers: str`
    :   Users assigned as reviewers

    `sha: str`
    :   SHA of the head commit

    `should_remove_source_branch: str`
    :   Whether source branch should be removed

    `source_branch: str`
    :   Source branch for the merge request

    `source_project_id: str`
    :   ID of the source project

    `squash: str`
    :   Whether to squash commits on merge

    `squash_commit_sha: str`
    :   SHA of the squash commit

    `state: str`
    :   State of the merge request

    `target_branch: str`
    :   Target branch for the merge request

    `target_project_id: str`
    :   ID of the target project

    `task_completion_status: str`
    :   Task completion status

    `time_stats: str`
    :   Time tracking statistics

    `title: str`
    :   Title of the merge request

    `updated_at: str`
    :   Timestamp when the merge request was last updated

    `upvotes: str`
    :   Number of upvotes

    `user_notes_count: str`
    :   Number of user notes

    `web_url: str`
    :   Web URL of the merge request

    `work_in_progress: str`
    :   Whether the merge request is a work in progress

<a id="PipelinesAndCondition"></a>

`PipelinesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.PipelinesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesInCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAnyCondition]`
    :   The type of the None singleton.

<a id="PipelinesAnyCondition"></a>

`PipelinesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gitlab.types.PipelinesAnyValueFilter`
    :   The type of the None singleton.

<a id="PipelinesAnyValueFilter"></a>

`PipelinesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the pipeline was created

    `id: Any`
    :   ID of the pipeline

    `iid: Any`
    :   Internal ID of the pipeline within the project

    `name: Any`
    :   Name of the pipeline

    `project_id: Any`
    :   ID of the project

    `ref: Any`
    :   Branch or tag that triggered the pipeline

    `sha: Any`
    :   SHA of the commit that triggered the pipeline

    `source: Any`
    :   Source that triggered the pipeline

    `status: Any`
    :   Status of the pipeline

    `updated_at: Any`
    :   Timestamp when the pipeline was last updated

    `web_url: Any`
    :   Web URL of the pipeline

<a id="PipelinesContainsCondition"></a>

`PipelinesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.PipelinesAnyValueFilter`
    :   The type of the None singleton.

<a id="PipelinesEqCondition"></a>

`PipelinesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.PipelinesSearchFilter`
    :   The type of the None singleton.

<a id="PipelinesFuzzyCondition"></a>

`PipelinesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.PipelinesStringFilter`
    :   The type of the None singleton.

<a id="PipelinesGetParams"></a>

`PipelinesGetParams(*args, **kwargs)`
:   Parameters for pipelines.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `pipeline_id: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="PipelinesGtCondition"></a>

`PipelinesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.PipelinesSearchFilter`
    :   The type of the None singleton.

<a id="PipelinesGteCondition"></a>

`PipelinesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.PipelinesSearchFilter`
    :   The type of the None singleton.

<a id="PipelinesInCondition"></a>

`PipelinesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gitlab.types.PipelinesInFilter`
    :   The type of the None singleton.

<a id="PipelinesInFilter"></a>

`PipelinesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the pipeline was created

    `id: list[int]`
    :   ID of the pipeline

    `iid: list[int]`
    :   Internal ID of the pipeline within the project

    `name: list[str]`
    :   Name of the pipeline

    `project_id: list[int]`
    :   ID of the project

    `ref: list[str]`
    :   Branch or tag that triggered the pipeline

    `sha: list[str]`
    :   SHA of the commit that triggered the pipeline

    `source: list[str]`
    :   Source that triggered the pipeline

    `status: list[str]`
    :   Status of the pipeline

    `updated_at: list[str]`
    :   Timestamp when the pipeline was last updated

    `web_url: list[str]`
    :   Web URL of the pipeline

<a id="PipelinesKeywordCondition"></a>

`PipelinesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.PipelinesStringFilter`
    :   The type of the None singleton.

<a id="PipelinesLikeCondition"></a>

`PipelinesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.PipelinesStringFilter`
    :   The type of the None singleton.

<a id="PipelinesListParams"></a>

`PipelinesListParams(*args, **kwargs)`
:   Parameters for pipelines.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_by: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `ref: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="PipelinesLtCondition"></a>

`PipelinesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.PipelinesSearchFilter`
    :   The type of the None singleton.

<a id="PipelinesLteCondition"></a>

`PipelinesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.PipelinesSearchFilter`
    :   The type of the None singleton.

<a id="PipelinesNeqCondition"></a>

`PipelinesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.PipelinesSearchFilter`
    :   The type of the None singleton.

<a id="PipelinesNotCondition"></a>

`PipelinesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gitlab.types.PipelinesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesInCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAnyCondition`
    :   The type of the None singleton.

<a id="PipelinesOrCondition"></a>

`PipelinesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.PipelinesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesInCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAnyCondition]`
    :   The type of the None singleton.

<a id="PipelinesSearchFilter"></a>

`PipelinesSearchFilter(*args, **kwargs)`
:   Available fields for filtering pipelines search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the pipeline was created

    `id: int | None`
    :   ID of the pipeline

    `iid: int | None`
    :   Internal ID of the pipeline within the project

    `name: str | None`
    :   Name of the pipeline

    `project_id: int | None`
    :   ID of the project

    `ref: str | None`
    :   Branch or tag that triggered the pipeline

    `sha: str | None`
    :   SHA of the commit that triggered the pipeline

    `source: str | None`
    :   Source that triggered the pipeline

    `status: str | None`
    :   Status of the pipeline

    `updated_at: str | None`
    :   Timestamp when the pipeline was last updated

    `web_url: str | None`
    :   Web URL of the pipeline

<a id="PipelinesSearchQuery"></a>

`PipelinesSearchQuery(*args, **kwargs)`
:   Search query for pipelines entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.PipelinesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesInCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.PipelinesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.PipelinesSortFilter]`
    :   The type of the None singleton.

<a id="PipelinesSortFilter"></a>

`PipelinesSortFilter(*args, **kwargs)`
:   Available fields for sorting pipelines search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the pipeline was created

    `id: Literal['asc', 'desc']`
    :   ID of the pipeline

    `iid: Literal['asc', 'desc']`
    :   Internal ID of the pipeline within the project

    `name: Literal['asc', 'desc']`
    :   Name of the pipeline

    `project_id: Literal['asc', 'desc']`
    :   ID of the project

    `ref: Literal['asc', 'desc']`
    :   Branch or tag that triggered the pipeline

    `sha: Literal['asc', 'desc']`
    :   SHA of the commit that triggered the pipeline

    `source: Literal['asc', 'desc']`
    :   Source that triggered the pipeline

    `status: Literal['asc', 'desc']`
    :   Status of the pipeline

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the pipeline was last updated

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the pipeline

<a id="PipelinesStringFilter"></a>

`PipelinesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the pipeline was created

    `id: str`
    :   ID of the pipeline

    `iid: str`
    :   Internal ID of the pipeline within the project

    `name: str`
    :   Name of the pipeline

    `project_id: str`
    :   ID of the project

    `ref: str`
    :   Branch or tag that triggered the pipeline

    `sha: str`
    :   SHA of the commit that triggered the pipeline

    `source: str`
    :   Source that triggered the pipeline

    `status: str`
    :   Status of the pipeline

    `updated_at: str`
    :   Timestamp when the pipeline was last updated

    `web_url: str`
    :   Web URL of the pipeline

<a id="ProjectMembersAndCondition"></a>

`ProjectMembersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectMembersAnyCondition"></a>

`ProjectMembersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectMembersAnyValueFilter"></a>

`ProjectMembersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: Any`
    :   Access level of the member

    `avatar_url: Any`
    :   URL of the member avatar

    `created_at: Any`
    :   Timestamp when the member was added

    `created_by: Any`
    :   User who added the member

    `expires_at: Any`
    :   Expiration date of the membership

    `id: Any`
    :   ID of the member

    `locked: Any`
    :   Whether the member account is locked

    `membership_state: Any`
    :   State of the membership

    `name: Any`
    :   Full name of the member

    `project_id: Any`
    :   ID of the project

    `state: Any`
    :   State of the member account

    `username: Any`
    :   Username of the member

    `web_url: Any`
    :   Web URL of the member profile

<a id="ProjectMembersContainsCondition"></a>

`ProjectMembersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectMembersEqCondition"></a>

`ProjectMembersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMembersFuzzyCondition"></a>

`ProjectMembersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersStringFilter`
    :   The type of the None singleton.

<a id="ProjectMembersGetParams"></a>

`ProjectMembersGetParams(*args, **kwargs)`
:   Parameters for project_members.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `project_id: str`
    :   The type of the None singleton.

    `user_id: str`
    :   The type of the None singleton.

<a id="ProjectMembersGtCondition"></a>

`ProjectMembersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMembersGteCondition"></a>

`ProjectMembersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMembersInCondition"></a>

`ProjectMembersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersInFilter`
    :   The type of the None singleton.

<a id="ProjectMembersInFilter"></a>

`ProjectMembersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: list[int]`
    :   Access level of the member

    `avatar_url: list[str]`
    :   URL of the member avatar

    `created_at: list[str]`
    :   Timestamp when the member was added

    `created_by: list[dict[str, typing.Any]]`
    :   User who added the member

    `expires_at: list[str]`
    :   Expiration date of the membership

    `id: list[int]`
    :   ID of the member

    `locked: list[bool]`
    :   Whether the member account is locked

    `membership_state: list[str]`
    :   State of the membership

    `name: list[str]`
    :   Full name of the member

    `project_id: list[int]`
    :   ID of the project

    `state: list[str]`
    :   State of the member account

    `username: list[str]`
    :   Username of the member

    `web_url: list[str]`
    :   Web URL of the member profile

<a id="ProjectMembersKeywordCondition"></a>

`ProjectMembersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersStringFilter`
    :   The type of the None singleton.

<a id="ProjectMembersLikeCondition"></a>

`ProjectMembersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersStringFilter`
    :   The type of the None singleton.

<a id="ProjectMembersListParams"></a>

`ProjectMembersListParams(*args, **kwargs)`
:   Parameters for project_members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="ProjectMembersLtCondition"></a>

`ProjectMembersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMembersLteCondition"></a>

`ProjectMembersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMembersNeqCondition"></a>

`ProjectMembersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMembersNotCondition"></a>

`ProjectMembersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAnyCondition`
    :   The type of the None singleton.

<a id="ProjectMembersOrCondition"></a>

`ProjectMembersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectMembersSearchFilter"></a>

`ProjectMembersSearchFilter(*args, **kwargs)`
:   Available fields for filtering project_members search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: int | None`
    :   Access level of the member

    `avatar_url: str | None`
    :   URL of the member avatar

    `created_at: str | None`
    :   Timestamp when the member was added

    `created_by: dict[str, typing.Any] | None`
    :   User who added the member

    `expires_at: str | None`
    :   Expiration date of the membership

    `id: int | None`
    :   ID of the member

    `locked: bool | None`
    :   Whether the member account is locked

    `membership_state: str | None`
    :   State of the membership

    `name: str | None`
    :   Full name of the member

    `project_id: int | None`
    :   ID of the project

    `state: str | None`
    :   State of the member account

    `username: str | None`
    :   Username of the member

    `web_url: str | None`
    :   Web URL of the member profile

<a id="ProjectMembersSearchQuery"></a>

`ProjectMembersSearchQuery(*args, **kwargs)`
:   Search query for project_members entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectMembersSortFilter]`
    :   The type of the None singleton.

<a id="ProjectMembersSortFilter"></a>

`ProjectMembersSortFilter(*args, **kwargs)`
:   Available fields for sorting project_members search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: Literal['asc', 'desc']`
    :   Access level of the member

    `avatar_url: Literal['asc', 'desc']`
    :   URL of the member avatar

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the member was added

    `created_by: Literal['asc', 'desc']`
    :   User who added the member

    `expires_at: Literal['asc', 'desc']`
    :   Expiration date of the membership

    `id: Literal['asc', 'desc']`
    :   ID of the member

    `locked: Literal['asc', 'desc']`
    :   Whether the member account is locked

    `membership_state: Literal['asc', 'desc']`
    :   State of the membership

    `name: Literal['asc', 'desc']`
    :   Full name of the member

    `project_id: Literal['asc', 'desc']`
    :   ID of the project

    `state: Literal['asc', 'desc']`
    :   State of the member account

    `username: Literal['asc', 'desc']`
    :   Username of the member

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the member profile

<a id="ProjectMembersStringFilter"></a>

`ProjectMembersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access_level: str`
    :   Access level of the member

    `avatar_url: str`
    :   URL of the member avatar

    `created_at: str`
    :   Timestamp when the member was added

    `created_by: str`
    :   User who added the member

    `expires_at: str`
    :   Expiration date of the membership

    `id: str`
    :   ID of the member

    `locked: str`
    :   Whether the member account is locked

    `membership_state: str`
    :   State of the membership

    `name: str`
    :   Full name of the member

    `project_id: str`
    :   ID of the project

    `state: str`
    :   State of the member account

    `username: str`
    :   Username of the member

    `web_url: str`
    :   Web URL of the member profile

<a id="ProjectMilestonesAndCondition"></a>

`ProjectMilestonesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectMilestonesAnyCondition"></a>

`ProjectMilestonesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesAnyValueFilter"></a>

`ProjectMilestonesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the milestone was created

    `description: Any`
    :   Description of the milestone

    `due_date: Any`
    :   Due date of the milestone

    `expired: Any`
    :   Whether the milestone is expired

    `id: Any`
    :   ID of the milestone

    `iid: Any`
    :   Internal ID of the milestone within the project

    `project_id: Any`
    :   ID of the project

    `start_date: Any`
    :   Start date of the milestone

    `state: Any`
    :   State of the milestone

    `title: Any`
    :   Title of the milestone

    `updated_at: Any`
    :   Timestamp when the milestone was last updated

    `web_url: Any`
    :   Web URL of the milestone

<a id="ProjectMilestonesContainsCondition"></a>

`ProjectMilestonesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesEqCondition"></a>

`ProjectMilestonesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesFuzzyCondition"></a>

`ProjectMilestonesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesStringFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesGetParams"></a>

`ProjectMilestonesGetParams(*args, **kwargs)`
:   Parameters for project_milestones.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `milestone_id: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="ProjectMilestonesGtCondition"></a>

`ProjectMilestonesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesGteCondition"></a>

`ProjectMilestonesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesInCondition"></a>

`ProjectMilestonesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesInFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesInFilter"></a>

`ProjectMilestonesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the milestone was created

    `description: list[str]`
    :   Description of the milestone

    `due_date: list[str]`
    :   Due date of the milestone

    `expired: list[bool]`
    :   Whether the milestone is expired

    `id: list[int]`
    :   ID of the milestone

    `iid: list[int]`
    :   Internal ID of the milestone within the project

    `project_id: list[int]`
    :   ID of the project

    `start_date: list[str]`
    :   Start date of the milestone

    `state: list[str]`
    :   State of the milestone

    `title: list[str]`
    :   Title of the milestone

    `updated_at: list[str]`
    :   Timestamp when the milestone was last updated

    `web_url: list[str]`
    :   Web URL of the milestone

<a id="ProjectMilestonesKeywordCondition"></a>

`ProjectMilestonesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesStringFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesLikeCondition"></a>

`ProjectMilestonesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesStringFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesListParams"></a>

`ProjectMilestonesListParams(*args, **kwargs)`
:   Parameters for project_milestones.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

<a id="ProjectMilestonesLtCondition"></a>

`ProjectMilestonesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesLteCondition"></a>

`ProjectMilestonesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesNeqCondition"></a>

`ProjectMilestonesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSearchFilter`
    :   The type of the None singleton.

<a id="ProjectMilestonesNotCondition"></a>

`ProjectMilestonesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAnyCondition`
    :   The type of the None singleton.

<a id="ProjectMilestonesOrCondition"></a>

`ProjectMilestonesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectMilestonesSearchFilter"></a>

`ProjectMilestonesSearchFilter(*args, **kwargs)`
:   Available fields for filtering project_milestones search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the milestone was created

    `description: str | None`
    :   Description of the milestone

    `due_date: str | None`
    :   Due date of the milestone

    `expired: bool | None`
    :   Whether the milestone is expired

    `id: int | None`
    :   ID of the milestone

    `iid: int | None`
    :   Internal ID of the milestone within the project

    `project_id: int | None`
    :   ID of the project

    `start_date: str | None`
    :   Start date of the milestone

    `state: str | None`
    :   State of the milestone

    `title: str | None`
    :   Title of the milestone

    `updated_at: str | None`
    :   Timestamp when the milestone was last updated

    `web_url: str | None`
    :   Web URL of the milestone

<a id="ProjectMilestonesSearchQuery"></a>

`ProjectMilestonesSearchQuery(*args, **kwargs)`
:   Search query for project_milestones entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectMilestonesSortFilter]`
    :   The type of the None singleton.

<a id="ProjectMilestonesSortFilter"></a>

`ProjectMilestonesSortFilter(*args, **kwargs)`
:   Available fields for sorting project_milestones search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the milestone was created

    `description: Literal['asc', 'desc']`
    :   Description of the milestone

    `due_date: Literal['asc', 'desc']`
    :   Due date of the milestone

    `expired: Literal['asc', 'desc']`
    :   Whether the milestone is expired

    `id: Literal['asc', 'desc']`
    :   ID of the milestone

    `iid: Literal['asc', 'desc']`
    :   Internal ID of the milestone within the project

    `project_id: Literal['asc', 'desc']`
    :   ID of the project

    `start_date: Literal['asc', 'desc']`
    :   Start date of the milestone

    `state: Literal['asc', 'desc']`
    :   State of the milestone

    `title: Literal['asc', 'desc']`
    :   Title of the milestone

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the milestone was last updated

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the milestone

<a id="ProjectMilestonesStringFilter"></a>

`ProjectMilestonesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the milestone was created

    `description: str`
    :   Description of the milestone

    `due_date: str`
    :   Due date of the milestone

    `expired: str`
    :   Whether the milestone is expired

    `id: str`
    :   ID of the milestone

    `iid: str`
    :   Internal ID of the milestone within the project

    `project_id: str`
    :   ID of the project

    `start_date: str`
    :   Start date of the milestone

    `state: str`
    :   State of the milestone

    `title: str`
    :   Title of the milestone

    `updated_at: str`
    :   Timestamp when the milestone was last updated

    `web_url: str`
    :   Web URL of the milestone

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsAnyValueFilter"></a>

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_merge_on_skipped_pipeline: Any`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: Any`
    :   Access level for analytics

    `archived: Any`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: Any`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: Any`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: Any`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: Any`
    :   Whether referenced issues are auto-closed

    `avatar_url: Any`
    :   URL of the project avatar

    `build_timeout: Any`
    :   Build timeout in seconds

    `builds_access_level: Any`
    :   Access level for builds

    `can_create_merge_request_in: Any`
    :   Whether user can create merge requests

    `ci_config_path: Any`
    :   Path to the CI configuration file

    `ci_default_git_depth: Any`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: Any`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: Any`
    :   Compliance frameworks for the project

    `container_expiration_policy: Any`
    :   Container expiration policy settings

    `container_registry_enabled: Any`
    :   Whether container registry is enabled

    `container_registry_image_prefix: Any`
    :   Prefix for container registry images

    `created_at: Any`
    :   Timestamp when the project was created

    `creator_id: Any`
    :   ID of the project creator

    `default_branch: Any`
    :   Default branch of the project

    `description: Any`
    :   Description of the project

    `description_html: Any`
    :   HTML-rendered description of the project

    `emails_disabled: Any`
    :   Whether emails are disabled

    `empty_repo: Any`
    :   Whether the repository is empty

    `external_authorization_classification_label: Any`
    :   External authorization classification label

    `forking_access_level: Any`
    :   Access level for forking

    `forks_count: Any`
    :   Number of forks

    `http_url_to_repo: Any`
    :   HTTP URL to the repository

    `id: Any`
    :   ID of the project

    `import_status: Any`
    :   Import status of the project

    `issues_access_level: Any`
    :   Access level for issues

    `issues_enabled: Any`
    :   Whether issues are enabled

    `jobs_enabled: Any`
    :   Whether jobs are enabled

    `keep_latest_artifact: Any`
    :   Whether the latest artifact is kept

    `last_activity_at: Any`
    :   Timestamp of last activity

    `lfs_enabled: Any`
    :   Whether Git LFS is enabled

    `links: Any`
    :   Related resource links

    `merge_method: Any`
    :   Merge method used for the project

    `merge_requests_access_level: Any`
    :   Access level for merge requests

    `merge_requests_enabled: Any`
    :   Whether merge requests are enabled

    `name: Any`
    :   Name of the project

    `name_with_namespace: Any`
    :   Full name including namespace

    `namespace: Any`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: Any`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: Any`
    :   Whether merge requires pipeline success

    `open_issues_count: Any`
    :   Number of open issues

    `operations_access_level: Any`
    :   Access level for operations

    `packages_enabled: Any`
    :   Whether packages are enabled

    `pages_access_level: Any`
    :   Access level for pages

    `path: Any`
    :   URL path of the project

    `path_with_namespace: Any`
    :   Full path including namespace

    `permissions: Any`
    :   User permissions for the project

    `printing_merge_request_link_enabled: Any`
    :   Whether MR link printing is enabled

    `public_jobs: Any`
    :   Whether jobs are public

    `readme_url: Any`
    :   URL to the project README

    `remove_source_branch_after_merge: Any`
    :   Whether source branch is removed after merge

    `repository_access_level: Any`
    :   Access level for the repository

    `request_access_enabled: Any`
    :   Whether access requests are enabled

    `requirements_enabled: Any`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: Any`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: Any`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: Any`
    :   Whether security and compliance is enabled

    `service_desk_address: Any`
    :   Email address for the service desk

    `service_desk_enabled: Any`
    :   Whether service desk is enabled

    `shared_runners_enabled: Any`
    :   Whether shared runners are enabled

    `shared_with_groups: Any`
    :   Groups the project is shared with

    `snippets_access_level: Any`
    :   Access level for snippets

    `snippets_enabled: Any`
    :   Whether snippets are enabled

    `ssh_url_to_repo: Any`
    :   SSH URL to the repository

    `star_count: Any`
    :   Number of stars

    `statistics: Any`
    :   Project statistics

    `tag_list: Any`
    :   List of tags for the project

    `topics: Any`
    :   List of topics for the project

    `updated_at: Any`
    :   Timestamp when the project was last updated

    `visibility: Any`
    :   Visibility level of the project

    `web_url: Any`
    :   Web URL of the project

    `wiki_access_level: Any`
    :   Access level for the wiki

    `wiki_enabled: Any`
    :   Whether wiki is enabled

<a id="ProjectsContainsCondition"></a>

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsEqCondition"></a>

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsFuzzyCondition"></a>

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsGetParams"></a>

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `statistics: bool`
    :   The type of the None singleton.

<a id="ProjectsGtCondition"></a>

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsGteCondition"></a>

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.ProjectsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.ProjectsInFilter`
    :   The type of the None singleton.

<a id="ProjectsInFilter"></a>

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_merge_on_skipped_pipeline: list[bool]`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: list[str]`
    :   Access level for analytics

    `archived: list[bool]`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: list[str]`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: list[str]`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: list[bool]`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: list[bool]`
    :   Whether referenced issues are auto-closed

    `avatar_url: list[str]`
    :   URL of the project avatar

    `build_timeout: list[int]`
    :   Build timeout in seconds

    `builds_access_level: list[str]`
    :   Access level for builds

    `can_create_merge_request_in: list[bool]`
    :   Whether user can create merge requests

    `ci_config_path: list[str]`
    :   Path to the CI configuration file

    `ci_default_git_depth: list[int]`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: list[bool]`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: list[list[typing.Any]]`
    :   Compliance frameworks for the project

    `container_expiration_policy: list[dict[str, typing.Any]]`
    :   Container expiration policy settings

    `container_registry_enabled: list[bool]`
    :   Whether container registry is enabled

    `container_registry_image_prefix: list[str]`
    :   Prefix for container registry images

    `created_at: list[str]`
    :   Timestamp when the project was created

    `creator_id: list[int]`
    :   ID of the project creator

    `default_branch: list[str]`
    :   Default branch of the project

    `description: list[str]`
    :   Description of the project

    `description_html: list[str]`
    :   HTML-rendered description of the project

    `emails_disabled: list[bool]`
    :   Whether emails are disabled

    `empty_repo: list[bool]`
    :   Whether the repository is empty

    `external_authorization_classification_label: list[str]`
    :   External authorization classification label

    `forking_access_level: list[str]`
    :   Access level for forking

    `forks_count: list[int]`
    :   Number of forks

    `http_url_to_repo: list[str]`
    :   HTTP URL to the repository

    `id: list[int]`
    :   ID of the project

    `import_status: list[str]`
    :   Import status of the project

    `issues_access_level: list[str]`
    :   Access level for issues

    `issues_enabled: list[bool]`
    :   Whether issues are enabled

    `jobs_enabled: list[bool]`
    :   Whether jobs are enabled

    `keep_latest_artifact: list[bool]`
    :   Whether the latest artifact is kept

    `last_activity_at: list[str]`
    :   Timestamp of last activity

    `lfs_enabled: list[bool]`
    :   Whether Git LFS is enabled

    `links: list[dict[str, typing.Any]]`
    :   Related resource links

    `merge_method: list[str]`
    :   Merge method used for the project

    `merge_requests_access_level: list[str]`
    :   Access level for merge requests

    `merge_requests_enabled: list[bool]`
    :   Whether merge requests are enabled

    `name: list[str]`
    :   Name of the project

    `name_with_namespace: list[str]`
    :   Full name including namespace

    `namespace: list[dict[str, typing.Any]]`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: list[bool]`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: list[bool]`
    :   Whether merge requires pipeline success

    `open_issues_count: list[int]`
    :   Number of open issues

    `operations_access_level: list[str]`
    :   Access level for operations

    `packages_enabled: list[bool]`
    :   Whether packages are enabled

    `pages_access_level: list[str]`
    :   Access level for pages

    `path: list[str]`
    :   URL path of the project

    `path_with_namespace: list[str]`
    :   Full path including namespace

    `permissions: list[dict[str, typing.Any]]`
    :   User permissions for the project

    `printing_merge_request_link_enabled: list[bool]`
    :   Whether MR link printing is enabled

    `public_jobs: list[bool]`
    :   Whether jobs are public

    `readme_url: list[str]`
    :   URL to the project README

    `remove_source_branch_after_merge: list[bool]`
    :   Whether source branch is removed after merge

    `repository_access_level: list[str]`
    :   Access level for the repository

    `request_access_enabled: list[bool]`
    :   Whether access requests are enabled

    `requirements_enabled: list[bool]`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: list[bool]`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: list[bool]`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: list[bool]`
    :   Whether security and compliance is enabled

    `service_desk_address: list[str]`
    :   Email address for the service desk

    `service_desk_enabled: list[bool]`
    :   Whether service desk is enabled

    `shared_runners_enabled: list[bool]`
    :   Whether shared runners are enabled

    `shared_with_groups: list[list[typing.Any]]`
    :   Groups the project is shared with

    `snippets_access_level: list[str]`
    :   Access level for snippets

    `snippets_enabled: list[bool]`
    :   Whether snippets are enabled

    `ssh_url_to_repo: list[str]`
    :   SSH URL to the repository

    `star_count: list[int]`
    :   Number of stars

    `statistics: list[dict[str, typing.Any]]`
    :   Project statistics

    `tag_list: list[list[typing.Any]]`
    :   List of tags for the project

    `topics: list[list[typing.Any]]`
    :   List of topics for the project

    `updated_at: list[str]`
    :   Timestamp when the project was last updated

    `visibility: list[str]`
    :   Visibility level of the project

    `web_url: list[str]`
    :   Web URL of the project

    `wiki_access_level: list[str]`
    :   Access level for the wiki

    `wiki_enabled: list[bool]`
    :   Whether wiki is enabled

<a id="ProjectsKeywordCondition"></a>

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsLikeCondition"></a>

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsListParams"></a>

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `membership: bool`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `owned: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="ProjectsLtCondition"></a>

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsLteCondition"></a>

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNeqCondition"></a>

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.ProjectsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsSearchFilter"></a>

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_merge_on_skipped_pipeline: bool | None`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: str | None`
    :   Access level for analytics

    `archived: bool | None`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: str | None`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: str | None`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: bool | None`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: bool | None`
    :   Whether referenced issues are auto-closed

    `avatar_url: str | None`
    :   URL of the project avatar

    `build_timeout: int | None`
    :   Build timeout in seconds

    `builds_access_level: str | None`
    :   Access level for builds

    `can_create_merge_request_in: bool | None`
    :   Whether user can create merge requests

    `ci_config_path: str | None`
    :   Path to the CI configuration file

    `ci_default_git_depth: int | None`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: bool | None`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: list[typing.Any] | None`
    :   Compliance frameworks for the project

    `container_expiration_policy: dict[str, typing.Any] | None`
    :   Container expiration policy settings

    `container_registry_enabled: bool | None`
    :   Whether container registry is enabled

    `container_registry_image_prefix: str | None`
    :   Prefix for container registry images

    `created_at: str | None`
    :   Timestamp when the project was created

    `creator_id: int | None`
    :   ID of the project creator

    `default_branch: str | None`
    :   Default branch of the project

    `description: str | None`
    :   Description of the project

    `description_html: str | None`
    :   HTML-rendered description of the project

    `emails_disabled: bool | None`
    :   Whether emails are disabled

    `empty_repo: bool | None`
    :   Whether the repository is empty

    `external_authorization_classification_label: str | None`
    :   External authorization classification label

    `forking_access_level: str | None`
    :   Access level for forking

    `forks_count: int | None`
    :   Number of forks

    `http_url_to_repo: str | None`
    :   HTTP URL to the repository

    `id: int | None`
    :   ID of the project

    `import_status: str | None`
    :   Import status of the project

    `issues_access_level: str | None`
    :   Access level for issues

    `issues_enabled: bool | None`
    :   Whether issues are enabled

    `jobs_enabled: bool | None`
    :   Whether jobs are enabled

    `keep_latest_artifact: bool | None`
    :   Whether the latest artifact is kept

    `last_activity_at: str | None`
    :   Timestamp of last activity

    `lfs_enabled: bool | None`
    :   Whether Git LFS is enabled

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `merge_method: str | None`
    :   Merge method used for the project

    `merge_requests_access_level: str | None`
    :   Access level for merge requests

    `merge_requests_enabled: bool | None`
    :   Whether merge requests are enabled

    `name: str | None`
    :   Name of the project

    `name_with_namespace: str | None`
    :   Full name including namespace

    `namespace: dict[str, typing.Any] | None`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: bool | None`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: bool | None`
    :   Whether merge requires pipeline success

    `open_issues_count: int | None`
    :   Number of open issues

    `operations_access_level: str | None`
    :   Access level for operations

    `packages_enabled: bool | None`
    :   Whether packages are enabled

    `pages_access_level: str | None`
    :   Access level for pages

    `path: str | None`
    :   URL path of the project

    `path_with_namespace: str | None`
    :   Full path including namespace

    `permissions: dict[str, typing.Any] | None`
    :   User permissions for the project

    `printing_merge_request_link_enabled: bool | None`
    :   Whether MR link printing is enabled

    `public_jobs: bool | None`
    :   Whether jobs are public

    `readme_url: str | None`
    :   URL to the project README

    `remove_source_branch_after_merge: bool | None`
    :   Whether source branch is removed after merge

    `repository_access_level: str | None`
    :   Access level for the repository

    `request_access_enabled: bool | None`
    :   Whether access requests are enabled

    `requirements_enabled: bool | None`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: bool | None`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: bool | None`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: bool | None`
    :   Whether security and compliance is enabled

    `service_desk_address: str | None`
    :   Email address for the service desk

    `service_desk_enabled: bool | None`
    :   Whether service desk is enabled

    `shared_runners_enabled: bool | None`
    :   Whether shared runners are enabled

    `shared_with_groups: list[typing.Any] | None`
    :   Groups the project is shared with

    `snippets_access_level: str | None`
    :   Access level for snippets

    `snippets_enabled: bool | None`
    :   Whether snippets are enabled

    `ssh_url_to_repo: str | None`
    :   SSH URL to the repository

    `star_count: int | None`
    :   Number of stars

    `statistics: dict[str, typing.Any] | None`
    :   Project statistics

    `tag_list: list[typing.Any] | None`
    :   List of tags for the project

    `topics: list[typing.Any] | None`
    :   List of topics for the project

    `updated_at: str | None`
    :   Timestamp when the project was last updated

    `visibility: str | None`
    :   Visibility level of the project

    `web_url: str | None`
    :   Web URL of the project

    `wiki_access_level: str | None`
    :   Access level for the wiki

    `wiki_enabled: bool | None`
    :   Whether wiki is enabled

<a id="ProjectsSearchQuery"></a>

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsInCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.ProjectsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectsSortFilter"></a>

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_merge_on_skipped_pipeline: Literal['asc', 'desc']`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: Literal['asc', 'desc']`
    :   Access level for analytics

    `archived: Literal['asc', 'desc']`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: Literal['asc', 'desc']`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: Literal['asc', 'desc']`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: Literal['asc', 'desc']`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: Literal['asc', 'desc']`
    :   Whether referenced issues are auto-closed

    `avatar_url: Literal['asc', 'desc']`
    :   URL of the project avatar

    `build_timeout: Literal['asc', 'desc']`
    :   Build timeout in seconds

    `builds_access_level: Literal['asc', 'desc']`
    :   Access level for builds

    `can_create_merge_request_in: Literal['asc', 'desc']`
    :   Whether user can create merge requests

    `ci_config_path: Literal['asc', 'desc']`
    :   Path to the CI configuration file

    `ci_default_git_depth: Literal['asc', 'desc']`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: Literal['asc', 'desc']`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: Literal['asc', 'desc']`
    :   Compliance frameworks for the project

    `container_expiration_policy: Literal['asc', 'desc']`
    :   Container expiration policy settings

    `container_registry_enabled: Literal['asc', 'desc']`
    :   Whether container registry is enabled

    `container_registry_image_prefix: Literal['asc', 'desc']`
    :   Prefix for container registry images

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the project was created

    `creator_id: Literal['asc', 'desc']`
    :   ID of the project creator

    `default_branch: Literal['asc', 'desc']`
    :   Default branch of the project

    `description: Literal['asc', 'desc']`
    :   Description of the project

    `description_html: Literal['asc', 'desc']`
    :   HTML-rendered description of the project

    `emails_disabled: Literal['asc', 'desc']`
    :   Whether emails are disabled

    `empty_repo: Literal['asc', 'desc']`
    :   Whether the repository is empty

    `external_authorization_classification_label: Literal['asc', 'desc']`
    :   External authorization classification label

    `forking_access_level: Literal['asc', 'desc']`
    :   Access level for forking

    `forks_count: Literal['asc', 'desc']`
    :   Number of forks

    `http_url_to_repo: Literal['asc', 'desc']`
    :   HTTP URL to the repository

    `id: Literal['asc', 'desc']`
    :   ID of the project

    `import_status: Literal['asc', 'desc']`
    :   Import status of the project

    `issues_access_level: Literal['asc', 'desc']`
    :   Access level for issues

    `issues_enabled: Literal['asc', 'desc']`
    :   Whether issues are enabled

    `jobs_enabled: Literal['asc', 'desc']`
    :   Whether jobs are enabled

    `keep_latest_artifact: Literal['asc', 'desc']`
    :   Whether the latest artifact is kept

    `last_activity_at: Literal['asc', 'desc']`
    :   Timestamp of last activity

    `lfs_enabled: Literal['asc', 'desc']`
    :   Whether Git LFS is enabled

    `links: Literal['asc', 'desc']`
    :   Related resource links

    `merge_method: Literal['asc', 'desc']`
    :   Merge method used for the project

    `merge_requests_access_level: Literal['asc', 'desc']`
    :   Access level for merge requests

    `merge_requests_enabled: Literal['asc', 'desc']`
    :   Whether merge requests are enabled

    `name: Literal['asc', 'desc']`
    :   Name of the project

    `name_with_namespace: Literal['asc', 'desc']`
    :   Full name including namespace

    `namespace: Literal['asc', 'desc']`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: Literal['asc', 'desc']`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: Literal['asc', 'desc']`
    :   Whether merge requires pipeline success

    `open_issues_count: Literal['asc', 'desc']`
    :   Number of open issues

    `operations_access_level: Literal['asc', 'desc']`
    :   Access level for operations

    `packages_enabled: Literal['asc', 'desc']`
    :   Whether packages are enabled

    `pages_access_level: Literal['asc', 'desc']`
    :   Access level for pages

    `path: Literal['asc', 'desc']`
    :   URL path of the project

    `path_with_namespace: Literal['asc', 'desc']`
    :   Full path including namespace

    `permissions: Literal['asc', 'desc']`
    :   User permissions for the project

    `printing_merge_request_link_enabled: Literal['asc', 'desc']`
    :   Whether MR link printing is enabled

    `public_jobs: Literal['asc', 'desc']`
    :   Whether jobs are public

    `readme_url: Literal['asc', 'desc']`
    :   URL to the project README

    `remove_source_branch_after_merge: Literal['asc', 'desc']`
    :   Whether source branch is removed after merge

    `repository_access_level: Literal['asc', 'desc']`
    :   Access level for the repository

    `request_access_enabled: Literal['asc', 'desc']`
    :   Whether access requests are enabled

    `requirements_enabled: Literal['asc', 'desc']`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: Literal['asc', 'desc']`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: Literal['asc', 'desc']`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: Literal['asc', 'desc']`
    :   Whether security and compliance is enabled

    `service_desk_address: Literal['asc', 'desc']`
    :   Email address for the service desk

    `service_desk_enabled: Literal['asc', 'desc']`
    :   Whether service desk is enabled

    `shared_runners_enabled: Literal['asc', 'desc']`
    :   Whether shared runners are enabled

    `shared_with_groups: Literal['asc', 'desc']`
    :   Groups the project is shared with

    `snippets_access_level: Literal['asc', 'desc']`
    :   Access level for snippets

    `snippets_enabled: Literal['asc', 'desc']`
    :   Whether snippets are enabled

    `ssh_url_to_repo: Literal['asc', 'desc']`
    :   SSH URL to the repository

    `star_count: Literal['asc', 'desc']`
    :   Number of stars

    `statistics: Literal['asc', 'desc']`
    :   Project statistics

    `tag_list: Literal['asc', 'desc']`
    :   List of tags for the project

    `topics: Literal['asc', 'desc']`
    :   List of topics for the project

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the project was last updated

    `visibility: Literal['asc', 'desc']`
    :   Visibility level of the project

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the project

    `wiki_access_level: Literal['asc', 'desc']`
    :   Access level for the wiki

    `wiki_enabled: Literal['asc', 'desc']`
    :   Whether wiki is enabled

<a id="ProjectsStringFilter"></a>

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_merge_on_skipped_pipeline: str`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: str`
    :   Access level for analytics

    `archived: str`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: str`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: str`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: str`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: str`
    :   Whether referenced issues are auto-closed

    `avatar_url: str`
    :   URL of the project avatar

    `build_timeout: str`
    :   Build timeout in seconds

    `builds_access_level: str`
    :   Access level for builds

    `can_create_merge_request_in: str`
    :   Whether user can create merge requests

    `ci_config_path: str`
    :   Path to the CI configuration file

    `ci_default_git_depth: str`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: str`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: str`
    :   Compliance frameworks for the project

    `container_expiration_policy: str`
    :   Container expiration policy settings

    `container_registry_enabled: str`
    :   Whether container registry is enabled

    `container_registry_image_prefix: str`
    :   Prefix for container registry images

    `created_at: str`
    :   Timestamp when the project was created

    `creator_id: str`
    :   ID of the project creator

    `default_branch: str`
    :   Default branch of the project

    `description: str`
    :   Description of the project

    `description_html: str`
    :   HTML-rendered description of the project

    `emails_disabled: str`
    :   Whether emails are disabled

    `empty_repo: str`
    :   Whether the repository is empty

    `external_authorization_classification_label: str`
    :   External authorization classification label

    `forking_access_level: str`
    :   Access level for forking

    `forks_count: str`
    :   Number of forks

    `http_url_to_repo: str`
    :   HTTP URL to the repository

    `id: str`
    :   ID of the project

    `import_status: str`
    :   Import status of the project

    `issues_access_level: str`
    :   Access level for issues

    `issues_enabled: str`
    :   Whether issues are enabled

    `jobs_enabled: str`
    :   Whether jobs are enabled

    `keep_latest_artifact: str`
    :   Whether the latest artifact is kept

    `last_activity_at: str`
    :   Timestamp of last activity

    `lfs_enabled: str`
    :   Whether Git LFS is enabled

    `links: str`
    :   Related resource links

    `merge_method: str`
    :   Merge method used for the project

    `merge_requests_access_level: str`
    :   Access level for merge requests

    `merge_requests_enabled: str`
    :   Whether merge requests are enabled

    `name: str`
    :   Name of the project

    `name_with_namespace: str`
    :   Full name including namespace

    `namespace: str`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: str`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: str`
    :   Whether merge requires pipeline success

    `open_issues_count: str`
    :   Number of open issues

    `operations_access_level: str`
    :   Access level for operations

    `packages_enabled: str`
    :   Whether packages are enabled

    `pages_access_level: str`
    :   Access level for pages

    `path: str`
    :   URL path of the project

    `path_with_namespace: str`
    :   Full path including namespace

    `permissions: str`
    :   User permissions for the project

    `printing_merge_request_link_enabled: str`
    :   Whether MR link printing is enabled

    `public_jobs: str`
    :   Whether jobs are public

    `readme_url: str`
    :   URL to the project README

    `remove_source_branch_after_merge: str`
    :   Whether source branch is removed after merge

    `repository_access_level: str`
    :   Access level for the repository

    `request_access_enabled: str`
    :   Whether access requests are enabled

    `requirements_enabled: str`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: str`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: str`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: str`
    :   Whether security and compliance is enabled

    `service_desk_address: str`
    :   Email address for the service desk

    `service_desk_enabled: str`
    :   Whether service desk is enabled

    `shared_runners_enabled: str`
    :   Whether shared runners are enabled

    `shared_with_groups: str`
    :   Groups the project is shared with

    `snippets_access_level: str`
    :   Access level for snippets

    `snippets_enabled: str`
    :   Whether snippets are enabled

    `ssh_url_to_repo: str`
    :   SSH URL to the repository

    `star_count: str`
    :   Number of stars

    `statistics: str`
    :   Project statistics

    `tag_list: str`
    :   List of tags for the project

    `topics: str`
    :   List of topics for the project

    `updated_at: str`
    :   Timestamp when the project was last updated

    `visibility: str`
    :   Visibility level of the project

    `web_url: str`
    :   Web URL of the project

    `wiki_access_level: str`
    :   Access level for the wiki

    `wiki_enabled: str`
    :   Whether wiki is enabled

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.ReleasesAnyValueFilter`
    :   The type of the None singleton.

<a id="ReleasesAnyValueFilter"></a>

`ReleasesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: Any`
    :   Assets attached to the release

    `author: Any`
    :   Author of the release

    `author_id: Any`
    :   ID of the author

    `commit: Any`
    :   Commit associated with the release

    `commit_id: Any`
    :   SHA of the associated commit

    `commit_path: Any`
    :   Path to the release commit

    `created_at: Any`
    :   Timestamp when the release was created

    `description: Any`
    :   Description of the release

    `evidences: Any`
    :   Evidences collected for the release

    `links: Any`
    :   Related resource links

    `milestones: Any`
    :   Milestones associated with the release

    `name: Any`
    :   Name of the release

    `project_id: Any`
    :   ID of the project

    `released_at: Any`
    :   Timestamp when the release was published

    `tag_name: Any`
    :   Tag name associated with the release

    `tag_path: Any`
    :   Path to the release tag

    `upcoming_release: Any`
    :   Whether this is an upcoming release

<a id="ReleasesContainsCondition"></a>

`ReleasesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.ReleasesAnyValueFilter`
    :   The type of the None singleton.

<a id="ReleasesEqCondition"></a>

`ReleasesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesFuzzyCondition"></a>

`ReleasesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesGetParams"></a>

`ReleasesGetParams(*args, **kwargs)`
:   Parameters for releases.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `project_id: str`
    :   The type of the None singleton.

    `tag_name: str`
    :   The type of the None singleton.

<a id="ReleasesGtCondition"></a>

`ReleasesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesGteCondition"></a>

`ReleasesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.ReleasesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.ReleasesInFilter`
    :   The type of the None singleton.

<a id="ReleasesInFilter"></a>

`ReleasesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: list[dict[str, typing.Any]]`
    :   Assets attached to the release

    `author: list[dict[str, typing.Any]]`
    :   Author of the release

    `author_id: list[int]`
    :   ID of the author

    `commit: list[dict[str, typing.Any]]`
    :   Commit associated with the release

    `commit_id: list[str]`
    :   SHA of the associated commit

    `commit_path: list[str]`
    :   Path to the release commit

    `created_at: list[str]`
    :   Timestamp when the release was created

    `description: list[str]`
    :   Description of the release

    `evidences: list[list[typing.Any]]`
    :   Evidences collected for the release

    `links: list[dict[str, typing.Any]]`
    :   Related resource links

    `milestones: list[list[typing.Any]]`
    :   Milestones associated with the release

    `name: list[str]`
    :   Name of the release

    `project_id: list[int]`
    :   ID of the project

    `released_at: list[str]`
    :   Timestamp when the release was published

    `tag_name: list[str]`
    :   Tag name associated with the release

    `tag_path: list[str]`
    :   Path to the release tag

    `upcoming_release: list[bool]`
    :   Whether this is an upcoming release

<a id="ReleasesKeywordCondition"></a>

`ReleasesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesLikeCondition"></a>

`ReleasesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.ReleasesStringFilter`
    :   The type of the None singleton.

<a id="ReleasesListParams"></a>

`ReleasesListParams(*args, **kwargs)`
:   Parameters for releases.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_by: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="ReleasesLtCondition"></a>

`ReleasesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesLteCondition"></a>

`ReleasesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.ReleasesSearchFilter`
    :   The type of the None singleton.

<a id="ReleasesNeqCondition"></a>

`ReleasesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.ReleasesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAnyCondition]`
    :   The type of the None singleton.

<a id="ReleasesSearchFilter"></a>

`ReleasesSearchFilter(*args, **kwargs)`
:   Available fields for filtering releases search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: dict[str, typing.Any] | None`
    :   Assets attached to the release

    `author: dict[str, typing.Any] | None`
    :   Author of the release

    `author_id: int | None`
    :   ID of the author

    `commit: dict[str, typing.Any] | None`
    :   Commit associated with the release

    `commit_id: str | None`
    :   SHA of the associated commit

    `commit_path: str | None`
    :   Path to the release commit

    `created_at: str | None`
    :   Timestamp when the release was created

    `description: str | None`
    :   Description of the release

    `evidences: list[typing.Any] | None`
    :   Evidences collected for the release

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `milestones: list[typing.Any] | None`
    :   Milestones associated with the release

    `name: str | None`
    :   Name of the release

    `project_id: int | None`
    :   ID of the project

    `released_at: str | None`
    :   Timestamp when the release was published

    `tag_name: str | None`
    :   Tag name associated with the release

    `tag_path: str | None`
    :   Path to the release tag

    `upcoming_release: bool | None`
    :   Whether this is an upcoming release

<a id="ReleasesSearchQuery"></a>

`ReleasesSearchQuery(*args, **kwargs)`
:   Search query for releases entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.ReleasesEqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesGteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLtCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLteCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesInCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesNotCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAndCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesOrCondition | airbyte_agent_sdk.connectors.gitlab.types.ReleasesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.ReleasesSortFilter]`
    :   The type of the None singleton.

<a id="ReleasesSortFilter"></a>

`ReleasesSortFilter(*args, **kwargs)`
:   Available fields for sorting releases search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: Literal['asc', 'desc']`
    :   Assets attached to the release

    `author: Literal['asc', 'desc']`
    :   Author of the release

    `author_id: Literal['asc', 'desc']`
    :   ID of the author

    `commit: Literal['asc', 'desc']`
    :   Commit associated with the release

    `commit_id: Literal['asc', 'desc']`
    :   SHA of the associated commit

    `commit_path: Literal['asc', 'desc']`
    :   Path to the release commit

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the release was created

    `description: Literal['asc', 'desc']`
    :   Description of the release

    `evidences: Literal['asc', 'desc']`
    :   Evidences collected for the release

    `links: Literal['asc', 'desc']`
    :   Related resource links

    `milestones: Literal['asc', 'desc']`
    :   Milestones associated with the release

    `name: Literal['asc', 'desc']`
    :   Name of the release

    `project_id: Literal['asc', 'desc']`
    :   ID of the project

    `released_at: Literal['asc', 'desc']`
    :   Timestamp when the release was published

    `tag_name: Literal['asc', 'desc']`
    :   Tag name associated with the release

    `tag_path: Literal['asc', 'desc']`
    :   Path to the release tag

    `upcoming_release: Literal['asc', 'desc']`
    :   Whether this is an upcoming release

<a id="ReleasesStringFilter"></a>

`ReleasesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assets: str`
    :   Assets attached to the release

    `author: str`
    :   Author of the release

    `author_id: str`
    :   ID of the author

    `commit: str`
    :   Commit associated with the release

    `commit_id: str`
    :   SHA of the associated commit

    `commit_path: str`
    :   Path to the release commit

    `created_at: str`
    :   Timestamp when the release was created

    `description: str`
    :   Description of the release

    `evidences: str`
    :   Evidences collected for the release

    `links: str`
    :   Related resource links

    `milestones: str`
    :   Milestones associated with the release

    `name: str`
    :   Name of the release

    `project_id: str`
    :   ID of the project

    `released_at: str`
    :   Timestamp when the release was published

    `tag_name: str`
    :   Tag name associated with the release

    `tag_path: str`
    :   Path to the release tag

    `upcoming_release: str`
    :   Whether this is an upcoming release

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.TagsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsInCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsAnyValueFilter"></a>

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commit: Any`
    :   Commit the tag points to

    `commit_id: Any`
    :   SHA of the tagged commit

    `message: Any`
    :   Annotation message of the tag

    `name: Any`
    :   Name of the tag

    `project_id: Any`
    :   ID of the project

    `protected: Any`
    :   Whether the tag is protected

    `release: Any`
    :   Release associated with the tag

    `target: Any`
    :   SHA the tag points to

<a id="TagsContainsCondition"></a>

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsEqCondition"></a>

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsFuzzyCondition"></a>

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsGetParams"></a>

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `project_id: str`
    :   The type of the None singleton.

    `tag_name: str`
    :   The type of the None singleton.

<a id="TagsGtCondition"></a>

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.gitlab.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsGteCondition"></a>

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.TagsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.TagsInFilter`
    :   The type of the None singleton.

<a id="TagsInFilter"></a>

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commit: list[dict[str, typing.Any]]`
    :   Commit the tag points to

    `commit_id: list[str]`
    :   SHA of the tagged commit

    `message: list[str]`
    :   Annotation message of the tag

    `name: list[str]`
    :   Name of the tag

    `project_id: list[int]`
    :   ID of the project

    `protected: list[bool]`
    :   Whether the tag is protected

    `release: list[dict[str, typing.Any]]`
    :   Release associated with the tag

    `target: list[str]`
    :   SHA the tag points to

<a id="TagsKeywordCondition"></a>

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsLikeCondition"></a>

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_by: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

<a id="TagsLtCondition"></a>

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsLteCondition"></a>

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsNeqCondition"></a>

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.TagsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.TagsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsInCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.TagsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsInCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAnyCondition]`
    :   The type of the None singleton.

<a id="TagsSearchFilter"></a>

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commit: dict[str, typing.Any] | None`
    :   Commit the tag points to

    `commit_id: str | None`
    :   SHA of the tagged commit

    `message: str | None`
    :   Annotation message of the tag

    `name: str | None`
    :   Name of the tag

    `project_id: int | None`
    :   ID of the project

    `protected: bool | None`
    :   Whether the tag is protected

    `release: dict[str, typing.Any] | None`
    :   Release associated with the tag

    `target: str | None`
    :   SHA the tag points to

<a id="TagsSearchQuery"></a>

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.TagsEqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsGteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLtCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLteCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsInCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsNotCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAndCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsOrCondition | airbyte_agent_sdk.connectors.gitlab.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.TagsSortFilter]`
    :   The type of the None singleton.

<a id="TagsSortFilter"></a>

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commit: Literal['asc', 'desc']`
    :   Commit the tag points to

    `commit_id: Literal['asc', 'desc']`
    :   SHA of the tagged commit

    `message: Literal['asc', 'desc']`
    :   Annotation message of the tag

    `name: Literal['asc', 'desc']`
    :   Name of the tag

    `project_id: Literal['asc', 'desc']`
    :   ID of the project

    `protected: Literal['asc', 'desc']`
    :   Whether the tag is protected

    `release: Literal['asc', 'desc']`
    :   Release associated with the tag

    `target: Literal['asc', 'desc']`
    :   SHA the tag points to

<a id="TagsStringFilter"></a>

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `commit: str`
    :   Commit the tag points to

    `commit_id: str`
    :   SHA of the tagged commit

    `message: str`
    :   Annotation message of the tag

    `name: str`
    :   Name of the tag

    `project_id: str`
    :   ID of the project

    `protected: str`
    :   Whether the tag is protected

    `release: str`
    :   Release associated with the tag

    `target: str`
    :   SHA the tag points to

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

    `and: list[airbyte_agent_sdk.connectors.gitlab.types.UsersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersInCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.gitlab.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Any`
    :   URL of the user avatar

    `id: Any`
    :   ID of the user

    `locked: Any`
    :   Whether the user account is locked

    `name: Any`
    :   Full name of the user

    `state: Any`
    :   State of the user account

    `username: Any`
    :   Username of the user

    `web_url: Any`
    :   Web URL of the user profile

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.gitlab.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.gitlab.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.gitlab.types.UsersStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.gitlab.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.gitlab.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.gitlab.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: list[str]`
    :   URL of the user avatar

    `id: list[int]`
    :   ID of the user

    `locked: list[bool]`
    :   Whether the user account is locked

    `name: list[str]`
    :   Full name of the user

    `state: list[str]`
    :   State of the user account

    `username: list[str]`
    :   Username of the user

    `web_url: list[str]`
    :   Web URL of the user profile

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.gitlab.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.gitlab.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `search: str`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.gitlab.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.gitlab.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.gitlab.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.gitlab.types.UsersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersInCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.gitlab.types.UsersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersInCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str | None`
    :   URL of the user avatar

    `id: int | None`
    :   ID of the user

    `locked: bool | None`
    :   Whether the user account is locked

    `name: str | None`
    :   Full name of the user

    `state: str | None`
    :   State of the user account

    `username: str | None`
    :   Username of the user

    `web_url: str | None`
    :   Web URL of the user profile

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.gitlab.types.UsersEqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNeqCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersGteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLtCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLteCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersInCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersLikeCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersContainsCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersNotCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAndCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersOrCondition | airbyte_agent_sdk.connectors.gitlab.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.gitlab.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: Literal['asc', 'desc']`
    :   URL of the user avatar

    `id: Literal['asc', 'desc']`
    :   ID of the user

    `locked: Literal['asc', 'desc']`
    :   Whether the user account is locked

    `name: Literal['asc', 'desc']`
    :   Full name of the user

    `state: Literal['asc', 'desc']`
    :   State of the user account

    `username: Literal['asc', 'desc']`
    :   Username of the user

    `web_url: Literal['asc', 'desc']`
    :   Web URL of the user profile

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar_url: str`
    :   URL of the user avatar

    `id: str`
    :   ID of the user

    `locked: str`
    :   Whether the user account is locked

    `name: str`
    :   Full name of the user

    `state: str`
    :   State of the user account

    `username: str`
    :   Username of the user

    `web_url: str`
    :   Web URL of the user profile