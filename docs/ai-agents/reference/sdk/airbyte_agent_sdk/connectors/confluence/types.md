---
id: airbyte_agent_sdk-connectors-confluence-types
title: airbyte_agent_sdk.connectors.confluence.types
---

Module airbyte_agent_sdk.connectors.confluence.types
====================================================
Type definitions for confluence connector.

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

<a id="AuditAndCondition"></a>

`AuditAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.confluence.types.AuditEqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNeqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditInCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLikeCondition | airbyte_agent_sdk.connectors.confluence.types.AuditFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.AuditKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.AuditContainsCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNotCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAndCondition | airbyte_agent_sdk.connectors.confluence.types.AuditOrCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAnyCondition]`
    :   The type of the None singleton.

<a id="AuditAnyCondition"></a>

`AuditAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.confluence.types.AuditAnyValueFilter`
    :   The type of the None singleton.

<a id="AuditAnyValueFilter"></a>

`AuditAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `affected_object: Any`
    :   The object that was affected by the audit event.

    `associated_objects: Any`
    :   Any associated objects related to the audit event.

    `author: Any`
    :   The user who triggered the audit event.

    `category: Any`
    :   The category under which the audit event falls.

    `changed_values: Any`
    :   Details of the values that were changed during the audit event.

    `creation_date: Any`
    :   The date and time when the audit event was created.

    `description: Any`
    :   A detailed description of the audit event.

    `remote_address: Any`
    :   The IP address from which the audit event originated.

    `summary: Any`
    :   A brief summary or title describing the audit event.

    `super_admin: Any`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: Any`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="AuditContainsCondition"></a>

`AuditContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.AuditAnyValueFilter`
    :   The type of the None singleton.

<a id="AuditEqCondition"></a>

`AuditEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

<a id="AuditFuzzyCondition"></a>

`AuditFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.AuditStringFilter`
    :   The type of the None singleton.

<a id="AuditGtCondition"></a>

`AuditGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

<a id="AuditGteCondition"></a>

`AuditGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

<a id="AuditInCondition"></a>

`AuditInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.confluence.types.AuditInFilter`
    :   The type of the None singleton.

<a id="AuditInFilter"></a>

`AuditInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `affected_object: list[dict[str, typing.Any]]`
    :   The object that was affected by the audit event.

    `associated_objects: list[list[typing.Any]]`
    :   Any associated objects related to the audit event.

    `author: list[dict[str, typing.Any]]`
    :   The user who triggered the audit event.

    `category: list[str]`
    :   The category under which the audit event falls.

    `changed_values: list[list[typing.Any]]`
    :   Details of the values that were changed during the audit event.

    `creation_date: list[int]`
    :   The date and time when the audit event was created.

    `description: list[str]`
    :   A detailed description of the audit event.

    `remote_address: list[str]`
    :   The IP address from which the audit event originated.

    `summary: list[str]`
    :   A brief summary or title describing the audit event.

    `super_admin: list[bool]`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: list[bool]`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="AuditKeywordCondition"></a>

`AuditKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.AuditStringFilter`
    :   The type of the None singleton.

<a id="AuditLikeCondition"></a>

`AuditLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.AuditStringFilter`
    :   The type of the None singleton.

<a id="AuditListParams"></a>

`AuditListParams(*args, **kwargs)`
:   Parameters for audit.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end_date: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `search_string: str`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

<a id="AuditLtCondition"></a>

`AuditLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

<a id="AuditLteCondition"></a>

`AuditLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

<a id="AuditNeqCondition"></a>

`AuditNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

<a id="AuditNotCondition"></a>

`AuditNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.confluence.types.AuditEqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNeqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditInCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLikeCondition | airbyte_agent_sdk.connectors.confluence.types.AuditFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.AuditKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.AuditContainsCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNotCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAndCondition | airbyte_agent_sdk.connectors.confluence.types.AuditOrCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAnyCondition`
    :   The type of the None singleton.

<a id="AuditOrCondition"></a>

`AuditOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.confluence.types.AuditEqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNeqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditInCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLikeCondition | airbyte_agent_sdk.connectors.confluence.types.AuditFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.AuditKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.AuditContainsCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNotCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAndCondition | airbyte_agent_sdk.connectors.confluence.types.AuditOrCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAnyCondition]`
    :   The type of the None singleton.

<a id="AuditSearchFilter"></a>

`AuditSearchFilter(*args, **kwargs)`
:   Available fields for filtering audit search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `affected_object: dict[str, typing.Any] | None`
    :   The object that was affected by the audit event.

    `associated_objects: list[typing.Any] | None`
    :   Any associated objects related to the audit event.

    `author: dict[str, typing.Any] | None`
    :   The user who triggered the audit event.

    `category: str | None`
    :   The category under which the audit event falls.

    `changed_values: list[typing.Any] | None`
    :   Details of the values that were changed during the audit event.

    `creation_date: int | None`
    :   The date and time when the audit event was created.

    `description: str | None`
    :   A detailed description of the audit event.

    `remote_address: str | None`
    :   The IP address from which the audit event originated.

    `summary: str | None`
    :   A brief summary or title describing the audit event.

    `super_admin: bool | None`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: bool | None`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="AuditSearchQuery"></a>

`AuditSearchQuery(*args, **kwargs)`
:   Search query for audit entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.AuditEqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNeqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditInCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLikeCondition | airbyte_agent_sdk.connectors.confluence.types.AuditFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.AuditKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.AuditContainsCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNotCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAndCondition | airbyte_agent_sdk.connectors.confluence.types.AuditOrCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.AuditSortFilter]`
    :   The type of the None singleton.

<a id="AuditSortFilter"></a>

`AuditSortFilter(*args, **kwargs)`
:   Available fields for sorting audit search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `affected_object: Literal['asc', 'desc']`
    :   The object that was affected by the audit event.

    `associated_objects: Literal['asc', 'desc']`
    :   Any associated objects related to the audit event.

    `author: Literal['asc', 'desc']`
    :   The user who triggered the audit event.

    `category: Literal['asc', 'desc']`
    :   The category under which the audit event falls.

    `changed_values: Literal['asc', 'desc']`
    :   Details of the values that were changed during the audit event.

    `creation_date: Literal['asc', 'desc']`
    :   The date and time when the audit event was created.

    `description: Literal['asc', 'desc']`
    :   A detailed description of the audit event.

    `remote_address: Literal['asc', 'desc']`
    :   The IP address from which the audit event originated.

    `summary: Literal['asc', 'desc']`
    :   A brief summary or title describing the audit event.

    `super_admin: Literal['asc', 'desc']`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: Literal['asc', 'desc']`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="AuditStringFilter"></a>

`AuditStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `affected_object: str`
    :   The object that was affected by the audit event.

    `associated_objects: str`
    :   Any associated objects related to the audit event.

    `author: str`
    :   The user who triggered the audit event.

    `category: str`
    :   The category under which the audit event falls.

    `changed_values: str`
    :   Details of the values that were changed during the audit event.

    `creation_date: str`
    :   The date and time when the audit event was created.

    `description: str`
    :   A detailed description of the audit event.

    `remote_address: str`
    :   The IP address from which the audit event originated.

    `summary: str`
    :   A brief summary or title describing the audit event.

    `super_admin: str`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: str`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="BlogPostsAndCondition"></a>

`BlogPostsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.confluence.types.BlogPostsEqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsInCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNotCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAndCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsOrCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyCondition]`
    :   The type of the None singleton.

<a id="BlogPostsAnyCondition"></a>

`BlogPostsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyValueFilter`
    :   The type of the None singleton.

<a id="BlogPostsAnyValueFilter"></a>

`BlogPostsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Any`
    :   ID of the user who created the blog post

    `body: Any`
    :   Blog post body content

    `created_at: Any`
    :   Timestamp when the blog post was created

    `id: Any`
    :   Unique blog post identifier

    `links: Any`
    :   Links related to the blog post

    `space_id: Any`
    :   ID of the space containing this blog post

    `status: Any`
    :   Blog post status (current, draft, trashed)

    `title: Any`
    :   Blog post title

    `version: Any`
    :   Version information

<a id="BlogPostsContainsCondition"></a>

`BlogPostsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyValueFilter`
    :   The type of the None singleton.

<a id="BlogPostsEqCondition"></a>

`BlogPostsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

<a id="BlogPostsFuzzyCondition"></a>

`BlogPostsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.BlogPostsStringFilter`
    :   The type of the None singleton.

<a id="BlogPostsGetParams"></a>

`BlogPostsGetParams(*args, **kwargs)`
:   Parameters for blog_posts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_format: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `version: int`
    :   The type of the None singleton.

<a id="BlogPostsGtCondition"></a>

`BlogPostsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

<a id="BlogPostsGteCondition"></a>

`BlogPostsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

<a id="BlogPostsInCondition"></a>

`BlogPostsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.confluence.types.BlogPostsInFilter`
    :   The type of the None singleton.

<a id="BlogPostsInFilter"></a>

`BlogPostsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: list[str]`
    :   ID of the user who created the blog post

    `body: list[dict[str, typing.Any]]`
    :   Blog post body content

    `created_at: list[str]`
    :   Timestamp when the blog post was created

    `id: list[str]`
    :   Unique blog post identifier

    `links: list[dict[str, typing.Any]]`
    :   Links related to the blog post

    `space_id: list[str]`
    :   ID of the space containing this blog post

    `status: list[str]`
    :   Blog post status (current, draft, trashed)

    `title: list[str]`
    :   Blog post title

    `version: list[dict[str, typing.Any]]`
    :   Version information

<a id="BlogPostsKeywordCondition"></a>

`BlogPostsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.BlogPostsStringFilter`
    :   The type of the None singleton.

<a id="BlogPostsLikeCondition"></a>

`BlogPostsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.BlogPostsStringFilter`
    :   The type of the None singleton.

<a id="BlogPostsListParams"></a>

`BlogPostsListParams(*args, **kwargs)`
:   Parameters for blog_posts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_format: str`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `space_id: list[int]`
    :   The type of the None singleton.

    `status: list[str]`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="BlogPostsLtCondition"></a>

`BlogPostsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

<a id="BlogPostsLteCondition"></a>

`BlogPostsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

<a id="BlogPostsNeqCondition"></a>

`BlogPostsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

<a id="BlogPostsNotCondition"></a>

`BlogPostsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.confluence.types.BlogPostsEqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsInCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNotCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAndCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsOrCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyCondition`
    :   The type of the None singleton.

<a id="BlogPostsOrCondition"></a>

`BlogPostsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.confluence.types.BlogPostsEqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsInCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNotCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAndCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsOrCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyCondition]`
    :   The type of the None singleton.

<a id="BlogPostsSearchFilter"></a>

`BlogPostsSearchFilter(*args, **kwargs)`
:   Available fields for filtering blog_posts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str | None`
    :   ID of the user who created the blog post

    `body: dict[str, typing.Any] | None`
    :   Blog post body content

    `created_at: str | None`
    :   Timestamp when the blog post was created

    `id: str | None`
    :   Unique blog post identifier

    `links: dict[str, typing.Any] | None`
    :   Links related to the blog post

    `space_id: str | None`
    :   ID of the space containing this blog post

    `status: str | None`
    :   Blog post status (current, draft, trashed)

    `title: str | None`
    :   Blog post title

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="BlogPostsSearchQuery"></a>

`BlogPostsSearchQuery(*args, **kwargs)`
:   Search query for blog_posts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.BlogPostsEqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsInCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNotCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAndCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsOrCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.BlogPostsSortFilter]`
    :   The type of the None singleton.

<a id="BlogPostsSortFilter"></a>

`BlogPostsSortFilter(*args, **kwargs)`
:   Available fields for sorting blog_posts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Literal['asc', 'desc']`
    :   ID of the user who created the blog post

    `body: Literal['asc', 'desc']`
    :   Blog post body content

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the blog post was created

    `id: Literal['asc', 'desc']`
    :   Unique blog post identifier

    `links: Literal['asc', 'desc']`
    :   Links related to the blog post

    `space_id: Literal['asc', 'desc']`
    :   ID of the space containing this blog post

    `status: Literal['asc', 'desc']`
    :   Blog post status (current, draft, trashed)

    `title: Literal['asc', 'desc']`
    :   Blog post title

    `version: Literal['asc', 'desc']`
    :   Version information

<a id="BlogPostsStringFilter"></a>

`BlogPostsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str`
    :   ID of the user who created the blog post

    `body: str`
    :   Blog post body content

    `created_at: str`
    :   Timestamp when the blog post was created

    `id: str`
    :   Unique blog post identifier

    `links: str`
    :   Links related to the blog post

    `space_id: str`
    :   ID of the space containing this blog post

    `status: str`
    :   Blog post status (current, draft, trashed)

    `title: str`
    :   Blog post title

    `version: str`
    :   Version information

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

    `and: list[airbyte_agent_sdk.connectors.confluence.types.GroupsEqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsInCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNotCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAndCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsOrCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.confluence.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsAnyValueFilter"></a>

`GroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   The unique identifier of the group

    `links: Any`
    :   Links related to the group

    `name: Any`
    :   The name of the group

    `type_: Any`
    :   The type of group

<a id="GroupsContainsCondition"></a>

`GroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsEqCondition"></a>

`GroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsFuzzyCondition"></a>

`GroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsGtCondition"></a>

`GroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsGteCondition"></a>

`GroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.confluence.types.GroupsInFilter`
    :   The type of the None singleton.

<a id="GroupsInFilter"></a>

`GroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   The unique identifier of the group

    `links: list[dict[str, typing.Any]]`
    :   Links related to the group

    `name: list[str]`
    :   The name of the group

    `type_: list[str]`
    :   The type of group

<a id="GroupsKeywordCondition"></a>

`GroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsLikeCondition"></a>

`GroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsListParams"></a>

`GroupsListParams(*args, **kwargs)`
:   Parameters for groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

<a id="GroupsLtCondition"></a>

`GroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsLteCondition"></a>

`GroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsNeqCondition"></a>

`GroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.confluence.types.GroupsEqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsInCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNotCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAndCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsOrCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.confluence.types.GroupsEqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsInCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNotCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAndCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsOrCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupsSearchFilter"></a>

`GroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str | None`
    :   The unique identifier of the group

    `links: dict[str, typing.Any] | None`
    :   Links related to the group

    `name: str | None`
    :   The name of the group

    `type_: str | None`
    :   The type of group

<a id="GroupsSearchQuery"></a>

`GroupsSearchQuery(*args, **kwargs)`
:   Search query for groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.GroupsEqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsInCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNotCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAndCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsOrCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.GroupsSortFilter]`
    :   The type of the None singleton.

<a id="GroupsSortFilter"></a>

`GroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the group

    `links: Literal['asc', 'desc']`
    :   Links related to the group

    `name: Literal['asc', 'desc']`
    :   The name of the group

    `type_: Literal['asc', 'desc']`
    :   The type of group

<a id="GroupsStringFilter"></a>

`GroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The unique identifier of the group

    `links: str`
    :   Links related to the group

    `name: str`
    :   The name of the group

    `type_: str`
    :   The type of group

<a id="PagesAndCondition"></a>

`PagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.confluence.types.PagesEqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesInCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.PagesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNotCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAndCondition | airbyte_agent_sdk.connectors.confluence.types.PagesOrCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAnyCondition]`
    :   The type of the None singleton.

<a id="PagesAnyCondition"></a>

`PagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.confluence.types.PagesAnyValueFilter`
    :   The type of the None singleton.

<a id="PagesAnyValueFilter"></a>

`PagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Any`
    :   ID of the user who created the page

    `body: Any`
    :   Page body content

    `created_at: Any`
    :   Timestamp when the page was created

    `id: Any`
    :   Unique page identifier

    `last_owner_id: Any`
    :   ID of the previous page owner

    `links: Any`
    :   Links related to the page

    `owner_id: Any`
    :   ID of the current page owner

    `parent_id: Any`
    :   ID of the parent page

    `parent_type: Any`
    :   Type of the parent (page or space)

    `position: Any`
    :   Position of the page among siblings

    `space_id: Any`
    :   ID of the space containing this page

    `status: Any`
    :   Page status (current, archived, trashed, draft)

    `title: Any`
    :   Page title

    `version: Any`
    :   Version information

<a id="PagesContainsCondition"></a>

`PagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.PagesAnyValueFilter`
    :   The type of the None singleton.

<a id="PagesEqCondition"></a>

`PagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesFuzzyCondition"></a>

`PagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesGetParams"></a>

`PagesGetParams(*args, **kwargs)`
:   Parameters for pages.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_format: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `version: int`
    :   The type of the None singleton.

<a id="PagesGtCondition"></a>

`PagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesGteCondition"></a>

`PagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesInCondition"></a>

`PagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.confluence.types.PagesInFilter`
    :   The type of the None singleton.

<a id="PagesInFilter"></a>

`PagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: list[str]`
    :   ID of the user who created the page

    `body: list[dict[str, typing.Any]]`
    :   Page body content

    `created_at: list[str]`
    :   Timestamp when the page was created

    `id: list[str]`
    :   Unique page identifier

    `last_owner_id: list[str]`
    :   ID of the previous page owner

    `links: list[dict[str, typing.Any]]`
    :   Links related to the page

    `owner_id: list[str]`
    :   ID of the current page owner

    `parent_id: list[str]`
    :   ID of the parent page

    `parent_type: list[str]`
    :   Type of the parent (page or space)

    `position: list[int]`
    :   Position of the page among siblings

    `space_id: list[str]`
    :   ID of the space containing this page

    `status: list[str]`
    :   Page status (current, archived, trashed, draft)

    `title: list[str]`
    :   Page title

    `version: list[dict[str, typing.Any]]`
    :   Version information

<a id="PagesKeywordCondition"></a>

`PagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesLikeCondition"></a>

`PagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.PagesStringFilter`
    :   The type of the None singleton.

<a id="PagesListParams"></a>

`PagesListParams(*args, **kwargs)`
:   Parameters for pages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_format: str`
    :   The type of the None singleton.

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `space_id: list[int]`
    :   The type of the None singleton.

    `status: list[str]`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="PagesLtCondition"></a>

`PagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesLteCondition"></a>

`PagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesNeqCondition"></a>

`PagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

<a id="PagesNotCondition"></a>

`PagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.confluence.types.PagesEqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesInCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.PagesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNotCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAndCondition | airbyte_agent_sdk.connectors.confluence.types.PagesOrCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAnyCondition`
    :   The type of the None singleton.

<a id="PagesOrCondition"></a>

`PagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.confluence.types.PagesEqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesInCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.PagesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNotCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAndCondition | airbyte_agent_sdk.connectors.confluence.types.PagesOrCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAnyCondition]`
    :   The type of the None singleton.

<a id="PagesSearchFilter"></a>

`PagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering pages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str | None`
    :   ID of the user who created the page

    `body: dict[str, typing.Any] | None`
    :   Page body content

    `created_at: str | None`
    :   Timestamp when the page was created

    `id: str | None`
    :   Unique page identifier

    `last_owner_id: str | None`
    :   ID of the previous page owner

    `links: dict[str, typing.Any] | None`
    :   Links related to the page

    `owner_id: str | None`
    :   ID of the current page owner

    `parent_id: str | None`
    :   ID of the parent page

    `parent_type: str | None`
    :   Type of the parent (page or space)

    `position: int | None`
    :   Position of the page among siblings

    `space_id: str | None`
    :   ID of the space containing this page

    `status: str | None`
    :   Page status (current, archived, trashed, draft)

    `title: str | None`
    :   Page title

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="PagesSearchQuery"></a>

`PagesSearchQuery(*args, **kwargs)`
:   Search query for pages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.PagesEqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesInCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.PagesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNotCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAndCondition | airbyte_agent_sdk.connectors.confluence.types.PagesOrCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.PagesSortFilter]`
    :   The type of the None singleton.

<a id="PagesSortFilter"></a>

`PagesSortFilter(*args, **kwargs)`
:   Available fields for sorting pages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Literal['asc', 'desc']`
    :   ID of the user who created the page

    `body: Literal['asc', 'desc']`
    :   Page body content

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the page was created

    `id: Literal['asc', 'desc']`
    :   Unique page identifier

    `last_owner_id: Literal['asc', 'desc']`
    :   ID of the previous page owner

    `links: Literal['asc', 'desc']`
    :   Links related to the page

    `owner_id: Literal['asc', 'desc']`
    :   ID of the current page owner

    `parent_id: Literal['asc', 'desc']`
    :   ID of the parent page

    `parent_type: Literal['asc', 'desc']`
    :   Type of the parent (page or space)

    `position: Literal['asc', 'desc']`
    :   Position of the page among siblings

    `space_id: Literal['asc', 'desc']`
    :   ID of the space containing this page

    `status: Literal['asc', 'desc']`
    :   Page status (current, archived, trashed, draft)

    `title: Literal['asc', 'desc']`
    :   Page title

    `version: Literal['asc', 'desc']`
    :   Version information

<a id="PagesStringFilter"></a>

`PagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str`
    :   ID of the user who created the page

    `body: str`
    :   Page body content

    `created_at: str`
    :   Timestamp when the page was created

    `id: str`
    :   Unique page identifier

    `last_owner_id: str`
    :   ID of the previous page owner

    `links: str`
    :   Links related to the page

    `owner_id: str`
    :   ID of the current page owner

    `parent_id: str`
    :   ID of the parent page

    `parent_type: str`
    :   Type of the parent (page or space)

    `position: str`
    :   Position of the page among siblings

    `space_id: str`
    :   ID of the space containing this page

    `status: str`
    :   Page status (current, archived, trashed, draft)

    `title: str`
    :   Page title

    `version: str`
    :   Version information

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

    `and: list[airbyte_agent_sdk.connectors.confluence.types.SpacesEqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesInCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNotCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAndCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesOrCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.confluence.types.SpacesAnyValueFilter`
    :   The type of the None singleton.

<a id="SpacesAnyValueFilter"></a>

`SpacesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Any`
    :   ID of the user who created the space

    `created_at: Any`
    :   Timestamp when the space was created

    `description: Any`
    :   Space description in various formats

    `homepage_id: Any`
    :   ID of the space homepage

    `icon: Any`
    :   Space icon information

    `id: Any`
    :   Unique space identifier

    `key: Any`
    :   Space key

    `links: Any`
    :   Links related to the space

    `name: Any`
    :   Space name

    `status: Any`
    :   Space status (current or archived)

    `type_: Any`
    :   Space type (global or personal)

<a id="SpacesContainsCondition"></a>

`SpacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.SpacesAnyValueFilter`
    :   The type of the None singleton.

<a id="SpacesEqCondition"></a>

`SpacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesFuzzyCondition"></a>

`SpacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.SpacesStringFilter`
    :   The type of the None singleton.

<a id="SpacesGetParams"></a>

`SpacesGetParams(*args, **kwargs)`
:   Parameters for spaces.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description_format: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="SpacesGtCondition"></a>

`SpacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesGteCondition"></a>

`SpacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.confluence.types.SpacesInFilter`
    :   The type of the None singleton.

<a id="SpacesInFilter"></a>

`SpacesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: list[str]`
    :   ID of the user who created the space

    `created_at: list[str]`
    :   Timestamp when the space was created

    `description: list[dict[str, typing.Any]]`
    :   Space description in various formats

    `homepage_id: list[str]`
    :   ID of the space homepage

    `icon: list[dict[str, typing.Any]]`
    :   Space icon information

    `id: list[str]`
    :   Unique space identifier

    `key: list[str]`
    :   Space key

    `links: list[dict[str, typing.Any]]`
    :   Links related to the space

    `name: list[str]`
    :   Space name

    `status: list[str]`
    :   Space status (current or archived)

    `type_: list[str]`
    :   Space type (global or personal)

<a id="SpacesKeywordCondition"></a>

`SpacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.SpacesStringFilter`
    :   The type of the None singleton.

<a id="SpacesLikeCondition"></a>

`SpacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.SpacesStringFilter`
    :   The type of the None singleton.

<a id="SpacesListParams"></a>

`SpacesListParams(*args, **kwargs)`
:   Parameters for spaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

    ### Methods

    `keys(self, /) ‑> list[str]`
    :   Return a set-like object providing a view on the dict's keys.

<a id="SpacesLtCondition"></a>

`SpacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesLteCondition"></a>

`SpacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

<a id="SpacesNeqCondition"></a>

`SpacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.confluence.types.SpacesEqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesInCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNotCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAndCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesOrCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.confluence.types.SpacesEqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesInCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNotCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAndCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesOrCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAnyCondition]`
    :   The type of the None singleton.

<a id="SpacesSearchFilter"></a>

`SpacesSearchFilter(*args, **kwargs)`
:   Available fields for filtering spaces search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str | None`
    :   ID of the user who created the space

    `created_at: str | None`
    :   Timestamp when the space was created

    `description: dict[str, typing.Any] | None`
    :   Space description in various formats

    `homepage_id: str | None`
    :   ID of the space homepage

    `icon: dict[str, typing.Any] | None`
    :   Space icon information

    `id: str | None`
    :   Unique space identifier

    `key: str | None`
    :   Space key

    `links: dict[str, typing.Any] | None`
    :   Links related to the space

    `name: str | None`
    :   Space name

    `status: str | None`
    :   Space status (current or archived)

    `type_: str | None`
    :   Space type (global or personal)

<a id="SpacesSearchQuery"></a>

`SpacesSearchQuery(*args, **kwargs)`
:   Search query for spaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.SpacesEqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesInCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNotCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAndCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesOrCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.SpacesSortFilter]`
    :   The type of the None singleton.

<a id="SpacesSortFilter"></a>

`SpacesSortFilter(*args, **kwargs)`
:   Available fields for sorting spaces search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Literal['asc', 'desc']`
    :   ID of the user who created the space

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the space was created

    `description: Literal['asc', 'desc']`
    :   Space description in various formats

    `homepage_id: Literal['asc', 'desc']`
    :   ID of the space homepage

    `icon: Literal['asc', 'desc']`
    :   Space icon information

    `id: Literal['asc', 'desc']`
    :   Unique space identifier

    `key: Literal['asc', 'desc']`
    :   Space key

    `links: Literal['asc', 'desc']`
    :   Links related to the space

    `name: Literal['asc', 'desc']`
    :   Space name

    `status: Literal['asc', 'desc']`
    :   Space status (current or archived)

    `type_: Literal['asc', 'desc']`
    :   Space type (global or personal)

<a id="SpacesStringFilter"></a>

`SpacesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str`
    :   ID of the user who created the space

    `created_at: str`
    :   Timestamp when the space was created

    `description: str`
    :   Space description in various formats

    `homepage_id: str`
    :   ID of the space homepage

    `icon: str`
    :   Space icon information

    `id: str`
    :   Unique space identifier

    `key: str`
    :   Space key

    `links: str`
    :   Links related to the space

    `name: str`
    :   Space name

    `status: str`
    :   Space status (current or archived)

    `type_: str`
    :   Space type (global or personal)