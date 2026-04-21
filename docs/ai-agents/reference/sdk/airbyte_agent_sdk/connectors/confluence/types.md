---
id: airbyte_agent_sdk-connectors-confluence-types
title: airbyte_agent_sdk.connectors.confluence.types
---

Module airbyte_agent_sdk.connectors.confluence.types
====================================================
Type definitions for confluence connector.

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

`AuditContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.AuditAnyValueFilter`
    :   The type of the None singleton.

`AuditEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

`AuditFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.AuditStringFilter`
    :   The type of the None singleton.

`AuditGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

`AuditGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

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

`AuditKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.AuditStringFilter`
    :   The type of the None singleton.

`AuditLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.AuditStringFilter`
    :   The type of the None singleton.

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

`AuditLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

`AuditLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

`AuditNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.AuditSearchFilter`
    :   The type of the None singleton.

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

`AuditSearchQuery(*args, **kwargs)`
:   Search query for audit entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.AuditEqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNeqCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditGteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLtCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLteCondition | airbyte_agent_sdk.connectors.confluence.types.AuditInCondition | airbyte_agent_sdk.connectors.confluence.types.AuditLikeCondition | airbyte_agent_sdk.connectors.confluence.types.AuditFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.AuditKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.AuditContainsCondition | airbyte_agent_sdk.connectors.confluence.types.AuditNotCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAndCondition | airbyte_agent_sdk.connectors.confluence.types.AuditOrCondition | airbyte_agent_sdk.connectors.confluence.types.AuditAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.AuditSortFilter]`
    :   The type of the None singleton.

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

`BlogPostsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyValueFilter`
    :   The type of the None singleton.

`BlogPostsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

`BlogPostsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.BlogPostsStringFilter`
    :   The type of the None singleton.

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

`BlogPostsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

`BlogPostsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

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

`BlogPostsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.BlogPostsStringFilter`
    :   The type of the None singleton.

`BlogPostsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.BlogPostsStringFilter`
    :   The type of the None singleton.

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

`BlogPostsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

`BlogPostsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

`BlogPostsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.BlogPostsSearchFilter`
    :   The type of the None singleton.

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

`BlogPostsSearchQuery(*args, **kwargs)`
:   Search query for blog_posts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.BlogPostsEqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsGteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLtCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLteCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsInCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsNotCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAndCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsOrCondition | airbyte_agent_sdk.connectors.confluence.types.BlogPostsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.BlogPostsSortFilter]`
    :   The type of the None singleton.

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

`GroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

`GroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.GroupsStringFilter`
    :   The type of the None singleton.

`GroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

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

`GroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.GroupsStringFilter`
    :   The type of the None singleton.

`GroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.GroupsStringFilter`
    :   The type of the None singleton.

`GroupsListParams(*args, **kwargs)`
:   Parameters for groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `start: int`
    :   The type of the None singleton.

`GroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.GroupsSearchFilter`
    :   The type of the None singleton.

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

`GroupsSearchQuery(*args, **kwargs)`
:   Search query for groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.GroupsEqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsGteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLtCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLteCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsInCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsNotCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAndCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsOrCondition | airbyte_agent_sdk.connectors.confluence.types.GroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.GroupsSortFilter]`
    :   The type of the None singleton.

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

`PagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.PagesAnyValueFilter`
    :   The type of the None singleton.

`PagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.PagesStringFilter`
    :   The type of the None singleton.

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

`PagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

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

`PagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.PagesStringFilter`
    :   The type of the None singleton.

`PagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.PagesStringFilter`
    :   The type of the None singleton.

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

`PagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

`PagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.PagesSearchFilter`
    :   The type of the None singleton.

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

`PagesSearchQuery(*args, **kwargs)`
:   Search query for pages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.PagesEqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesGteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLtCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLteCondition | airbyte_agent_sdk.connectors.confluence.types.PagesInCondition | airbyte_agent_sdk.connectors.confluence.types.PagesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.PagesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.PagesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.PagesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.PagesNotCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAndCondition | airbyte_agent_sdk.connectors.confluence.types.PagesOrCondition | airbyte_agent_sdk.connectors.confluence.types.PagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.PagesSortFilter]`
    :   The type of the None singleton.

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

`SpacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.confluence.types.SpacesAnyValueFilter`
    :   The type of the None singleton.

`SpacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

`SpacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.confluence.types.SpacesStringFilter`
    :   The type of the None singleton.

`SpacesGetParams(*args, **kwargs)`
:   Parameters for spaces.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description_format: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`SpacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

`SpacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

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

`SpacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.confluence.types.SpacesStringFilter`
    :   The type of the None singleton.

`SpacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.confluence.types.SpacesStringFilter`
    :   The type of the None singleton.

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

`SpacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

`SpacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

`SpacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.confluence.types.SpacesSearchFilter`
    :   The type of the None singleton.

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

`SpacesSearchQuery(*args, **kwargs)`
:   Search query for spaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.confluence.types.SpacesEqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNeqCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesGteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLtCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLteCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesInCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesLikeCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesFuzzyCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesKeywordCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesContainsCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesNotCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAndCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesOrCondition | airbyte_agent_sdk.connectors.confluence.types.SpacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.confluence.types.SpacesSortFilter]`
    :   The type of the None singleton.

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