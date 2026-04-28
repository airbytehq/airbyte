---
id: airbyte_agent_sdk-connectors-jira-types
title: airbyte_agent_sdk.connectors.jira.types
---

Module airbyte_agent_sdk.connectors.jira.types
==============================================
Type definitions for jira connector.

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

<a id="IssueCommentsAndCondition"></a>

`IssueCommentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAnyCondition]`
    :   The type of the None singleton.

<a id="IssueCommentsAnyCondition"></a>

`IssueCommentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.jira.types.IssueCommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="IssueCommentsAnyValueFilter"></a>

`IssueCommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: Any`
    :   The ID of the user who created the comment

    `body: Any`
    :   The comment text in Atlassian Document Format

    `created: Any`
    :   The date and time at which the comment was created

    `id: Any`
    :   The ID of the comment

    `issue_id: Any`
    :   Id of the related issue

    `jsd_public: Any`
    :   Whether the comment is visible in Jira Service Desk

    `properties: Any`
    :   A list of comment properties

    `rendered_body: Any`
    :   The rendered version of the comment

    `self: Any`
    :   The URL of the comment

    `update_author: Any`
    :   The ID of the user who updated the comment last

    `updated: Any`
    :   The date and time at which the comment was updated last

    `visibility: Any`
    :   The group or role to which this item is visible

<a id="IssueCommentsContainsCondition"></a>

`IssueCommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.jira.types.IssueCommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="IssueCommentsCreateParams"></a>

`IssueCommentsCreateParams(*args, **kwargs)`
:   Parameters for issue_comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: airbyte_agent_sdk.connectors.jira.types.IssueCommentsCreateParamsBody`
    :   The type of the None singleton.

    `expand: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `properties: list[dict[str, typing.Any]]`
    :   The type of the None singleton.

    `visibility: airbyte_agent_sdk.connectors.jira.types.IssueCommentsCreateParamsVisibility`
    :   The type of the None singleton.

<a id="IssueCommentsCreateParamsBody"></a>

`IssueCommentsCreateParamsBody(*args, **kwargs)`
:   Comment content in Atlassian Document Format (ADF)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsCreateParamsBodyContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `version: int`
    :   The type of the None singleton.

<a id="IssueCommentsCreateParamsBodyContentItem"></a>

`IssueCommentsCreateParamsBodyContentItem(*args, **kwargs)`
:   Nested schema for IssueCommentsCreateParamsBody.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsCreateParamsBodyContentItemContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssueCommentsCreateParamsBodyContentItemContentItem"></a>

`IssueCommentsCreateParamsBodyContentItemContentItem(*args, **kwargs)`
:   Nested schema for IssueCommentsCreateParamsBodyContentItem.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `text: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssueCommentsCreateParamsVisibility"></a>

`IssueCommentsCreateParamsVisibility(*args, **kwargs)`
:   Restrict comment visibility to a group or role

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `identifier: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="IssueCommentsDeleteParams"></a>

`IssueCommentsDeleteParams(*args, **kwargs)`
:   Parameters for issue_comments.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

<a id="IssueCommentsEqCondition"></a>

`IssueCommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.jira.types.IssueCommentsSearchFilter`
    :   The type of the None singleton.

<a id="IssueCommentsFuzzyCondition"></a>

`IssueCommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.jira.types.IssueCommentsStringFilter`
    :   The type of the None singleton.

<a id="IssueCommentsGetParams"></a>

`IssueCommentsGetParams(*args, **kwargs)`
:   Parameters for issue_comments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment_id: str`
    :   The type of the None singleton.

    `expand: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

<a id="IssueCommentsGtCondition"></a>

`IssueCommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.jira.types.IssueCommentsSearchFilter`
    :   The type of the None singleton.

<a id="IssueCommentsGteCondition"></a>

`IssueCommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.jira.types.IssueCommentsSearchFilter`
    :   The type of the None singleton.

<a id="IssueCommentsInCondition"></a>

`IssueCommentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.jira.types.IssueCommentsInFilter`
    :   The type of the None singleton.

<a id="IssueCommentsInFilter"></a>

`IssueCommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: list[dict[str, typing.Any]]`
    :   The ID of the user who created the comment

    `body: list[dict[str, typing.Any]]`
    :   The comment text in Atlassian Document Format

    `created: list[str]`
    :   The date and time at which the comment was created

    `id: list[str]`
    :   The ID of the comment

    `issue_id: list[str]`
    :   Id of the related issue

    `jsd_public: list[bool]`
    :   Whether the comment is visible in Jira Service Desk

    `properties: list[list[typing.Any]]`
    :   A list of comment properties

    `rendered_body: list[str]`
    :   The rendered version of the comment

    `self: list[str]`
    :   The URL of the comment

    `update_author: list[dict[str, typing.Any]]`
    :   The ID of the user who updated the comment last

    `updated: list[str]`
    :   The date and time at which the comment was updated last

    `visibility: list[dict[str, typing.Any]]`
    :   The group or role to which this item is visible

<a id="IssueCommentsKeywordCondition"></a>

`IssueCommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.jira.types.IssueCommentsStringFilter`
    :   The type of the None singleton.

<a id="IssueCommentsLikeCondition"></a>

`IssueCommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.jira.types.IssueCommentsStringFilter`
    :   The type of the None singleton.

<a id="IssueCommentsListParams"></a>

`IssueCommentsListParams(*args, **kwargs)`
:   Parameters for issue_comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `start_at: int`
    :   The type of the None singleton.

<a id="IssueCommentsLtCondition"></a>

`IssueCommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.jira.types.IssueCommentsSearchFilter`
    :   The type of the None singleton.

<a id="IssueCommentsLteCondition"></a>

`IssueCommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.jira.types.IssueCommentsSearchFilter`
    :   The type of the None singleton.

<a id="IssueCommentsNeqCondition"></a>

`IssueCommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.jira.types.IssueCommentsSearchFilter`
    :   The type of the None singleton.

<a id="IssueCommentsNotCondition"></a>

`IssueCommentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.jira.types.IssueCommentsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAnyCondition`
    :   The type of the None singleton.

<a id="IssueCommentsOrCondition"></a>

`IssueCommentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAnyCondition]`
    :   The type of the None singleton.

<a id="IssueCommentsSearchFilter"></a>

`IssueCommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering issue_comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: dict[str, typing.Any] | None`
    :   The ID of the user who created the comment

    `body: dict[str, typing.Any]`
    :   The comment text in Atlassian Document Format

    `created: str`
    :   The date and time at which the comment was created

    `id: str`
    :   The ID of the comment

    `issue_id: str | None`
    :   Id of the related issue

    `jsd_public: bool`
    :   Whether the comment is visible in Jira Service Desk

    `properties: list[typing.Any]`
    :   A list of comment properties

    `rendered_body: str | None`
    :   The rendered version of the comment

    `self: str`
    :   The URL of the comment

    `update_author: dict[str, typing.Any] | None`
    :   The ID of the user who updated the comment last

    `updated: str`
    :   The date and time at which the comment was updated last

    `visibility: dict[str, typing.Any] | None`
    :   The group or role to which this item is visible

<a id="IssueCommentsSearchQuery"></a>

`IssueCommentsSearchQuery(*args, **kwargs)`
:   Search query for issue_comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.jira.types.IssueCommentsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueCommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsSortFilter]`
    :   The type of the None singleton.

<a id="IssueCommentsSortFilter"></a>

`IssueCommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting issue_comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: Literal['asc', 'desc']`
    :   The ID of the user who created the comment

    `body: Literal['asc', 'desc']`
    :   The comment text in Atlassian Document Format

    `created: Literal['asc', 'desc']`
    :   The date and time at which the comment was created

    `id: Literal['asc', 'desc']`
    :   The ID of the comment

    `issue_id: Literal['asc', 'desc']`
    :   Id of the related issue

    `jsd_public: Literal['asc', 'desc']`
    :   Whether the comment is visible in Jira Service Desk

    `properties: Literal['asc', 'desc']`
    :   A list of comment properties

    `rendered_body: Literal['asc', 'desc']`
    :   The rendered version of the comment

    `self: Literal['asc', 'desc']`
    :   The URL of the comment

    `update_author: Literal['asc', 'desc']`
    :   The ID of the user who updated the comment last

    `updated: Literal['asc', 'desc']`
    :   The date and time at which the comment was updated last

    `visibility: Literal['asc', 'desc']`
    :   The group or role to which this item is visible

<a id="IssueCommentsStringFilter"></a>

`IssueCommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: str`
    :   The ID of the user who created the comment

    `body: str`
    :   The comment text in Atlassian Document Format

    `created: str`
    :   The date and time at which the comment was created

    `id: str`
    :   The ID of the comment

    `issue_id: str`
    :   Id of the related issue

    `jsd_public: str`
    :   Whether the comment is visible in Jira Service Desk

    `properties: str`
    :   A list of comment properties

    `rendered_body: str`
    :   The rendered version of the comment

    `self: str`
    :   The URL of the comment

    `update_author: str`
    :   The ID of the user who updated the comment last

    `updated: str`
    :   The date and time at which the comment was updated last

    `visibility: str`
    :   The group or role to which this item is visible

<a id="IssueCommentsUpdateParams"></a>

`IssueCommentsUpdateParams(*args, **kwargs)`
:   Parameters for issue_comments.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: airbyte_agent_sdk.connectors.jira.types.IssueCommentsUpdateParamsBody`
    :   The type of the None singleton.

    `comment_id: str`
    :   The type of the None singleton.

    `expand: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `notify_users: bool`
    :   The type of the None singleton.

    `visibility: airbyte_agent_sdk.connectors.jira.types.IssueCommentsUpdateParamsVisibility`
    :   The type of the None singleton.

<a id="IssueCommentsUpdateParamsBody"></a>

`IssueCommentsUpdateParamsBody(*args, **kwargs)`
:   Updated comment content in Atlassian Document Format (ADF)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsUpdateParamsBodyContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `version: int`
    :   The type of the None singleton.

<a id="IssueCommentsUpdateParamsBodyContentItem"></a>

`IssueCommentsUpdateParamsBodyContentItem(*args, **kwargs)`
:   Nested schema for IssueCommentsUpdateParamsBody.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssueCommentsUpdateParamsBodyContentItemContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssueCommentsUpdateParamsBodyContentItemContentItem"></a>

`IssueCommentsUpdateParamsBodyContentItemContentItem(*args, **kwargs)`
:   Nested schema for IssueCommentsUpdateParamsBodyContentItem.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `text: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssueCommentsUpdateParamsVisibility"></a>

`IssueCommentsUpdateParamsVisibility(*args, **kwargs)`
:   Restrict comment visibility to a group or role

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `identifier: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="IssueFieldsAndCondition"></a>

`IssueFieldsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.jira.types.IssueFieldsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="IssueFieldsAnyCondition"></a>

`IssueFieldsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.jira.types.IssueFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="IssueFieldsAnyValueFilter"></a>

`IssueFieldsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clause_names: Any`
    :   The names that can be used to reference the field in an advanced search

    `custom: Any`
    :   Whether the field is a custom field

    `id: Any`
    :   The ID of the field

    `key: Any`
    :   The key of the field

    `name: Any`
    :   The name of the field

    `navigable: Any`
    :   Whether the field can be used as a column on the issue navigator

    `orderable: Any`
    :   Whether the content of the field can be used to order lists

    `schema_: Any`
    :   The data schema for the field

    `scope: Any`
    :   The scope of the field

    `searchable: Any`
    :   Whether the content of the field can be searched

    `untranslated_name: Any`
    :   The untranslated name of the field

<a id="IssueFieldsApiSearchParams"></a>

`IssueFieldsApiSearchParams(*args, **kwargs)`
:   Parameters for issue_fields.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `id: list[str]`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `start_at: int`
    :   The type of the None singleton.

    `type: list[str]`
    :   The type of the None singleton.

<a id="IssueFieldsContainsCondition"></a>

`IssueFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.jira.types.IssueFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="IssueFieldsEqCondition"></a>

`IssueFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.jira.types.IssueFieldsSearchFilter`
    :   The type of the None singleton.

<a id="IssueFieldsFuzzyCondition"></a>

`IssueFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.jira.types.IssueFieldsStringFilter`
    :   The type of the None singleton.

<a id="IssueFieldsGtCondition"></a>

`IssueFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.jira.types.IssueFieldsSearchFilter`
    :   The type of the None singleton.

<a id="IssueFieldsGteCondition"></a>

`IssueFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.jira.types.IssueFieldsSearchFilter`
    :   The type of the None singleton.

<a id="IssueFieldsInCondition"></a>

`IssueFieldsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.jira.types.IssueFieldsInFilter`
    :   The type of the None singleton.

<a id="IssueFieldsInFilter"></a>

`IssueFieldsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clause_names: list[list[typing.Any]]`
    :   The names that can be used to reference the field in an advanced search

    `custom: list[bool]`
    :   Whether the field is a custom field

    `id: list[str]`
    :   The ID of the field

    `key: list[str]`
    :   The key of the field

    `name: list[str]`
    :   The name of the field

    `navigable: list[bool]`
    :   Whether the field can be used as a column on the issue navigator

    `orderable: list[bool]`
    :   Whether the content of the field can be used to order lists

    `schema_: list[dict[str, typing.Any]]`
    :   The data schema for the field

    `scope: list[dict[str, typing.Any]]`
    :   The scope of the field

    `searchable: list[bool]`
    :   Whether the content of the field can be searched

    `untranslated_name: list[str]`
    :   The untranslated name of the field

<a id="IssueFieldsKeywordCondition"></a>

`IssueFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.jira.types.IssueFieldsStringFilter`
    :   The type of the None singleton.

<a id="IssueFieldsLikeCondition"></a>

`IssueFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.jira.types.IssueFieldsStringFilter`
    :   The type of the None singleton.

<a id="IssueFieldsListParams"></a>

`IssueFieldsListParams(*args, **kwargs)`
:   Parameters for issue_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="IssueFieldsLtCondition"></a>

`IssueFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.jira.types.IssueFieldsSearchFilter`
    :   The type of the None singleton.

<a id="IssueFieldsLteCondition"></a>

`IssueFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.jira.types.IssueFieldsSearchFilter`
    :   The type of the None singleton.

<a id="IssueFieldsNeqCondition"></a>

`IssueFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.jira.types.IssueFieldsSearchFilter`
    :   The type of the None singleton.

<a id="IssueFieldsNotCondition"></a>

`IssueFieldsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.jira.types.IssueFieldsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAnyCondition`
    :   The type of the None singleton.

<a id="IssueFieldsOrCondition"></a>

`IssueFieldsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.jira.types.IssueFieldsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="IssueFieldsSearchFilter"></a>

`IssueFieldsSearchFilter(*args, **kwargs)`
:   Available fields for filtering issue_fields search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clause_names: list[typing.Any]`
    :   The names that can be used to reference the field in an advanced search

    `custom: bool`
    :   Whether the field is a custom field

    `id: str`
    :   The ID of the field

    `key: str | None`
    :   The key of the field

    `name: str`
    :   The name of the field

    `navigable: bool`
    :   Whether the field can be used as a column on the issue navigator

    `orderable: bool`
    :   Whether the content of the field can be used to order lists

    `schema_: dict[str, typing.Any] | None`
    :   The data schema for the field

    `scope: dict[str, typing.Any] | None`
    :   The scope of the field

    `searchable: bool`
    :   Whether the content of the field can be searched

    `untranslated_name: str | None`
    :   The untranslated name of the field

<a id="IssueFieldsSearchQuery"></a>

`IssueFieldsSearchQuery(*args, **kwargs)`
:   Search query for issue_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.jira.types.IssueFieldsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.jira.types.IssueFieldsSortFilter]`
    :   The type of the None singleton.

<a id="IssueFieldsSortFilter"></a>

`IssueFieldsSortFilter(*args, **kwargs)`
:   Available fields for sorting issue_fields search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clause_names: Literal['asc', 'desc']`
    :   The names that can be used to reference the field in an advanced search

    `custom: Literal['asc', 'desc']`
    :   Whether the field is a custom field

    `id: Literal['asc', 'desc']`
    :   The ID of the field

    `key: Literal['asc', 'desc']`
    :   The key of the field

    `name: Literal['asc', 'desc']`
    :   The name of the field

    `navigable: Literal['asc', 'desc']`
    :   Whether the field can be used as a column on the issue navigator

    `orderable: Literal['asc', 'desc']`
    :   Whether the content of the field can be used to order lists

    `schema_: Literal['asc', 'desc']`
    :   The data schema for the field

    `scope: Literal['asc', 'desc']`
    :   The scope of the field

    `searchable: Literal['asc', 'desc']`
    :   Whether the content of the field can be searched

    `untranslated_name: Literal['asc', 'desc']`
    :   The untranslated name of the field

<a id="IssueFieldsStringFilter"></a>

`IssueFieldsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `clause_names: str`
    :   The names that can be used to reference the field in an advanced search

    `custom: str`
    :   Whether the field is a custom field

    `id: str`
    :   The ID of the field

    `key: str`
    :   The key of the field

    `name: str`
    :   The name of the field

    `navigable: str`
    :   Whether the field can be used as a column on the issue navigator

    `orderable: str`
    :   Whether the content of the field can be used to order lists

    `schema_: str`
    :   The data schema for the field

    `scope: str`
    :   The scope of the field

    `searchable: str`
    :   Whether the content of the field can be searched

    `untranslated_name: str`
    :   The untranslated name of the field

<a id="IssueWorklogsAndCondition"></a>

`IssueWorklogsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.jira.types.IssueWorklogsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAnyCondition]`
    :   The type of the None singleton.

<a id="IssueWorklogsAnyCondition"></a>

`IssueWorklogsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAnyValueFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsAnyValueFilter"></a>

`IssueWorklogsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: Any`
    :   Details of the user who created the worklog

    `comment: Any`
    :   A comment about the worklog in Atlassian Document Format

    `created: Any`
    :   The datetime on which the worklog was created

    `id: Any`
    :   The ID of the worklog record

    `issue_id: Any`
    :   The ID of the issue this worklog is for

    `properties: Any`
    :   Details of properties for the worklog

    `self: Any`
    :   The URL of the worklog item

    `started: Any`
    :   The datetime on which the worklog effort was started

    `time_spent: Any`
    :   The time spent working on the issue as days, hours, or minutes

    `time_spent_seconds: Any`
    :   The time in seconds spent working on the issue

    `update_author: Any`
    :   Details of the user who last updated the worklog

    `updated: Any`
    :   The datetime on which the worklog was last updated

    `visibility: Any`
    :   Details about any restrictions in the visibility of the worklog

<a id="IssueWorklogsContainsCondition"></a>

`IssueWorklogsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAnyValueFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsEqCondition"></a>

`IssueWorklogsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSearchFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsFuzzyCondition"></a>

`IssueWorklogsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsStringFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsGetParams"></a>

`IssueWorklogsGetParams(*args, **kwargs)`
:   Parameters for issue_worklogs.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `worklog_id: str`
    :   The type of the None singleton.

<a id="IssueWorklogsGtCondition"></a>

`IssueWorklogsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSearchFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsGteCondition"></a>

`IssueWorklogsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSearchFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsInCondition"></a>

`IssueWorklogsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsInFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsInFilter"></a>

`IssueWorklogsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: list[dict[str, typing.Any]]`
    :   Details of the user who created the worklog

    `comment: list[dict[str, typing.Any]]`
    :   A comment about the worklog in Atlassian Document Format

    `created: list[str]`
    :   The datetime on which the worklog was created

    `id: list[str]`
    :   The ID of the worklog record

    `issue_id: list[str]`
    :   The ID of the issue this worklog is for

    `properties: list[list[typing.Any]]`
    :   Details of properties for the worklog

    `self: list[str]`
    :   The URL of the worklog item

    `started: list[str]`
    :   The datetime on which the worklog effort was started

    `time_spent: list[str]`
    :   The time spent working on the issue as days, hours, or minutes

    `time_spent_seconds: list[int]`
    :   The time in seconds spent working on the issue

    `update_author: list[dict[str, typing.Any]]`
    :   Details of the user who last updated the worklog

    `updated: list[str]`
    :   The datetime on which the worklog was last updated

    `visibility: list[dict[str, typing.Any]]`
    :   Details about any restrictions in the visibility of the worklog

<a id="IssueWorklogsKeywordCondition"></a>

`IssueWorklogsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsStringFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsLikeCondition"></a>

`IssueWorklogsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsStringFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsListParams"></a>

`IssueWorklogsListParams(*args, **kwargs)`
:   Parameters for issue_worklogs.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `start_at: int`
    :   The type of the None singleton.

<a id="IssueWorklogsLtCondition"></a>

`IssueWorklogsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSearchFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsLteCondition"></a>

`IssueWorklogsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSearchFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsNeqCondition"></a>

`IssueWorklogsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSearchFilter`
    :   The type of the None singleton.

<a id="IssueWorklogsNotCondition"></a>

`IssueWorklogsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAnyCondition`
    :   The type of the None singleton.

<a id="IssueWorklogsOrCondition"></a>

`IssueWorklogsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.jira.types.IssueWorklogsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAnyCondition]`
    :   The type of the None singleton.

<a id="IssueWorklogsSearchFilter"></a>

`IssueWorklogsSearchFilter(*args, **kwargs)`
:   Available fields for filtering issue_worklogs search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: dict[str, typing.Any]`
    :   Details of the user who created the worklog

    `comment: dict[str, typing.Any] | None`
    :   A comment about the worklog in Atlassian Document Format

    `created: str`
    :   The datetime on which the worklog was created

    `id: str`
    :   The ID of the worklog record

    `issue_id: str`
    :   The ID of the issue this worklog is for

    `properties: list[typing.Any]`
    :   Details of properties for the worklog

    `self: str`
    :   The URL of the worklog item

    `started: str`
    :   The datetime on which the worklog effort was started

    `time_spent: str | None`
    :   The time spent working on the issue as days, hours, or minutes

    `time_spent_seconds: int`
    :   The time in seconds spent working on the issue

    `update_author: dict[str, typing.Any] | None`
    :   Details of the user who last updated the worklog

    `updated: str`
    :   The datetime on which the worklog was last updated

    `visibility: dict[str, typing.Any] | None`
    :   Details about any restrictions in the visibility of the worklog

<a id="IssueWorklogsSearchQuery"></a>

`IssueWorklogsSearchQuery(*args, **kwargs)`
:   Search query for issue_worklogs entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.jira.types.IssueWorklogsEqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsGteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLtCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLteCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsInCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsNotCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAndCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsOrCondition | airbyte_agent_sdk.connectors.jira.types.IssueWorklogsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.jira.types.IssueWorklogsSortFilter]`
    :   The type of the None singleton.

<a id="IssueWorklogsSortFilter"></a>

`IssueWorklogsSortFilter(*args, **kwargs)`
:   Available fields for sorting issue_worklogs search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: Literal['asc', 'desc']`
    :   Details of the user who created the worklog

    `comment: Literal['asc', 'desc']`
    :   A comment about the worklog in Atlassian Document Format

    `created: Literal['asc', 'desc']`
    :   The datetime on which the worklog was created

    `id: Literal['asc', 'desc']`
    :   The ID of the worklog record

    `issue_id: Literal['asc', 'desc']`
    :   The ID of the issue this worklog is for

    `properties: Literal['asc', 'desc']`
    :   Details of properties for the worklog

    `self: Literal['asc', 'desc']`
    :   The URL of the worklog item

    `started: Literal['asc', 'desc']`
    :   The datetime on which the worklog effort was started

    `time_spent: Literal['asc', 'desc']`
    :   The time spent working on the issue as days, hours, or minutes

    `time_spent_seconds: Literal['asc', 'desc']`
    :   The time in seconds spent working on the issue

    `update_author: Literal['asc', 'desc']`
    :   Details of the user who last updated the worklog

    `updated: Literal['asc', 'desc']`
    :   The datetime on which the worklog was last updated

    `visibility: Literal['asc', 'desc']`
    :   Details about any restrictions in the visibility of the worklog

<a id="IssueWorklogsStringFilter"></a>

`IssueWorklogsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author: str`
    :   Details of the user who created the worklog

    `comment: str`
    :   A comment about the worklog in Atlassian Document Format

    `created: str`
    :   The datetime on which the worklog was created

    `id: str`
    :   The ID of the worklog record

    `issue_id: str`
    :   The ID of the issue this worklog is for

    `properties: str`
    :   Details of properties for the worklog

    `self: str`
    :   The URL of the worklog item

    `started: str`
    :   The datetime on which the worklog effort was started

    `time_spent: str`
    :   The time spent working on the issue as days, hours, or minutes

    `time_spent_seconds: str`
    :   The time in seconds spent working on the issue

    `update_author: str`
    :   Details of the user who last updated the worklog

    `updated: str`
    :   The datetime on which the worklog was last updated

    `visibility: str`
    :   Details about any restrictions in the visibility of the worklog

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

    `and: list[airbyte_agent_sdk.connectors.jira.types.IssuesEqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesInCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNotCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAndCondition | airbyte_agent_sdk.connectors.jira.types.IssuesOrCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.jira.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesAnyValueFilter"></a>

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `changelog: Any`
    :   Details of changelogs associated with the issue

    `created: Any`
    :   The timestamp when the issue was created

    `editmeta: Any`
    :   The metadata for the fields on the issue that can be amended

    `expand: Any`
    :   Expand options that include additional issue details in the response

    `fields: Any`
    :   Details of various fields associated with the issue

    `fields_to_include: Any`
    :   Specify the fields to include in the fetched issues data

    `id: Any`
    :   The unique ID of the issue

    `key: Any`
    :   The unique key of the issue

    `names: Any`
    :   The ID and name of each field present on the issue

    `operations: Any`
    :   The operations that can be performed on the issue

    `project_id: Any`
    :   The ID of the project containing the issue

    `project_key: Any`
    :   The key of the project containing the issue

    `properties: Any`
    :   Details of the issue properties identified in the request

    `rendered_fields: Any`
    :   The rendered value of each field present on the issue

    `schema_: Any`
    :   The schema describing each field present on the issue

    `self: Any`
    :   The URL of the issue details

    `transitions: Any`
    :   The transitions that can be performed on the issue

    `updated: Any`
    :   The timestamp when the issue was last updated

    `versioned_representations: Any`
    :   The versions of each field on the issue

<a id="IssuesApiSearchParams"></a>

`IssuesApiSearchParams(*args, **kwargs)`
:   Parameters for issues.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `fail_fast: bool`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `fields_by_keys: bool`
    :   The type of the None singleton.

    `jql: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `next_page_token: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

<a id="IssuesAssigneeUpdateParams"></a>

`IssuesAssigneeUpdateParams(*args, **kwargs)`
:   Parameters for issues_assignee.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

<a id="IssuesContainsCondition"></a>

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.jira.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesCreateParams"></a>

`IssuesCreateParams(*args, **kwargs)`
:   Parameters for issues.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFields`
    :   The type of the None singleton.

    `update_history: bool`
    :   The type of the None singleton.

    ### Methods

    `update(...) ‑> dict[str, typing.Any]`
    :   D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E.keys(): D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]

<a id="IssuesCreateParamsFields"></a>

`IssuesCreateParamsFields(*args, **kwargs)`
:   The issue fields to set

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsAssignee`
    :   The type of the None singleton.

    `description: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsDescription`
    :   The type of the None singleton.

    `issuetype: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsIssuetype`
    :   The type of the None singleton.

    `labels: list[str]`
    :   The type of the None singleton.

    `parent: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsParent`
    :   The type of the None singleton.

    `priority: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsPriority`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsProject`
    :   The type of the None singleton.

    `summary: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsAssignee"></a>

`IssuesCreateParamsFieldsAssignee(*args, **kwargs)`
:   The user to assign the issue to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accountId: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsDescription"></a>

`IssuesCreateParamsFieldsDescription(*args, **kwargs)`
:   Issue description in Atlassian Document Format (ADF)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsDescriptionContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `version: int`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsDescriptionContentItem"></a>

`IssuesCreateParamsFieldsDescriptionContentItem(*args, **kwargs)`
:   Nested schema for IssuesCreateParamsFieldsDescription.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssuesCreateParamsFieldsDescriptionContentItemContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsDescriptionContentItemContentItem"></a>

`IssuesCreateParamsFieldsDescriptionContentItemContentItem(*args, **kwargs)`
:   Nested schema for IssuesCreateParamsFieldsDescriptionContentItem.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `text: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsIssuetype"></a>

`IssuesCreateParamsFieldsIssuetype(*args, **kwargs)`
:   The type of issue (e.g., Bug, Task, Story)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsParent"></a>

`IssuesCreateParamsFieldsParent(*args, **kwargs)`
:   Parent issue for subtasks

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `key: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsPriority"></a>

`IssuesCreateParamsFieldsPriority(*args, **kwargs)`
:   Issue priority

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="IssuesCreateParamsFieldsProject"></a>

`IssuesCreateParamsFieldsProject(*args, **kwargs)`
:   The project to create the issue in

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `key: str`
    :   The type of the None singleton.

<a id="IssuesDeleteParams"></a>

`IssuesDeleteParams(*args, **kwargs)`
:   Parameters for issues.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `delete_subtasks: bool`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

<a id="IssuesEqCondition"></a>

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.jira.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesFuzzyCondition"></a>

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.jira.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesGetParams"></a>

`IssuesGetParams(*args, **kwargs)`
:   Parameters for issues.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `fail_fast: bool`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `fields_by_keys: bool`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

    `update_history: bool`
    :   The type of the None singleton.

<a id="IssuesGtCondition"></a>

`IssuesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.jira.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesGteCondition"></a>

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.jira.types.IssuesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.jira.types.IssuesInFilter`
    :   The type of the None singleton.

<a id="IssuesInFilter"></a>

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `changelog: list[dict[str, typing.Any]]`
    :   Details of changelogs associated with the issue

    `created: list[str]`
    :   The timestamp when the issue was created

    `editmeta: list[dict[str, typing.Any]]`
    :   The metadata for the fields on the issue that can be amended

    `expand: list[str]`
    :   Expand options that include additional issue details in the response

    `fields: list[dict[str, typing.Any]]`
    :   Details of various fields associated with the issue

    `fields_to_include: list[dict[str, typing.Any]]`
    :   Specify the fields to include in the fetched issues data

    `id: list[str]`
    :   The unique ID of the issue

    `key: list[str]`
    :   The unique key of the issue

    `names: list[dict[str, typing.Any]]`
    :   The ID and name of each field present on the issue

    `operations: list[dict[str, typing.Any]]`
    :   The operations that can be performed on the issue

    `project_id: list[str]`
    :   The ID of the project containing the issue

    `project_key: list[str]`
    :   The key of the project containing the issue

    `properties: list[dict[str, typing.Any]]`
    :   Details of the issue properties identified in the request

    `rendered_fields: list[dict[str, typing.Any]]`
    :   The rendered value of each field present on the issue

    `schema_: list[dict[str, typing.Any]]`
    :   The schema describing each field present on the issue

    `self: list[str]`
    :   The URL of the issue details

    `transitions: list[list[typing.Any]]`
    :   The transitions that can be performed on the issue

    `updated: list[str]`
    :   The timestamp when the issue was last updated

    `versioned_representations: list[dict[str, typing.Any]]`
    :   The versions of each field on the issue

<a id="IssuesKeywordCondition"></a>

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.jira.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLikeCondition"></a>

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.jira.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLtCondition"></a>

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.jira.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesLteCondition"></a>

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.jira.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNeqCondition"></a>

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.jira.types.IssuesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.jira.types.IssuesEqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesInCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNotCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAndCondition | airbyte_agent_sdk.connectors.jira.types.IssuesOrCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.jira.types.IssuesEqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesInCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNotCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAndCondition | airbyte_agent_sdk.connectors.jira.types.IssuesOrCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesSearchFilter"></a>

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `changelog: dict[str, typing.Any] | None`
    :   Details of changelogs associated with the issue

    `created: str | None`
    :   The timestamp when the issue was created

    `editmeta: dict[str, typing.Any] | None`
    :   The metadata for the fields on the issue that can be amended

    `expand: str`
    :   Expand options that include additional issue details in the response

    `fields: dict[str, typing.Any]`
    :   Details of various fields associated with the issue

    `fields_to_include: dict[str, typing.Any]`
    :   Specify the fields to include in the fetched issues data

    `id: str`
    :   The unique ID of the issue

    `key: str`
    :   The unique key of the issue

    `names: dict[str, typing.Any]`
    :   The ID and name of each field present on the issue

    `operations: dict[str, typing.Any] | None`
    :   The operations that can be performed on the issue

    `project_id: str`
    :   The ID of the project containing the issue

    `project_key: str`
    :   The key of the project containing the issue

    `properties: dict[str, typing.Any]`
    :   Details of the issue properties identified in the request

    `rendered_fields: dict[str, typing.Any]`
    :   The rendered value of each field present on the issue

    `schema_: dict[str, typing.Any]`
    :   The schema describing each field present on the issue

    `self: str`
    :   The URL of the issue details

    `transitions: list[typing.Any]`
    :   The transitions that can be performed on the issue

    `updated: str | None`
    :   The timestamp when the issue was last updated

    `versioned_representations: dict[str, typing.Any]`
    :   The versions of each field on the issue

<a id="IssuesSearchQuery"></a>

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.jira.types.IssuesEqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesGteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLtCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLteCondition | airbyte_agent_sdk.connectors.jira.types.IssuesInCondition | airbyte_agent_sdk.connectors.jira.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.jira.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.jira.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.jira.types.IssuesNotCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAndCondition | airbyte_agent_sdk.connectors.jira.types.IssuesOrCondition | airbyte_agent_sdk.connectors.jira.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.jira.types.IssuesSortFilter]`
    :   The type of the None singleton.

<a id="IssuesSortFilter"></a>

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `changelog: Literal['asc', 'desc']`
    :   Details of changelogs associated with the issue

    `created: Literal['asc', 'desc']`
    :   The timestamp when the issue was created

    `editmeta: Literal['asc', 'desc']`
    :   The metadata for the fields on the issue that can be amended

    `expand: Literal['asc', 'desc']`
    :   Expand options that include additional issue details in the response

    `fields: Literal['asc', 'desc']`
    :   Details of various fields associated with the issue

    `fields_to_include: Literal['asc', 'desc']`
    :   Specify the fields to include in the fetched issues data

    `id: Literal['asc', 'desc']`
    :   The unique ID of the issue

    `key: Literal['asc', 'desc']`
    :   The unique key of the issue

    `names: Literal['asc', 'desc']`
    :   The ID and name of each field present on the issue

    `operations: Literal['asc', 'desc']`
    :   The operations that can be performed on the issue

    `project_id: Literal['asc', 'desc']`
    :   The ID of the project containing the issue

    `project_key: Literal['asc', 'desc']`
    :   The key of the project containing the issue

    `properties: Literal['asc', 'desc']`
    :   Details of the issue properties identified in the request

    `rendered_fields: Literal['asc', 'desc']`
    :   The rendered value of each field present on the issue

    `schema_: Literal['asc', 'desc']`
    :   The schema describing each field present on the issue

    `self: Literal['asc', 'desc']`
    :   The URL of the issue details

    `transitions: Literal['asc', 'desc']`
    :   The transitions that can be performed on the issue

    `updated: Literal['asc', 'desc']`
    :   The timestamp when the issue was last updated

    `versioned_representations: Literal['asc', 'desc']`
    :   The versions of each field on the issue

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `changelog: str`
    :   Details of changelogs associated with the issue

    `created: str`
    :   The timestamp when the issue was created

    `editmeta: str`
    :   The metadata for the fields on the issue that can be amended

    `expand: str`
    :   Expand options that include additional issue details in the response

    `fields: str`
    :   Details of various fields associated with the issue

    `fields_to_include: str`
    :   Specify the fields to include in the fetched issues data

    `id: str`
    :   The unique ID of the issue

    `key: str`
    :   The unique key of the issue

    `names: str`
    :   The ID and name of each field present on the issue

    `operations: str`
    :   The operations that can be performed on the issue

    `project_id: str`
    :   The ID of the project containing the issue

    `project_key: str`
    :   The key of the project containing the issue

    `properties: str`
    :   Details of the issue properties identified in the request

    `rendered_fields: str`
    :   The rendered value of each field present on the issue

    `schema_: str`
    :   The schema describing each field present on the issue

    `self: str`
    :   The URL of the issue details

    `transitions: str`
    :   The transitions that can be performed on the issue

    `updated: str`
    :   The timestamp when the issue was last updated

    `versioned_representations: str`
    :   The versions of each field on the issue

<a id="IssuesUpdateParams"></a>

`IssuesUpdateParams(*args, **kwargs)`
:   Parameters for issues.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `fields: airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsFields`
    :   The type of the None singleton.

    `issue_id_or_key: str`
    :   The type of the None singleton.

    `notify_users: bool`
    :   The type of the None singleton.

    `override_editable_flag: bool`
    :   The type of the None singleton.

    `override_screen_security: bool`
    :   The type of the None singleton.

    `return_issue: bool`
    :   The type of the None singleton.

    `transition: airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsTransition`
    :   The type of the None singleton.

    ### Methods

    `update(...) ‑> dict[str, typing.Any]`
    :   D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E.keys(): D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]

<a id="IssuesUpdateParamsFields"></a>

`IssuesUpdateParamsFields(*args, **kwargs)`
:   The issue fields to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee: airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsFieldsAssignee`
    :   The type of the None singleton.

    `description: airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsFieldsDescription`
    :   The type of the None singleton.

    `labels: list[str]`
    :   The type of the None singleton.

    `priority: airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsFieldsPriority`
    :   The type of the None singleton.

    `summary: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParamsFieldsAssignee"></a>

`IssuesUpdateParamsFieldsAssignee(*args, **kwargs)`
:   The user to assign the issue to

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accountId: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParamsFieldsDescription"></a>

`IssuesUpdateParamsFieldsDescription(*args, **kwargs)`
:   Issue description in Atlassian Document Format (ADF)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsFieldsDescriptionContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    `version: int`
    :   The type of the None singleton.

<a id="IssuesUpdateParamsFieldsDescriptionContentItem"></a>

`IssuesUpdateParamsFieldsDescriptionContentItem(*args, **kwargs)`
:   Nested schema for IssuesUpdateParamsFieldsDescription.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.types.IssuesUpdateParamsFieldsDescriptionContentItemContentItem]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParamsFieldsDescriptionContentItemContentItem"></a>

`IssuesUpdateParamsFieldsDescriptionContentItemContentItem(*args, **kwargs)`
:   Nested schema for IssuesUpdateParamsFieldsDescriptionContentItem.content_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `text: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParamsFieldsPriority"></a>

`IssuesUpdateParamsFieldsPriority(*args, **kwargs)`
:   Issue priority

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="IssuesUpdateParamsTransition"></a>

`IssuesUpdateParamsTransition(*args, **kwargs)`
:   Transition the issue to a new status

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
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

    `and: list[airbyte_agent_sdk.connectors.jira.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsInCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.jira.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsAnyValueFilter"></a>

`ProjectsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Any`
    :   Whether the project is archived

    `archived_by: Any`
    :   The user who archived the project

    `archived_date: Any`
    :   The date when the project was archived

    `assignee_type: Any`
    :   The default assignee when creating issues for this project

    `avatar_urls: Any`
    :   The URLs of the project's avatars

    `components: Any`
    :   List of the components contained in the project

    `deleted: Any`
    :   Whether the project is marked as deleted

    `deleted_by: Any`
    :   The user who marked the project as deleted

    `deleted_date: Any`
    :   The date when the project was marked as deleted

    `description: Any`
    :   A brief description of the project

    `email: Any`
    :   An email address associated with the project

    `entity_id: Any`
    :   The unique identifier of the project entity

    `expand: Any`
    :   Expand options that include additional project details in the response

    `favourite: Any`
    :   Whether the project is selected as a favorite

    `id: Any`
    :   The ID of the project

    `insight: Any`
    :   Insights about the project

    `is_private: Any`
    :   Whether the project is private

    `issue_type_hierarchy: Any`
    :   The issue type hierarchy for the project

    `issue_types: Any`
    :   List of the issue types available in the project

    `key: Any`
    :   The key of the project

    `lead: Any`
    :   The username of the project lead

    `name: Any`
    :   The name of the project

    `permissions: Any`
    :   User permissions on the project

    `project_category: Any`
    :   The category the project belongs to

    `project_type_key: Any`
    :   The project type of the project

    `properties: Any`
    :   Map of project properties

    `retention_till_date: Any`
    :   The date when the project is deleted permanently

    `roles: Any`
    :   The name and self URL for each role defined in the project

    `self: Any`
    :   The URL of the project details

    `simplified: Any`
    :   Whether the project is simplified

    `style: Any`
    :   The type of the project

    `url: Any`
    :   A link to information about this project

    `uuid: Any`
    :   Unique ID for next-gen projects

    `versions: Any`
    :   The versions defined in the project

<a id="ProjectsApiSearchParams"></a>

`ProjectsApiSearchParams(*args, **kwargs)`
:   Parameters for projects.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action: str`
    :   The type of the None singleton.

    `category_id: int`
    :   The type of the None singleton.

    `expand: str`
    :   The type of the None singleton.

    `id: list[int]`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `order_by: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `start_at: int`
    :   The type of the None singleton.

    `status: list[str]`
    :   The type of the None singleton.

    `type_key: str`
    :   The type of the None singleton.

    ### Methods

    `keys(self, /) ‑> list[str]`
    :   Return a set-like object providing a view on the dict's keys.

<a id="ProjectsContainsCondition"></a>

`ProjectsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.jira.types.ProjectsAnyValueFilter`
    :   The type of the None singleton.

<a id="ProjectsEqCondition"></a>

`ProjectsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.jira.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsFuzzyCondition"></a>

`ProjectsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.jira.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsGetParams"></a>

`ProjectsGetParams(*args, **kwargs)`
:   Parameters for projects.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `expand: str`
    :   The type of the None singleton.

    `project_id_or_key: str`
    :   The type of the None singleton.

    `properties: str`
    :   The type of the None singleton.

<a id="ProjectsGtCondition"></a>

`ProjectsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.jira.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsGteCondition"></a>

`ProjectsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.jira.types.ProjectsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.jira.types.ProjectsInFilter`
    :   The type of the None singleton.

<a id="ProjectsInFilter"></a>

`ProjectsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: list[bool]`
    :   Whether the project is archived

    `archived_by: list[dict[str, typing.Any]]`
    :   The user who archived the project

    `archived_date: list[str]`
    :   The date when the project was archived

    `assignee_type: list[str]`
    :   The default assignee when creating issues for this project

    `avatar_urls: list[dict[str, typing.Any]]`
    :   The URLs of the project's avatars

    `components: list[list[typing.Any]]`
    :   List of the components contained in the project

    `deleted: list[bool]`
    :   Whether the project is marked as deleted

    `deleted_by: list[dict[str, typing.Any]]`
    :   The user who marked the project as deleted

    `deleted_date: list[str]`
    :   The date when the project was marked as deleted

    `description: list[str]`
    :   A brief description of the project

    `email: list[str]`
    :   An email address associated with the project

    `entity_id: list[str]`
    :   The unique identifier of the project entity

    `expand: list[str]`
    :   Expand options that include additional project details in the response

    `favourite: list[bool]`
    :   Whether the project is selected as a favorite

    `id: list[str]`
    :   The ID of the project

    `insight: list[dict[str, typing.Any]]`
    :   Insights about the project

    `is_private: list[bool]`
    :   Whether the project is private

    `issue_type_hierarchy: list[dict[str, typing.Any]]`
    :   The issue type hierarchy for the project

    `issue_types: list[list[typing.Any]]`
    :   List of the issue types available in the project

    `key: list[str]`
    :   The key of the project

    `lead: list[dict[str, typing.Any]]`
    :   The username of the project lead

    `name: list[str]`
    :   The name of the project

    `permissions: list[dict[str, typing.Any]]`
    :   User permissions on the project

    `project_category: list[dict[str, typing.Any]]`
    :   The category the project belongs to

    `project_type_key: list[str]`
    :   The project type of the project

    `properties: list[dict[str, typing.Any]]`
    :   Map of project properties

    `retention_till_date: list[str]`
    :   The date when the project is deleted permanently

    `roles: list[dict[str, typing.Any]]`
    :   The name and self URL for each role defined in the project

    `self: list[str]`
    :   The URL of the project details

    `simplified: list[bool]`
    :   Whether the project is simplified

    `style: list[str]`
    :   The type of the project

    `url: list[str]`
    :   A link to information about this project

    `uuid: list[str]`
    :   Unique ID for next-gen projects

    `versions: list[list[typing.Any]]`
    :   The versions defined in the project

<a id="ProjectsKeywordCondition"></a>

`ProjectsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.jira.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsLikeCondition"></a>

`ProjectsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.jira.types.ProjectsStringFilter`
    :   The type of the None singleton.

<a id="ProjectsLtCondition"></a>

`ProjectsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.jira.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsLteCondition"></a>

`ProjectsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.jira.types.ProjectsSearchFilter`
    :   The type of the None singleton.

<a id="ProjectsNeqCondition"></a>

`ProjectsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.jira.types.ProjectsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.jira.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsInCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.jira.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsInCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAnyCondition]`
    :   The type of the None singleton.

<a id="ProjectsSearchFilter"></a>

`ProjectsSearchFilter(*args, **kwargs)`
:   Available fields for filtering projects search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: bool`
    :   Whether the project is archived

    `archived_by: dict[str, typing.Any] | None`
    :   The user who archived the project

    `archived_date: str | None`
    :   The date when the project was archived

    `assignee_type: str | None`
    :   The default assignee when creating issues for this project

    `avatar_urls: dict[str, typing.Any]`
    :   The URLs of the project's avatars

    `components: list[typing.Any]`
    :   List of the components contained in the project

    `deleted: bool`
    :   Whether the project is marked as deleted

    `deleted_by: dict[str, typing.Any] | None`
    :   The user who marked the project as deleted

    `deleted_date: str | None`
    :   The date when the project was marked as deleted

    `description: str | None`
    :   A brief description of the project

    `email: str | None`
    :   An email address associated with the project

    `entity_id: str | None`
    :   The unique identifier of the project entity

    `expand: str | None`
    :   Expand options that include additional project details in the response

    `favourite: bool`
    :   Whether the project is selected as a favorite

    `id: str`
    :   The ID of the project

    `insight: dict[str, typing.Any] | None`
    :   Insights about the project

    `is_private: bool`
    :   Whether the project is private

    `issue_type_hierarchy: dict[str, typing.Any] | None`
    :   The issue type hierarchy for the project

    `issue_types: list[typing.Any]`
    :   List of the issue types available in the project

    `key: str`
    :   The key of the project

    `lead: dict[str, typing.Any] | None`
    :   The username of the project lead

    `name: str`
    :   The name of the project

    `permissions: dict[str, typing.Any] | None`
    :   User permissions on the project

    `project_category: dict[str, typing.Any] | None`
    :   The category the project belongs to

    `project_type_key: str | None`
    :   The project type of the project

    `properties: dict[str, typing.Any]`
    :   Map of project properties

    `retention_till_date: str | None`
    :   The date when the project is deleted permanently

    `roles: dict[str, typing.Any]`
    :   The name and self URL for each role defined in the project

    `self: str`
    :   The URL of the project details

    `simplified: bool`
    :   Whether the project is simplified

    `style: str | None`
    :   The type of the project

    `url: str | None`
    :   A link to information about this project

    `uuid: str | None`
    :   Unique ID for next-gen projects

    `versions: list[typing.Any]`
    :   The versions defined in the project

<a id="ProjectsSearchQuery"></a>

`ProjectsSearchQuery(*args, **kwargs)`
:   Search query for projects entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.jira.types.ProjectsEqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNeqCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsGteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLtCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLteCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsInCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsLikeCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsKeywordCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsContainsCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsNotCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAndCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsOrCondition | airbyte_agent_sdk.connectors.jira.types.ProjectsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.jira.types.ProjectsSortFilter]`
    :   The type of the None singleton.

<a id="ProjectsSortFilter"></a>

`ProjectsSortFilter(*args, **kwargs)`
:   Available fields for sorting projects search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: Literal['asc', 'desc']`
    :   Whether the project is archived

    `archived_by: Literal['asc', 'desc']`
    :   The user who archived the project

    `archived_date: Literal['asc', 'desc']`
    :   The date when the project was archived

    `assignee_type: Literal['asc', 'desc']`
    :   The default assignee when creating issues for this project

    `avatar_urls: Literal['asc', 'desc']`
    :   The URLs of the project's avatars

    `components: Literal['asc', 'desc']`
    :   List of the components contained in the project

    `deleted: Literal['asc', 'desc']`
    :   Whether the project is marked as deleted

    `deleted_by: Literal['asc', 'desc']`
    :   The user who marked the project as deleted

    `deleted_date: Literal['asc', 'desc']`
    :   The date when the project was marked as deleted

    `description: Literal['asc', 'desc']`
    :   A brief description of the project

    `email: Literal['asc', 'desc']`
    :   An email address associated with the project

    `entity_id: Literal['asc', 'desc']`
    :   The unique identifier of the project entity

    `expand: Literal['asc', 'desc']`
    :   Expand options that include additional project details in the response

    `favourite: Literal['asc', 'desc']`
    :   Whether the project is selected as a favorite

    `id: Literal['asc', 'desc']`
    :   The ID of the project

    `insight: Literal['asc', 'desc']`
    :   Insights about the project

    `is_private: Literal['asc', 'desc']`
    :   Whether the project is private

    `issue_type_hierarchy: Literal['asc', 'desc']`
    :   The issue type hierarchy for the project

    `issue_types: Literal['asc', 'desc']`
    :   List of the issue types available in the project

    `key: Literal['asc', 'desc']`
    :   The key of the project

    `lead: Literal['asc', 'desc']`
    :   The username of the project lead

    `name: Literal['asc', 'desc']`
    :   The name of the project

    `permissions: Literal['asc', 'desc']`
    :   User permissions on the project

    `project_category: Literal['asc', 'desc']`
    :   The category the project belongs to

    `project_type_key: Literal['asc', 'desc']`
    :   The project type of the project

    `properties: Literal['asc', 'desc']`
    :   Map of project properties

    `retention_till_date: Literal['asc', 'desc']`
    :   The date when the project is deleted permanently

    `roles: Literal['asc', 'desc']`
    :   The name and self URL for each role defined in the project

    `self: Literal['asc', 'desc']`
    :   The URL of the project details

    `simplified: Literal['asc', 'desc']`
    :   Whether the project is simplified

    `style: Literal['asc', 'desc']`
    :   The type of the project

    `url: Literal['asc', 'desc']`
    :   A link to information about this project

    `uuid: Literal['asc', 'desc']`
    :   Unique ID for next-gen projects

    `versions: Literal['asc', 'desc']`
    :   The versions defined in the project

<a id="ProjectsStringFilter"></a>

`ProjectsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `archived: str`
    :   Whether the project is archived

    `archived_by: str`
    :   The user who archived the project

    `archived_date: str`
    :   The date when the project was archived

    `assignee_type: str`
    :   The default assignee when creating issues for this project

    `avatar_urls: str`
    :   The URLs of the project's avatars

    `components: str`
    :   List of the components contained in the project

    `deleted: str`
    :   Whether the project is marked as deleted

    `deleted_by: str`
    :   The user who marked the project as deleted

    `deleted_date: str`
    :   The date when the project was marked as deleted

    `description: str`
    :   A brief description of the project

    `email: str`
    :   An email address associated with the project

    `entity_id: str`
    :   The unique identifier of the project entity

    `expand: str`
    :   Expand options that include additional project details in the response

    `favourite: str`
    :   Whether the project is selected as a favorite

    `id: str`
    :   The ID of the project

    `insight: str`
    :   Insights about the project

    `is_private: str`
    :   Whether the project is private

    `issue_type_hierarchy: str`
    :   The issue type hierarchy for the project

    `issue_types: str`
    :   List of the issue types available in the project

    `key: str`
    :   The key of the project

    `lead: str`
    :   The username of the project lead

    `name: str`
    :   The name of the project

    `permissions: str`
    :   User permissions on the project

    `project_category: str`
    :   The category the project belongs to

    `project_type_key: str`
    :   The project type of the project

    `properties: str`
    :   Map of project properties

    `retention_till_date: str`
    :   The date when the project is deleted permanently

    `roles: str`
    :   The name and self URL for each role defined in the project

    `self: str`
    :   The URL of the project details

    `simplified: str`
    :   Whether the project is simplified

    `style: str`
    :   The type of the project

    `url: str`
    :   A link to information about this project

    `uuid: str`
    :   Unique ID for next-gen projects

    `versions: str`
    :   The versions defined in the project

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

    `and: list[airbyte_agent_sdk.connectors.jira.types.UsersEqCondition | airbyte_agent_sdk.connectors.jira.types.UsersNeqCondition | airbyte_agent_sdk.connectors.jira.types.UsersGtCondition | airbyte_agent_sdk.connectors.jira.types.UsersGteCondition | airbyte_agent_sdk.connectors.jira.types.UsersLtCondition | airbyte_agent_sdk.connectors.jira.types.UsersLteCondition | airbyte_agent_sdk.connectors.jira.types.UsersInCondition | airbyte_agent_sdk.connectors.jira.types.UsersLikeCondition | airbyte_agent_sdk.connectors.jira.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.jira.types.UsersContainsCondition | airbyte_agent_sdk.connectors.jira.types.UsersNotCondition | airbyte_agent_sdk.connectors.jira.types.UsersAndCondition | airbyte_agent_sdk.connectors.jira.types.UsersOrCondition | airbyte_agent_sdk.connectors.jira.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.jira.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   The account ID of the user, uniquely identifying the user across all Atlassian products

    `account_type: Any`
    :   The user account type (atlassian, app, or customer)

    `active: Any`
    :   Indicates whether the user is active

    `application_roles: Any`
    :   The application roles assigned to the user

    `avatar_urls: Any`
    :   The avatars of the user

    `display_name: Any`
    :   The display name of the user

    `email_address: Any`
    :   The email address of the user

    `expand: Any`
    :   Options to include additional user details in the response

    `groups: Any`
    :   The groups to which the user belongs

    `key: Any`
    :   Deprecated property

    `locale: Any`
    :   The locale of the user

    `name: Any`
    :   Deprecated property

    `self: Any`
    :   The URL of the user

    `time_zone: Any`
    :   The time zone specified in the user's profile

<a id="UsersApiSearchParams"></a>

`UsersApiSearchParams(*args, **kwargs)`
:   Parameters for users.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `max_results: int`
    :   The type of the None singleton.

    `property: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `start_at: int`
    :   The type of the None singleton.

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.jira.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.jira.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.jira.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `expand: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.jira.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.jira.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.jira.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   The account ID of the user, uniquely identifying the user across all Atlassian products

    `account_type: list[str]`
    :   The user account type (atlassian, app, or customer)

    `active: list[bool]`
    :   Indicates whether the user is active

    `application_roles: list[dict[str, typing.Any]]`
    :   The application roles assigned to the user

    `avatar_urls: list[dict[str, typing.Any]]`
    :   The avatars of the user

    `display_name: list[str]`
    :   The display name of the user

    `email_address: list[str]`
    :   The email address of the user

    `expand: list[str]`
    :   Options to include additional user details in the response

    `groups: list[dict[str, typing.Any]]`
    :   The groups to which the user belongs

    `key: list[str]`
    :   Deprecated property

    `locale: list[str]`
    :   The locale of the user

    `name: list[str]`
    :   Deprecated property

    `self: list[str]`
    :   The URL of the user

    `time_zone: list[str]`
    :   The time zone specified in the user's profile

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.jira.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.jira.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results: int`
    :   The type of the None singleton.

    `start_at: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.jira.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.jira.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.jira.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.jira.types.UsersEqCondition | airbyte_agent_sdk.connectors.jira.types.UsersNeqCondition | airbyte_agent_sdk.connectors.jira.types.UsersGtCondition | airbyte_agent_sdk.connectors.jira.types.UsersGteCondition | airbyte_agent_sdk.connectors.jira.types.UsersLtCondition | airbyte_agent_sdk.connectors.jira.types.UsersLteCondition | airbyte_agent_sdk.connectors.jira.types.UsersInCondition | airbyte_agent_sdk.connectors.jira.types.UsersLikeCondition | airbyte_agent_sdk.connectors.jira.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.jira.types.UsersContainsCondition | airbyte_agent_sdk.connectors.jira.types.UsersNotCondition | airbyte_agent_sdk.connectors.jira.types.UsersAndCondition | airbyte_agent_sdk.connectors.jira.types.UsersOrCondition | airbyte_agent_sdk.connectors.jira.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.jira.types.UsersEqCondition | airbyte_agent_sdk.connectors.jira.types.UsersNeqCondition | airbyte_agent_sdk.connectors.jira.types.UsersGtCondition | airbyte_agent_sdk.connectors.jira.types.UsersGteCondition | airbyte_agent_sdk.connectors.jira.types.UsersLtCondition | airbyte_agent_sdk.connectors.jira.types.UsersLteCondition | airbyte_agent_sdk.connectors.jira.types.UsersInCondition | airbyte_agent_sdk.connectors.jira.types.UsersLikeCondition | airbyte_agent_sdk.connectors.jira.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.jira.types.UsersContainsCondition | airbyte_agent_sdk.connectors.jira.types.UsersNotCondition | airbyte_agent_sdk.connectors.jira.types.UsersAndCondition | airbyte_agent_sdk.connectors.jira.types.UsersOrCondition | airbyte_agent_sdk.connectors.jira.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The account ID of the user, uniquely identifying the user across all Atlassian products

    `account_type: str | None`
    :   The user account type (atlassian, app, or customer)

    `active: bool`
    :   Indicates whether the user is active

    `application_roles: dict[str, typing.Any] | None`
    :   The application roles assigned to the user

    `avatar_urls: dict[str, typing.Any]`
    :   The avatars of the user

    `display_name: str | None`
    :   The display name of the user

    `email_address: str | None`
    :   The email address of the user

    `expand: str | None`
    :   Options to include additional user details in the response

    `groups: dict[str, typing.Any] | None`
    :   The groups to which the user belongs

    `key: str | None`
    :   Deprecated property

    `locale: str | None`
    :   The locale of the user

    `name: str | None`
    :   Deprecated property

    `self: str`
    :   The URL of the user

    `time_zone: str | None`
    :   The time zone specified in the user's profile

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.jira.types.UsersEqCondition | airbyte_agent_sdk.connectors.jira.types.UsersNeqCondition | airbyte_agent_sdk.connectors.jira.types.UsersGtCondition | airbyte_agent_sdk.connectors.jira.types.UsersGteCondition | airbyte_agent_sdk.connectors.jira.types.UsersLtCondition | airbyte_agent_sdk.connectors.jira.types.UsersLteCondition | airbyte_agent_sdk.connectors.jira.types.UsersInCondition | airbyte_agent_sdk.connectors.jira.types.UsersLikeCondition | airbyte_agent_sdk.connectors.jira.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.jira.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.jira.types.UsersContainsCondition | airbyte_agent_sdk.connectors.jira.types.UsersNotCondition | airbyte_agent_sdk.connectors.jira.types.UsersAndCondition | airbyte_agent_sdk.connectors.jira.types.UsersOrCondition | airbyte_agent_sdk.connectors.jira.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.jira.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   The account ID of the user, uniquely identifying the user across all Atlassian products

    `account_type: Literal['asc', 'desc']`
    :   The user account type (atlassian, app, or customer)

    `active: Literal['asc', 'desc']`
    :   Indicates whether the user is active

    `application_roles: Literal['asc', 'desc']`
    :   The application roles assigned to the user

    `avatar_urls: Literal['asc', 'desc']`
    :   The avatars of the user

    `display_name: Literal['asc', 'desc']`
    :   The display name of the user

    `email_address: Literal['asc', 'desc']`
    :   The email address of the user

    `expand: Literal['asc', 'desc']`
    :   Options to include additional user details in the response

    `groups: Literal['asc', 'desc']`
    :   The groups to which the user belongs

    `key: Literal['asc', 'desc']`
    :   Deprecated property

    `locale: Literal['asc', 'desc']`
    :   The locale of the user

    `name: Literal['asc', 'desc']`
    :   Deprecated property

    `self: Literal['asc', 'desc']`
    :   The URL of the user

    `time_zone: Literal['asc', 'desc']`
    :   The time zone specified in the user's profile

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The account ID of the user, uniquely identifying the user across all Atlassian products

    `account_type: str`
    :   The user account type (atlassian, app, or customer)

    `active: str`
    :   Indicates whether the user is active

    `application_roles: str`
    :   The application roles assigned to the user

    `avatar_urls: str`
    :   The avatars of the user

    `display_name: str`
    :   The display name of the user

    `email_address: str`
    :   The email address of the user

    `expand: str`
    :   Options to include additional user details in the response

    `groups: str`
    :   The groups to which the user belongs

    `key: str`
    :   Deprecated property

    `locale: str`
    :   The locale of the user

    `name: str`
    :   Deprecated property

    `self: str`
    :   The URL of the user

    `time_zone: str`
    :   The time zone specified in the user's profile