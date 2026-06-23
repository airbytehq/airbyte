---
id: airbyte_agent_sdk-connectors-linear-types
title: airbyte_agent_sdk.connectors.linear.types
---

Module airbyte_agent_sdk.connectors.linear.types
================================================
Type definitions for linear connector.

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

    `and: list[airbyte_agent_sdk.connectors.linear.types.CommentsEqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsInCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.linear.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNotCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAndCondition | airbyte_agent_sdk.connectors.linear.types.CommentsOrCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linear.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsAnyValueFilter"></a>

`CommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: Any`
    :   The type of the None singleton.

    `body_data: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `edited_at: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `issue: Any`
    :   The type of the None singleton.

    `issue_id: Any`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `parent_comment_id: Any`
    :   The type of the None singleton.

    `resolving_comment_id: Any`
    :   The type of the None singleton.

    `resolving_user_id: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

    `url: Any`
    :   The type of the None singleton.

    `user: Any`
    :   The type of the None singleton.

    `user_id: Any`
    :   The type of the None singleton.

<a id="CommentsContainsCondition"></a>

`CommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linear.types.CommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="CommentsCreateParams"></a>

`CommentsCreateParams(*args, **kwargs)`
:   Parameters for comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   The type of the None singleton.

    `issue_id: str`
    :   The type of the None singleton.

<a id="CommentsEqCondition"></a>

`CommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linear.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsFuzzyCondition"></a>

`CommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linear.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsGetParams"></a>

`CommentsGetParams(*args, **kwargs)`
:   Parameters for comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CommentsGtCondition"></a>

`CommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linear.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsGteCondition"></a>

`CommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linear.types.CommentsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linear.types.CommentsInFilter`
    :   The type of the None singleton.

<a id="CommentsInFilter"></a>

`CommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: list[str]`
    :   The type of the None singleton.

    `body_data: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `edited_at: list[str]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `issue: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `issue_id: list[str]`
    :   The type of the None singleton.

    `parent: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `parent_comment_id: list[str]`
    :   The type of the None singleton.

    `resolving_comment_id: list[str]`
    :   The type of the None singleton.

    `resolving_user_id: list[str]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

    `url: list[str]`
    :   The type of the None singleton.

    `user: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `user_id: list[str]`
    :   The type of the None singleton.

<a id="CommentsKeywordCondition"></a>

`CommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linear.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsLikeCondition"></a>

`CommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linear.types.CommentsStringFilter`
    :   The type of the None singleton.

<a id="CommentsListParams"></a>

`CommentsListParams(*args, **kwargs)`
:   Parameters for comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `first: int`
    :   The type of the None singleton.

    `issue_id: str`
    :   The type of the None singleton.

<a id="CommentsLtCondition"></a>

`CommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linear.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsLteCondition"></a>

`CommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linear.types.CommentsSearchFilter`
    :   The type of the None singleton.

<a id="CommentsNeqCondition"></a>

`CommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linear.types.CommentsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linear.types.CommentsEqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsInCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.linear.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNotCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAndCondition | airbyte_agent_sdk.connectors.linear.types.CommentsOrCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linear.types.CommentsEqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsInCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.linear.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNotCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAndCondition | airbyte_agent_sdk.connectors.linear.types.CommentsOrCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAnyCondition]`
    :   The type of the None singleton.

<a id="CommentsSearchFilter"></a>

`CommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str | None`
    :   The type of the None singleton.

    `body_data: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `edited_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `issue: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `issue_id: str | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `parent_comment_id: str | None`
    :   The type of the None singleton.

    `resolving_comment_id: str | None`
    :   The type of the None singleton.

    `resolving_user_id: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `user_id: str | None`
    :   The type of the None singleton.

<a id="CommentsSearchQuery"></a>

`CommentsSearchQuery(*args, **kwargs)`
:   Search query for comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linear.types.CommentsEqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNeqCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsGteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLtCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLteCondition | airbyte_agent_sdk.connectors.linear.types.CommentsInCondition | airbyte_agent_sdk.connectors.linear.types.CommentsLikeCondition | airbyte_agent_sdk.connectors.linear.types.CommentsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.CommentsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.CommentsContainsCondition | airbyte_agent_sdk.connectors.linear.types.CommentsNotCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAndCondition | airbyte_agent_sdk.connectors.linear.types.CommentsOrCondition | airbyte_agent_sdk.connectors.linear.types.CommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linear.types.CommentsSortFilter]`
    :   The type of the None singleton.

<a id="CommentsSortFilter"></a>

`CommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `body_data: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `edited_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent_comment_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resolving_comment_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `resolving_user_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `user: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `user_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="CommentsStringFilter"></a>

`CommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   The type of the None singleton.

    `body_data: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `edited_at: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `issue: str`
    :   The type of the None singleton.

    `issue_id: str`
    :   The type of the None singleton.

    `parent: str`
    :   The type of the None singleton.

    `parent_comment_id: str`
    :   The type of the None singleton.

    `resolving_comment_id: str`
    :   The type of the None singleton.

    `resolving_user_id: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

    `user: str`
    :   The type of the None singleton.

    `user_id: str`
    :   The type of the None singleton.

<a id="CommentsUpdateParams"></a>

`CommentsUpdateParams(*args, **kwargs)`
:   Parameters for comments.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   The type of the None singleton.

    `id: str`
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

    `and: list[airbyte_agent_sdk.connectors.linear.types.IssuesEqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesInCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.linear.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNotCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAndCondition | airbyte_agent_sdk.connectors.linear.types.IssuesOrCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linear.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesAnyValueFilter"></a>

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `added_to_cycle_at: Any`
    :   The type of the None singleton.

    `added_to_project_at: Any`
    :   The type of the None singleton.

    `added_to_team_at: Any`
    :   The type of the None singleton.

    `assignee: Any`
    :   The type of the None singleton.

    `assignee_id: Any`
    :   The type of the None singleton.

    `attachment_ids: Any`
    :   The type of the None singleton.

    `attachments: Any`
    :   The type of the None singleton.

    `branch_name: Any`
    :   The type of the None singleton.

    `canceled_at: Any`
    :   The type of the None singleton.

    `completed_at: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `creator: Any`
    :   The type of the None singleton.

    `creator_id: Any`
    :   The type of the None singleton.

    `customer_ticket_count: Any`
    :   The type of the None singleton.

    `cycle: Any`
    :   The type of the None singleton.

    `cycle_id: Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `description_state: Any`
    :   The type of the None singleton.

    `due_date: Any`
    :   The type of the None singleton.

    `estimate: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `identifier: Any`
    :   The type of the None singleton.

    `integration_source_type: Any`
    :   The type of the None singleton.

    `label_ids: Any`
    :   The type of the None singleton.

    `labels: Any`
    :   The type of the None singleton.

    `milestone_id: Any`
    :   The type of the None singleton.

    `number: Any`
    :   The type of the None singleton.

    `parent: Any`
    :   The type of the None singleton.

    `parent_id: Any`
    :   The type of the None singleton.

    `previous_identifiers: Any`
    :   The type of the None singleton.

    `priority: Any`
    :   The type of the None singleton.

    `priority_label: Any`
    :   The type of the None singleton.

    `priority_sort_order: Any`
    :   The type of the None singleton.

    `project: Any`
    :   The type of the None singleton.

    `project_id: Any`
    :   The type of the None singleton.

    `project_milestone: Any`
    :   The type of the None singleton.

    `reaction_data: Any`
    :   The type of the None singleton.

    `relation_ids: Any`
    :   The type of the None singleton.

    `relations: Any`
    :   The type of the None singleton.

    `sla_type: Any`
    :   The type of the None singleton.

    `sort_order: Any`
    :   The type of the None singleton.

    `source_comment_id: Any`
    :   The type of the None singleton.

    `started_at: Any`
    :   The type of the None singleton.

    `state: Any`
    :   The type of the None singleton.

    `state_id: Any`
    :   The type of the None singleton.

    `sub_issue_sort_order: Any`
    :   The type of the None singleton.

    `subscriber_ids: Any`
    :   The type of the None singleton.

    `subscribers: Any`
    :   The type of the None singleton.

    `team: Any`
    :   The type of the None singleton.

    `team_id: Any`
    :   The type of the None singleton.

    `title: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

    `url: Any`
    :   The type of the None singleton.

<a id="IssuesContainsCondition"></a>

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linear.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesCreateParams"></a>

`IssuesCreateParams(*args, **kwargs)`
:   Parameters for issues.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `priority: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `state_id: str`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="IssuesEqCondition"></a>

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linear.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesFuzzyCondition"></a>

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linear.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesGetParams"></a>

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IssuesGtCondition"></a>

`IssuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linear.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesGteCondition"></a>

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linear.types.IssuesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linear.types.IssuesInFilter`
    :   The type of the None singleton.

<a id="IssuesInFilter"></a>

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `added_to_cycle_at: list[str]`
    :   The type of the None singleton.

    `added_to_project_at: list[str]`
    :   The type of the None singleton.

    `added_to_team_at: list[str]`
    :   The type of the None singleton.

    `assignee: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `assignee_id: list[str]`
    :   The type of the None singleton.

    `attachment_ids: list[list[typing.Any]]`
    :   The type of the None singleton.

    `attachments: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `branch_name: list[str]`
    :   The type of the None singleton.

    `canceled_at: list[str]`
    :   The type of the None singleton.

    `completed_at: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `creator: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `creator_id: list[str]`
    :   The type of the None singleton.

    `customer_ticket_count: list[float]`
    :   The type of the None singleton.

    `cycle: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `cycle_id: list[str]`
    :   The type of the None singleton.

    `description: list[str]`
    :   The type of the None singleton.

    `description_state: list[str]`
    :   The type of the None singleton.

    `due_date: list[str]`
    :   The type of the None singleton.

    `estimate: list[float]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `identifier: list[str]`
    :   The type of the None singleton.

    `integration_source_type: list[str]`
    :   The type of the None singleton.

    `label_ids: list[list[typing.Any]]`
    :   The type of the None singleton.

    `labels: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `milestone_id: list[str]`
    :   The type of the None singleton.

    `number: list[float]`
    :   The type of the None singleton.

    `parent: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `parent_id: list[str]`
    :   The type of the None singleton.

    `previous_identifiers: list[list[typing.Any]]`
    :   The type of the None singleton.

    `priority: list[float]`
    :   The type of the None singleton.

    `priority_label: list[str]`
    :   The type of the None singleton.

    `priority_sort_order: list[float]`
    :   The type of the None singleton.

    `project: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `project_id: list[str]`
    :   The type of the None singleton.

    `project_milestone: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `reaction_data: list[list[typing.Any]]`
    :   The type of the None singleton.

    `relation_ids: list[list[typing.Any]]`
    :   The type of the None singleton.

    `relations: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `sla_type: list[str]`
    :   The type of the None singleton.

    `sort_order: list[float]`
    :   The type of the None singleton.

    `source_comment_id: list[str]`
    :   The type of the None singleton.

    `started_at: list[str]`
    :   The type of the None singleton.

    `state: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `state_id: list[str]`
    :   The type of the None singleton.

    `sub_issue_sort_order: list[float]`
    :   The type of the None singleton.

    `subscriber_ids: list[list[typing.Any]]`
    :   The type of the None singleton.

    `subscribers: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `team: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `team_id: list[str]`
    :   The type of the None singleton.

    `title: list[str]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

    `url: list[str]`
    :   The type of the None singleton.

<a id="IssuesKeywordCondition"></a>

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linear.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLikeCondition"></a>

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linear.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesListParams"></a>

`IssuesListParams(*args, **kwargs)`
:   Parameters for issues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `first: int`
    :   The type of the None singleton.

<a id="IssuesLtCondition"></a>

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linear.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesLteCondition"></a>

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linear.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNeqCondition"></a>

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linear.types.IssuesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linear.types.IssuesEqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesInCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.linear.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNotCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAndCondition | airbyte_agent_sdk.connectors.linear.types.IssuesOrCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linear.types.IssuesEqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesInCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.linear.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNotCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAndCondition | airbyte_agent_sdk.connectors.linear.types.IssuesOrCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesSearchFilter"></a>

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `added_to_cycle_at: str | None`
    :   The type of the None singleton.

    `added_to_project_at: str | None`
    :   The type of the None singleton.

    `added_to_team_at: str | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `assignee_id: str | None`
    :   The type of the None singleton.

    `attachment_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `attachments: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `branch_name: str | None`
    :   The type of the None singleton.

    `canceled_at: str | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `customer_ticket_count: float | None`
    :   The type of the None singleton.

    `cycle: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `cycle_id: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `description_state: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `estimate: float | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `identifier: str | None`
    :   The type of the None singleton.

    `integration_source_type: str | None`
    :   The type of the None singleton.

    `label_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `labels: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `milestone_id: str | None`
    :   The type of the None singleton.

    `number: float | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `parent_id: str | None`
    :   The type of the None singleton.

    `previous_identifiers: list[typing.Any] | None`
    :   The type of the None singleton.

    `priority: float | None`
    :   The type of the None singleton.

    `priority_label: str | None`
    :   The type of the None singleton.

    `priority_sort_order: float | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `project_id: str | None`
    :   The type of the None singleton.

    `project_milestone: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `reaction_data: list[typing.Any] | None`
    :   The type of the None singleton.

    `relation_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `relations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `sla_type: str | None`
    :   The type of the None singleton.

    `sort_order: float | None`
    :   The type of the None singleton.

    `source_comment_id: str | None`
    :   The type of the None singleton.

    `started_at: str | None`
    :   The type of the None singleton.

    `state: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `state_id: str | None`
    :   The type of the None singleton.

    `sub_issue_sort_order: float | None`
    :   The type of the None singleton.

    `subscriber_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `subscribers: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="IssuesSearchQuery"></a>

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linear.types.IssuesEqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesGteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLtCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLteCondition | airbyte_agent_sdk.connectors.linear.types.IssuesInCondition | airbyte_agent_sdk.connectors.linear.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.linear.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.linear.types.IssuesNotCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAndCondition | airbyte_agent_sdk.connectors.linear.types.IssuesOrCondition | airbyte_agent_sdk.connectors.linear.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linear.types.IssuesSortFilter]`
    :   The type of the None singleton.

<a id="IssuesSortFilter"></a>

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `added_to_cycle_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `added_to_project_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `added_to_team_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `assignee: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `assignee_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `attachment_ids: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `attachments: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `branch_name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `canceled_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `creator: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `creator_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `customer_ticket_count: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `description: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `description_state: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `due_date: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `estimate: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `identifier: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `integration_source_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `label_ids: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `labels: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `milestone_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `number: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `previous_identifiers: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `priority: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `priority_label: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `priority_sort_order: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `project: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `project_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `project_milestone: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `reaction_data: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relation_ids: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `relations: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `sla_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `sort_order: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `source_comment_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `started_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `state: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `state_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `sub_issue_sort_order: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `subscriber_ids: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `subscribers: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `title: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `url: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `added_to_cycle_at: str`
    :   The type of the None singleton.

    `added_to_project_at: str`
    :   The type of the None singleton.

    `added_to_team_at: str`
    :   The type of the None singleton.

    `assignee: str`
    :   The type of the None singleton.

    `assignee_id: str`
    :   The type of the None singleton.

    `attachment_ids: str`
    :   The type of the None singleton.

    `attachments: str`
    :   The type of the None singleton.

    `branch_name: str`
    :   The type of the None singleton.

    `canceled_at: str`
    :   The type of the None singleton.

    `completed_at: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `creator: str`
    :   The type of the None singleton.

    `creator_id: str`
    :   The type of the None singleton.

    `customer_ticket_count: str`
    :   The type of the None singleton.

    `cycle: str`
    :   The type of the None singleton.

    `cycle_id: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `description_state: str`
    :   The type of the None singleton.

    `due_date: str`
    :   The type of the None singleton.

    `estimate: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `identifier: str`
    :   The type of the None singleton.

    `integration_source_type: str`
    :   The type of the None singleton.

    `label_ids: str`
    :   The type of the None singleton.

    `labels: str`
    :   The type of the None singleton.

    `milestone_id: str`
    :   The type of the None singleton.

    `number: str`
    :   The type of the None singleton.

    `parent: str`
    :   The type of the None singleton.

    `parent_id: str`
    :   The type of the None singleton.

    `previous_identifiers: str`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `priority_label: str`
    :   The type of the None singleton.

    `priority_sort_order: str`
    :   The type of the None singleton.

    `project: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `project_milestone: str`
    :   The type of the None singleton.

    `reaction_data: str`
    :   The type of the None singleton.

    `relation_ids: str`
    :   The type of the None singleton.

    `relations: str`
    :   The type of the None singleton.

    `sla_type: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

    `source_comment_id: str`
    :   The type of the None singleton.

    `started_at: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `state_id: str`
    :   The type of the None singleton.

    `sub_issue_sort_order: str`
    :   The type of the None singleton.

    `subscriber_ids: str`
    :   The type of the None singleton.

    `subscribers: str`
    :   The type of the None singleton.

    `team: str`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParams"></a>

`IssuesUpdateParams(*args, **kwargs)`
:   Parameters for issues.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `priority: int`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `state_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linear.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsInCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linear.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsAnyValueFilter"></a>

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `canceled_at: Any`
    :   The type of the None singleton.

    `color: Any`
    :   The type of the None singleton.

    `completed_at: Any`
    :   The type of the None singleton.

    `completed_issue_count_history: Any`
    :   The type of the None singleton.

    `completed_scope_history: Any`
    :   The type of the None singleton.

    `content: Any`
    :   The type of the None singleton.

    `content_state: Any`
    :   The type of the None singleton.

    `converted_from_issue: Any`
    :   The type of the None singleton.

    `converted_from_issue_id: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `creator: Any`
    :   The type of the None singleton.

    `creator_id: Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `health: Any`
    :   The type of the None singleton.

    `health_updated_at: Any`
    :   The type of the None singleton.

    `icon: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `in_progress_scope_history: Any`
    :   The type of the None singleton.

    `issue_count_history: Any`
    :   The type of the None singleton.

    `lead: Any`
    :   The type of the None singleton.

    `lead_id: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `priority: Any`
    :   The type of the None singleton.

    `priority_sort_order: Any`
    :   The type of the None singleton.

    `progress: Any`
    :   The type of the None singleton.

    `scope: Any`
    :   The type of the None singleton.

    `scope_history: Any`
    :   The type of the None singleton.

    `slug_id: Any`
    :   The type of the None singleton.

    `sort_order: Any`
    :   The type of the None singleton.

    `start_date: Any`
    :   The type of the None singleton.

    `started_at: Any`
    :   The type of the None singleton.

    `status: Any`
    :   The type of the None singleton.

    `status_id: Any`
    :   The type of the None singleton.

    `target_date: Any`
    :   The type of the None singleton.

    `team_ids: Any`
    :   The type of the None singleton.

    `teams: Any`
    :   The type of the None singleton.

    `update_reminders_day: Any`
    :   The type of the None singleton.

    `update_reminders_hour: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

    `url: Any`
    :   The type of the None singleton.

<a id="ProjectsContainsCondition"></a>

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linear.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsCreateParams"></a>

`ProjectsCreateParams(*args, **kwargs)`
:   Parameters for projects.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `lead_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `target_date: str`
    :   The type of the None singleton.

    `team_ids: list[str]`
    :   The type of the None singleton.

<a id="ProjectsEqCondition"></a>

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linear.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsFuzzyCondition"></a>

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linear.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsGetParams"></a>

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProjectsGtCondition"></a>

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linear.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsGteCondition"></a>

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linear.types.ProjectsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linear.types.ProjectsInFilter`
    :   The type of the None singleton.

<a id="ProjectsInFilter"></a>

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `canceled_at: list[str]`
    :   The type of the None singleton.

    `color: list[str]`
    :   The type of the None singleton.

    `completed_at: list[str]`
    :   The type of the None singleton.

    `completed_issue_count_history: list[list[typing.Any]]`
    :   The type of the None singleton.

    `completed_scope_history: list[list[typing.Any]]`
    :   The type of the None singleton.

    `content: list[str]`
    :   The type of the None singleton.

    `content_state: list[str]`
    :   The type of the None singleton.

    `converted_from_issue: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `converted_from_issue_id: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `creator: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `creator_id: list[str]`
    :   The type of the None singleton.

    `description: list[str]`
    :   The type of the None singleton.

    `health: list[str]`
    :   The type of the None singleton.

    `health_updated_at: list[str]`
    :   The type of the None singleton.

    `icon: list[str]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `in_progress_scope_history: list[list[typing.Any]]`
    :   The type of the None singleton.

    `issue_count_history: list[list[typing.Any]]`
    :   The type of the None singleton.

    `lead: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `lead_id: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `priority: list[float]`
    :   The type of the None singleton.

    `priority_sort_order: list[float]`
    :   The type of the None singleton.

    `progress: list[float]`
    :   The type of the None singleton.

    `scope: list[float]`
    :   The type of the None singleton.

    `scope_history: list[list[typing.Any]]`
    :   The type of the None singleton.

    `slug_id: list[str]`
    :   The type of the None singleton.

    `sort_order: list[float]`
    :   The type of the None singleton.

    `start_date: list[str]`
    :   The type of the None singleton.

    `started_at: list[str]`
    :   The type of the None singleton.

    `status: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `status_id: list[str]`
    :   The type of the None singleton.

    `target_date: list[str]`
    :   The type of the None singleton.

    `team_ids: list[list[typing.Any]]`
    :   The type of the None singleton.

    `teams: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `update_reminders_day: list[str]`
    :   The type of the None singleton.

    `update_reminders_hour: list[float]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

    `url: list[str]`
    :   The type of the None singleton.

<a id="ProjectsKeywordCondition"></a>

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linear.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsLikeCondition"></a>

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linear.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsListParams"></a>

`ProjectsListParams(*args, **kwargs)`
:   Parameters for projects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `first: int`
    :   The type of the None singleton.

<a id="ProjectsLtCondition"></a>

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linear.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsLteCondition"></a>

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linear.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNeqCondition"></a>

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linear.types.ProjectsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linear.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsInCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linear.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsInCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsSearchFilter"></a>

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `canceled_at: str | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `completed_issue_count_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `completed_scope_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `content: str | None`
    :   The type of the None singleton.

    `content_state: str | None`
    :   The type of the None singleton.

    `converted_from_issue: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `converted_from_issue_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `health: str | None`
    :   The type of the None singleton.

    `health_updated_at: str | None`
    :   The type of the None singleton.

    `icon: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `in_progress_scope_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `issue_count_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `lead: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `lead_id: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `priority: float | None`
    :   The type of the None singleton.

    `priority_sort_order: float | None`
    :   The type of the None singleton.

    `progress: float | None`
    :   The type of the None singleton.

    `scope: float | None`
    :   The type of the None singleton.

    `scope_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `slug_id: str | None`
    :   The type of the None singleton.

    `sort_order: float | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `started_at: str | None`
    :   The type of the None singleton.

    `status: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `status_id: str | None`
    :   The type of the None singleton.

    `target_date: str | None`
    :   The type of the None singleton.

    `team_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `teams: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `update_reminders_day: str | None`
    :   The type of the None singleton.

    `update_reminders_hour: float | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="ProjectsSearchQuery"></a>

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linear.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsInCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.linear.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linear.types.ProjectsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectsSortFilter"></a>

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `canceled_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `color: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed_issue_count_history: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `completed_scope_history: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `content: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `content_state: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `converted_from_issue: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `converted_from_issue_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `creator: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `creator_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `description: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `health: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `health_updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `icon: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `in_progress_scope_history: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue_count_history: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `lead: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `lead_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `priority: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `priority_sort_order: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `progress: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `scope: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `scope_history: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `slug_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `sort_order: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `start_date: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `started_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `status: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `status_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `target_date: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team_ids: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `teams: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `update_reminders_day: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `update_reminders_hour: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `url: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="ProjectsStringFilter"></a>

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `canceled_at: str`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `completed_at: str`
    :   The type of the None singleton.

    `completed_issue_count_history: str`
    :   The type of the None singleton.

    `completed_scope_history: str`
    :   The type of the None singleton.

    `content: str`
    :   The type of the None singleton.

    `content_state: str`
    :   The type of the None singleton.

    `converted_from_issue: str`
    :   The type of the None singleton.

    `converted_from_issue_id: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `creator: str`
    :   The type of the None singleton.

    `creator_id: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `health: str`
    :   The type of the None singleton.

    `health_updated_at: str`
    :   The type of the None singleton.

    `icon: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `in_progress_scope_history: str`
    :   The type of the None singleton.

    `issue_count_history: str`
    :   The type of the None singleton.

    `lead: str`
    :   The type of the None singleton.

    `lead_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `priority_sort_order: str`
    :   The type of the None singleton.

    `progress: str`
    :   The type of the None singleton.

    `scope: str`
    :   The type of the None singleton.

    `scope_history: str`
    :   The type of the None singleton.

    `slug_id: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `started_at: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `status_id: str`
    :   The type of the None singleton.

    `target_date: str`
    :   The type of the None singleton.

    `team_ids: str`
    :   The type of the None singleton.

    `teams: str`
    :   The type of the None singleton.

    `update_reminders_day: str`
    :   The type of the None singleton.

    `update_reminders_hour: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="ProjectsUpdateParams"></a>

`ProjectsUpdateParams(*args, **kwargs)`
:   Parameters for projects.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `lead_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `target_date: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linear.types.TeamsEqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsInCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.linear.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNotCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAndCondition | airbyte_agent_sdk.connectors.linear.types.TeamsOrCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linear.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsAnyValueFilter"></a>

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active_cycle: Any`
    :   The type of the None singleton.

    `active_cycle_id: Any`
    :   The type of the None singleton.

    `auto_archive_period: Any`
    :   The type of the None singleton.

    `auto_close_period: Any`
    :   The type of the None singleton.

    `auto_close_state_id: Any`
    :   The type of the None singleton.

    `color: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `cycle_calender_url: Any`
    :   The type of the None singleton.

    `cycle_cooldown_time: Any`
    :   The type of the None singleton.

    `cycle_duration: Any`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_completed: Any`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_started: Any`
    :   The type of the None singleton.

    `cycle_lock_to_active: Any`
    :   The type of the None singleton.

    `cycle_start_day: Any`
    :   The type of the None singleton.

    `cycles_enabled: Any`
    :   The type of the None singleton.

    `default_issue_estimate: Any`
    :   The type of the None singleton.

    `default_issue_state: Any`
    :   The type of the None singleton.

    `default_issue_state_id: Any`
    :   The type of the None singleton.

    `group_issue_history: Any`
    :   The type of the None singleton.

    `icon: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `invite_hash: Any`
    :   The type of the None singleton.

    `issue_count: Any`
    :   The type of the None singleton.

    `issue_estimation_allow_zero: Any`
    :   The type of the None singleton.

    `issue_estimation_extended: Any`
    :   The type of the None singleton.

    `issue_estimation_type: Any`
    :   The type of the None singleton.

    `key: Any`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state: Any`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state_id: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `parent_team_id: Any`
    :   The type of the None singleton.

    `private: Any`
    :   The type of the None singleton.

    `require_priority_to_leave_triage: Any`
    :   The type of the None singleton.

    `scim_managed: Any`
    :   The type of the None singleton.

    `set_issue_sort_order_on_state_change: Any`
    :   The type of the None singleton.

    `timezone: Any`
    :   The type of the None singleton.

    `triage_enabled: Any`
    :   The type of the None singleton.

    `triage_issue_state_id: Any`
    :   The type of the None singleton.

    `upcoming_cycle_count: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

<a id="TeamsContainsCondition"></a>

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linear.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsEqCondition"></a>

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linear.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsFuzzyCondition"></a>

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linear.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsGetParams"></a>

`TeamsGetParams(*args, **kwargs)`
:   Parameters for teams.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TeamsGtCondition"></a>

`TeamsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linear.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsGteCondition"></a>

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linear.types.TeamsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linear.types.TeamsInFilter`
    :   The type of the None singleton.

<a id="TeamsInFilter"></a>

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active_cycle: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `active_cycle_id: list[str]`
    :   The type of the None singleton.

    `auto_archive_period: list[float]`
    :   The type of the None singleton.

    `auto_close_period: list[float]`
    :   The type of the None singleton.

    `auto_close_state_id: list[str]`
    :   The type of the None singleton.

    `color: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `cycle_calender_url: list[str]`
    :   The type of the None singleton.

    `cycle_cooldown_time: list[float]`
    :   The type of the None singleton.

    `cycle_duration: list[float]`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_completed: list[bool]`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_started: list[bool]`
    :   The type of the None singleton.

    `cycle_lock_to_active: list[bool]`
    :   The type of the None singleton.

    `cycle_start_day: list[float]`
    :   The type of the None singleton.

    `cycles_enabled: list[bool]`
    :   The type of the None singleton.

    `default_issue_estimate: list[float]`
    :   The type of the None singleton.

    `default_issue_state: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `default_issue_state_id: list[str]`
    :   The type of the None singleton.

    `group_issue_history: list[bool]`
    :   The type of the None singleton.

    `icon: list[str]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `invite_hash: list[str]`
    :   The type of the None singleton.

    `issue_count: list[float]`
    :   The type of the None singleton.

    `issue_estimation_allow_zero: list[bool]`
    :   The type of the None singleton.

    `issue_estimation_extended: list[bool]`
    :   The type of the None singleton.

    `issue_estimation_type: list[str]`
    :   The type of the None singleton.

    `key: list[str]`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state_id: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `parent_team_id: list[str]`
    :   The type of the None singleton.

    `private: list[bool]`
    :   The type of the None singleton.

    `require_priority_to_leave_triage: list[bool]`
    :   The type of the None singleton.

    `scim_managed: list[bool]`
    :   The type of the None singleton.

    `set_issue_sort_order_on_state_change: list[str]`
    :   The type of the None singleton.

    `timezone: list[str]`
    :   The type of the None singleton.

    `triage_enabled: list[bool]`
    :   The type of the None singleton.

    `triage_issue_state_id: list[str]`
    :   The type of the None singleton.

    `upcoming_cycle_count: list[float]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

<a id="TeamsKeywordCondition"></a>

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linear.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsLikeCondition"></a>

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linear.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsListParams"></a>

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `first: int`
    :   The type of the None singleton.

<a id="TeamsLtCondition"></a>

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linear.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsLteCondition"></a>

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linear.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsNeqCondition"></a>

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linear.types.TeamsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linear.types.TeamsEqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsInCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.linear.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNotCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAndCondition | airbyte_agent_sdk.connectors.linear.types.TeamsOrCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linear.types.TeamsEqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsInCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.linear.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNotCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAndCondition | airbyte_agent_sdk.connectors.linear.types.TeamsOrCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAnyCondition]`
    :   The type of the None singleton.

<a id="TeamsSearchFilter"></a>

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active_cycle: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `active_cycle_id: str | None`
    :   The type of the None singleton.

    `auto_archive_period: float | None`
    :   The type of the None singleton.

    `auto_close_period: float | None`
    :   The type of the None singleton.

    `auto_close_state_id: str | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `cycle_calender_url: str | None`
    :   The type of the None singleton.

    `cycle_cooldown_time: float | None`
    :   The type of the None singleton.

    `cycle_duration: float | None`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_completed: bool | None`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_started: bool | None`
    :   The type of the None singleton.

    `cycle_lock_to_active: bool | None`
    :   The type of the None singleton.

    `cycle_start_day: float | None`
    :   The type of the None singleton.

    `cycles_enabled: bool | None`
    :   The type of the None singleton.

    `default_issue_estimate: float | None`
    :   The type of the None singleton.

    `default_issue_state: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `default_issue_state_id: str | None`
    :   The type of the None singleton.

    `group_issue_history: bool | None`
    :   The type of the None singleton.

    `icon: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `invite_hash: str | None`
    :   The type of the None singleton.

    `issue_count: float | None`
    :   The type of the None singleton.

    `issue_estimation_allow_zero: bool | None`
    :   The type of the None singleton.

    `issue_estimation_extended: bool | None`
    :   The type of the None singleton.

    `issue_estimation_type: str | None`
    :   The type of the None singleton.

    `key: str | None`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state_id: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_team_id: str | None`
    :   The type of the None singleton.

    `private: bool | None`
    :   The type of the None singleton.

    `require_priority_to_leave_triage: bool | None`
    :   The type of the None singleton.

    `scim_managed: bool | None`
    :   The type of the None singleton.

    `set_issue_sort_order_on_state_change: str | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `triage_enabled: bool | None`
    :   The type of the None singleton.

    `triage_issue_state_id: str | None`
    :   The type of the None singleton.

    `upcoming_cycle_count: float | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TeamsSearchQuery"></a>

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linear.types.TeamsEqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsGteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLtCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLteCondition | airbyte_agent_sdk.connectors.linear.types.TeamsInCondition | airbyte_agent_sdk.connectors.linear.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.linear.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.linear.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.linear.types.TeamsNotCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAndCondition | airbyte_agent_sdk.connectors.linear.types.TeamsOrCondition | airbyte_agent_sdk.connectors.linear.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linear.types.TeamsSortFilter]`
    :   The type of the None singleton.

<a id="TeamsSortFilter"></a>

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active_cycle: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `active_cycle_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `auto_archive_period: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `auto_close_period: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `auto_close_state_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `color: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_calender_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_cooldown_time: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_duration: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_completed: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_started: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_lock_to_active: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycle_start_day: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `cycles_enabled: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `default_issue_estimate: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `default_issue_state: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `default_issue_state_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `group_issue_history: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `icon: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `invite_hash: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue_count: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue_estimation_allow_zero: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue_estimation_extended: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `issue_estimation_type: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `key: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `parent_team_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `private: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `require_priority_to_leave_triage: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `scim_managed: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `set_issue_sort_order_on_state_change: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `timezone: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `triage_enabled: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `triage_issue_state_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `upcoming_cycle_count: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="TeamsStringFilter"></a>

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active_cycle: str`
    :   The type of the None singleton.

    `active_cycle_id: str`
    :   The type of the None singleton.

    `auto_archive_period: str`
    :   The type of the None singleton.

    `auto_close_period: str`
    :   The type of the None singleton.

    `auto_close_state_id: str`
    :   The type of the None singleton.

    `color: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `cycle_calender_url: str`
    :   The type of the None singleton.

    `cycle_cooldown_time: str`
    :   The type of the None singleton.

    `cycle_duration: str`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_completed: str`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_started: str`
    :   The type of the None singleton.

    `cycle_lock_to_active: str`
    :   The type of the None singleton.

    `cycle_start_day: str`
    :   The type of the None singleton.

    `cycles_enabled: str`
    :   The type of the None singleton.

    `default_issue_estimate: str`
    :   The type of the None singleton.

    `default_issue_state: str`
    :   The type of the None singleton.

    `default_issue_state_id: str`
    :   The type of the None singleton.

    `group_issue_history: str`
    :   The type of the None singleton.

    `icon: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `invite_hash: str`
    :   The type of the None singleton.

    `issue_count: str`
    :   The type of the None singleton.

    `issue_estimation_allow_zero: str`
    :   The type of the None singleton.

    `issue_estimation_extended: str`
    :   The type of the None singleton.

    `issue_estimation_type: str`
    :   The type of the None singleton.

    `key: str`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state: str`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `parent_team_id: str`
    :   The type of the None singleton.

    `private: str`
    :   The type of the None singleton.

    `require_priority_to_leave_triage: str`
    :   The type of the None singleton.

    `scim_managed: str`
    :   The type of the None singleton.

    `set_issue_sort_order_on_state_change: str`
    :   The type of the None singleton.

    `timezone: str`
    :   The type of the None singleton.

    `triage_enabled: str`
    :   The type of the None singleton.

    `triage_issue_state_id: str`
    :   The type of the None singleton.

    `upcoming_cycle_count: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.linear.types.UsersEqCondition | airbyte_agent_sdk.connectors.linear.types.UsersNeqCondition | airbyte_agent_sdk.connectors.linear.types.UsersGtCondition | airbyte_agent_sdk.connectors.linear.types.UsersGteCondition | airbyte_agent_sdk.connectors.linear.types.UsersLtCondition | airbyte_agent_sdk.connectors.linear.types.UsersLteCondition | airbyte_agent_sdk.connectors.linear.types.UsersInCondition | airbyte_agent_sdk.connectors.linear.types.UsersLikeCondition | airbyte_agent_sdk.connectors.linear.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.linear.types.UsersContainsCondition | airbyte_agent_sdk.connectors.linear.types.UsersNotCondition | airbyte_agent_sdk.connectors.linear.types.UsersAndCondition | airbyte_agent_sdk.connectors.linear.types.UsersOrCondition | airbyte_agent_sdk.connectors.linear.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.linear.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   The type of the None singleton.

    `admin: Any`
    :   The type of the None singleton.

    `avatar_background_color: Any`
    :   The type of the None singleton.

    `avatar_url: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `created_issue_count: Any`
    :   The type of the None singleton.

    `display_name: Any`
    :   The type of the None singleton.

    `email: Any`
    :   The type of the None singleton.

    `guest: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `initials: Any`
    :   The type of the None singleton.

    `invite_hash: Any`
    :   The type of the None singleton.

    `is_me: Any`
    :   The type of the None singleton.

    `last_seen: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `team_ids: Any`
    :   The type of the None singleton.

    `teams: Any`
    :   The type of the None singleton.

    `timezone: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

    `url: Any`
    :   The type of the None singleton.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linear.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linear.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linear.types.UsersStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.linear.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linear.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.linear.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   The type of the None singleton.

    `admin: list[bool]`
    :   The type of the None singleton.

    `avatar_background_color: list[str]`
    :   The type of the None singleton.

    `avatar_url: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `created_issue_count: list[float]`
    :   The type of the None singleton.

    `display_name: list[str]`
    :   The type of the None singleton.

    `email: list[str]`
    :   The type of the None singleton.

    `guest: list[bool]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `initials: list[str]`
    :   The type of the None singleton.

    `invite_hash: list[str]`
    :   The type of the None singleton.

    `is_me: list[bool]`
    :   The type of the None singleton.

    `last_seen: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `team_ids: list[list[typing.Any]]`
    :   The type of the None singleton.

    `teams: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `timezone: list[str]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

    `url: list[str]`
    :   The type of the None singleton.

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linear.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linear.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `first: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linear.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linear.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linear.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.linear.types.UsersEqCondition | airbyte_agent_sdk.connectors.linear.types.UsersNeqCondition | airbyte_agent_sdk.connectors.linear.types.UsersGtCondition | airbyte_agent_sdk.connectors.linear.types.UsersGteCondition | airbyte_agent_sdk.connectors.linear.types.UsersLtCondition | airbyte_agent_sdk.connectors.linear.types.UsersLteCondition | airbyte_agent_sdk.connectors.linear.types.UsersInCondition | airbyte_agent_sdk.connectors.linear.types.UsersLikeCondition | airbyte_agent_sdk.connectors.linear.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.linear.types.UsersContainsCondition | airbyte_agent_sdk.connectors.linear.types.UsersNotCondition | airbyte_agent_sdk.connectors.linear.types.UsersAndCondition | airbyte_agent_sdk.connectors.linear.types.UsersOrCondition | airbyte_agent_sdk.connectors.linear.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.linear.types.UsersEqCondition | airbyte_agent_sdk.connectors.linear.types.UsersNeqCondition | airbyte_agent_sdk.connectors.linear.types.UsersGtCondition | airbyte_agent_sdk.connectors.linear.types.UsersGteCondition | airbyte_agent_sdk.connectors.linear.types.UsersLtCondition | airbyte_agent_sdk.connectors.linear.types.UsersLteCondition | airbyte_agent_sdk.connectors.linear.types.UsersInCondition | airbyte_agent_sdk.connectors.linear.types.UsersLikeCondition | airbyte_agent_sdk.connectors.linear.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.linear.types.UsersContainsCondition | airbyte_agent_sdk.connectors.linear.types.UsersNotCondition | airbyte_agent_sdk.connectors.linear.types.UsersAndCondition | airbyte_agent_sdk.connectors.linear.types.UsersOrCondition | airbyte_agent_sdk.connectors.linear.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   The type of the None singleton.

    `admin: bool | None`
    :   The type of the None singleton.

    `avatar_background_color: str | None`
    :   The type of the None singleton.

    `avatar_url: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `created_issue_count: float | None`
    :   The type of the None singleton.

    `display_name: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `guest: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `initials: str | None`
    :   The type of the None singleton.

    `invite_hash: str | None`
    :   The type of the None singleton.

    `is_me: bool | None`
    :   The type of the None singleton.

    `last_seen: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `team_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `teams: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linear.types.UsersEqCondition | airbyte_agent_sdk.connectors.linear.types.UsersNeqCondition | airbyte_agent_sdk.connectors.linear.types.UsersGtCondition | airbyte_agent_sdk.connectors.linear.types.UsersGteCondition | airbyte_agent_sdk.connectors.linear.types.UsersLtCondition | airbyte_agent_sdk.connectors.linear.types.UsersLteCondition | airbyte_agent_sdk.connectors.linear.types.UsersInCondition | airbyte_agent_sdk.connectors.linear.types.UsersLikeCondition | airbyte_agent_sdk.connectors.linear.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.linear.types.UsersContainsCondition | airbyte_agent_sdk.connectors.linear.types.UsersNotCondition | airbyte_agent_sdk.connectors.linear.types.UsersAndCondition | airbyte_agent_sdk.connectors.linear.types.UsersOrCondition | airbyte_agent_sdk.connectors.linear.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linear.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `admin: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `avatar_background_color: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `avatar_url: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_issue_count: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `display_name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `email: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `guest: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `initials: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `invite_hash: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `is_me: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `last_seen: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team_ids: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `teams: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `timezone: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `url: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   The type of the None singleton.

    `admin: str`
    :   The type of the None singleton.

    `avatar_background_color: str`
    :   The type of the None singleton.

    `avatar_url: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `created_issue_count: str`
    :   The type of the None singleton.

    `display_name: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `guest: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `initials: str`
    :   The type of the None singleton.

    `invite_hash: str`
    :   The type of the None singleton.

    `is_me: str`
    :   The type of the None singleton.

    `last_seen: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `team_ids: str`
    :   The type of the None singleton.

    `teams: str`
    :   The type of the None singleton.

    `timezone: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="WorkflowStatesAndCondition"></a>

`WorkflowStatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.linear.types.WorkflowStatesEqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNeqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesInCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLikeCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesContainsCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNotCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAndCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesOrCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAnyCondition]`
    :   The type of the None singleton.

<a id="WorkflowStatesAnyCondition"></a>

`WorkflowStatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAnyValueFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesAnyValueFilter"></a>

`WorkflowStatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Any`
    :   The type of the None singleton.

    `created_at: Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `inherited_from_id: Any`
    :   The type of the None singleton.

    `name: Any`
    :   The type of the None singleton.

    `position: Any`
    :   The type of the None singleton.

    `team: Any`
    :   The type of the None singleton.

    `team_id: Any`
    :   The type of the None singleton.

    `type_: Any`
    :   The type of the None singleton.

    `updated_at: Any`
    :   The type of the None singleton.

<a id="WorkflowStatesContainsCondition"></a>

`WorkflowStatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAnyValueFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesEqCondition"></a>

`WorkflowStatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSearchFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesFuzzyCondition"></a>

`WorkflowStatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesStringFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesGtCondition"></a>

`WorkflowStatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSearchFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesGteCondition"></a>

`WorkflowStatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSearchFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesInCondition"></a>

`WorkflowStatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesInFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesInFilter"></a>

`WorkflowStatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: list[str]`
    :   The type of the None singleton.

    `created_at: list[str]`
    :   The type of the None singleton.

    `description: list[str]`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `inherited_from_id: list[str]`
    :   The type of the None singleton.

    `name: list[str]`
    :   The type of the None singleton.

    `position: list[float]`
    :   The type of the None singleton.

    `team: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `team_id: list[str]`
    :   The type of the None singleton.

    `type_: list[str]`
    :   The type of the None singleton.

    `updated_at: list[str]`
    :   The type of the None singleton.

<a id="WorkflowStatesKeywordCondition"></a>

`WorkflowStatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesStringFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesLikeCondition"></a>

`WorkflowStatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesStringFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesListParams"></a>

`WorkflowStatesListParams(*args, **kwargs)`
:   Parameters for workflow_states.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `first: int`
    :   The type of the None singleton.

<a id="WorkflowStatesLtCondition"></a>

`WorkflowStatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSearchFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesLteCondition"></a>

`WorkflowStatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSearchFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesNeqCondition"></a>

`WorkflowStatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSearchFilter`
    :   The type of the None singleton.

<a id="WorkflowStatesNotCondition"></a>

`WorkflowStatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesEqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNeqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesInCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLikeCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesContainsCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNotCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAndCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesOrCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAnyCondition`
    :   The type of the None singleton.

<a id="WorkflowStatesOrCondition"></a>

`WorkflowStatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.linear.types.WorkflowStatesEqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNeqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesInCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLikeCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesContainsCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNotCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAndCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesOrCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAnyCondition]`
    :   The type of the None singleton.

<a id="WorkflowStatesSearchFilter"></a>

`WorkflowStatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering workflow_states search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `inherited_from_id: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `position: float | None`
    :   The type of the None singleton.

    `team: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="WorkflowStatesSearchQuery"></a>

`WorkflowStatesSearchQuery(*args, **kwargs)`
:   Search query for workflow_states entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.linear.types.WorkflowStatesEqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNeqCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesGteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLtCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLteCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesInCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesLikeCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesFuzzyCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesKeywordCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesContainsCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesNotCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAndCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesOrCondition | airbyte_agent_sdk.connectors.linear.types.WorkflowStatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.linear.types.WorkflowStatesSortFilter]`
    :   The type of the None singleton.

<a id="WorkflowStatesSortFilter"></a>

`WorkflowStatesSortFilter(*args, **kwargs)`
:   Available fields for sorting workflow_states search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `created_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `description: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `inherited_from_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `name: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `position: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `team_id: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `type_: Literal['asc', 'desc']`
    :   The type of the None singleton.

    `updated_at: Literal['asc', 'desc']`
    :   The type of the None singleton.

<a id="WorkflowStatesStringFilter"></a>

`WorkflowStatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `color: str`
    :   The type of the None singleton.

    `created_at: str`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `inherited_from_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `position: str`
    :   The type of the None singleton.

    `team: str`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

    `type_: str`
    :   The type of the None singleton.

    `updated_at: str`
    :   The type of the None singleton.